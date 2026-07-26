"""Fixed, documented vector adaptation of the existing novelty-scent encoder."""

from __future__ import annotations

import numpy as np

from abiogenesis.agents.memory import NoveltyScentEncoder
from abiogenesis.envs.bacteria_world import Action

FEATURE_NAMES = (
    "north_tile",
    "south_tile",
    "east_tile",
    "west_tile",
    "north_conflict_scent",
    "south_conflict_scent",
    "east_conflict_scent",
    "west_conflict_scent",
    "energy_bucket",
    "north_novelty",
    "south_novelty",
    "east_novelty",
    "west_novelty",
)
FEATURE_MAXIMA = (3.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0, 2.0, 2.0, 2.0, 2.0, 2.0)
ACTION_ORDER = tuple(action.name.lower() for action in Action)


class ObservationAdapter:
    """Normalize novelty-scent state without reading hidden environment state."""

    def __init__(self) -> None:
        self.encoder = NoveltyScentEncoder()
        self._initialized = False

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        self.encoder.reset(observation)
        self._initialized = True

    def update(self, *, action: int, observation: dict[str, np.ndarray]) -> None:
        if not self._initialized:
            raise RuntimeError("Observation adapter must be reset before update.")
        self.encoder.update_after_step(action=action, observation=observation)

    def vector(self, observation: dict[str, np.ndarray]) -> tuple[float, ...]:
        if not self._initialized:
            raise RuntimeError("Observation adapter must be reset before encoding.")
        encoded = self.encoder(observation)
        if len(encoded) != len(FEATURE_NAMES):
            raise ValueError(
                f"novelty-scent produced {len(encoded)} values; expected {len(FEATURE_NAMES)}"
            )
        return tuple(
            float(value) / maximum for value, maximum in zip(encoded, FEATURE_MAXIMA, strict=True)
        )
