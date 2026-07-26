"""Dependency-light validation for NEAT research artifacts."""

from __future__ import annotations

import configparser
import json
import re
from pathlib import Path, PurePosixPath

from abiogenesis.neuroevolution import ACTION_ORDER, FEATURE_NAMES
from abiogenesis.neuroevolution.artifacts import (
    ARTIFACT_CONTRACT,
    ARTIFACT_TYPE,
    RUN_PREFIX,
    sha256_file,
)

RUN_ID_PATTERN = re.compile(rf"^\d{{8}}T\d{{6}}Z_{re.escape(RUN_PREFIX)}_[0-9a-f]{{4}}$")
TERMINAL_STATUSES = {"completed", "partial", "failed", "interrupted"}
SUCCESS_FILES = {
    "generation_metrics.json",
    "holdout_metrics.json",
    "summary.md",
    "neat-config.ini",
    "winner_genome.pkl",
    "winner_network.json",
}


class ArtifactValidationError(ValueError):
    """Raised when a NEAT artifact violates the provisional contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactValidationError(message)


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ArtifactValidationError(f"Cannot read JSON artifact {path.name}: {error}") from error


def validate_run(run_directory: str | Path) -> dict[str, object]:
    """Validate structure, identity, dimensions, declarations, and hashes."""

    directory = Path(run_directory)
    _require(directory.is_dir(), f"Run directory does not exist: {directory}")
    manifest_path = directory / "manifest.json"
    _require(manifest_path.is_file(), "Required artifact is missing: manifest.json")
    manifest = _read_json(manifest_path)
    _require(isinstance(manifest, dict), "manifest.json must contain an object")
    assert isinstance(manifest, dict)

    run_id = manifest.get("run_id")
    _require(isinstance(run_id, str) and bool(RUN_ID_PATTERN.fullmatch(run_id)), "Invalid run_id")
    _require(directory.name == run_id, "Run directory name must match manifest run_id")
    _require(manifest.get("artifact_type") == ARTIFACT_TYPE, "Unexpected artifact_type")
    _require(
        manifest.get("artifact_contract") == ARTIFACT_CONTRACT,
        "Unexpected artifact_contract",
    )
    status = manifest.get("status")
    _require(status in TERMINAL_STATUSES, "Manifest must have a terminal status")
    _require(manifest.get("policy_id") == RUN_PREFIX, "Unexpected policy_id")
    _require(manifest.get("input_features") == list(FEATURE_NAMES), "Input feature order changed")
    _require(manifest.get("action_order") == list(ACTION_ORDER), "Action order changed")
    _require(
        manifest.get("fitness_definition")
        == "mean unmodified environment reward across ordered fitness roots and episodes",
        "Unexpected fitness definition",
    )

    seeds = manifest.get("seeds")
    _require(isinstance(seeds, dict), "seeds must be an object")
    assert isinstance(seeds, dict)
    fitness_seeds = seeds.get("fitness")
    holdout_seeds = seeds.get("holdout")
    _require(isinstance(fitness_seeds, list) and fitness_seeds, "fitness seeds are missing")
    _require(isinstance(holdout_seeds, list) and holdout_seeds, "holdout seeds are missing")
    _require(
        all(isinstance(seed, int) and seed >= 0 for seed in fitness_seeds),
        "fitness seeds must be non-negative integers",
    )
    _require(
        all(isinstance(seed, int) and seed >= 0 for seed in holdout_seeds),
        "holdout seeds must be non-negative integers",
    )
    _require(
        isinstance(seeds.get("experiment"), int) and seeds["experiment"] >= 0,
        "experiment seed must be a non-negative integer",
    )
    _require(len(set(fitness_seeds)) == len(fitness_seeds), "fitness seeds are not unique")
    _require(len(set(holdout_seeds)) == len(holdout_seeds), "holdout seeds are not unique")
    _require(not set(fitness_seeds).intersection(holdout_seeds), "seed roles overlap")

    artifacts = manifest.get("artifacts")
    _require(isinstance(artifacts, list), "artifacts must be an array")
    assert isinstance(artifacts, list)
    declared_paths: set[str] = set()
    for declaration in artifacts:
        _require(isinstance(declaration, dict), "artifact declaration must be an object")
        assert isinstance(declaration, dict)
        relative = declaration.get("path")
        digest = declaration.get("sha256")
        _require(isinstance(relative, str), "artifact path must be a string")
        path = PurePosixPath(relative)
        _require(
            not path.is_absolute() and ".." not in path.parts, "artifact path must be relative"
        )
        _require(relative not in declared_paths, f"duplicate artifact declaration: {relative}")
        declared_paths.add(relative)
        artifact_path = directory.joinpath(*path.parts)
        _require(artifact_path.is_file(), f"Declared artifact is missing: {relative}")
        _require(
            isinstance(digest, str) and digest == sha256_file(artifact_path),
            f"SHA-256 mismatch: {relative}",
        )

    if status in {"completed", "partial"}:
        _require(isinstance(manifest.get("winner"), dict), "winner metadata is missing")
        missing = SUCCESS_FILES.difference(declared_paths)
        _require(not missing, f"Required success artifacts are undeclared: {sorted(missing)}")
        config = configparser.ConfigParser()
        try:
            config.read(directory / "neat-config.ini", encoding="utf-8")
            neat = config["NEAT"]
            genome = config["DefaultGenome"]
        except (KeyError, configparser.Error) as error:
            raise ArtifactValidationError(f"Invalid effective NEAT config: {error}") from error
        _require(int(genome["num_inputs"]) == len(FEATURE_NAMES), "Config input count changed")
        _require(int(genome["num_outputs"]) == len(ACTION_ORDER), "Config output count changed")
        _require(genome.getboolean("feed_forward"), "Config is not feed-forward")
        _require(
            int(neat["pop_size"]) == manifest.get("population_size"),
            "Config population size differs from manifest",
        )
        _require(
            int(neat["seed"]) == seeds.get("experiment"),
            "Config experiment seed differs from manifest",
        )
        for filename in ("generation_metrics.json", "holdout_metrics.json", "winner_network.json"):
            _read_json(directory / filename)

    return manifest
