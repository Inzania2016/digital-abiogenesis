from abiogenesis.agents import RandomAgent
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.training.train_random import evaluate_random, format_summary, run_episode


def test_random_agent_samples_valid_action() -> None:
    env = BacteriaWorldEnv()
    agent = RandomAgent(env.action_space)

    action = agent.act()

    assert env.action_space.contains(action)


def test_random_agent_is_deterministic_with_seed() -> None:
    env = BacteriaWorldEnv()
    agent_a = RandomAgent(env.action_space, seed=7)
    agent_b = RandomAgent(env.action_space, seed=7)

    actions_a = [agent_a.act() for _ in range(10)]
    actions_b = [agent_b.act() for _ in range(10)]

    assert actions_a == actions_b


def test_run_episode_records_practical_metrics() -> None:
    record = run_episode(seed=3, grid_size=10)

    assert record.steps > 0
    assert record.total_reward <= record.food_eaten
    assert record.food_eaten >= 0
    assert record.poison_collisions >= 0
    assert record.wasted_moves >= 0


def test_evaluate_random_is_deterministic() -> None:
    _, summary_a = evaluate_random(seed=11, episodes=5, grid_size=10)
    _, summary_b = evaluate_random(seed=11, episodes=5, grid_size=10)

    assert summary_a == summary_b


def test_format_summary_contains_key_metrics() -> None:
    _, summary = evaluate_random(seed=0, episodes=2, grid_size=10)

    text = format_summary(summary)

    assert "average reward:" in text
    assert "average lifespan:" in text
    assert "food eaten:" in text
    assert "poison collisions:" in text
    assert "wasted moves:" in text
