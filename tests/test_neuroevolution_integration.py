from datetime import UTC, datetime
from pathlib import Path

import pytest

from abiogenesis.neuroevolution.artifacts import generate_run_id
from abiogenesis.neuroevolution.config import load_neat_config, write_effective_config
from abiogenesis.neuroevolution.replay import load_replay_policy
from abiogenesis.neuroevolution.trainer import ExperimentSettings, run_experiment
from abiogenesis.neuroevolution.validation import ArtifactValidationError, validate_run

neat = pytest.importorskip("neat")


def clean_source() -> dict[str, object]:
    return {
        "kind": "git",
        "repository_url": "https://example.invalid/digital-abiogenesis.git",
        "commit": "a" * 40,
        "dirty": False,
    }


def tiny_settings(tmp_path: Path, run_id: str) -> ExperimentSettings:
    return ExperimentSettings(
        population_size=4,
        generations=1,
        fitness_seeds=(1,),
        holdout_seeds=(11,),
        episodes_per_seed=1,
        output_root=tmp_path,
        experiment_seed=9,
        run_id=run_id,
        baseline_training_episodes=2,
    )


def test_population_seed_is_repeatable_and_different_seed_changes_population(
    tmp_path: Path,
) -> None:
    snapshots = []
    for seed in (9, 9, 10):
        config_path = tmp_path / f"config-{seed}-{len(snapshots)}.ini"
        write_effective_config(
            ExperimentSettings().config_path,
            config_path,
            population_size=4,
            experiment_seed=seed,
        )
        config = load_neat_config(neat, config_path)
        population = neat.Population(config, seed=seed)
        snapshots.append(tuple(str(genome) for genome in population.population.values()))

    assert snapshots[0] == snapshots[1]
    assert snapshots[0] != snapshots[2]


def test_tiny_evolution_artifacts_validation_reload_and_action(tmp_path: Path, monkeypatch) -> None:
    run_id = generate_run_id(
        now=datetime(2026, 7, 26, 12, 0, tzinfo=UTC),
        suffix="a1b2",
    )
    monkeypatch.setattr("abiogenesis.neuroevolution.trainer.source_identity", clean_source)

    run_directory = run_experiment(tiny_settings(tmp_path, run_id), command="tiny-test")
    manifest = validate_run(run_directory)
    loaded_manifest, policy = load_replay_policy(run_directory)
    environment = loaded_manifest["environment"]
    from abiogenesis.core.config import BacteriaWorldConfig
    from abiogenesis.envs import BacteriaWorldEnv

    observation, _ = BacteriaWorldEnv(BacteriaWorldConfig(**environment)).reset(seed=11)
    policy.reset(observation)

    assert manifest["status"] == "completed"
    assert manifest["winner"]["genome_id"] is not None
    assert 0 <= policy.act(observation) < 5
    expected_files = {
        "manifest.json",
        "generation_metrics.json",
        "holdout_metrics.json",
        "summary.md",
        "neat-config.ini",
        "winner_genome.pkl",
        "winner_network.json",
    }
    assert expected_files.issubset(path.name for path in run_directory.iterdir())

    network_path = run_directory / "winner_network.json"
    original = network_path.read_bytes()
    network_path.write_bytes(original + b" ")
    with pytest.raises(ArtifactValidationError, match="SHA-256"):
        validate_run(run_directory)
    network_path.write_bytes(original)
    validate_run(run_directory)

    with pytest.raises(FileExistsError):
        run_experiment(tiny_settings(tmp_path, run_id), command="tiny-test")


def test_failed_run_records_terminal_status(tmp_path: Path, monkeypatch) -> None:
    run_id = generate_run_id(
        now=datetime(2026, 7, 26, 12, 1, tzinfo=UTC),
        suffix="c3d4",
    )
    monkeypatch.setattr(
        "abiogenesis.neuroevolution.trainer.load_neat_config",
        lambda *args: (_ for _ in ()).throw(RuntimeError("deliberate test failure")),
    )

    with pytest.raises(RuntimeError, match="deliberate"):
        run_experiment(tiny_settings(tmp_path, run_id), command="failed-test")

    import json

    manifest = json.loads((tmp_path / run_id / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "failed"
    assert manifest["failures"][0]["type"] == "RuntimeError"
    assert validate_run(tmp_path / run_id)["status"] == "failed"
