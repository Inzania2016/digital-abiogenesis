"""Gymnasium environment for Bacterium-0."""

from enum import IntEnum
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.core.types import Position
from abiogenesis.render.ascii_renderer import render_ascii


class Action(IntEnum):
    """Actions available to the organism."""

    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3
    WAIT = 4


_ACTION_DELTAS: dict[Action, Position] = {
    Action.NORTH: (0, -1),
    Action.SOUTH: (0, 1),
    Action.EAST: (1, 0),
    Action.WEST: (-1, 0),
    Action.WAIT: (0, 0),
}


class BacteriaWorldEnv(gym.Env):
    """A tiny grid-world where one organism seeks food and avoids poison."""

    metadata = {"render_modes": ["ansi"], "render_fps": 4}

    def __init__(
        self,
        config: BacteriaWorldConfig | None = None,
        render_mode: str | None = None,
    ) -> None:
        self.config = config or BacteriaWorldConfig()
        if render_mode not in (None, "ansi"):
            raise ValueError("BacteriaWorldEnv only supports render_mode='ansi'.")
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(len(Action))
        self.observation_space = spaces.Dict(
            {
                "organism": spaces.Box(
                    low=np.array([0, 0], dtype=np.int64),
                    high=np.array(
                        [self.config.width - 1, self.config.height - 1],
                        dtype=np.int64,
                    ),
                    dtype=np.int64,
                ),
                "food": spaces.MultiBinary((self.config.height, self.config.width)),
                "poison": spaces.MultiBinary((self.config.height, self.config.width)),
                "energy": spaces.Box(
                    low=0,
                    high=np.iinfo(np.int32).max,
                    shape=(1,),
                    dtype=np.int32,
                ),
                "steps": spaces.Box(
                    low=0,
                    high=self.config.max_steps,
                    shape=(1,),
                    dtype=np.int32,
                ),
            }
        )

        self.organism: Position = (0, 0)
        self.food = np.zeros((self.config.height, self.config.width), dtype=np.int8)
        self.poison = np.zeros((self.config.height, self.config.width), dtype=np.int8)
        self.energy = self.config.initial_energy
        self.steps = 0

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
        """Reset the Petri dish with deterministic placement when seeded."""

        super().reset(seed=seed)
        del options

        self.energy = self.config.initial_energy
        self.steps = 0
        self.food.fill(0)
        self.poison.fill(0)

        cell_count = self.config.width * self.config.height
        needed = 1 + self.config.food_count + self.config.poison_count
        if needed > cell_count:
            raise ValueError("World is too small for organism, food, and poison.")

        chosen = self.np_random.choice(cell_count, size=needed, replace=False)
        self.organism = self._index_to_position(int(chosen[0]))
        food_indexes = chosen[1 : 1 + self.config.food_count]
        poison_indexes = chosen[1 + self.config.food_count :]

        for index in food_indexes:
            x, y = self._index_to_position(int(index))
            self.food[y, x] = 1
        for index in poison_indexes:
            x, y = self._index_to_position(int(index))
            self.poison[y, x] = 1

        return self._observation(), self._info()

    def step(
        self,
        action: int,
    ) -> tuple[dict[str, np.ndarray], float, bool, bool, dict[str, Any]]:
        """Move the organism one tick and apply consequences."""

        action_enum = Action(int(action))
        previous_position = self.organism
        self.organism = self._move(self.organism, action_enum)
        self.steps += 1
        self.energy -= self.config.step_energy_cost

        reward = self.config.step_penalty
        x, y = self.organism
        ate_food = False
        hit_poison = False

        if self.food[y, x]:
            self.food[y, x] = 0
            self.energy += self.config.food_energy
            reward += self.config.food_reward
            ate_food = True

        if self.poison[y, x]:
            self.poison[y, x] = 0
            self.energy -= self.config.poison_energy_cost
            reward += self.config.poison_penalty
            hit_poison = True

        terminated = self.energy <= 0
        if terminated:
            self.energy = 0
        truncated = self.steps >= self.config.max_steps

        info = self._info()
        info.update(
            {
                "action": action_enum.name.lower(),
                "ate_food": ate_food,
                "hit_poison": hit_poison,
                "moved": self.organism != previous_position,
                "wasted_move": self.organism == previous_position,
            }
        )
        return self._observation(), reward, terminated, truncated, info

    def render(self) -> str:
        """Render the current world as ASCII."""

        return render_ascii(
            width=self.config.width,
            height=self.config.height,
            organism=self.organism,
            food=self.food,
            poison=self.poison,
            energy=self.energy,
            steps=self.steps,
            max_steps=self.config.max_steps,
        )

    def _move(self, position: Position, action: Action) -> Position:
        dx, dy = _ACTION_DELTAS[action]
        x, y = position
        next_x = min(max(x + dx, 0), self.config.width - 1)
        next_y = min(max(y + dy, 0), self.config.height - 1)
        return next_x, next_y

    def _index_to_position(self, index: int) -> Position:
        return index % self.config.width, index // self.config.width

    def _observation(self) -> dict[str, np.ndarray]:
        return {
            "organism": np.array(self.organism, dtype=np.int64),
            "food": self.food.copy(),
            "poison": self.poison.copy(),
            "energy": np.array([self.energy], dtype=np.int32),
            "steps": np.array([self.steps], dtype=np.int32),
        }

    def _info(self) -> dict[str, Any]:
        return {
            "energy": self.energy,
            "steps": self.steps,
            "organism": self.organism,
        }
