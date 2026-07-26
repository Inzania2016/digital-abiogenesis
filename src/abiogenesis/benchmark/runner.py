"""Run named Bacterium-0 benchmarks and write contract 1.0 artifacts."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from dataclasses import asdict, replace
from pathlib import Path
from statistics import pstdev

from abiogenesis.agents import QLearningAgent
from abiogenesis.benchmark.artifacts import (
    artifact_declaration,
    atomic_write_json,
    atomic_write_text,
    create_run_directory,
    format_utc,
    generate_run_id,
    sha256_file,
    utc_now,
)
from abiogenesis.benchmark.catalog import (
    BENCHMARK_VERSION,
    CANONICAL_POLICY_IDS,
    CONTRACT_VERSION,
    SEED_DERIVATION,
    resolve_policies,
    resolve_scenario,
    resolve_suite,
)
from abiogenesis.benchmark.models import (
    METRIC_KEYS,
    Deviation,
    PolicyDefinition,
    RunStatus,
    ScenarioDefinition,
    SuiteDefinition,
)
from abiogenesis.benchmark.summary import render_summary
from abiogenesis.benchmark.validation import (
    RUN_ID_PATTERN,
    ArtifactValidationError,
    validate_run,
)
from abiogenesis.metrics.recorder import RunSummary
from abiogenesis.training.evaluate_q_learning import run_greedy_episode
from abiogenesis.training.train_q_learning import train_q_learning
from abiogenesis.training.train_random import evaluate_random

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def _run_git(*arguments: str) -> str | None:
    try:
        result = subprocess.run(
            ("git", *arguments),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def source_identity() -> dict[str, object]:
    commit = _run_git("rev-parse", "HEAD")
    if commit is None:
        return {
            "kind": "unknown",
            "repository_url": None,
            "commit": None,
            "dirty": None,
        }
    status = _run_git("status", "--porcelain=v1", "--untracked-files=all")
    return {
        "kind": "git",
        "repository_url": _run_git("config", "--get", "remote.origin.url"),
        "commit": commit,
        "dirty": None if status is None else bool(status),
    }


def runtime_identity() -> dict[str, str]:
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
    }


def summary_metrics(summary: RunSummary) -> dict[str, int | float]:
    return {
        "average_reward": summary.average_reward,
        "average_lifespan": summary.average_lifespan,
        "food_eaten": summary.food_eaten,
        "poison_collisions": summary.poison_collisions,
        "wasted_moves": summary.wasted_moves,
        "repeated_positions": summary.repeated_positions,
        "unique_tiles_visited": summary.unique_tiles_visited,
        "revisit_ratio": summary.revisit_ratio,
        "loop_detections": summary.loop_detections,
        "short_loops": summary.short_loops,
        "medium_loops": summary.medium_loops,
        "long_loops": summary.long_loops,
        "novelty_bonuses": summary.novelty_bonuses,
        "novelty_reward_total": summary.novelty_reward_total,
        "episode_count": summary.episodes,
    }


def aggregate_seed_metrics(
    seed_records: list[dict[str, object]],
) -> dict[str, dict[str, int | float] | None]:
    aggregates: dict[str, dict[str, int | float] | None] = {}
    for metric in METRIC_KEYS:
        values = [
            record["metrics"][metric]
            for record in seed_records
            if isinstance(record.get("metrics"), dict) and record["metrics"].get(metric) is not None
        ]
        if not values:
            aggregates[metric] = None
            continue
        numeric_values = [float(value) for value in values]
        aggregates[metric] = {
            "count": len(values),
            "mean": sum(numeric_values) / len(numeric_values),
            "population_stddev": pstdev(numeric_values),
            "min": min(values),
            "max": max(values),
        }
    return aggregates


def _policy_manifest(
    policy: PolicyDefinition,
    *,
    keep_policies: bool,
) -> dict[str, object]:
    learning = (
        {
            "alpha": 0.2,
            "gamma": 0.95,
            "epsilon_initial": 1.0,
            "epsilon_decay": 0.995,
            "epsilon_min": 0.05,
        }
        if policy.learned
        else None
    )
    return {
        "policy_id": policy.policy_id,
        "agent_type": policy.agent_type,
        "encoder": policy.encoder,
        "learning": learning,
        "reward_shaping": {
            "loop_penalty": policy.loop_penalty,
            "novelty_reward": policy.novelty_reward,
        },
        "evaluation_exploration": False,
        "policy_artifact_requested": keep_policies and policy.learned,
    }


def _base_manifest(
    *,
    run_id: str,
    scenario: ScenarioDefinition,
    suite: SuiteDefinition,
    policies: tuple[PolicyDefinition, ...],
    source: dict[str, object],
    command: str,
    started_at: str,
    deviations: tuple[Deviation, ...],
    keep_policies: bool,
) -> dict[str, object]:
    return {
        "contract_version": CONTRACT_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "run_id": run_id,
        "status": RunStatus.RUNNING.value,
        "started_at": started_at,
        "completed_at": None,
        "scenario_id": scenario.scenario_id,
        "suite_id": suite.suite_id,
        "source": source,
        "runtime": runtime_identity(),
        "environment": {
            "training": asdict(scenario.training_config),
            "evaluation": asdict(scenario.evaluation_config),
        },
        "policies": [_policy_manifest(policy, keep_policies=keep_policies) for policy in policies],
        "seeds": {
            "replicate_roots": list(suite.replicate_roots),
            "training_roots": list(suite.training_roots),
            "evaluation_roots": list(suite.evaluation_roots),
            "derivation": SEED_DERIVATION,
        },
        "budgets": {
            "training_episodes_per_learned_policy_per_seed": suite.training_episodes,
            "evaluation_episodes_per_policy_per_seed": suite.evaluation_episodes,
            "policy_count": len(policies),
            "learned_policy_count": sum(policy.learned for policy in policies),
        },
        "invocation": {
            "command": command,
            "working_directory": "repository-root",
        },
        "artifacts": {
            "metrics": {
                "path": "metrics.json",
                "media_type": "application/json",
                "sha256": None,
            },
            "summary": {
                "path": "summary.md",
                "media_type": "text/markdown",
                "sha256": None,
            },
            "policies": [],
        },
        "verification": {
            "automated": {
                "status": "not_run",
                "commands": [],
                "notes": [],
            },
            "visual": {
                "status": "not_performed",
                "verified_by": None,
                "notes": ["No pygame verification is implied by benchmark execution."],
            },
        },
        "deviations": [deviation.as_dict() for deviation in deviations],
        "notes": [
            suite.evidence_label,
            "Evaluation is greedy and does not update learned policies.",
        ],
    }


def _failed_metrics() -> dict[str, None]:
    return dict.fromkeys(METRIC_KEYS)


def _evaluate_policy_seed(
    *,
    policy: PolicyDefinition,
    replicate_seed: int,
    evaluation_seed: int,
    suite: SuiteDefinition,
    scenario: ScenarioDefinition,
) -> tuple[RunSummary, QLearningAgent | None]:
    grid_size = scenario.evaluation_config.width
    if policy.policy_id == "random":
        _, summary = evaluate_random(
            seed=evaluation_seed,
            episodes=suite.evaluation_episodes,
            grid_size=grid_size,
            config=scenario.evaluation_config,
        )
        return summary, None

    assert policy.encoder is not None
    agent, _, _ = train_q_learning(
        seed=replicate_seed,
        episodes=suite.training_episodes,
        grid_size=scenario.training_config.width,
        encoder_name=policy.encoder,
        config=scenario.training_config,
        loop_penalty=policy.loop_penalty,
        novelty_reward=policy.novelty_reward,
    )
    records = [
        run_greedy_episode(
            agent=agent,
            seed=evaluation_seed + episode_index,
            grid_size=grid_size,
            config=scenario.evaluation_config,
            loop_penalty=policy.loop_penalty,
            novelty_reward=policy.novelty_reward,
        )
        for episode_index in range(suite.evaluation_episodes)
    ]
    return (
        RunSummary.from_records(
            records=records,
            seed=evaluation_seed,
            grid_size=grid_size,
        ),
        agent,
    )


def _save_policy(
    *,
    run_directory: Path,
    policy: PolicyDefinition,
    replicate_seed: int,
    agent: QLearningAgent,
) -> dict[str, object]:
    policy_directory = run_directory / "policy"
    policy_directory.mkdir(exist_ok=True)
    filename = f"{policy.policy_id}-seed-{replicate_seed}.json"
    path = policy_directory / filename
    temporary_path = policy_directory / f".{filename}.tmp"
    agent.save(temporary_path)
    os.replace(temporary_path, path)
    relative_path = path.relative_to(run_directory).as_posix()
    return {
        "policy_id": policy.policy_id,
        "replicate_seed": replicate_seed,
        "encoder": policy.encoder,
        "path": relative_path,
        "format": "abiogenesis-q-table-json-v1",
        "sha256": sha256_file(path),
        "byte_count": path.stat().st_size,
        "load_command": (
            ".\\.venv\\Scripts\\python.exe -m abiogenesis.render.play_episode "
            f"--agent q-learning --q-path <run-directory>/{relative_path} "
            f"--encoder {policy.encoder} "
            f"--seed {replicate_seed + 100_000} --renderer ascii"
        ),
        "retention_status": "generated-ignored",
    }


def _run_policies(
    *,
    run_directory: Path,
    scenario: ScenarioDefinition,
    suite: SuiteDefinition,
    policies: tuple[PolicyDefinition, ...],
    keep_policies: bool,
) -> tuple[list[dict[str, object]], list[dict[str, object]], tuple[Deviation, ...]]:
    policy_results: list[dict[str, object]] = []
    policy_artifacts: list[dict[str, object]] = []
    deviations: list[Deviation] = []
    for policy in policies:
        seed_results: list[dict[str, object]] = []
        success_count = 0
        for replicate_seed, evaluation_seed in zip(
            suite.replicate_roots, suite.evaluation_roots, strict=True
        ):
            seed_deviations: list[dict[str, str]] = []
            try:
                summary, agent = _evaluate_policy_seed(
                    policy=policy,
                    replicate_seed=replicate_seed,
                    evaluation_seed=evaluation_seed,
                    suite=suite,
                    scenario=scenario,
                )
                metrics = summary_metrics(summary)
                seed_status = "completed"
                sample_count = summary.episodes
                success_count += 1
                if keep_policies and agent is not None:
                    policy_artifacts.append(
                        _save_policy(
                            run_directory=run_directory,
                            policy=policy,
                            replicate_seed=replicate_seed,
                            agent=agent,
                        )
                    )
            except Exception as error:  # preserve other seed evidence before terminal reporting
                message = f"{type(error).__name__}: {error}"
                deviation = Deviation(
                    code="seed-execution-failed",
                    message=(f"{policy.policy_id} replicate {replicate_seed} failed: {message}"),
                    effect="The policy and run are not complete canonical evidence.",
                )
                deviations.append(deviation)
                seed_deviations.append(deviation.as_dict())
                metrics = _failed_metrics()
                seed_status = "failed"
                sample_count = 0
            seed_results.append(
                {
                    "replicate_seed": replicate_seed,
                    "training_seed": replicate_seed if policy.learned else None,
                    "evaluation_seed": evaluation_seed,
                    "training_episode_count": (suite.training_episodes if policy.learned else 0),
                    "evaluation_episode_count": suite.evaluation_episodes,
                    "sample_count": sample_count,
                    "status": seed_status,
                    "deviations": seed_deviations,
                    "metrics": metrics,
                }
            )
        if success_count == len(suite.replicate_roots):
            policy_status = "completed"
        elif success_count:
            policy_status = "partial"
        else:
            policy_status = "failed"
        policy_results.append(
            {
                "policy_id": policy.policy_id,
                "status": policy_status,
                "per_seed": seed_results,
                "aggregate": aggregate_seed_metrics(seed_results),
            }
        )
    return policy_results, policy_artifacts, tuple(deviations)


def _portable_command(arguments: list[str]) -> str:
    executable = r".\.venv\Scripts\python.exe" if os.name == "nt" else "python"
    return subprocess.list2cmdline([executable, "-m", "abiogenesis.benchmark.runner", *arguments])


def _plan_payload(
    *,
    scenario: ScenarioDefinition,
    suite: SuiteDefinition,
    policies: tuple[PolicyDefinition, ...],
    deviations: tuple[Deviation, ...],
) -> dict[str, object]:
    return {
        "contract_version": CONTRACT_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "scenario_id": scenario.scenario_id,
        "suite_id": suite.suite_id,
        "replicate_roots": list(suite.replicate_roots),
        "training_roots": list(suite.training_roots),
        "evaluation_roots": list(suite.evaluation_roots),
        "training_episodes": suite.training_episodes,
        "evaluation_episodes": suite.evaluation_episodes,
        "training_environment": asdict(scenario.training_config),
        "evaluation_environment": asdict(scenario.evaluation_config),
        "policies": [policy.policy_id for policy in policies],
        "deviations": [deviation.as_dict() for deviation in deviations],
        "dry_run": True,
    }


def run_benchmark(
    *,
    scenario_id: str = "stable-default-v1",
    suite_id: str = "b0-quick-v1",
    output_root: Path = Path("runs"),
    policy_ids: tuple[str, ...] | None = None,
    run_id: str | None = None,
    keep_policies: bool = False,
    test_smoke: bool = False,
    command: str = "python -m abiogenesis.benchmark.runner",
) -> Path:
    """Execute a named run, write artifacts, validate, and return its directory."""

    scenario = resolve_scenario(scenario_id)
    suite = resolve_suite(suite_id)
    policies = resolve_policies(policy_ids)
    deviations: list[Deviation] = []
    if test_smoke:
        if suite.suite_id != "b0-quick-v1":
            raise ValueError("--test-smoke is compatible only with b0-quick-v1.")
        suite = replace(
            suite,
            replicate_roots=(21,),
            training_episodes=2,
            evaluation_episodes=2,
            evidence_label="noncanonical R1B test-smoke evidence only",
            canonical=False,
        )
        deviations.append(
            Deviation(
                code="test-smoke-profile",
                message="R1B test-smoke overrides quick seeds and episode budgets.",
                effect="This run is structural verification, not benchmark evidence.",
            )
        )
    if tuple(policy.policy_id for policy in policies) != CANONICAL_POLICY_IDS:
        deviations.append(
            Deviation(
                code="policy-subset",
                message="The run selected a canonical-order subset of policies.",
                effect="This run cannot be completed canonical benchmark evidence.",
            )
        )

    source = source_identity()
    if source["kind"] != "git" or source["commit"] is None or source["dirty"] is not False:
        deviations.append(
            Deviation(
                code="source-not-clean",
                message="Git source identity is unknown or the worktree is dirty.",
                effect="This run cannot be frozen canonical benchmark evidence.",
            )
        )

    effective_run_id = run_id or generate_run_id(scenario, suite)
    if not RUN_ID_PATTERN.fullmatch(effective_run_id):
        raise ValueError(f"Invalid explicit run ID: {effective_run_id!r}")
    expected_middle = f"_{scenario.scenario_id}_{suite.suite_id}_"
    if expected_middle not in effective_run_id:
        raise ValueError("Explicit run ID must contain the resolved scenario and suite IDs.")

    run_directory = create_run_directory(output_root, effective_run_id)
    started_at = format_utc(utc_now())
    manifest = _base_manifest(
        run_id=effective_run_id,
        scenario=scenario,
        suite=suite,
        policies=policies,
        source=source,
        command=command,
        started_at=started_at,
        deviations=tuple(deviations),
        keep_policies=keep_policies,
    )
    manifest_path = run_directory / "manifest.json"
    atomic_write_json(manifest_path, manifest)

    try:
        policy_results, policy_artifacts, execution_deviations = _run_policies(
            run_directory=run_directory,
            scenario=scenario,
            suite=suite,
            policies=policies,
            keep_policies=keep_policies,
        )
        deviations.extend(execution_deviations)
        metrics = {
            "contract_version": CONTRACT_VERSION,
            "benchmark_version": BENCHMARK_VERSION,
            "run_id": effective_run_id,
            "scenario_id": scenario.scenario_id,
            "suite_id": suite.suite_id,
            "example_only": False,
            "policies": policy_results,
        }
        metrics_path = run_directory / "metrics.json"
        atomic_write_json(metrics_path, metrics)
        summary_path = run_directory / "summary.md"
        atomic_write_text(
            summary_path,
            render_summary(
                run_id=effective_run_id,
                scenario=scenario,
                suite=suite,
                policies=policies,
                metrics=metrics,
                source=source,
                deviations=tuple(deviations),
            ),
        )

        all_policies_completed = all(result["status"] == "completed" for result in policy_results)
        final_status = (
            RunStatus.COMPLETED if not deviations and all_policies_completed else RunStatus.PARTIAL
        )
        manifest["status"] = final_status.value
        manifest["completed_at"] = format_utc(utc_now())
        manifest["deviations"] = [deviation.as_dict() for deviation in deviations]
        manifest["artifacts"] = {
            "metrics": artifact_declaration(
                metrics_path,
                run_directory=run_directory,
                media_type="application/json",
            ),
            "summary": artifact_declaration(
                summary_path,
                run_directory=run_directory,
                media_type="text/markdown",
            ),
            "policies": policy_artifacts,
        }
        manifest["verification"]["automated"] = {
            "status": "passed",
            "commands": ["internal dependency-free contract validation"],
            "notes": ["Validation executed after final artifact hashes were written."],
        }
        atomic_write_json(manifest_path, manifest)
        validate_run(run_directory)
    except BaseException as error:
        if isinstance(error, KeyboardInterrupt):
            failure_status = RunStatus.INTERRUPTED
        else:
            failure_status = RunStatus.FAILED
        failure = Deviation(
            code="runner-failure",
            message=f"{type(error).__name__}: {error}",
            effect="The run did not complete contract validation.",
        )
        manifest["status"] = failure_status.value
        manifest["completed_at"] = format_utc(utc_now())
        manifest["deviations"] = [
            *manifest.get("deviations", []),
            failure.as_dict(),
        ]
        manifest["verification"]["automated"] = {
            "status": "failed",
            "commands": ["internal dependency-free contract validation"],
            "notes": [str(error)],
        }
        atomic_write_json(manifest_path, manifest)
        raise
    return run_directory


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="stable-default-v1")
    parser.add_argument("--suite", default="b0-quick-v1")
    parser.add_argument("--output-root", type=Path, default=Path("runs"))
    parser.add_argument("--policies", help="Comma-separated canonical-order subset.")
    parser.add_argument("--run-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-only", type=Path)
    parser.add_argument("--keep-policies", action="store_true")
    parser.add_argument(
        "--test-smoke",
        action="store_true",
        help="Use a noncanonical one-seed, two-episode R1B verification profile.",
    )
    return parser


def main(arguments: list[str] | None = None) -> int:
    parser = _parser()
    raw_arguments = list(sys.argv[1:] if arguments is None else arguments)
    args = parser.parse_args(raw_arguments)
    try:
        if args.validate_only is not None:
            incompatible = (
                args.dry_run
                or args.keep_policies
                or args.test_smoke
                or args.policies is not None
                or args.run_id is not None
            )
            if incompatible:
                raise ValueError("--validate-only cannot be combined with execution options.")
            validate_run(args.validate_only)
            print(f"Artifact validation passed: {args.validate_only}")
            return 0

        scenario = resolve_scenario(args.scenario)
        suite = resolve_suite(args.suite)
        policy_ids = (
            tuple(part.strip() for part in args.policies.split(",") if part.strip())
            if args.policies
            else None
        )
        policies = resolve_policies(policy_ids)
        plan_deviations: list[Deviation] = []
        if args.test_smoke:
            if suite.suite_id != "b0-quick-v1":
                raise ValueError("--test-smoke is compatible only with b0-quick-v1.")
            suite = replace(
                suite,
                replicate_roots=(21,),
                training_episodes=2,
                evaluation_episodes=2,
                evidence_label="noncanonical R1B test-smoke evidence only",
                canonical=False,
            )
            plan_deviations.append(
                Deviation(
                    code="test-smoke-profile",
                    message="R1B test-smoke overrides quick seeds and episode budgets.",
                    effect="This plan is structural verification, not benchmark evidence.",
                )
            )
        if tuple(policy.policy_id for policy in policies) != CANONICAL_POLICY_IDS:
            plan_deviations.append(
                Deviation(
                    code="policy-subset",
                    message="The plan selects a canonical-order subset of policies.",
                    effect="This plan cannot become completed canonical evidence.",
                )
            )
        if args.dry_run:
            print(
                json.dumps(
                    _plan_payload(
                        scenario=scenario,
                        suite=suite,
                        policies=policies,
                        deviations=tuple(plan_deviations),
                    ),
                    indent=2,
                )
            )
            return 0

        run_directory = run_benchmark(
            scenario_id=args.scenario,
            suite_id=args.suite,
            output_root=args.output_root,
            policy_ids=policy_ids,
            run_id=args.run_id,
            keep_policies=args.keep_policies,
            test_smoke=args.test_smoke,
            command=_portable_command(raw_arguments),
        )
        manifest = json.loads((run_directory / "manifest.json").read_text(encoding="utf-8"))
        print(f"Benchmark run {manifest['status']}: {run_directory}")
        return 0
    except (ArtifactValidationError, FileExistsError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
