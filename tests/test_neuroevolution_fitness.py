from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.metrics.recorder import EpisodeRecord
from abiogenesis.neuroevolution.fitness import (
    evaluate_network,
    run_policy_episode,
    validate_seed_roles,
)


class WaitNetwork:
    def activate(self, inputs):
        return (0.0, 0.0, 0.0, 0.0, 1.0)


def test_fitness_uses_raw_environment_reward_and_separate_diagnostics() -> None:
    config = BacteriaWorldConfig(food_count=0, poison_count=0, initial_energy=3, max_steps=10)

    record = run_policy_episode(network=WaitNetwork(), seed=7, config=config)

    assert record.steps == 3
    assert record.total_reward == -0.03
    assert record.novelty_bonuses == 0
    assert record.novelty_reward_total == 0.0
    assert record.unique_tiles_visited == 1
    assert record.wasted_moves == 3


def test_evaluation_preserves_seed_order_and_averages_episode_rewards() -> None:
    seen: list[int] = []

    def fake_episode_runner(*, network, seed, config):
        del network, config
        seen.append(seed)
        return EpisodeRecord(total_reward=float(seed), steps=1, final_energy=1)

    batch = evaluate_network(
        network=WaitNetwork(),
        root_seeds=(5, 2),
        episodes_per_seed=2,
        episode_runner=fake_episode_runner,
    )

    assert seen == [5, 6, 2, 3]
    assert batch.root_seeds == (5, 2)
    assert batch.mean_reward == 4.0
    assert [summary.average_reward for summary in batch.seed_summaries] == [5.5, 2.5]


def test_fitness_and_holdout_seed_roles_must_be_disjoint_and_unique() -> None:
    validate_seed_roles((21, 22, 23), (31, 32, 33))

    for fitness, holdout in (
        ((21, 21), (31,)),
        ((21,), (31, 31)),
        ((21, 22), (22, 31)),
    ):
        try:
            validate_seed_roles(fitness, holdout)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid seed roles were accepted")
