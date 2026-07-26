"""Feed-forward NEAT policy adapter for existing Bacterium-0 actions."""

from __future__ import annotations

import math
from typing import Protocol, Sequence

import numpy as np

from abiogenesis.neuroevolution.observation import ACTION_ORDER, ObservationAdapter


class ActivatingNetwork(Protocol):
    def activate(self, inputs: Sequence[float]) -> Sequence[float]:
        """Return one score per Bacterium-0 action."""


class NeatPolicy:
    """Choose the first maximum score in the existing action order."""

    def __init__(self, network: ActivatingNetwork) -> None:
        self.network = network
        self.observation = ObservationAdapter()
        self.last_input: tuple[float, ...] | None = None
        self.last_scores: tuple[float, ...] | None = None

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        self.observation.reset(observation)
        self.last_input = None
        self.last_scores = None

    def update(self, *, action: int, observation: dict[str, np.ndarray]) -> None:
        self.observation.update(action=action, observation=observation)

    def act(self, observation: dict[str, np.ndarray]) -> int:
        inputs = self.observation.vector(observation)
        scores = tuple(float(value) for value in self.network.activate(inputs))
        if len(scores) != len(ACTION_ORDER):
            raise ValueError(
                f"NEAT network returned {len(scores)} outputs; expected {len(ACTION_ORDER)}."
            )
        if not all(math.isfinite(value) for value in scores):
            raise ValueError("NEAT network outputs must all be finite.")
        self.last_input = inputs
        self.last_scores = scores
        return max(range(len(scores)), key=scores.__getitem__)
