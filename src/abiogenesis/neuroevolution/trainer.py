"""Evolve and validate the experimental feed-forward NEAT Bacterium-0 policy."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import pickle
import random
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean

import numpy as np

from abiogenesis.benchmark.runner import runtime_identity, source_identity
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.metrics.recorder import EpisodeRecord, RunSummary
from abiogenesis.neuroevolution import ACTION_ORDER, FEATURE_NAMES, POLICY_ID
from abiogenesis.neuroevolution.artifacts import (
    ARTIFACT_CONTRACT,
    ARTIFACT_TYPE,
    artifact_declaration,
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_text,
    create_run_directory,
    format_utc,
    generate_run_id,
    utc_now,
)
from abiogenesis.neuroevolution.config import (
    DEFAULT_CONFIG_PATH,
    load_neat_config,
    require_neat,
    write_effective_config,
)
from abiogenesis.neuroevolution.fitness import (
    EvaluationBatch,
    evaluate_network,
    validate_seed_roles,
)
from abiogenesis.neuroevolution.validation import RUN_ID_PATTERN, validate_run
from abiogenesis.training.evaluate_q_learning import run_greedy_episode
from abiogenesis.training.train_q_learning import train_q_learning
from abiogenesis.training.train_random import run_episode as run_random_episode

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_ROOT = REPOSITORY_ROOT / "runs" / "neat"
FITNESS_DEFINITION = "mean unmodified environment reward across ordered fitness roots and episodes"


@dataclass(frozen=True)
class ExperimentSettings:
    """Resolved bounded experiment settings."""

    config_path: Path = DEFAULT_CONFIG_PATH
    population_size: int = 30
    generations: int = 10
    fitness_seeds: tuple[int, ...] = (21, 22, 23)
    holdout_seeds: tuple[int, ...] = (31, 32, 33)
    episodes_per_seed: int = 5
    output_root: Path = DEFAULT_OUTPUT_ROOT
    experiment_seed: int = 21
    workers: int = 1
    run_id: str | None = None
    baseline_training_episodes: int = 200

    def validate(self) -> None:
        validate_seed_roles(self.fitness_seeds, self.holdout_seeds)
        if self.population_size < 2:
            raise ValueError("population-size must be at least 2")
        if self.generations < 1:
            raise ValueError("generations must be at least 1")
        if self.episodes_per_seed < 1:
            raise ValueError("episodes-per-seed must be at least 1")
        if self.experiment_seed < 0:
            raise ValueError("experiment-seed must be non-negative")
        if self.workers != 1:
            raise ValueError("RS-01 supports workers=1 only")
        if self.baseline_training_episodes < 1:
            raise ValueError("baseline-training-episodes must be at least 1")
        if self.run_id is not None and not RUN_ID_PATTERN.fullmatch(self.run_id):
            raise ValueError("run-id does not match the NEAT research run ID format")
        if not self.config_path.is_file():
            raise ValueError(f"NEAT configuration does not exist: {self.config_path}")


def _parse_seeds(value: str) -> tuple[int, ...]:
    try:
        seeds = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as error:
        raise argparse.ArgumentTypeError("seeds must be comma-separated integers") from error
    if not seeds:
        raise argparse.ArgumentTypeError("seed list must not be empty")
    return seeds


def _artifact(path: Path, run_directory: Path, media_type: str) -> dict[str, object]:
    return artifact_declaration(path, run_directory=run_directory, media_type=media_type)


def _summary_dict(summary: RunSummary) -> dict[str, int | float]:
    return asdict(summary)


def _evaluate_baselines(
    settings: ExperimentSettings,
    config: BacteriaWorldConfig,
) -> dict[str, object]:
    """Run a small explicitly noncanonical comparison on holdout worlds."""

    random_records: list[EpisodeRecord] = []
    local_records: list[EpisodeRecord] = []
    novelty_records: list[EpisodeRecord] = []
    for index, holdout_seed in enumerate(settings.holdout_seeds):
        training_seed = settings.fitness_seeds[index % len(settings.fitness_seeds)]
        local_agent, _, _ = train_q_learning(
            seed=training_seed,
            episodes=settings.baseline_training_episodes,
            encoder_name="local",
            config=config,
        )
        novelty_agent, _, _ = train_q_learning(
            seed=training_seed,
            episodes=settings.baseline_training_episodes,
            encoder_name="novelty-scent",
            novelty_reward=0.0,
            config=config,
        )
        for episode_index in range(settings.episodes_per_seed):
            episode_seed = holdout_seed + episode_index
            random_records.append(run_random_episode(seed=episode_seed, config=config))
            local_records.append(
                run_greedy_episode(
                    agent=local_agent, seed=episode_seed, grid_size=10, config=config
                )
            )
            novelty_records.append(
                run_greedy_episode(
                    agent=novelty_agent,
                    seed=episode_seed,
                    grid_size=10,
                    config=config,
                    novelty_reward=0.0,
                )
            )

    seed_label = settings.holdout_seeds[0]
    return {
        "status": "exploratory-noncanonical",
        "warning": (
            "Q-learning training budgets are a bounded RS-01 convenience, not the canonical "
            "Bacterium-0 benchmark suite and not a promotion test for NEAT."
        ),
        "q_learning_training_episodes_per_holdout_root": settings.baseline_training_episodes,
        "random": _summary_dict(
            RunSummary.from_records(records=random_records, seed=seed_label, grid_size=10)
        ),
        "local-q": _summary_dict(
            RunSummary.from_records(records=local_records, seed=seed_label, grid_size=10)
        ),
        "novelty-scent-q": _summary_dict(
            RunSummary.from_records(records=novelty_records, seed=seed_label, grid_size=10)
        ),
    }


def _render_summary(
    *,
    manifest: dict[str, object],
    fitness: EvaluationBatch,
    holdout: EvaluationBatch,
    comparison: dict[str, object],
) -> str:
    comparison_lines = []
    for policy_id in ("random", "local-q", "novelty-scent-q"):
        metrics = comparison[policy_id]
        assert isinstance(metrics, dict)
        comparison_lines.append(f"- `{policy_id}` mean reward: {metrics['average_reward']:.6f}")
    return "\n".join(
        [
            "# Experimental NEAT Research Run",
            "",
            "This is exploratory, noncanonical evidence. It does not alter benchmark contract 1.0.",
            "",
            "## Question",
            "",
            "Can a feed-forward NEAT policy use the existing novelty-scent representation and "
            "complete deterministic Bacterium-0 evaluation and artifact plumbing?",
            "",
            "## Fitness",
            "",
            f"- Definition: {FITNESS_DEFINITION}.",
            f"- Winner evolutionary fitness: {fitness.mean_reward:.6f}.",
            f"- Holdout mean reward: {holdout.mean_reward:.6f}.",
            "- No novelty, lifespan, food, poison, loop, or exploration shaping was used.",
            "",
            "## Exploratory Comparison",
            "",
            *comparison_lines,
            f"- `{POLICY_ID}` holdout mean reward: {holdout.mean_reward:.6f}",
            "",
            "These policies did not receive canonical R1 benchmark budgets in this run. A single "
            "bounded run cannot establish superiority or canonical eligibility.",
            "",
            "## Reproducibility",
            "",
            f"- Run ID: `{manifest['run_id']}`",
            f"- Experiment seed: `{manifest['seeds']['experiment']}`",
            f"- Fitness roots: `{manifest['seeds']['fitness']}`",
            f"- Holdout roots: `{manifest['seeds']['holdout']}`",
            "- Evaluation is serial. Environment reset seeds and order are recorded.",
            "- Cross-platform bit-for-bit reproducibility is not claimed.",
            "",
            "## Artifact Safety",
            "",
            "`winner_genome.pkl` is Python pickle data. Load only artifacts produced and retained "
            "locally by a trusted run; unpickling untrusted files can execute code.",
            "",
            "## Deviations",
            "",
            *(
                [f"- {item['code']}: {item['message']}" for item in manifest["deviations"]]
                or ["- None."]
            ),
            "",
        ]
    )


def _base_manifest(
    *,
    run_id: str,
    settings: ExperimentSettings,
    source: dict[str, object],
    command: str,
    started_at: str,
) -> dict[str, object]:
    config_path = settings.config_path.resolve()
    try:
        config_label = config_path.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        config_label = str(config_path)
    return {
        "artifact_type": ARTIFACT_TYPE,
        "artifact_contract": ARTIFACT_CONTRACT,
        "run_id": run_id,
        "status": "running",
        "research_status": "exploratory-noncanonical",
        "policy_id": POLICY_ID,
        "network_type": "feed-forward",
        "input_features": list(FEATURE_NAMES),
        "action_order": list(ACTION_ORDER),
        "fitness_definition": FITNESS_DEFINITION,
        "population_size": settings.population_size,
        "generation_count": settings.generations,
        "episodes_per_seed": settings.episodes_per_seed,
        "baseline_training_episodes": settings.baseline_training_episodes,
        "workers": settings.workers,
        "seeds": {
            "experiment": settings.experiment_seed,
            "fitness": list(settings.fitness_seeds),
            "holdout": list(settings.holdout_seeds),
            "episode_derivation": "root_seed + zero-based episode index",
        },
        "determinism": {
            "evaluation_order": "serial in recorded root, episode, and genome order",
            "seeded_sources": ["Python random", "NumPy", "NEAT population", "environment reset"],
            "strongest_tested_guarantee": (
                "same NEAT-Python version, config, and experiment seed reproduce the initial "
                "population in this runtime"
            ),
            "remaining_nondeterminism": [
                "cross-platform and dependency-version floating-point behavior",
                "wall-clock timestamps, run suffixes, and exporter metadata timestamps",
            ],
            "bit_for_bit_cross_platform_claimed": False,
        },
        "environment": asdict(BacteriaWorldConfig()),
        "reward_shaping": {"novelty_reward": 0.0, "loop_penalty": 0.0},
        "dependency": {
            "name": "neat-python",
            "version": importlib.metadata.version("neat-python"),
            "constraint": ">=2.0,<3",
        },
        "config_source": config_label,
        "source": source,
        "runtime": runtime_identity(),
        "command": command,
        "started_at": started_at,
        "finished_at": None,
        "winner": None,
        "failures": [],
        "deviations": [],
        "artifacts": [],
    }


def run_experiment(
    settings: ExperimentSettings,
    *,
    command: str = "python -m abiogenesis.neuroevolution.trainer",
) -> Path:
    """Execute one serial research run and return its validated directory."""

    settings.validate()
    neat = require_neat()
    run_id = settings.run_id or generate_run_id()
    run_directory = create_run_directory(settings.output_root, run_id)
    started_at = format_utc(utc_now())
    source = source_identity()
    manifest = _base_manifest(
        run_id=run_id,
        settings=settings,
        source=source,
        command=command,
        started_at=started_at,
    )
    manifest_path = run_directory / "manifest.json"
    atomic_write_json(manifest_path, manifest)
    config_path = run_directory / "neat-config.ini"

    try:
        write_effective_config(
            settings.config_path,
            config_path,
            population_size=settings.population_size,
            experiment_seed=settings.experiment_seed,
        )
        config = load_neat_config(neat, config_path)
        random.seed(settings.experiment_seed)
        np.random.seed(settings.experiment_seed)
        population = neat.Population(config, seed=settings.experiment_seed)
        generation_metrics: list[dict[str, object]] = []

        def evaluate_genomes(genomes, neat_config) -> None:
            rewards: list[float] = []
            winner_key: int | None = None
            winner_fitness = float("-inf")
            for genome_id, genome in genomes:
                network = neat.nn.FeedForwardNetwork.create(genome, neat_config)
                batch = evaluate_network(
                    network=network,
                    root_seeds=settings.fitness_seeds,
                    episodes_per_seed=settings.episodes_per_seed,
                )
                genome.fitness = batch.mean_reward
                rewards.append(batch.mean_reward)
                if batch.mean_reward > winner_fitness:
                    winner_key = int(genome_id)
                    winner_fitness = batch.mean_reward
            generation_metrics.append(
                {
                    "generation": len(generation_metrics),
                    "genome_count": len(rewards),
                    "mean_fitness": fmean(rewards),
                    "minimum_fitness": min(rewards),
                    "maximum_fitness": max(rewards),
                    "generation_winner_genome_id": winner_key,
                }
            )

        winner = population.run(evaluate_genomes, settings.generations)
        winner_network = neat.nn.FeedForwardNetwork.create(winner, config)
        fitness_batch = evaluate_network(
            network=winner_network,
            root_seeds=settings.fitness_seeds,
            episodes_per_seed=settings.episodes_per_seed,
        )
        holdout_batch = evaluate_network(
            network=winner_network,
            root_seeds=settings.holdout_seeds,
            episodes_per_seed=settings.episodes_per_seed,
        )
        comparison = _evaluate_baselines(settings, BacteriaWorldConfig())

        generation_path = run_directory / "generation_metrics.json"
        holdout_path = run_directory / "holdout_metrics.json"
        network_path = run_directory / "winner_network.json"
        genome_path = run_directory / "winner_genome.pkl"
        summary_path = run_directory / "summary.md"
        atomic_write_json(
            generation_path,
            {
                "fitness_definition": FITNESS_DEFINITION,
                "fitness_evaluation": fitness_batch.as_dict(),
                "generations": generation_metrics,
            },
        )
        atomic_write_json(
            holdout_path,
            {
                "seed_role": "holdout-only-after-winner-selection",
                "winner": holdout_batch.as_dict(),
                "exploratory_comparison": comparison,
            },
        )
        from neat.export import export_network_json

        network_json = export_network_json(
            winner_network,
            metadata={
                "fitness": fitness_batch.mean_reward,
                "genome_id": int(winner.key),
                "policy_id": POLICY_ID,
            },
        )
        json.loads(network_json)
        atomic_write_text(network_path, network_json + "\n")
        atomic_write_bytes(genome_path, pickle.dumps(winner, protocol=pickle.HIGHEST_PROTOCOL))

        manifest["winner"] = {
            "genome_id": int(winner.key),
            "reported_training_fitness": float(winner.fitness),
            "recomputed_training_fitness": fitness_batch.mean_reward,
            "holdout_mean_reward": holdout_batch.mean_reward,
        }
        if source.get("kind") != "git" or source.get("commit") is None:
            manifest["deviations"].append(
                {
                    "code": "source-identity-unavailable",
                    "message": "A Git commit identity was not available.",
                    "effect": "Run is partial and cannot be treated as clean-source evidence.",
                }
            )
        elif source.get("dirty") is not False:
            manifest["deviations"].append(
                {
                    "code": "source-not-clean",
                    "message": "The experiment ran from a dirty research worktree.",
                    "effect": "Run is partial and cannot be treated as clean-source evidence.",
                }
            )
        manifest["status"] = "partial" if manifest["deviations"] else "completed"
        manifest["finished_at"] = format_utc(utc_now())
        atomic_write_text(
            summary_path,
            _render_summary(
                manifest=manifest,
                fitness=fitness_batch,
                holdout=holdout_batch,
                comparison=comparison,
            ),
        )
        manifest["artifacts"] = [
            _artifact(generation_path, run_directory, "application/json"),
            _artifact(holdout_path, run_directory, "application/json"),
            _artifact(summary_path, run_directory, "text/markdown"),
            _artifact(config_path, run_directory, "text/plain"),
            _artifact(genome_path, run_directory, "application/python-pickle"),
            _artifact(network_path, run_directory, "application/json"),
        ]
        atomic_write_json(manifest_path, manifest)
        validate_run(run_directory)
        return run_directory
    except BaseException as error:
        manifest["status"] = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
        manifest["finished_at"] = format_utc(utc_now())
        manifest["failures"] = [
            {"type": type(error).__name__, "message": str(error) or type(error).__name__}
        ]
        if config_path.is_file():
            manifest["artifacts"] = [_artifact(config_path, run_directory, "text/plain")]
        atomic_write_json(manifest_path, manifest)
        raise


def _dry_run(settings: ExperimentSettings) -> None:
    settings.validate()
    neat = require_neat()
    import tempfile

    with tempfile.TemporaryDirectory(prefix="abiogenesis-neat-dry-") as temporary:
        effective = Path(temporary) / "neat-config.ini"
        write_effective_config(
            settings.config_path,
            effective,
            population_size=settings.population_size,
            experiment_seed=settings.experiment_seed,
        )
        config = load_neat_config(neat, effective)
    print("NEAT RS-01 dry run (exploratory, noncanonical)")
    print(f"neat-python: {importlib.metadata.version('neat-python')}")
    print(f"inputs: {config.genome_config.num_inputs} {list(FEATURE_NAMES)}")
    print(f"outputs: {config.genome_config.num_outputs} {list(ACTION_ORDER)}")
    print(f"experiment seed: {settings.experiment_seed}")
    print(f"fitness seeds: {list(settings.fitness_seeds)}")
    print(f"holdout seeds: {list(settings.holdout_seeds)}")
    print(
        f"budget: population={settings.population_size}, generations={settings.generations}, "
        f"episodes-per-seed={settings.episodes_per_seed}, workers={settings.workers}"
    )
    print("No run directory was created.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--population-size", type=int, default=30)
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--fitness-seeds", type=_parse_seeds, default=(21, 22, 23))
    parser.add_argument("--holdout-seeds", type=_parse_seeds, default=(31, 32, 33))
    parser.add_argument("--episodes-per-seed", type=int, default=5)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--experiment-seed", type=int, default=21)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--run-id")
    parser.add_argument("--baseline-training-episodes", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-only", type=Path)
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.validate_only is not None:
        manifest = validate_run(args.validate_only)
        print(f"Valid NEAT research run: {manifest['run_id']} ({manifest['status']})")
        return
    settings = ExperimentSettings(
        config_path=args.config,
        population_size=args.population_size,
        generations=args.generations,
        fitness_seeds=args.fitness_seeds,
        holdout_seeds=args.holdout_seeds,
        episodes_per_seed=args.episodes_per_seed,
        output_root=args.output_root,
        experiment_seed=args.experiment_seed,
        workers=args.workers,
        run_id=args.run_id,
        baseline_training_episodes=args.baseline_training_episodes,
    )
    if args.dry_run:
        _dry_run(settings)
        return
    command = subprocess.list2cmdline([sys.executable, "-m", __spec__.name, *sys.argv[1:]])
    run_directory = run_experiment(settings, command=command)
    manifest = validate_run(run_directory)
    print(f"NEAT research run: {run_directory}")
    print(f"status: {manifest['status']}")
    print(f"winner: {manifest['winner']}")


if __name__ == "__main__":
    main()
