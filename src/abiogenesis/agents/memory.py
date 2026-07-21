"""Tiny episode memory for tabular encoders."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from abiogenesis.agents.q_learning_agent import State, encode_conflict_scent_observation
from abiogenesis.core.types import Position

NO_PREVIOUS_ACTION = 5
NOVELTY_BLOCKED = 0
NOVELTY_VISITED = 1
NOVELTY_UNVISITED = 2


@dataclass
class TinyMemoryTracker:
    """Track only the last action and repeated-position streak."""

    previous_action: int = NO_PREVIOUS_ACTION
    previous_position: Position | None = None
    same_position: bool = False
    repeat_count: int = 0

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        """Reset memory at the start of an episode."""

        self.previous_action = NO_PREVIOUS_ACTION
        self.previous_position = _position_from_observation(observation)
        self.same_position = False
        self.repeat_count = 0

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        """Update memory after an environment step has produced an observation."""

        current_position = _position_from_observation(observation)
        self.same_position = current_position == self.previous_position
        self.repeat_count = self.repeat_count + 1 if self.same_position else 0
        self.previous_action = int(action)
        self.previous_position = current_position

    @property
    def repeat_bucket(self) -> int:
        """Return a compact repeat streak bucket."""

        if self.repeat_count <= 0:
            return 0
        if self.repeat_count == 1:
            return 1
        return 2


class MemoryScentEncoder:
    """Conflict-scent encoder augmented with tiny episode memory."""

    def __init__(self) -> None:
        self.memory = TinyMemoryTracker()

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        self.memory.reset(observation)

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        self.memory.update_after_step(action=action, observation=observation)

    def __call__(self, observation: dict[str, np.ndarray]) -> State:
        return encode_memory_scent_observation(observation, memory=self.memory)


def encode_memory_scent_observation(
    observation: dict[str, np.ndarray],
    *,
    memory: TinyMemoryTracker | None = None,
) -> State:
    """Encode conflict scent plus previous action and repeat-position memory."""

    memory = memory or TinyMemoryTracker()
    conflict_state = encode_conflict_scent_observation(observation)
    return (
        *conflict_state,
        memory.previous_action,
        int(memory.same_position),
        memory.repeat_bucket,
    )


@dataclass
class VisitMemoryTracker:
    """Track visited positions during one episode."""

    visited_positions: set[Position] | None = None
    current_position: Position | None = None
    current_tile_visited_before: bool = False

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        """Reset visited memory at the start of an episode."""

        self.current_position = _position_from_observation(observation)
        self.visited_positions = {self.current_position}
        self.current_tile_visited_before = False

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        """Update visited memory after an environment step."""

        del action
        if self.visited_positions is None:
            self.reset(observation)
            return

        self.current_position = _position_from_observation(observation)
        self.current_tile_visited_before = self.current_position in self.visited_positions
        self.visited_positions.add(self.current_position)

    @property
    def unique_tiles_visited(self) -> int:
        """Return the number of unique positions seen this episode."""

        return len(self.visited_positions or set())

    def adjacent_visited_flags(self) -> tuple[int, int, int, int]:
        """Return north, south, east, west visited flags."""

        if self.current_position is None:
            return (0, 0, 0, 0)
        visited = self.visited_positions or set()
        x, y = self.current_position
        return (
            int((x, y - 1) in visited),
            int((x, y + 1) in visited),
            int((x + 1, y) in visited),
            int((x - 1, y) in visited),
        )


class VisitScentEncoder:
    """Conflict-scent encoder augmented with visited-tile memory."""

    def __init__(self) -> None:
        self.memory = VisitMemoryTracker()

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        self.memory.reset(observation)

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        self.memory.update_after_step(action=action, observation=observation)

    def __call__(self, observation: dict[str, np.ndarray]) -> State:
        return encode_visit_scent_observation(observation, memory=self.memory)


def encode_visit_scent_observation(
    observation: dict[str, np.ndarray],
    *,
    memory: VisitMemoryTracker | None = None,
) -> State:
    """Encode conflict scent plus current and adjacent visited flags."""

    memory = memory or VisitMemoryTracker()
    conflict_state = encode_conflict_scent_observation(observation)
    return (
        *conflict_state,
        int(memory.current_tile_visited_before),
        *memory.adjacent_visited_flags(),
    )


@dataclass
class DirectionalNoveltyTracker:
    """Track visited positions and report adjacent novelty by direction."""

    visited_positions: set[Position] | None = None
    current_position: Position | None = None

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        """Reset novelty memory at the start of an episode."""

        self.current_position = _position_from_observation(observation)
        self.visited_positions = {self.current_position}

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        """Update novelty memory after an environment step."""

        del action
        if self.visited_positions is None:
            self.reset(observation)
            return

        self.current_position = _position_from_observation(observation)
        self.visited_positions.add(self.current_position)

    @property
    def unique_tiles_visited(self) -> int:
        """Return the number of unique positions seen this episode."""

        return len(self.visited_positions or set())

    def directional_novelty(self, observation: dict[str, np.ndarray]) -> tuple[int, int, int, int]:
        """Return north, south, east, west novelty buckets."""

        if self.current_position is None:
            self.current_position = _position_from_observation(observation)
        visited = self.visited_positions or set()
        food = observation["food"]
        height, width = food.shape
        x, y = self.current_position
        return (
            _novelty_at((x, y - 1), width=width, height=height, visited=visited),
            _novelty_at((x, y + 1), width=width, height=height, visited=visited),
            _novelty_at((x + 1, y), width=width, height=height, visited=visited),
            _novelty_at((x - 1, y), width=width, height=height, visited=visited),
        )


class NoveltyScentEncoder:
    """Conflict-scent encoder augmented with directional novelty hints."""

    def __init__(self) -> None:
        self.memory = DirectionalNoveltyTracker()

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        self.memory.reset(observation)

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        self.memory.update_after_step(action=action, observation=observation)

    def __call__(self, observation: dict[str, np.ndarray]) -> State:
        return encode_novelty_scent_observation(observation, memory=self.memory)


def encode_novelty_scent_observation(
    observation: dict[str, np.ndarray],
    *,
    memory: DirectionalNoveltyTracker | None = None,
) -> State:
    """Encode conflict scent plus directional blocked/visited/unvisited hints."""

    memory = memory or DirectionalNoveltyTracker()
    conflict_state = encode_conflict_scent_observation(observation)
    return (
        *conflict_state,
        *memory.directional_novelty(observation),
    )


@dataclass
class LoopMemoryTracker:
    """Track recent positions and detect simple movement cycles."""

    max_loop_length: int = 4
    previous_action: int = NO_PREVIOUS_ACTION
    recent_positions: deque[Position] = field(default_factory=lambda: deque(maxlen=8))
    loop_detected: bool = False
    loop_length: int = 0
    loop_detections: int = 0
    short_loops: int = 0
    medium_loops: int = 0
    long_loops: int = 0

    def __post_init__(self) -> None:
        self.recent_positions = deque(
            self.recent_positions,
            maxlen=max(4, self.max_loop_length * 2),
        )

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        """Reset loop memory at the start of an episode."""

        self.previous_action = NO_PREVIOUS_ACTION
        self.recent_positions.clear()
        self.recent_positions.append(_position_from_observation(observation))
        self.loop_detected = False
        self.loop_length = 0
        self.loop_detections = 0
        self.short_loops = 0
        self.medium_loops = 0
        self.long_loops = 0

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        """Update loop memory after an environment step."""

        self.previous_action = int(action)
        self.recent_positions.append(_position_from_observation(observation))
        self.loop_length = self._detect_loop_length()
        self.loop_detected = self.loop_length > 0
        if self.loop_detected:
            self.loop_detections += 1
            if self.loop_length == 2:
                self.short_loops += 1
            elif self.loop_length == 3:
                self.medium_loops += 1
            else:
                self.long_loops += 1

    @property
    def loop_bucket(self) -> int:
        """Return a compact loop-length bucket."""

        if self.loop_length == 0:
            return 0
        if self.loop_length == 2:
            return 1
        if self.loop_length == 3:
            return 2
        return 3

    def recent_history(self) -> tuple[Position, ...]:
        """Return recent positions for concise debugging."""

        return tuple(self.recent_positions)

    def _detect_loop_length(self) -> int:
        positions = tuple(self.recent_positions)
        for loop_length in range(2, self.max_loop_length + 1):
            needed = loop_length * 2
            if len(positions) < needed:
                continue
            if positions[-needed:-loop_length] == positions[-loop_length:]:
                return loop_length
        return 0


class LoopScentEncoder:
    """Conflict-scent encoder augmented with previous action and loop state."""

    def __init__(self) -> None:
        self.memory = LoopMemoryTracker()

    def reset(self, observation: dict[str, np.ndarray]) -> None:
        self.memory.reset(observation)

    def update_after_step(
        self,
        *,
        action: int,
        observation: dict[str, np.ndarray],
    ) -> None:
        self.memory.update_after_step(action=action, observation=observation)

    def __call__(self, observation: dict[str, np.ndarray]) -> State:
        return encode_loop_scent_observation(observation, memory=self.memory)


def encode_loop_scent_observation(
    observation: dict[str, np.ndarray],
    *,
    memory: LoopMemoryTracker | None = None,
) -> State:
    """Encode conflict scent plus previous action and loop bucket."""

    memory = memory or LoopMemoryTracker()
    conflict_state = encode_conflict_scent_observation(observation)
    return (
        *conflict_state,
        memory.previous_action,
        memory.loop_bucket,
    )


def reset_encoder_memory(encoder: Any, observation: dict[str, np.ndarray]) -> None:
    """Reset an encoder if it has episode memory."""

    reset = getattr(encoder, "reset", None)
    if reset is not None:
        reset(observation)


def update_encoder_memory(
    encoder: Any,
    *,
    action: int,
    observation: dict[str, np.ndarray],
) -> None:
    """Update an encoder if it has episode memory."""

    update = getattr(encoder, "update_after_step", None)
    if update is not None:
        update(action=action, observation=observation)


def _position_from_observation(observation: dict[str, np.ndarray]) -> Position:
    return tuple(int(value) for value in observation["organism"])


def _novelty_at(
    position: Position,
    *,
    width: int,
    height: int,
    visited: set[Position],
) -> int:
    x, y = position
    if x < 0 or x >= width or y < 0 or y >= height:
        return NOVELTY_BLOCKED
    if position in visited:
        return NOVELTY_VISITED
    return NOVELTY_UNVISITED
