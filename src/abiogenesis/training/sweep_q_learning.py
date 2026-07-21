"""Sweep small Q-learning settings for Bacterium-0."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from abiogenesis.agents import QLearningAgent
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.metrics.recorder import RunSummary
from abiogenesis.training.evaluate_q_learning import run_greedy_episode
from abiogenesis.training.train_q_learning import ENCODERS, train_q_learning

MetricName = str


@dataclass(frozen=True)
class SweepSettings:
    """One Q-learning setting combination."""

    encoder: str
    alpha: float
    gamma: float
    epsilon_decay: float
    min_epsilon: float
    train_episodes: int


@dataclass(frozen=True)
class SweepMetrics:
    """Mean evaluation metrics for one setting combination."""

    average_reward: float
    average_lifespan: float
    food_eaten: float
    poison_collisions: float
    wasted_moves: float


@dataclass(frozen=True)
class SeedSweepResult:
    """One seed's trained agent and evaluation summary."""

    seed: int
    summary: RunSummary
    agent: QLearningAgent


@dataclass(frozen=True)
class SweepResult:
    """Aggregated result for one setting combination."""

    settings: SweepSettings
    metrics: SweepMetrics
    seed_results: tuple[SeedSweepResult, ...]


def run_sweep(
    *,
    seed: int = 0,
    seeds: int = 3,
    eval_episodes: int = 20,
    grid_size: int = 10,
    encoders: tuple[str, ...] = ("scent", "conflict-scent"),
    alphas: tuple[float, ...] = (0.2,),
    gammas: tuple[float, ...] = (0.9, 0.95),
    epsilon_decays: tuple[float, ...] = (0.99, 0.995),
    min_epsilons: tuple[float, ...] = (0.05,),
    train_episodes_options: tuple[int, ...] = (300, 600),
) -> list[SweepResult]:
    """Run a deterministic, practical Q-learning hyperparameter sweep."""

    if seeds < 1:
        raise ValueError("seeds must be at least 1")
    if eval_episodes < 1:
        raise ValueError("eval_episodes must be at least 1")
    for encoder in encoders:
        if encoder not in ENCODERS:
            raise ValueError(f"Unknown encoder: {encoder}")

    results: list[SweepResult] = []
    for settings in _settings_grid(
        encoders=encoders,
        alphas=alphas,
        gammas=gammas,
        epsilon_decays=epsilon_decays,
        min_epsilons=min_epsilons,
        train_episodes_options=train_episodes_options,
    ):
        seed_results = tuple(
            _run_seed(
                settings=settings,
                seed=seed + seed_index,
                eval_episodes=eval_episodes,
                grid_size=grid_size,
            )
            for seed_index in range(seeds)
        )
        results.append(
            SweepResult(
                settings=settings,
                metrics=_mean_metrics([result.summary for result in seed_results]),
                seed_results=seed_results,
            )
        )

    return results


def select_best_result(
    results: list[SweepResult],
    *,
    metric: MetricName = "average_reward",
) -> SweepResult:
    """Select the best sweep result for a metric."""

    if not results:
        raise ValueError("Cannot select from an empty sweep.")
    reverse = _higher_is_better(metric)
    return sorted(
        results,
        key=lambda result: _metric_value(result.metrics, metric),
        reverse=reverse,
    )[0]


def select_best_seed_result(
    result: SweepResult,
    *,
    metric: MetricName = "average_reward",
) -> SeedSweepResult:
    """Select the best seed-level agent inside one sweep result."""

    reverse = _higher_is_better(metric)
    return sorted(
        result.seed_results,
        key=lambda seed_result: _summary_metric_value(seed_result.summary, metric),
        reverse=reverse,
    )[0]


def format_sweep_results(
    results: list[SweepResult],
    *,
    best_metric: MetricName = "average_reward",
) -> str:
    """Format sweep results as a readable fixed-width table."""

    sorted_results = sorted(
        results,
        key=lambda result: _metric_value(result.metrics, best_metric),
        reverse=_higher_is_better(best_metric),
    )
    lines = [
        "Phase 2E Q-Learning Sweep",
        f"settings tested: {len(sorted_results)}",
        f"best metric: {best_metric}",
        "",
        ("encoder          alpha gamma decay  min_eps episodes reward lifespan food poison wasted"),
    ]
    for result in sorted_results:
        settings = result.settings
        metrics = result.metrics
        lines.append(
            f"{settings.encoder:<16}"
            f" {settings.alpha:5.2f}"
            f" {settings.gamma:5.2f}"
            f" {settings.epsilon_decay:5.3f}"
            f" {settings.min_epsilon:7.3f}"
            f" {settings.train_episodes:8d}"
            f" {metrics.average_reward:6.3f}"
            f" {metrics.average_lifespan:8.3f}"
            f" {metrics.food_eaten:4.1f}"
            f" {metrics.poison_collisions:6.1f}"
            f" {metrics.wasted_moves:6.1f}"
        )
    return "\n".join(lines)


