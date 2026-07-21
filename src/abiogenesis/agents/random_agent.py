"""A baseline agent that samples random actions."""

from typing import Any

import gymnasium as gym
import numpy as np


class RandomAgent:
    """Choose actions uniformly from an environment's action space."""

    def __init__(self, action_space: gym.Space, seed: int | None = None) -> None:
        self.action_space = action_space
        self.rng = np.random.default_rng(seed)

    def act(self, observation: Any | None = None) -> int:
        """Return a random valid action.

        The observation is accepted for a consistent agent interface, but this
        baseline ignores the world and stumbles blindly.
        """

        del observation
        if isinstance(self.action_space, gym.spaces.Discrete):
            return int(self.rng.integers(self.action_space.n))
        return int(self.action_space.sample())
