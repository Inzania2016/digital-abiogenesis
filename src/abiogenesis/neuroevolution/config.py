"""NEAT dependency and effective-configuration handling."""

from __future__ import annotations

import importlib
import re
from pathlib import Path
from types import ModuleType

from abiogenesis.benchmark.artifacts import atomic_write_text
from abiogenesis.neuroevolution.observation import ACTION_ORDER, FEATURE_NAMES

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = REPOSITORY_ROOT / "configs" / "neat" / "bacterium0-feedforward.ini"


def require_neat() -> ModuleType:
    """Load the optional dependency with an actionable failure."""

    try:
        return importlib.import_module("neat")
    except ImportError as error:
        raise RuntimeError(
            'NEAT-Python is not installed. Run python -m pip install -e ".[dev,render,neat]".'
        ) from error


def _replace_value(text: str, key: str, value: int) -> str:
    pattern = re.compile(rf"^(\s*{re.escape(key)}\s*=\s*).*$", re.MULTILINE)
    replaced, count = pattern.subn(rf"\g<1>{value}", text)
    if count != 1:
        raise ValueError(f"NEAT configuration must define {key!r} exactly once.")
    return replaced


def write_effective_config(
    source: Path,
    destination: Path,
    *,
    population_size: int,
    experiment_seed: int,
) -> None:
    """Copy the source config with the two supported runtime overrides resolved."""

    if population_size < 2:
        raise ValueError("population-size must be at least 2")
    if experiment_seed < 0:
        raise ValueError("experiment-seed must be non-negative")
    text = source.read_text(encoding="utf-8")
    text = _replace_value(text, "pop_size", population_size)
    text = _replace_value(text, "seed", experiment_seed)
    atomic_write_text(destination, text)


def load_neat_config(neat_module: ModuleType, path: Path):
    """Load and verify the feed-forward Bacterium-0 dimensions."""

    config = neat_module.Config(
        neat_module.DefaultGenome,
        neat_module.DefaultReproduction,
        neat_module.DefaultSpeciesSet,
        neat_module.DefaultStagnation,
        str(path),
    )
    if config.genome_config.num_inputs != len(FEATURE_NAMES):
        raise ValueError(
            f"NEAT num_inputs is {config.genome_config.num_inputs}; expected {len(FEATURE_NAMES)}."
        )
    if config.genome_config.num_outputs != len(ACTION_ORDER):
        raise ValueError(
            f"NEAT num_outputs is {config.genome_config.num_outputs}; expected {len(ACTION_ORDER)}."
        )
    if not config.genome_config.feed_forward:
        raise ValueError("RS-01 requires feed_forward = True.")
    return config
