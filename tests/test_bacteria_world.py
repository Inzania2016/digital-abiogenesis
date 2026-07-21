import numpy as np

from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import Action, BacteriaWorldEnv
from abiogenesis.envs.sensors import (
    NO_SCENT,
    STRONG_SCENT,
    WEAK_SCENT,
    directional_scent,
)


def make_env(**kwargs) -> BacteriaWorldEnv:
    return BacteriaWorldEnv(BacteriaWorldConfig(**kwargs))


def test_reset_returns_valid_observation() -> None:
    env = make_env()

    observation, info = env.reset(seed=123)

    assert env.observation_space.contains(observation)
    assert observation["energy"][0] == env.config.initial_energy
    assert observation["steps"][0] == 0
    assert int(observation["food"].sum()) == env.config.food_count
    assert int(observation["poison"].sum()) == env.config.poison_count
    assert info["organism"] == tuple(observation["organism"])


def test_reset_is_deterministic_with_seed() -> None:
    env_a = make_env()
    env_b = make_env()

    observation_a, _ = env_a.reset(seed=42)
    observation_b, _ = env_b.reset(seed=42)

    assert np.array_equal(observation_a["organism"], observation_b["organism"])
    assert np.array_equal(observation_a["food"], observation_b["food"])
    assert np.array_equal(observation_a["poison"], observation_b["poison"])


def test_movement_changes_position() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (5, 5)

    observation, _, _, _, _ = env.step(Action.NORTH)

    assert tuple(observation["organism"]) == (5, 4)


def test_boundary_behavior_clamps_to_grid() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (0, 0)

    observation, _, _, _, _ = env.step(Action.NORTH)
    assert tuple(observation["organism"]) == (0, 0)

    observation, _, _, _, _ = env.step(Action.WEST)
    assert tuple(observation["organism"]) == (0, 0)


def test_food_reward_and_energy_gain() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (1, 1)
    env.food[1, 2] = 1

    observation, reward, terminated, truncated, info = env.step(Action.EAST)

    assert reward == env.config.step_penalty + env.config.food_reward
    assert observation["energy"][0] == (
        env.config.initial_energy - env.config.step_energy_cost + env.config.food_energy
    )
    assert observation["food"][1, 2] == 0
    assert info["ate_food"]
    assert not info["hit_poison"]
    assert not terminated
    assert not truncated


def test_poison_penalty_and_energy_loss() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (1, 1)
    env.poison[1, 2] = 1

    observation, reward, terminated, truncated, info = env.step(Action.EAST)

    assert reward == env.config.step_penalty + env.config.poison_penalty
    assert observation["energy"][0] == (
        env.config.initial_energy - env.config.step_energy_cost - env.config.poison_energy_cost
    )
    assert observation["poison"][1, 2] == 0
    assert not info["ate_food"]
    assert info["hit_poison"]
    assert not terminated
    assert not truncated


def test_energy_loss_on_wait() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)

    observation, reward, _, _, _ = env.step(Action.WAIT)

    assert reward == env.config.step_penalty
    assert observation["energy"][0] == (env.config.initial_energy - env.config.step_energy_cost)


def test_episode_terminates_when_energy_reaches_zero() -> None:
    env = make_env(
        food_count=0,
        poison_count=0,
        initial_energy=1,
        step_energy_cost=1,
        max_steps=10,
    )
    env.reset(seed=1)

    observation, _, terminated, truncated, _ = env.step(Action.WAIT)

    assert observation["energy"][0] == 0
    assert terminated
    assert not truncated


def test_episode_truncates_at_max_steps() -> None:
    env = make_env(
        food_count=0,
        poison_count=0,
        initial_energy=10,
        step_energy_cost=0,
        max_steps=2,
    )
    env.reset(seed=1)

    env.step(Action.WAIT)
    _, _, terminated, truncated, _ = env.step(Action.WAIT)

    assert not terminated
    assert truncated


def test_ascii_render_marks_world_state() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (0, 0)
    env.food[0, 1] = 1
    env.poison[1, 0] = 1

    rendered = env.render()

    assert "energy=" in rendered
    assert "BF" in rendered
    assert "P" in rendered


def test_food_north_produces_north_food_scent() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (2, 2)
    env.food[1, 2] = 1

    scent = directional_scent(
        organism=env.organism,
        targets=env.food,
        direction="north",
    )

    assert scent == STRONG_SCENT


def test_poison_east_produces_east_poison_scent() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (2, 2)
    env.poison[2, 3] = 1

    scent = directional_scent(
        organism=env.organism,
        targets=env.poison,
        direction="east",
    )

    assert scent == STRONG_SCENT


def test_farther_objects_produce_weaker_scent() -> None:
    env = make_env(width=6, height=6, food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (2, 2)
    env.food[0, 2] = 1

    scent = directional_scent(
        organism=env.organism,
        targets=env.food,
        direction="north",
    )

    assert scent == WEAK_SCENT


def test_no_object_produces_zero_scent() -> None:
    env = make_env(food_count=0, poison_count=0)
    env.reset(seed=1)
    env.organism = (2, 2)

    scent = directional_scent(
        organism=env.organism,
        targets=env.food,
        direction="north",
    )

    assert scent == NO_SCENT
