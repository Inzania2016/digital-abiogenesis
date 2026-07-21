"""Compare a trained Q-learning microbe against the random baseline."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from abiogenesis.agents import QLearningAgent
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.metrics.recorder import EpisodeRecord, RunSummary
from abiogenesis.agents.memory import LoopMemoryTracker, reset_encoder_memory, update_encoder_memory
from abiogenesis.training.train_q_learning import (
    ENCODERS,
    build_encoder,
    novelty_bonus_for_position,
    train_q_learning,
)
from abiogenesis.training.train_random import evaluate_random


@dataclass(frozen=True)
class RewardOverrides:
    """Optional knobs for reward and energy tradeoff experiments."""

    poison_penalty: float | None = None
    poison_energy_cost: int | None = None
    food_reward: float | None = None
    step_penalty: float | None = None
    loop_penalty: float = 0.0
    novelty_reward: float = 0.0


@dataclass(frozen=True)
class MeanMetrics:
    """Mean metrics across a set of seed-level summaries."""

    average_reward: float
    average_lifespan: float
    food_eaten: float
    poison_collisions: float
    wasted_moves: float
    repeated_positions: float
    unique_tiles_visited: float
    loop_detections: float
    short_loops: float
    medium_loops: float
    long_loops: float
    novelty_bonuses: float
    novelty_reward_total: float
    revisit_ratio: float


@dataclass(frozen=True)
class MultiSeedComparison:
    """Agent comparison averaged across multiple seeds."""

    seeds: tuple[int, ...]
    train_episodes: int
    eval_episodes: int
    grid_size: int
    novelty_reward: float
    random: MeanMetrics
    local_q: MeanMetrics
    scent_q: MeanMetrics
    conflict_scent_q: MeanMetrics
    memory_scent_q: MeanMetrics
    visit_scent_q: MeanMetrics
    loop_scent_q: MeanMetrics
    novelty_scent_q: MeanMetrics
    novelty_scent_reward_q: MeanMetrics | None = None
    loop_scent_penalty_q: MeanMetrics | None = None


def run_greedy_episode(
    *,
    agent: QLearningAgent,
    seed: int,
    grid_size: int,
    config: BacteriaWorldConfig | None = None,
    loop_penalty: float = 0.0,
    novelty_reward: float = 0.0,
) -> EpisodeRecord:
    """Run one evaluation episode without exploration."""

    env = BacteriaWorldEnv(config or BacteriaWorldConfig(width=grid_size, height=grid_size))
    observation, _ = env.reset(seed=seed)
    reset_encoder_memory(agent.encoder, observation)
    total_reward = 0.0
    food_eaten = 0
    poison_collisions = 0
    wasted_moves = 0
    repeated_positions = 0
    loop_detections = 0
    short_loops = 0
    medium_loops = 0
    long_loops = 0
    novelty_bonuses = 0
    novelty_reward_total = 0.0
    visited_positions = {tuple(int(value) for value in observation["organism"])}
    loop_memory = LoopMemoryTracker()
    loop_memory.reset(observation)
    terminated = False
    truncated = False

    while not (terminated or truncated):
        action = agent.act(observation, explore=False)
        observation, reward, terminated, truncated, info = env.step(action)
        update_encoder_memory(
            agent.encoder,
            action=action,
            observation=observation,
        )
        loop_memory.update_after_step(action=action, observation=observation)
        encoder_loop_memory = getattr(agent.encoder, "memory", None)
        loop_detected = bool(
            getattr(encoder_loop_memory, "loop_detected", False) or loop_memory.loop_detected
        )
        position = tuple(int(value) for value in observation["organism"])
        novelty_bonus = novelty_bonus_for_position(
            position=position,
            visited_positions=visited_positions,
            novelty_reward=novelty_reward,
        )
        shaped_reward = reward + (loop_penalty if loop_detected else 0.0) + novelty_bonus
        total_reward += shaped_reward
        food_eaten += int(info["ate_food"])
        poison_collisions += int(info["hit_poison"])
        wasted_moves += int(info["wasted_move"])
        repeated_positions += int(info["wasted_move"])
        if loop_detected:
            loop_detections += 1
            bucket = int(
                getattr(
                    encoder_loop_memory,
                    "loop_bucket",
                    loop_memory.loop_bucket,
                )
            )
            short_loops += int(bucket == 1)
            medium_loops += int(bucket == 2)
            long_loops += int(bucket == 3)
        if novelty_bonus != 0.0:
            novelty_bonuses += 1
            novelty_reward_total += novelty_bonus
        visited_positions.add(position)

    return EpisodeRecord(
        total_reward=total_reward,
        steps=env.steps,
        final_energy=env.energy,
        food_eaten=food_eaten,
        poison_collisions=poison_collisions,
        wasted_moves=wasted_moves,
        repeated_positions=repeated_positions,
        unique_tiles_visited=len(visited_positions),
        loop_detections=loop_detections,
        short_loops=short_loops,
        medium_loops=medium_loops,
        long_loops=long_loops,
        novelty_bonuses=novelty_bonuses,
        novelty_reward_total=novelty_reward_total,
    )


def evaluate_q_learning(
    *,
    seed: int = 0,
    train_episodes: int = 500,
    eval_episodes: int = 50,
    grid_size: int = 10,
    load_path: str | Path | None = None,
    encoder_name: str = "local",
    config: BacteriaWorldConfig | None = None,
    loop_penalty: float = 0.0,
    novelty_reward: float = 0.0,
) -> tuple[RunSummary, RunSummary, QLearningAgent]:
    """Return random and trained Q-learning summaries on matching eval worlds."""

    if eval_episodes < 1:
        raise ValueError("eval_episodes must be at least 1")
    if encoder_name not in ENCODERS:
        raise ValueError(f"Unknown encoder: {encoder_name}")

    world_config = config or BacteriaWorldConfig(width=grid_size, height=grid_size)
    env = BacteriaWorldEnv(world_config)
    if load_path is None:
        agent, _, _ = train_q_learning(
            seed=seed,
            episodes=train_episodes,
            grid_size=grid_size,
            encoder_name=encoder_name,
            config=world_config,
            loop_penalty=loop_penalty,
            novelty_reward=novelty_reward,
        )
    else:
        agent = QLearningAgent(
            env.action_space,
            seed=seed,
            encoder=build_encoder(encoder_name),
        )
        agent.load(load_path)

    eval_seed = seed + 100_000
    _, random_summary = evaluate_random(
        seed=eval_seed,
        episodes=eval_episodes,
        grid_size=grid_size,
        config=world_config,
    )
    q_records = [
        run_greedy_episode(
            agent=agent,
            seed=eval_seed + episode_index,
            grid_size=grid_size,
            config=world_config,
            loop_penalty=loop_penalty,
            novelty_reward=novelty_reward,
        )
        for episode_index in range(eval_episodes)
    ]
    q_summary = RunSummary.from_records(
        records=q_records,
        seed=eval_seed,
        grid_size=grid_size,
    )
    return random_summary, q_summary, agent


def evaluate_q_learning_variants(
    *,
    seed: int = 0,
    train_episodes: int = 500,
    eval_episodes: int = 50,
    grid_size: int = 10,
    config: BacteriaWorldConfig | None = None,
) -> tuple[
    RunSummary,
    RunSummary,
    RunSummary,
    RunSummary,
    RunSummary,
    RunSummary,
    RunSummary,
    QLearningAgent,
    QLearningAgent,
    QLearningAgent,
    QLearningAgent,
    QLearningAgent,
    QLearningAgent,
    QLearningAgent,
]:
    """Compare random, local, scent, memory, visit memory, and loop memory."""

    random_summary, local_summary, local_agent = evaluate_q_learning(
        seed=seed,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        config=config,
        encoder_name="local",
    )
    _, scent_summary, scent_agent = evaluate_q_learning(
        seed=seed,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        config=config,
        encoder_name="scent",
    )
    _, conflict_summary, conflict_agent = evaluate_q_learning(
        seed=seed,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        config=config,
        encoder_name="conflict-scent",
    )
    _, memory_summary, memory_agent = evaluate_q_learning(
        seed=seed,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        config=config,
        encoder_name="memory-scent",
    )
    _, visit_summary, visit_agent = evaluate_q_learning(
        seed=seed,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        config=config,
        encoder_name="visit-scent",
    )
    _, loop_summary, loop_agent = evaluate_q_learning(
        seed=seed,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        config=config,
        encoder_name="loop-scent",
    )
    _, novelty_summary, novelty_agent = evaluate_q_learning(
        seed=seed,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        config=config,
        encoder_name="novelty-scent",
    )
    return (
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
    )


def build_config(
    *,
    grid_size: int,
    overrides: RewardOverrides | None = None,
) -> BacteriaWorldConfig:
    """Build a world config with optional experiment knobs."""

    overrides = overrides or RewardOverrides()
    base = BacteriaWorldConfig(width=grid_size, height=grid_size)
    return BacteriaWorldConfig(
        width=grid_size,
        height=grid_size,
        food_count=base.food_count,
        poison_count=base.poison_count,
        initial_energy=base.initial_energy,
        max_steps=base.max_steps,
        step_energy_cost=base.step_energy_cost,
        food_energy=base.food_energy,
        poison_energy_cost=(
            base.poison_energy_cost
            if overrides.poison_energy_cost is None
            else overrides.poison_energy_cost
        ),
        food_reward=(base.food_reward if overrides.food_reward is None else overrides.food_reward),
        poison_penalty=(
            base.poison_penalty if overrides.poison_penalty is None else overrides.poison_penalty
        ),
        step_penalty=(
            base.step_penalty if overrides.step_penalty is None else overrides.step_penalty
        ),
    )


def evaluate_multi_seed_variants(
    *,
    seed: int = 0,
    seeds: int = 5,
    train_episodes: int = 500,
    eval_episodes: int = 50,
    grid_size: int = 10,
    overrides: RewardOverrides | None = None,
) -> MultiSeedComparison:
    """Run the three-way comparison across several deterministic seeds."""

    if seeds < 1:
        raise ValueError("seeds must be at least 1")

    seed_values = tuple(seed + index for index in range(seeds))
    random_summaries: list[RunSummary] = []
    local_summaries: list[RunSummary] = []
    scent_summaries: list[RunSummary] = []
    conflict_summaries: list[RunSummary] = []
    memory_summaries: list[RunSummary] = []
    visit_summaries: list[RunSummary] = []
    loop_summaries: list[RunSummary] = []
    novelty_summaries: list[RunSummary] = []
    novelty_reward_summaries: list[RunSummary] = []
    loop_penalty_summaries: list[RunSummary] = []
    config = build_config(grid_size=grid_size, overrides=overrides)
    reward_overrides = overrides or RewardOverrides()
    loop_penalty = reward_overrides.loop_penalty
    novelty_reward = reward_overrides.novelty_reward

    for seed_value in seed_values:
        (
            random_summary,
            local_summary,
            scent_summary,
            conflict_summary,
            memory_summary,
            visit_summary,
            loop_summary,
            novelty_summary,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = evaluate_q_learning_variants(
            seed=seed_value,
            train_episodes=train_episodes,
            eval_episodes=eval_episodes,
            grid_size=grid_size,
            config=config,
        )
        random_summaries.append(random_summary)
        local_summaries.append(local_summary)
        scent_summaries.append(scent_summary)
        conflict_summaries.append(conflict_summary)
        memory_summaries.append(memory_summary)
        visit_summaries.append(visit_summary)
        loop_summaries.append(loop_summary)
        novelty_summaries.append(novelty_summary)

        if loop_penalty != 0.0:
            _, loop_penalty_summary, _ = evaluate_q_learning(
                seed=seed_value,
                train_episodes=train_episodes,
                eval_episodes=eval_episodes,
                grid_size=grid_size,
                config=config,
                encoder_name="loop-scent",
                loop_penalty=loop_penalty,
            )
            loop_penalty_summaries.append(loop_penalty_summary)

        if novelty_reward != 0.0:
            _, novelty_reward_summary, _ = evaluate_q_learning(
                seed=seed_value,
                train_episodes=train_episodes,
                eval_episodes=eval_episodes,
                grid_size=grid_size,
                config=config,
                encoder_name="novelty-scent",
                novelty_reward=novelty_reward,
            )
            novelty_reward_summaries.append(novelty_reward_summary)

    return MultiSeedComparison(
        seeds=seed_values,
        train_episodes=train_episodes,
        eval_episodes=eval_episodes,
        grid_size=grid_size,
        novelty_reward=novelty_reward,
        random=_mean_metrics(random_summaries),
        local_q=_mean_metrics(local_summaries),
        scent_q=_mean_metrics(scent_summaries),
        conflict_scent_q=_mean_metrics(conflict_summaries),
        memory_scent_q=_mean_metrics(memory_summaries),
        visit_scent_q=_mean_metrics(visit_summaries),
        loop_scent_q=_mean_metrics(loop_summaries),
        novelty_scent_q=_mean_metrics(novelty_summaries),
        novelty_scent_reward_q=(
            _mean_metrics(novelty_reward_summaries) if novelty_reward_summaries else None
        ),
        loop_scent_penalty_q=(
            _mean_metrics(loop_penalty_summaries) if loop_penalty_summaries else None
        ),
    )


def format_comparison(random_summary: RunSummary, q_summary: RunSummary) -> str:
    """Create a clear baseline comparison."""

    return "\n".join(
        [
            "Phase 2A Comparison: Random vs Q-Learning",
            f"episodes: {q_summary.episodes}",
            f"seed: {q_summary.seed}",
            f"grid: {q_summary.grid_size}x{q_summary.grid_size}",
            "",
            "random baseline:",
            f"  average reward: {random_summary.average_reward:.3f}",
            f"  average lifespan: {random_summary.average_lifespan:.2f} steps",
            f"  food eaten: {random_summary.food_eaten}",
            f"  poison collisions: {random_summary.poison_collisions}",
            "",
            "q-learning:",
            f"  average reward: {q_summary.average_reward:.3f}",
            f"  average lifespan: {q_summary.average_lifespan:.2f} steps",
            f"  food eaten: {q_summary.food_eaten}",
            f"  poison collisions: {q_summary.poison_collisions}",
        ]
    )


def format_variant_comparison(
    random_summary: RunSummary,
    local_summary: RunSummary,
    scent_summary: RunSummary,
    conflict_summary: RunSummary,
    memory_summary: RunSummary,
    visit_summary: RunSummary,
    loop_summary: RunSummary,
    novelty_summary: RunSummary,
) -> str:
    """Create a Phase 3D comparison."""

    return "\n".join(
        [
            "Phase 3D Comparison: Directional Novelty",
            f"episodes: {visit_summary.episodes}",
            f"seed: {visit_summary.seed}",
            f"grid: {visit_summary.grid_size}x{visit_summary.grid_size}",
            "",
            "metric                 random      local-q   raw-scent    conflict     memory      visit       loop    novelty",
            _format_summary_row(
                "average reward",
                random_summary.average_reward,
                local_summary.average_reward,
                scent_summary.average_reward,
                conflict_summary.average_reward,
                memory_summary.average_reward,
                visit_summary.average_reward,
                loop_summary.average_reward,
                novelty_summary.average_reward,
            ),
            _format_summary_row(
                "average lifespan",
                random_summary.average_lifespan,
                local_summary.average_lifespan,
                scent_summary.average_lifespan,
                conflict_summary.average_lifespan,
                memory_summary.average_lifespan,
                visit_summary.average_lifespan,
                loop_summary.average_lifespan,
                novelty_summary.average_lifespan,
            ),
            _format_summary_row(
                "food eaten",
                random_summary.food_eaten,
                local_summary.food_eaten,
                scent_summary.food_eaten,
                conflict_summary.food_eaten,
                memory_summary.food_eaten,
                visit_summary.food_eaten,
                loop_summary.food_eaten,
                novelty_summary.food_eaten,
            ),
            _format_summary_row(
                "poison collisions",
                random_summary.poison_collisions,
                local_summary.poison_collisions,
                scent_summary.poison_collisions,
                conflict_summary.poison_collisions,
                memory_summary.poison_collisions,
                visit_summary.poison_collisions,
                loop_summary.poison_collisions,
                novelty_summary.poison_collisions,
            ),
            _format_summary_row(
                "wasted moves",
                random_summary.wasted_moves,
                local_summary.wasted_moves,
                scent_summary.wasted_moves,
                conflict_summary.wasted_moves,
                memory_summary.wasted_moves,
                visit_summary.wasted_moves,
                loop_summary.wasted_moves,
                novelty_summary.wasted_moves,
            ),
            _format_summary_row(
                "repeated positions",
                random_summary.repeated_positions,
                local_summary.repeated_positions,
                scent_summary.repeated_positions,
                conflict_summary.repeated_positions,
                memory_summary.repeated_positions,
                visit_summary.repeated_positions,
                loop_summary.repeated_positions,
                novelty_summary.repeated_positions,
            ),
            _format_summary_row(
                "unique tiles",
                random_summary.unique_tiles_visited,
                local_summary.unique_tiles_visited,
                scent_summary.unique_tiles_visited,
                conflict_summary.unique_tiles_visited,
                memory_summary.unique_tiles_visited,
                visit_summary.unique_tiles_visited,
                loop_summary.unique_tiles_visited,
                novelty_summary.unique_tiles_visited,
            ),
            _format_summary_row(
                "loop detections",
                random_summary.loop_detections,
                local_summary.loop_detections,
                scent_summary.loop_detections,
                conflict_summary.loop_detections,
                memory_summary.loop_detections,
                visit_summary.loop_detections,
                loop_summary.loop_detections,
                novelty_summary.loop_detections,
            ),
            _format_summary_row(
                "revisit ratio",
                random_summary.revisit_ratio,
                local_summary.revisit_ratio,
                scent_summary.revisit_ratio,
                conflict_summary.revisit_ratio,
                memory_summary.revisit_ratio,
                visit_summary.revisit_ratio,
                loop_summary.revisit_ratio,
                novelty_summary.revisit_ratio,
            ),
        ]
    )


def format_multi_seed_comparison(comparison: MultiSeedComparison) -> str:
    """Create a clear multi-seed comparison table."""

    lines = [
        "Phase 3D Multi-Seed Comparison: Directional Novelty",
        f"seeds: {comparison.seeds[0]}..{comparison.seeds[-1]} ({len(comparison.seeds)} seeds)",
        f"train episodes per Q agent: {comparison.train_episodes}",
        f"eval episodes per seed: {comparison.eval_episodes}",
        f"grid: {comparison.grid_size}x{comparison.grid_size}",
        "",
        "metric                 random      local-q   raw-scent    conflict     memory      visit       loop    novelty",
        _format_mean_row(
            "average reward",
            comparison.random.average_reward,
            comparison.local_q.average_reward,
            comparison.scent_q.average_reward,
            comparison.conflict_scent_q.average_reward,
            comparison.memory_scent_q.average_reward,
            comparison.visit_scent_q.average_reward,
            comparison.loop_scent_q.average_reward,
            comparison.novelty_scent_q.average_reward,
        ),
        _format_mean_row(
            "average lifespan",
            comparison.random.average_lifespan,
            comparison.local_q.average_lifespan,
            comparison.scent_q.average_lifespan,
            comparison.conflict_scent_q.average_lifespan,
            comparison.memory_scent_q.average_lifespan,
            comparison.visit_scent_q.average_lifespan,
            comparison.loop_scent_q.average_lifespan,
            comparison.novelty_scent_q.average_lifespan,
        ),
        _format_mean_row(
            "food eaten",
            comparison.random.food_eaten,
            comparison.local_q.food_eaten,
            comparison.scent_q.food_eaten,
            comparison.conflict_scent_q.food_eaten,
            comparison.memory_scent_q.food_eaten,
            comparison.visit_scent_q.food_eaten,
            comparison.loop_scent_q.food_eaten,
            comparison.novelty_scent_q.food_eaten,
        ),
        _format_mean_row(
            "poison collisions",
            comparison.random.poison_collisions,
            comparison.local_q.poison_collisions,
            comparison.scent_q.poison_collisions,
            comparison.conflict_scent_q.poison_collisions,
            comparison.memory_scent_q.poison_collisions,
            comparison.visit_scent_q.poison_collisions,
            comparison.loop_scent_q.poison_collisions,
            comparison.novelty_scent_q.poison_collisions,
        ),
        _format_mean_row(
            "wasted moves",
            comparison.random.wasted_moves,
            comparison.local_q.wasted_moves,
            comparison.scent_q.wasted_moves,
            comparison.conflict_scent_q.wasted_moves,
            comparison.memory_scent_q.wasted_moves,
            comparison.visit_scent_q.wasted_moves,
            comparison.loop_scent_q.wasted_moves,
            comparison.novelty_scent_q.wasted_moves,
        ),
        _format_mean_row(
            "repeated positions",
            comparison.random.repeated_positions,
            comparison.local_q.repeated_positions,
            comparison.scent_q.repeated_positions,
            comparison.conflict_scent_q.repeated_positions,
            comparison.memory_scent_q.repeated_positions,
            comparison.visit_scent_q.repeated_positions,
            comparison.loop_scent_q.repeated_positions,
            comparison.novelty_scent_q.repeated_positions,
        ),
        _format_mean_row(
            "unique tiles",
            comparison.random.unique_tiles_visited,
            comparison.local_q.unique_tiles_visited,
            comparison.scent_q.unique_tiles_visited,
            comparison.conflict_scent_q.unique_tiles_visited,
            comparison.memory_scent_q.unique_tiles_visited,
            comparison.visit_scent_q.unique_tiles_visited,
            comparison.loop_scent_q.unique_tiles_visited,
            comparison.novelty_scent_q.unique_tiles_visited,
        ),
        _format_mean_row(
            "loop detections",
            comparison.random.loop_detections,
            comparison.local_q.loop_detections,
            comparison.scent_q.loop_detections,
            comparison.conflict_scent_q.loop_detections,
            comparison.memory_scent_q.loop_detections,
            comparison.visit_scent_q.loop_detections,
            comparison.loop_scent_q.loop_detections,
            comparison.novelty_scent_q.loop_detections,
        ),
        _format_mean_row(
            "revisit ratio",
            comparison.random.revisit_ratio,
            comparison.local_q.revisit_ratio,
            comparison.scent_q.revisit_ratio,
            comparison.conflict_scent_q.revisit_ratio,
            comparison.memory_scent_q.revisit_ratio,
            comparison.visit_scent_q.revisit_ratio,
            comparison.loop_scent_q.revisit_ratio,
            comparison.novelty_scent_q.revisit_ratio,
        ),
    ]
    if comparison.novelty_scent_reward_q is not None:
        novelty = comparison.novelty_scent_reward_q
        lines.extend(
            [
                "",
                f"novelty-scent-reward-{comparison.novelty_reward:g}:",
                f"  average reward: {novelty.average_reward:.3f}",
                f"  average lifespan: {novelty.average_lifespan:.3f}",
                f"  food eaten: {novelty.food_eaten:.3f}",
                f"  poison collisions: {novelty.poison_collisions:.3f}",
                f"  novelty bonuses: {novelty.novelty_bonuses:.3f}",
                f"  novelty reward total: {novelty.novelty_reward_total:.3f}",
                f"  loop detections: {novelty.loop_detections:.3f}",
                f"  unique tiles: {novelty.unique_tiles_visited:.3f}",
                f"  revisit ratio: {novelty.revisit_ratio:.3f}",
            ]
        )
    if comparison.loop_scent_penalty_q is not None:
        penalty = comparison.loop_scent_penalty_q
        lines.extend(
            [
                "",
                "loop-scent-loop-penalty:",
                f"  average reward: {penalty.average_reward:.3f}",
                f"  average lifespan: {penalty.average_lifespan:.3f}",
                f"  food eaten: {penalty.food_eaten:.3f}",
                f"  poison collisions: {penalty.poison_collisions:.3f}",
                f"  loop detections: {penalty.loop_detections:.3f}",
                f"  unique tiles: {penalty.unique_tiles_visited:.3f}",
                f"  revisit ratio: {penalty.revisit_ratio:.3f}",
            ]
        )
    return "\n".join(lines)


def _mean_metrics(summaries: list[RunSummary]) -> MeanMetrics:
    if not summaries:
        raise ValueError("Cannot average an empty summary list.")
    count = len(summaries)
    return MeanMetrics(
        average_reward=sum(summary.average_reward for summary in summaries) / count,
        average_lifespan=sum(summary.average_lifespan for summary in summaries) / count,
        food_eaten=sum(summary.food_eaten for summary in summaries) / count,
        poison_collisions=sum(summary.poison_collisions for summary in summaries) / count,
        wasted_moves=sum(summary.wasted_moves for summary in summaries) / count,
        repeated_positions=sum(summary.repeated_positions for summary in summaries) / count,
        unique_tiles_visited=sum(summary.unique_tiles_visited for summary in summaries) / count,
        loop_detections=sum(summary.loop_detections for summary in summaries) / count,
        short_loops=sum(summary.short_loops for summary in summaries) / count,
        medium_loops=sum(summary.medium_loops for summary in summaries) / count,
        long_loops=sum(summary.long_loops for summary in summaries) / count,
        novelty_bonuses=sum(summary.novelty_bonuses for summary in summaries) / count,
        novelty_reward_total=sum(summary.novelty_reward_total for summary in summaries) / count,
        revisit_ratio=sum(summary.revisit_ratio for summary in summaries) / count,
    )


def _format_mean_row(
    label: str,
    random: float,
    local: float,
    scent: float,
    conflict: float,
    memory: float,
    visit: float,
    loop: float,
    novelty: float,
) -> str:
    return (
        f"{label:<18} {random:10.3f} {local:10.3f}"
        f" {scent:10.3f} {conflict:10.3f} {memory:10.3f}"
        f" {visit:10.3f} {loop:10.3f} {novelty:10.3f}"
    )


def _format_summary_row(
    label: str,
    random: float,
    local: float,
    scent: float,
    conflict: float,
    memory: float,
    visit: float,
    loop: float,
    novelty: float,
) -> str:
    return _format_mean_row(
        label,
        random,
        local,
        scent,
        conflict,
        memory,
        visit,
        loop,
        novelty,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-episodes", type=int, default=500)
    parser.add_argument("--eval-episodes", type=int, default=50)
    parser.add_argument("--grid-size", type=int, default=10)
    parser.add_argument("--load-path", type=Path)
    parser.add_argument("--encoder", choices=sorted(ENCODERS), default="local")
    parser.add_argument("--poison-penalty", type=float)
    parser.add_argument("--poison-energy-cost", type=int)
    parser.add_argument("--food-reward", type=float)
    parser.add_argument("--step-penalty", type=float)
    parser.add_argument(
        "--loop-penalty",
        type=float,
        default=0.0,
        help="Optional reward penalty applied when a loop is detected.",
    )
    parser.add_argument(
        "--novelty-reward",
        type=float,
        default=0.0,
        help="Optional reward bonus for entering a new tile in the episode.",
    )
    parser.add_argument(
        "--compare-scent",
        action="store_true",
        help=(
            "Compare random, local-tile Q-learning, raw scent Q-learning, "
            "conflict-scent, memory-scent, and visit-scent Q-learning."
        ),
    )
    parser.add_argument(
        "--multi-seed",
        action="store_true",
        help=(
            "Average random, local Q-learning, raw scent Q-learning, and "
            "conflict-scent, memory-scent, and visit-scent Q-learning across seeds."
        ),
    )
    parser.add_argument("--seeds", type=int, default=5)
    args = parser.parse_args()
    overrides = RewardOverrides(
        poison_penalty=args.poison_penalty,
        poison_energy_cost=args.poison_energy_cost,
        food_reward=args.food_reward,
        step_penalty=args.step_penalty,
        loop_penalty=args.loop_penalty,
        novelty_reward=args.novelty_reward,
    )
    config = build_config(grid_size=args.grid_size, overrides=overrides)

    if args.multi_seed:
        comparison = evaluate_multi_seed_variants(
            seed=args.seed,
            seeds=args.seeds,
            train_episodes=args.train_episodes,
            eval_episodes=args.eval_episodes,
            grid_size=args.grid_size,
            overrides=overrides,
        )
        print(format_multi_seed_comparison(comparison))
        return

    if args.compare_scent:
        (
            random_summary,
            local_summary,
            scent_summary,
            conflict_summary,
            memory_summary,
            visit_summary,
            loop_summary,
            novelty_summary,
            _,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = evaluate_q_learning_variants(
            seed=args.seed,
            train_episodes=args.train_episodes,
            eval_episodes=args.eval_episodes,
            grid_size=args.grid_size,
            config=config,
        )
        print(
            format_variant_comparison(
                random_summary,
                local_summary,
                scent_summary,
                conflict_summary,
                memory_summary,
                visit_summary,
                loop_summary,
                novelty_summary,
            )
        )
        return

    random_summary, q_summary, _ = evaluate_q_learning(
        seed=args.seed,
        train_episodes=args.train_episodes,
        eval_episodes=args.eval_episodes,
        grid_size=args.grid_size,
        load_path=args.load_path,
        encoder_name=args.encoder,
        config=config,
        loop_penalty=args.loop_penalty,
        novelty_reward=args.novelty_reward,
    )
    print(format_comparison(random_summary, q_summary))


if __name__ == "__main__":
    main()
