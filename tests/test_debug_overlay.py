import numpy as np

from abiogenesis.agents import QLearningAgent
from abiogenesis.agents.q_learning_agent import encode_conflict_scent_observation
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.render.debug_overlay import (
    format_q_debug_overlay,
    format_q_values,
    format_scent_lines,
    q_values_for_state,
)


def test_q_values_for_state_does_not_insert_missing_state() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(food_count=0, poison_count=0))
    agent = QLearningAgent(env.action_space)
    state = (0, 0, 0, 0, 2)

    values = q_values_for_state(agent, state)

    assert np.array_equal(values, np.zeros(5))
    assert state not in agent.q_table


def test_format_q_values_names_all_actions() -> None:
    text = format_q_values(np.array([0.1, 0.2, 0.3, 0.4, 0.5]))

    assert "north=0.100" in text
    assert "south=0.200" in text
    assert "east=0.300" in text
    assert "west=0.400" in text
    assert "wait=0.500" in text


def test_format_scent_lines_for_raw_scent_state() -> None:
    state = (
        0,
        0,
        0,
        0,
        2,
        1,
        0,
        0,
        0,
        2,
        1,
        0,
        2,
    )

    lines = format_scent_lines(state=state, encoder_name="scent")

    assert lines == [
        "food scent: north=strong, south=weak, east=none, west=none",
        "poison scent: north=none, south=strong, east=weak, west=none",
    ]


def test_format_scent_lines_for_conflict_scent_state() -> None:
    state = (0, 0, 0, 0, 1, 2, 3, 4, 2)

    lines = format_scent_lines(state=state, encoder_name="conflict-scent")

    assert lines == ["conflict scent: north=food, south=poison, east=both, west=adjacent-poison"]


def test_format_scent_lines_for_loop_scent_state() -> None:
    state = (0, 0, 0, 0, 1, 2, 3, 4, 2, 3, 1)

    lines = format_scent_lines(state=state, encoder_name="loop-scent")

    assert lines == [
        "conflict scent: north=food, south=poison, east=both, west=adjacent-poison",
        "loop: previous_action=3:west, bucket=1 (length-2)",
    ]


def test_format_scent_lines_for_novelty_scent_state() -> None:
    state = (0, 0, 0, 0, 1, 2, 3, 4, 2, 0, 1, 2, 2)

    lines = format_scent_lines(state=state, encoder_name="novelty-scent")

    assert lines == [
        "conflict scent: north=food, south=poison, east=both, west=adjacent-poison",
        "novelty: north=blocked, south=visited, east=unvisited, west=unvisited",
    ]


def test_format_q_debug_overlay_includes_policy_details() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(width=5, height=5, food_count=0, poison_count=0))
    observation, _ = env.reset(seed=1)
    env.organism = (2, 2)
    env.food[0, 2] = 1
    observation = env._observation()
    agent = QLearningAgent(
        env.action_space,
        encoder=encode_conflict_scent_observation,
    )
    state = agent.encoder(observation)
    agent.q_table[state] = np.array([0.0, 0.1, 0.5, 0.2, 0.3])

    overlay = format_q_debug_overlay(
        agent=agent,
        observation=observation,
        encoder_name="conflict-scent",
        chosen_action=2,
    )

    assert "encoder: conflict-scent" in overlay
    assert f"state: {state}" in overlay
    assert "chosen action: 2:east" in overlay
    assert "best table action: 2:east" in overlay
    assert "q-values:" in overlay
    assert "conflict scent:" in overlay
