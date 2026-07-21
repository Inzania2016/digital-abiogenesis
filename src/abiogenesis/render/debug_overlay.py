"""ASCII debug overlay for tabular Q-learning replay."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from abiogenesis.agents import QLearningAgent
    from abiogenesis.agents.q_learning_agent import State

DIRECTIONS = ("north", "south", "east", "west")
ACTION_NAMES = ("north", "south", "east", "west", "wait")
RAW_SCENT_LABELS = {
    0: "none",
    1: "weak",
    2: "strong",
}
CONFLICT_SCENT_LABELS = {
    0: "none",
    1: "food",
    2: "poison",
    3: "both",
    4: "adjacent-poison",
}
NOVELTY_LABELS = {
    0: "blocked",
    1: "visited",
    2: "unvisited",
}


def format_q_debug_overlay(
    *,
    agent: QLearningAgent,
    observation: dict[str, np.ndarray],
    encoder_name: str,
    chosen_action: int,
) -> str:
    """Format a read-only view of the current tabular policy state."""

    state = agent.encoder(observation)
    q_values = q_values_for_state(agent, state)
    best_action = int(np.flatnonzero(q_values == np.max(q_values))[0])

    lines = [
        "debug overlay:",
        f"  encoder: {encoder_name}",
        f"  state: {state}",
        f"  chosen action: {format_action(chosen_action)}",
        f"  best table action: {format_action(best_action)}",
        f"  q-values: {format_q_values(q_values)}",
    ]
    scent_lines = format_scent_lines(state=state, encoder_name=encoder_name)
    if scent_lines:
        lines.extend(f"  {line}" for line in scent_lines)
    return "\n".join(lines)


def q_values_for_state(agent: Any, state: State) -> np.ndarray:
    """Return Q-values without inserting a missing state into the table."""

    values = agent.q_table.get(state)
    if values is None:
        return np.zeros(agent.action_count, dtype=np.float64)
    return values.copy()


def format_action(action: int) -> str:
    """Format an action id as a stable replay label."""

    if int(action) == 5:
        return "5:none"
    return f"{int(action)}:{ACTION_NAMES[int(action)]}"


def format_q_values(q_values: np.ndarray) -> str:
    """Format all action values in action-space order."""

    return ", ".join(
        f"{ACTION_NAMES[index]}={float(value):.3f}" for index, value in enumerate(q_values)
    )


def format_scent_lines(*, state: State, encoder_name: str) -> list[str]:
    """Format scent or conflict-scent values when the encoder carries them."""

    if encoder_name == "scent" and len(state) >= 13:
        food_values = state[4:8]
        poison_values = state[8:12]
        return [
            "food scent: " + _format_direction_values(food_values, labels=RAW_SCENT_LABELS),
            "poison scent: " + _format_direction_values(poison_values, labels=RAW_SCENT_LABELS),
        ]
    if (
        encoder_name
        in {"conflict-scent", "memory-scent", "visit-scent", "loop-scent", "novelty-scent"}
        and len(state) >= 9
    ):
        lines = [
            "conflict scent: " + _format_direction_values(state[4:8], labels=CONFLICT_SCENT_LABELS)
        ]
        if encoder_name == "memory-scent" and len(state) >= 12:
            lines.append(
                "memory: "
                f"previous_action={format_action(state[-3])}, "
                f"same_position={bool(state[-2])}, "
                f"repeat_bucket={state[-1]}"
            )
        if encoder_name == "visit-scent" and len(state) >= 14:
            lines.append(
                "visited: "
                f"current={bool(state[-5])}, "
                + _format_direction_values(
                    state[-4:],
                    labels={0: "no", 1: "yes"},
                )
            )
        if encoder_name == "loop-scent" and len(state) >= 11:
            lines.append(
                "loop: "
                f"previous_action={format_action(state[-2])}, "
                f"bucket={state[-1]} ({_loop_bucket_label(state[-1])})"
            )
        if encoder_name == "novelty-scent" and len(state) >= 13:
            lines.append(
                "novelty: "
                + _format_direction_values(
                    state[-4:],
                    labels=NOVELTY_LABELS,
                )
            )
        return lines
    return []


def _format_direction_values(
    values: tuple[int, ...],
    *,
    labels: dict[int, str],
) -> str:
    return ", ".join(
        f"{direction}={labels.get(int(value), str(value))}"
        for direction, value in zip(DIRECTIONS, values, strict=True)
    )


def _loop_bucket_label(bucket: int) -> str:
    labels = {
        0: "none",
        1: "length-2",
        2: "length-3",
        3: "longer",
    }
    return labels.get(int(bucket), str(bucket))
