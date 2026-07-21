"""A small tabular Q-learning agent for Bacterium-0."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import gymnasium as gym
import numpy as np

from abiogenesis.envs.sensors import directional_scents


TileCode = int
State = tuple[int, ...]
ObservationEncoder = Callable[[dict[str, np.ndarray]], State]

EMPTY = 0
FOOD = 1
POISON = 2
WALL = 3

NO_DIRECTIONAL_SIGNAL = 0
FOOD_ONLY_SIGNAL = 1
POISON_ONLY_SIGNAL = 2
BOTH_FOOD_AND_POISON_SIGNAL = 3
ADJACENT_POISON_SIGNAL = 4


class QLearningAgent:
    """Tabular Q-learning over local sensor states.

    State layout:
    north tile, south tile, east tile, west tile, energy bucket.
    """

    def __init__(
        self,
        action_space: gym.Space,
        *,
        alpha: float = 0.2,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        min_epsilon: float = 0.05,
        seed: int | None = None,
        encoder: ObservationEncoder | None = None,
    ) -> None:
        if not isinstance(action_space, gym.spaces.Discrete):
            raise TypeError("QLearningAgent requires a discrete action space.")

        self.action_space = action_space
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self.rng = np.random.default_rng(seed)
        self.q_table: dict[State, np.ndarray] = {}
        self.encoder = encoder or encode_observation

    @property
    def action_count(self) -> int:
        return int(self.action_space.n)

    def act(self, observation: dict[str, np.ndarray], *, explore: bool = True) -> int:
        """Choose an action with epsilon-greedy exploration."""

        state = self.encoder(observation)
        if explore and self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.action_count))
        return self.best_action(state)

    def best_action(self, state: State) -> int:
        """Return a greedy action, breaking ties deterministically by RNG."""

        q_values = self._values(state)
        best_value = np.max(q_values)
        candidates = np.flatnonzero(q_values == best_value)
        return int(self.rng.choice(candidates))

    def update(
        self,
        state: State,
        action: int,
        reward: float,
        next_state: State,
        *,
        done: bool,
    ) -> float:
        """Apply the Q-learning update and return the new Q value."""

        q_values = self._values(state)
        next_best = 0.0 if done else float(np.max(self._values(next_state)))
        target = reward + self.gamma * next_best
        q_values[action] += self.alpha * (target - q_values[action])
        return float(q_values[action])

    def decay_epsilon(self) -> float:
        """Decay exploration after an episode."""

        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        return self.epsilon

    def save(self, path: str | Path) -> None:
        """Save the Q-table to a small JSON file."""

        payload: dict[str, Any] = {
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "epsilon_decay": self.epsilon_decay,
            "min_epsilon": self.min_epsilon,
            "q_table": [
                {"state": list(state), "values": values.tolist()}
                for state, values in sorted(self.q_table.items())
            ],
        }
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self, path: str | Path) -> None:
        """Load a Q-table saved by :meth:`save`."""

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        self.alpha = float(payload["alpha"])
        self.gamma = float(payload["gamma"])
        self.epsilon = float(payload["epsilon"])
        self.epsilon_decay = float(payload["epsilon_decay"])
        self.min_epsilon = float(payload["min_epsilon"])
        self.q_table = {
            tuple(item["state"]): np.array(item["values"], dtype=np.float64)
            for item in payload["q_table"]
        }

    def _values(self, state: State) -> np.ndarray:
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_count, dtype=np.float64)
        return self.q_table[state]


def encode_observation(observation: dict[str, np.ndarray]) -> State:
    """Encode a full environment observation into a small local discrete state."""

    x, y = (int(value) for value in observation["organism"])
    food = observation["food"]
    poison = observation["poison"]
    height, width = food.shape

    return (
        _tile_at(x, y - 1, width, height, food, poison),
        _tile_at(x, y + 1, width, height, food, poison),
        _tile_at(x + 1, y, width, height, food, poison),
        _tile_at(x - 1, y, width, height, food, poison),
        _energy_bucket(int(observation["energy"][0])),
    )


def encode_scent_observation(observation: dict[str, np.ndarray]) -> State:
    """Encode local tiles, directional scents, and energy for tabular learning.

    State layout:
    north tile, south tile, east tile, west tile,
    north/south/east/west food scent,
    north/south/east/west poison scent,
    energy bucket.
    """

    local_state = encode_observation(observation)
    x, y = (int(value) for value in observation["organism"])
    organism = (x, y)
    food_scents = directional_scents(
        organism=organism,
        targets=observation["food"],
    )
    poison_scents = directional_scents(
        organism=organism,
        targets=observation["poison"],
    )

    return (
        *local_state[:4],
        *food_scents,
        *poison_scents,
        local_state[4],
    )


def encode_conflict_scent_observation(observation: dict[str, np.ndarray]) -> State:
    """Encode local tiles, directional food/poison conflict, and energy.

    Directional conflict values:
    0 = no signal
    1 = food only
    2 = poison only
    3 = both food and poison
    4 = adjacent poison
    """

    local_state = encode_observation(observation)
    x, y = (int(value) for value in observation["organism"])
    organism = (x, y)
    food_scents = directional_scents(
        organism=organism,
        targets=observation["food"],
    )
    poison_scents = directional_scents(
        organism=organism,
        targets=observation["poison"],
    )
    conflict_scents = tuple(
        _conflict_signal(food_scent, poison_scent)
        for food_scent, poison_scent in zip(food_scents, poison_scents, strict=True)
    )

    return (
        *local_state[:4],
        *conflict_scents,
        local_state[4],
    )


def _conflict_signal(food_scent: int, poison_scent: int) -> int:
    if poison_scent == 2:
        return ADJACENT_POISON_SIGNAL
    if food_scent and poison_scent:
        return BOTH_FOOD_AND_POISON_SIGNAL
    if poison_scent:
        return POISON_ONLY_SIGNAL
    if food_scent:
        return FOOD_ONLY_SIGNAL
    return NO_DIRECTIONAL_SIGNAL


def _tile_at(
    x: int,
    y: int,
    width: int,
    height: int,
    food: np.ndarray,
    poison: np.ndarray,
) -> TileCode:
    if x < 0 or x >= width or y < 0 or y >= height:
        return WALL
    if food[y, x]:
        return FOOD
    if poison[y, x]:
        return POISON
    return EMPTY


def _energy_bucket(energy: int) -> int:
    if energy <= 5:
        return 0
    if energy <= 15:
        return 1
    return 2
