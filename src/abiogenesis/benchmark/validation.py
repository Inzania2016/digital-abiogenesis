"""Dependency-free cross-file validation for benchmark contract 1.0."""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from abiogenesis.benchmark.artifacts import sha256_file
from abiogenesis.benchmark.catalog import (
    BENCHMARK_VERSION,
    CANONICAL_POLICY_IDS,
    CONTRACT_VERSION,
    resolve_policies,
    resolve_scenario,
    resolve_suite,
)
from abiogenesis.benchmark.models import METRIC_KEYS, SUMMARY_HEADINGS, RunStatus

RUN_ID_PATTERN = re.compile(r"^\d{8}T\d{6}Z_[a-z0-9-]+_[a-z0-9-]+_[0-9a-f]{4}$")
ABSOLUTE_WINDOWS_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")
AGGREGATE_KEYS = {"count", "mean", "population_stddev", "min", "max"}


class ArtifactValidationError(ValueError):
    """Raised with all detected artifact contract violations."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("Artifact validation failed:\n- " + "\n- ".join(errors))


def _load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"Missing required file: {path.name}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"Could not parse {path.name}: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.name} must contain a JSON object.")
        return None
    return value


def _require_keys(payload: dict[str, Any], keys: set[str], label: str, errors: list[str]) -> None:
    missing = sorted(keys - payload.keys())
    if missing:
        errors.append(f"{label} is missing keys: {', '.join(missing)}")


def _deviation_codes(manifest: dict[str, Any]) -> set[str]:
    deviations = manifest.get("deviations", [])
    if not isinstance(deviations, list):
        return set()
    return {
        deviation.get("code")
        for deviation in deviations
        if isinstance(deviation, dict) and isinstance(deviation.get("code"), str)
    }


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _validate_manifest(
    manifest: dict[str, Any],
    run_directory: Path,
    errors: list[str],
) -> tuple[Any, Any] | None:
    required = {
        "contract_version",
        "benchmark_version",
        "run_id",
        "status",
        "started_at",
        "completed_at",
        "scenario_id",
        "suite_id",
        "source",
        "runtime",
        "environment",
        "policies",
        "seeds",
        "budgets",
        "invocation",
        "artifacts",
        "verification",
        "deviations",
        "notes",
    }
    error_count = len(errors)
    _require_keys(manifest, required, "manifest", errors)
    if len(errors) != error_count:
        return None

    if manifest["contract_version"] != CONTRACT_VERSION:
        errors.append(f"Unsupported contract version: {manifest['contract_version']!r}")
    if manifest["benchmark_version"] != BENCHMARK_VERSION:
        errors.append(f"Unsupported benchmark version: {manifest['benchmark_version']!r}")

    run_id = manifest["run_id"]
    if not isinstance(run_id, str) or not RUN_ID_PATTERN.fullmatch(run_id):
        errors.append(f"Invalid run ID format: {run_id!r}")
    elif run_id != run_directory.name:
        errors.append(
            f"Manifest run ID {run_id!r} does not match directory {run_directory.name!r}."
        )

    try:
        status = RunStatus(manifest["status"])
    except (TypeError, ValueError):
        errors.append(f"Invalid manifest status: {manifest['status']!r}")
        status = None
    if status is not None:
        terminal = {
            RunStatus.COMPLETED,
            RunStatus.PARTIAL,
            RunStatus.FAILED,
            RunStatus.INTERRUPTED,
        }
        if status in terminal and not manifest["completed_at"]:
            errors.append(f"{status.value} manifest requires completed_at.")
        if status not in terminal and manifest["completed_at"] is not None:
            errors.append(f"{status.value} manifest must not set completed_at.")
        if status is RunStatus.PARTIAL and not manifest["deviations"]:
            errors.append("partial manifest requires at least one deviation.")

    try:
        scenario = resolve_scenario(manifest["scenario_id"])
        suite = resolve_suite(manifest["suite_id"])
    except (TypeError, ValueError) as error:
        errors.append(str(error))
        return None

    environment = manifest["environment"]
    expected_environment = {
        "training": asdict(scenario.training_config),
        "evaluation": asdict(scenario.evaluation_config),
    }
    if environment != expected_environment:
        errors.append("Manifest environment does not match the scenario registry.")

    policies = manifest["policies"]
    if not isinstance(policies, list):
        errors.append("Manifest policies must be an array.")
        policy_ids: tuple[str, ...] = ()
    else:
        policy_ids = tuple(
            policy.get("policy_id") if isinstance(policy, dict) else None for policy in policies
        )
        if not all(isinstance(policy_id, str) for policy_id in policy_ids):
            errors.append("Every manifest policy requires a string policy_id.")
            policy_ids = ()
        else:
            try:
                resolved = resolve_policies(policy_ids)
            except ValueError as error:
                errors.append(str(error))
            else:
                for declaration, policy in zip(policies, resolved, strict=True):
                    if declaration.get("agent_type") != policy.agent_type:
                        errors.append(f"{policy.policy_id} agent_type does not match catalog.")
                    if declaration.get("encoder") != policy.encoder:
                        errors.append(f"{policy.policy_id} encoder does not match catalog.")
                    shaping = declaration.get("reward_shaping")
                    expected_shaping = {
                        "loop_penalty": policy.loop_penalty,
                        "novelty_reward": policy.novelty_reward,
                    }
                    if shaping != expected_shaping:
                        errors.append(f"{policy.policy_id} reward_shaping does not match catalog.")

    if status is RunStatus.COMPLETED and policy_ids != CANONICAL_POLICY_IDS:
        errors.append("completed canonical run requires every canonical policy in order.")

    source = manifest["source"]
    if not isinstance(source, dict):
        errors.append("Manifest source must be an object.")
    elif status is RunStatus.COMPLETED:
        if (
            source.get("kind") != "git"
            or not isinstance(source.get("commit"), str)
            or source.get("dirty") is not False
        ):
            errors.append("completed canonical run requires a known clean Git source.")
        if manifest["deviations"]:
            errors.append("completed canonical run must not declare deviations.")

    deviations = _deviation_codes(manifest)
    test_smoke = "test-smoke-profile" in deviations
    seeds = manifest["seeds"]
    expected_seeds = {
        "replicate_roots": list(suite.replicate_roots),
        "training_roots": list(suite.training_roots),
        "evaluation_roots": list(suite.evaluation_roots),
    }
    if not isinstance(seeds, dict):
        errors.append("Manifest seeds must be an object.")
    else:
        for key, expected in expected_seeds.items():
            if not test_smoke and seeds.get(key) != expected:
                errors.append(f"Manifest {key} does not match suite order.")
        if not isinstance(seeds.get("derivation"), str):
            errors.append("Manifest seed derivation must be a string.")

    budgets = manifest["budgets"]
    expected_budgets = {
        "training_episodes_per_learned_policy_per_seed": suite.training_episodes,
        "evaluation_episodes_per_policy_per_seed": suite.evaluation_episodes,
    }
    if not isinstance(budgets, dict):
        errors.append("Manifest budgets must be an object.")
    else:
        for key, expected in expected_budgets.items():
            if not test_smoke and budgets.get(key) != expected:
                errors.append(f"Manifest {key} does not match suite budget.")
        if budgets.get("policy_count") != len(policy_ids):
            errors.append("Manifest policy_count does not match policy declarations.")
        learned_count = sum(policy_id != "random" for policy_id in policy_ids)
        if budgets.get("learned_policy_count") != learned_count:
            errors.append("Manifest learned_policy_count does not match policy declarations.")

    serialized = json.dumps(manifest, ensure_ascii=True)
    if ABSOLUTE_WINDOWS_PATH_PATTERN.search(serialized):
        errors.append("Manifest contains an absolute Windows path.")
    return scenario, suite


def _validate_metrics(
    manifest: dict[str, Any],
    metrics: dict[str, Any],
    errors: list[str],
) -> None:
    required = {
        "contract_version",
        "benchmark_version",
        "run_id",
        "scenario_id",
        "suite_id",
        "example_only",
        "policies",
    }
    _require_keys(metrics, required, "metrics", errors)
    for key in (
        "contract_version",
        "benchmark_version",
        "run_id",
        "scenario_id",
        "suite_id",
    ):
        if metrics.get(key) != manifest.get(key):
            errors.append(f"metrics {key} does not match manifest.")
    if not isinstance(metrics.get("example_only"), bool):
        errors.append("metrics example_only must be boolean.")

    manifest_policies = manifest.get("policies", [])
    expected_policy_ids = [
        policy.get("policy_id") for policy in manifest_policies if isinstance(policy, dict)
    ]
    policy_records = metrics.get("policies")
    if not isinstance(policy_records, list):
        errors.append("metrics policies must be an array.")
        return
    actual_policy_ids = [
        record.get("policy_id") for record in policy_records if isinstance(record, dict)
    ]
    if actual_policy_ids != expected_policy_ids:
        errors.append("Metrics policy order does not match manifest.")

    seeds = manifest.get("seeds", {})
    replicate_roots = seeds.get("replicate_roots", []) if isinstance(seeds, dict) else []
    training_roots = seeds.get("training_roots", []) if isinstance(seeds, dict) else []
    evaluation_roots = seeds.get("evaluation_roots", []) if isinstance(seeds, dict) else []
    budgets = manifest.get("budgets", {})
    train_episodes = (
        budgets.get("training_episodes_per_learned_policy_per_seed", 0)
        if isinstance(budgets, dict)
        else 0
    )
    eval_episodes = (
        budgets.get("evaluation_episodes_per_policy_per_seed", 0)
        if isinstance(budgets, dict)
        else 0
    )

    for record in policy_records:
        if not isinstance(record, dict):
            errors.append("Each policy result must be an object.")
            continue
        policy_id = record.get("policy_id")
        per_seed = record.get("per_seed")
        aggregate = record.get("aggregate")
        if not isinstance(per_seed, list):
            errors.append(f"{policy_id} per_seed must be an array.")
            continue
        if [item.get("replicate_seed") for item in per_seed if isinstance(item, dict)] != list(
            replicate_roots
        ):
            errors.append(f"{policy_id} per_seed replicate order does not match manifest.")
        values_by_metric: dict[str, list[float]] = {key: [] for key in METRIC_KEYS}
        for index, seed_record in enumerate(per_seed):
            if not isinstance(seed_record, dict):
                errors.append(f"{policy_id} seed record {index} must be an object.")
                continue
            if (
                index >= len(training_roots)
                or index >= len(evaluation_roots)
                or index >= len(replicate_roots)
            ):
                errors.append(f"{policy_id} has more seed records than the manifest.")
                continue
            expected_training_seed = None if policy_id == "random" else training_roots[index]
            expected_training_count = 0 if policy_id == "random" else train_episodes
            comparisons = {
                "training_seed": expected_training_seed,
                "evaluation_seed": evaluation_roots[index],
                "training_episode_count": expected_training_count,
                "evaluation_episode_count": eval_episodes,
            }
            for key, expected in comparisons.items():
                if seed_record.get(key) != expected:
                    errors.append(f"{policy_id} seed {index} has invalid {key}.")
            values = seed_record.get("metrics")
            if not isinstance(values, dict) or set(values) != set(METRIC_KEYS):
                errors.append(f"{policy_id} seed {index} metric keys do not match contract.")
                continue
            if seed_record.get("sample_count") != values["episode_count"]:
                errors.append(f"{policy_id} seed {index} sample_count mismatch.")
            for key, value in values.items():
                if value is not None:
                    if not _is_number(value):
                        errors.append(f"{policy_id} seed {index} {key} is not finite numeric.")
                    else:
                        values_by_metric[key].append(float(value))

        if not isinstance(aggregate, dict) or set(aggregate) != set(METRIC_KEYS):
            errors.append(f"{policy_id} aggregate metric keys do not match contract.")
            continue
        for key, values in values_by_metric.items():
            aggregate_value = aggregate[key]
            if not values:
                if aggregate_value is not None:
                    errors.append(f"{policy_id} {key} aggregate must be null.")
                continue
            if not isinstance(aggregate_value, dict) or set(aggregate_value) != AGGREGATE_KEYS:
                errors.append(f"{policy_id} {key} aggregate shape is invalid.")
                continue
            mean = sum(values) / len(values)
            expected = {
                "count": len(values),
                "mean": mean,
                "population_stddev": math.sqrt(
                    sum((value - mean) ** 2 for value in values) / len(values)
                ),
                "min": min(values),
                "max": max(values),
            }
            for aggregate_key, expected_value in expected.items():
                actual = aggregate_value.get(aggregate_key)
                if not _is_number(actual) or not math.isclose(
                    float(actual), float(expected_value), rel_tol=1e-12, abs_tol=1e-12
                ):
                    errors.append(
                        f"{policy_id} {key} {aggregate_key} does not match per-seed values."
                    )


def _validate_artifacts(
    run_directory: Path,
    manifest: dict[str, Any],
    summary_text: str | None,
    errors: list[str],
) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("Manifest artifacts must be an object.")
        return
    declared_paths = {"manifest.json"}
    for key in ("metrics", "summary"):
        declaration = artifacts.get(key)
        if not isinstance(declaration, dict):
            errors.append(f"Missing {key} artifact declaration.")
            continue
        relative_path = declaration.get("path")
        digest = declaration.get("sha256")
        if not isinstance(relative_path, str):
            errors.append(f"{key} artifact path must be a string.")
            continue
        path = run_directory / relative_path
        declared_paths.add(Path(relative_path).as_posix())
        if not path.is_file():
            errors.append(f"Declared artifact is missing: {relative_path}")
        elif not isinstance(digest, str) or sha256_file(path) != digest:
            errors.append(f"Artifact hash mismatch: {relative_path}")

    policy_declarations = artifacts.get("policies")
    if not isinstance(policy_declarations, list):
        errors.append("artifacts policies must be an array.")
        policy_declarations = []
    for declaration in policy_declarations:
        if not isinstance(declaration, dict):
            errors.append("Policy artifact declaration must be an object.")
            continue
        required_policy_fields = {
            "policy_id",
            "path",
            "format",
            "sha256",
            "load_command",
            "byte_count",
        }
        missing = sorted(required_policy_fields - declaration.keys())
        if missing:
            errors.append(f"Policy artifact declaration is missing: {', '.join(missing)}")
            continue
        relative_path = declaration.get("path")
        if not isinstance(relative_path, str) or not relative_path.startswith("policy/"):
            errors.append("Policy artifact path must be under policy/.")
            continue
        path = run_directory / relative_path
        declared_paths.add(Path(relative_path).as_posix())
        if not path.is_file():
            errors.append(f"Declared policy artifact is missing: {relative_path}")
        elif sha256_file(path) != declaration.get("sha256"):
            errors.append(f"Policy artifact hash mismatch: {relative_path}")
        elif path.stat().st_size != declaration.get("byte_count"):
            errors.append(f"Policy artifact byte_count mismatch: {relative_path}")

    policy_directory = run_directory / "policy"
    if not policy_declarations and policy_directory.exists():
        errors.append("policy/ exists without declared policy artifacts.")
    actual_paths = {
        path.relative_to(run_directory).as_posix()
        for path in run_directory.rglob("*")
        if path.is_file() and not path.name.startswith(".")
    }
    undeclared = sorted(actual_paths - declared_paths)
    if undeclared:
        errors.append(f"Run directory contains undeclared files: {', '.join(undeclared)}")

    if summary_text is not None:
        for heading in SUMMARY_HEADINGS:
            if f"## {heading}" not in summary_text:
                errors.append(f"summary.md is missing heading: {heading}")


def validate_run(run_directory: str | Path) -> None:
    """Validate a run directory or raise one error containing every violation."""

    path = Path(run_directory)
    errors: list[str] = []
    if not path.is_dir():
        raise ArtifactValidationError([f"Run directory does not exist: {path}"])
    manifest = _load_json(path / "manifest.json", errors)
    metrics = _load_json(path / "metrics.json", errors)
    summary_path = path / "summary.md"
    summary_text = summary_path.read_text(encoding="utf-8") if summary_path.is_file() else None
    if summary_text is None:
        errors.append("Missing required file: summary.md")

    if manifest is not None:
        _validate_manifest(manifest, path, errors)
    if manifest is not None and metrics is not None:
        _validate_metrics(manifest, metrics, errors)
    if manifest is not None:
        _validate_artifacts(path, manifest, summary_text, errors)
    if errors:
        raise ArtifactValidationError(errors)
