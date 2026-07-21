import numpy as np

from abiogenesis.agents.q_learning_agent import (
    EMPTY,
    FOOD,
    POISON,
    WALL,
    ADJACENT_POISON_SIGNAL,
    BOTH_FOOD_AND_POISON_SIGNAL,
    FOOD_ONLY_SIGNAL,
    NO_DIRECTIONAL_SIGNAL,
    POISON_ONLY_SIGNAL,
    QLearningAgent,
    encode_conflict_scent_observation,
    encode_observation,
    encode_scent_observation,
)
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import Action, BacteriaWorldEnv
from abiogenesis.training.evaluate_q_learning import (
    RewardOverrides,
    build_config,
    evaluate_q_learning,
    evaluate_multi_seed_variants,
    evaluate_q_learning_variants,
    format_multi_seed_comparison,
)
from abiogenesis.training.train_q_learning import novelty_bonus_for_position, train_q_learning


def test_encode_observation_uses_local_tiles_and_energy_bucket() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(food_count=0, poison_count=0))
    observation, _ = env.reset(seed=1)
    env.organism = (0, 0)
    env.food[0, 1] = 1
    env.poison[1, 0] = 1
    observation = env._observation()

    state = encode_observation(observation)

    assert state == (WALL, POISON, FOOD, WALL, 2)


def test_encode_scent_observation_adds_directional_signals() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(width=6, height=6, food_count=0, poison_count=0))
    observation, _ = env.reset(seed=1)
    env.organism = (2, 2)
    env.food[0, 2] = 1
    env.poison[2, 3] = 1
    observation = env._observation()

    state = encode_scent_observation(observation)

    assert state == (
        EMPTY,
        EMPTY,
        POISON,
        EMPTY,
        1,
        0,
        0,
        0,
        0,
        0,
        2,
        0,
        2,
    )


def test_encode_conflict_scent_observation_combines_food_and_poison() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(width=7, height=7, food_count=0, poison_count=0))
    env.reset(seed=1)
    env.organism = (3, 3)
    env.food[1, 3] = 1
    env.food[5, 3] = 1
    env.poison[6, 3] = 1
    env.poison[3, 4] = 1
    env.poison[3, 1] = 1
    observation = env._observation()

    state = encode_conflict_scent_observation(observation)

    assert state == (
        EMPTY,
        EMPTY,
        POISON,
        EMPTY,
        FOOD_ONLY_SIGNAL,
        BOTH_FOOD_AND_POISON_SIGNAL,
        ADJACENT_POISON_SIGNAL,
        POISON_ONLY_SIGNAL,
        2,
    )


def test_encode_conflict_scent_observation_reports_no_signal() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(width=5, height=5, food_count=0, poison_count=0))
    env.reset(seed=1)
    env.organism = (2, 2)

    state = encode_conflict_scent_observation(env._observation())

    assert state == (
        EMPTY,
        EMPTY,
        EMPTY,
        EMPTY,
        NO_DIRECTIONAL_SIGNAL,
        NO_DIRECTIONAL_SIGNAL,
        NO_DIRECTIONAL_SIGNAL,
        NO_DIRECTIONAL_SIGNAL,
        2,
    )


def test_q_learning_update_moves_value_toward_target() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(food_count=0, poison_count=0))
    agent = QLearningAgent(env.action_space, alpha=0.5, gamma=0.9, epsilon=0.0)
    state = (EMPTY, EMPTY, FOOD, EMPTY, 2)
    next_state = (EMPTY, EMPTY, EMPTY, EMPTY, 2)
    agent.q_table[next_state] = np.array([0.0, 0.0, 2.0, 0.0, 0.0])

    new_value = agent.update(
        state,
        Action.EAST,
        reward=1.0,
        next_state=next_state,
        done=False,
    )

    assert new_value == 1.4
    assert agent.q_table[state][Action.EAST] == 1.4


def test_q_learning_terminal_update_ignores_next_state() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(food_count=0, poison_count=0))
    agent = QLearningAgent(env.action_space, alpha=0.5, gamma=0.9, epsilon=0.0)
    state = (EMPTY, POISON, EMPTY, EMPTY, 1)
    next_state = (EMPTY, EMPTY, EMPTY, EMPTY, 0)
    agent.q_table[next_state] = np.array([10.0, 10.0, 10.0, 10.0, 10.0])

    new_value = agent.update(
        state,
        Action.SOUTH,
        reward=-1.0,
        next_state=next_state,
        done=True,
    )

    assert new_value == -0.5


def test_epsilon_decay_respects_floor() -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(food_count=0, poison_count=0))
    agent = QLearningAgent(
        env.action_space,
        epsilon=0.2,
        epsilon_decay=0.5,
        min_epsilon=0.15,
    )

    agent.decay_epsilon()
    agent.decay_epsilon()

    assert agent.epsilon == 0.15


def test_q_table_save_and_load_round_trip(tmp_path) -> None:
    env = BacteriaWorldEnv(BacteriaWorldConfig(food_count=0, poison_count=0))
    agent = QLearningAgent(env.action_space, epsilon=0.3)
    state = (EMPTY, EMPTY, FOOD, EMPTY, 2)
    agent.q_table[state] = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
    path = tmp_path / "microbe-q.json"

    agent.save(path)
    loaded = QLearningAgent(env.action_space)
    loaded.load(path)

    assert loaded.epsilon == 0.3
    assert np.array_equal(loaded.q_table[state], agent.q_table[state])