def _run_seed(
    *,
    settings: SweepSettings,
    seed: int,
    eval_episodes: int,
    grid_size: int,
) -> SeedSweepResult:
    config = BacteriaWorldConfig(width=grid_size, height=grid_size)
    agent, _, _ = train_q_learning(
        seed=seed,
        episodes=settings.train_episodes,
        grid_size=grid_size,
        alpha=settings.alpha,
        gamma=settings.gamma,
        epsilon_decay=settings.epsilon_decay,
        min_epsilon=settings.min_epsilon,
        encoder_name=settings.encoder,
        config=config,
    )
    eval_seed = seed + 100_000
    records = [
        run_greedy_episode(
            agent=agent,
            seed=eval_seed + episode_index,
            grid_size=grid_size,
            config=config,
        )
        for episode_index in range(eval_episodes)
    ]
    return SeedSweepResult(
        seed=seed,
        summary=RunSummary.from_records(
            records=records,
            seed=eval_seed,
            grid_size=grid_size,
        ),
        agent=agent,
    )


def _settings_grid(
    *,
    encoders: tuple[str, ...],
    alphas: tuple[float, ...],
    gammas: tuple[float, ...],
    epsilon_decays: tuple[float, ...],
    min_epsilons: tuple[float, ...],
    train_episodes_options: tuple[int, ...],
) -> tuple[SweepSettings, ...]:
    return tuple(
        SweepSettings(
            encoder=encoder,
            alpha=alpha,
            gamma=gamma,
            epsilon_decay=epsilon_decay,
            min_epsilon=min_epsilon,
            train_episodes=train_episodes,
        )
        for encoder in encoders
        for alpha in alphas
        for gamma in gammas
        for epsilon_decay in epsilon_decays
        for min_epsilon in min_epsilons
        for train_episodes in train_episodes_options
    )


def _mean_metrics(summaries: list[RunSummary]) -> SweepMetrics:
    if not summaries:
        raise ValueError("Cannot average an empty summary list.")
    count = len(summaries)
    return SweepMetrics(
        average_reward=sum(summary.average_reward for summary in summaries) / count,
        average_lifespan=sum(summary.average_lifespan for summary in summaries) / count,
        food_eaten=sum(summary.food_eaten for summary in summaries) / count,
        poison_collisions=sum(summary.poison_collisions for summary in summaries) / count,
        wasted_moves=sum(summary.wasted_moves for summary in summaries) / count,
    )


def _metric_value(metrics: SweepMetrics, metric: MetricName) -> float:
    try:
        return float(getattr(metrics, metric))
    except AttributeError as exc:
        raise ValueError(f"Unknown metric: {metric}") from exc


def _summary_metric_value(summary: RunSummary, metric: MetricName) -> float:
    if metric == "average_reward":
        return summary.average_reward
    if metric == "average_lifespan":
        return summary.average_lifespan
    if metric == "food_eaten":
        return float(summary.food_eaten)
    if metric == "poison_collisions":
        return float(summary.poison_collisions)
    if metric == "wasted_moves":
        return float(summary.wasted_moves)
    raise ValueError(f"Unknown metric: {metric}")


def _higher_is_better(metric: MetricName) -> bool:
    return metric not in {"poison_collisions", "wasted_moves"}


def _parse_float_tuple(value: str) -> tuple[float, ...]:
    return tuple(float(part.strip()) for part in value.split(",") if part.strip())


def _parse_int_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


def _parse_str_tuple(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--eval-episodes", type=int, default=20)
    parser.add_argument("--grid-size", type=int, default=10)
    parser.add_argument(
        "--encoders",
        default="scent,conflict-scent",
        help="Comma-separated encoder names.",
    )
    parser.add_argument("--alphas", default="0.2")
    parser.add_argument("--gammas", default="0.9,0.95")
    parser.add_argument("--epsilon-decays", default="0.99,0.995")
    parser.add_argument("--min-epsilons", default="0.05")
    parser.add_argument("--train-episodes", default="300,600")
    parser.add_argument(
        "--best-metric",
        choices=[
            "average_reward",
            "average_lifespan",
            "food_eaten",
            "poison_collisions",
            "wasted_moves",
        ],
        default="average_reward",
    )
    parser.add_argument("--save-best-path", type=Path)
    args = parser.parse_args()

    results = run_sweep(
        seed=args.seed,
        seeds=args.seeds,
        eval_episodes=args.eval_episodes,
        grid_size=args.grid_size,
        encoders=_parse_str_tuple(args.encoders),
        alphas=_parse_float_tuple(args.alphas),
        gammas=_parse_float_tuple(args.gammas),
        epsilon_decays=_parse_float_tuple(args.epsilon_decays),
        min_epsilons=_parse_float_tuple(args.min_epsilons),
        train_episodes_options=_parse_int_tuple(args.train_episodes),
    )
    print(format_sweep_results(results, best_metric=args.best_metric))

    if args.save_best_path is not None:
        best_result = select_best_result(results, metric=args.best_metric)
        best_seed = select_best_seed_result(best_result, metric=args.best_metric)
        args.save_best_path.parent.mkdir(parents=True, exist_ok=True)
        best_seed.agent.save(args.save_best_path)
        settings = best_result.settings
        print()
        print(f"saved best q-table: {args.save_best_path}")
        print(f"encoder: {settings.encoder}")
        print(f"seed: {best_seed.seed}")
        print(f"best metric: {args.best_metric}")


if __name__ == "__main__":
    main()
