from abiogenesis.training.sweep_q_learning import (
    SweepMetrics,
    SweepResult,
    SweepSettings,
    format_sweep_results,
    run_sweep,
    select_best_result,
    select_best_seed_result,
)


def test_sweep_runs_small_configuration() -> None:
    results = run_sweep(
        seed=3,
        seeds=1,
        eval_episodes=1,
        grid_size=6,
        encoders=("scent",),
        alphas=(0.2,),
        gammas=(0.9,),
        epsilon_decays=(0.99,),
        min_epsilons=(0.05,),
        train_episodes_options=(2,),
    )

    assert len(results) == 1
    assert results[0].settings.encoder == "scent"
    assert len(results[0].seed_results) == 1
    assert results[0].metrics.wasted_moves >= 0.0


def test_select_best_result_respects_metric_direction() -> None:
    high_reward = SweepResult(
        settings=SweepSettings("scent", 0.2, 0.95, 0.995, 0.05, 10),
        metrics=SweepMetrics(
            average_reward=2.0,
            average_lifespan=5.0,
            food_eaten=3.0,
            poison_collisions=4.0,
            wasted_moves=8.0,
        ),
        seed_results=(),
    )
    low_poison = SweepResult(
        settings=SweepSettings("conflict-scent", 0.2, 0.95, 0.995, 0.05, 10),
        metrics=SweepMetrics(
            average_reward=1.0,
            average_lifespan=6.0,
            food_eaten=2.0,
            poison_collisions=1.0,
            wasted_moves=10.0,
        ),
        seed_results=(),
    )

    assert select_best_result([high_reward, low_poison]).settings.encoder == "scent"
    assert (
        select_best_result(
            [high_reward, low_poison],
            metric="poison_collisions",
        ).settings.encoder
        == "conflict-scent"
    )


def test_format_sweep_results_includes_metrics() -> None:
    results = run_sweep(
        seed=4,
        seeds=1,
        eval_episodes=1,
        grid_size=6,
        encoders=("conflict-scent",),
        alphas=(0.2,),
        gammas=(0.9,),
        epsilon_decays=(0.99,),
        min_epsilons=(0.05,),
        train_episodes_options=(2,),
    )

    text = format_sweep_results(results)

    assert "Phase 2E Q-Learning Sweep" in text
    assert "conflict-scent" in text
    assert "poison" in text


def test_select_best_seed_result_returns_agent() -> None:
    result = run_sweep(
        seed=5,
        seeds=1,
        eval_episodes=1,
        grid_size=6,
        encoders=("scent",),
        alphas=(0.2,),
        gammas=(0.9,),
        epsilon_decays=(0.99,),
        min_epsilons=(0.05,),
        train_episodes_options=(2,),
    )[0]

    seed_result = select_best_seed_result(result)

    assert seed_result.agent.q_table