def test_train_q_learning_returns_summary_and_agent() -> None:
    agent, records, summary = train_q_learning(seed=5, episodes=3, grid_size=10)

    assert len(records) == 3
    assert summary.episodes == 3
    assert len(agent.q_table) > 0


def test_novelty_reward_defaults_to_zero() -> None:
    reward = novelty_bonus_for_position(
        position=(1, 0),
        visited_positions={(0, 0)},
        novelty_reward=0.0,
    )

    assert reward == 0.0


def test_novelty_reward_applies_once_for_new_tile() -> None:
    visited = {(0, 0)}

    reward = novelty_bonus_for_position(
        position=(1, 0),
        visited_positions=visited,
        novelty_reward=0.02,
    )
    visited.add((1, 0))
    repeat_reward = novelty_bonus_for_position(
        position=(1, 0),
        visited_positions=visited,
        novelty_reward=0.02,
    )

    assert reward == 0.02
    assert repeat_reward == 0.0


def test_training_zero_novelty_reward_leaves_no_bonus_metrics() -> None:
    _, records, summary = train_q_learning(
        seed=5,
        episodes=2,
        grid_size=5,
        encoder_name="novelty-scent",
        novelty_reward=0.0,
    )

    assert [record.novelty_bonuses for record in records] == [0, 0]
    assert summary.novelty_bonuses == 0
    assert summary.novelty_reward_total == 0.0


def test_training_novelty_reward_records_bonus_metrics() -> None:
    _, records, summary = train_q_learning(
        seed=5,
        episodes=2,
        grid_size=5,
        encoder_name="novelty-scent",
        novelty_reward=0.02,
    )

    assert sum(record.novelty_bonuses for record in records) > 0
    assert summary.novelty_bonuses > 0
    assert summary.novelty_reward_total > 0.0


def test_evaluate_q_learning_compares_against_random() -> None:
    random_summary, q_summary, agent = evaluate_q_learning(
        seed=5,
        train_episodes=5,
        eval_episodes=3,
        grid_size=10,
    )

    assert random_summary.episodes == 3
    assert q_summary.episodes == 3
    assert len(agent.q_table) > 0


def test_evaluate_q_learning_variants_compares_scent_agent() -> None:
    (
        random_summary,
        local_summary,
        scent_summary,
        conflict_summary,
        memory_summary,
        visit_summary,
        loop_summary,
        novelty_summary,
        local_agent,
        scent_agent,
        conflict_agent,
        memory_agent,
        visit_agent,
        loop_agent,
        novelty_agent,
    ) = evaluate_q_learning_variants(
        seed=5,
        train_episodes=5,
        eval_episodes=3,
        grid_size=10,
    )

    assert random_summary.episodes == 3
    assert local_summary.episodes == 3
    assert scent_summary.episodes == 3
    assert conflict_summary.episodes == 3
    assert memory_summary.episodes == 3
    assert visit_summary.episodes == 3
    assert loop_summary.episodes == 3
    assert novelty_summary.episodes == 3
    assert len(local_agent.q_table) > 0
    assert len(scent_agent.q_table) > 0
    assert len(conflict_agent.q_table) > 0
    assert len(memory_agent.q_table) > 0
    assert len(visit_agent.q_table) > 0
    assert len(loop_agent.q_table) > 0
    assert len(novelty_agent.q_table) > 0


def test_build_config_applies_reward_overrides() -> None:
    config = build_config(
        grid_size=8,
        overrides=RewardOverrides(
            poison_penalty=-2.5,
            poison_energy_cost=12,
            food_reward=1.5,
            step_penalty=-0.02,
        ),
    )

    assert config.width == 8
    assert config.height == 8
    assert config.poison_penalty == -2.5
    assert config.poison_energy_cost == 12
    assert config.food_reward == 1.5
    assert config.step_penalty == -0.02


def test_multi_seed_variant_comparison_reports_mean_metrics() -> None:
    comparison = evaluate_multi_seed_variants(
        seed=5,
        seeds=2,
        train_episodes=3,
        eval_episodes=2,
        grid_size=10,
    )

    assert comparison.seeds == (5, 6)
    assert comparison.random.average_reward == comparison.random.average_reward
    assert comparison.local_q.wasted_moves >= 0.0
    assert comparison.scent_q.poison_collisions >= 0.0
    assert comparison.conflict_scent_q.poison_collisions >= 0.0
    assert comparison.memory_scent_q.repeated_positions >= 0.0
    assert comparison.visit_scent_q.unique_tiles_visited >= 0.0
    assert comparison.loop_scent_q.loop_detections >= 0.0
    assert comparison.novelty_scent_q.revisit_ratio >= 0.0

    formatted = format_multi_seed_comparison(comparison)
    assert "Phase 3D Multi-Seed Comparison" in formatted
    assert "wasted moves" in formatted
    assert "unique tiles" in formatted
    assert "loop detections" in formatted
    assert "novelty" in formatted


def test_multi_seed_with_novelty_reward_reports_reward_variant() -> None:
    comparison = evaluate_multi_seed_variants(
        seed=5,
        seeds=1,
        train_episodes=3,
        eval_episodes=2,
        grid_size=10,
        overrides=RewardOverrides(novelty_reward=0.02),
    )

    assert comparison.novelty_scent_reward_q is not None
    assert comparison.novelty_scent_reward_q.novelty_reward_total >= 0.0
    assert "novelty-scent-reward-0.02" in format_multi_seed_comparison(comparison)
