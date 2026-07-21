"""Run and summarize the random baseline."""

import argparse

from abiogenesis.agents import RandomAgent
from abiogenesis.agents.memory import LoopMemoryTracker
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.metrics.recorder import EpisodeRecord, RunSummary


def run_episode(
    *,
    seed: int,
    grid_size: int = 10,
    config: BacteriaWorldConfig | None = None,
) -> EpisodeRecord:
    """Run one random episode and return measured behavior."""

    world_config = config or BacteriaWorldConfig(width=grid_size, height=grid_size)
    env = BacteriaWorldEnv(world_config)
    agent = RandomAgent(env.action_space, seed=seed)
    observation, _ = env.reset(seed=seed)
    total_reward = 0.0
    food_eaten = 0
    poison_collisions = 0
    wasted_moves = 0
    repeated_positions = 0
    loop_detections = 0
    short_loops = 0
    medium_loops = 0
    long_loops = 0
    visited_positions = {tuple(int(value) for value in observation["organism"])}
    loop_memory = LoopMemoryTracker()
    loop_memory.reset(observation)

    terminated = False
    truncated = False
    while not (terminated or truncated):
        action = agent.act(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        loop_memory.update_after_step(action=action, observation=observation)
        total_reward += reward
        food_eaten += int(info["ate_food"])
        poison_collisions += int(info["hit_poison"])
        wasted_moves += int(info["wasted_move"])
        repeated_positions += int(info["wasted_move"])
        if loop_memory.loop_detected:
            loop_detections += 1
            short_loops += int(loop_memory.loop_bucket == 1)
            medium_loops += int(loop_memory.loop_bucket == 2)
            long_loops += int(loop_memory.loop_bucket == 3)
        visited_positions.add(tuple(int(value) for value in observation["organism"]))

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
    )


def evaluate_random(
    *,
    seed: int = 0,
    episodes: int = 20,
    grid_size: int = 10,
    config: BacteriaWorldConfig | None = None,
) -> tuple[list[EpisodeRecord], RunSummary]:
    """Run a batch of deterministic random baseline episodes."""

    if episodes < 1:
        raise ValueError("episodes must be at least 1")
    if grid_size < 2:
        raise ValueError("grid_size must be at least 2")

    records = [
        run_episode(
            seed=seed + episode_index,
            grid_size=grid_size,
            config=config,
        )
        for episode_index in range(episodes)
    ]
    summary = RunSummary.from_records(
        records=records,
        seed=seed,
        grid_size=grid_size,
    )
    return records, summary


def format_summary(summary: RunSummary) -> str:
    """Create a clear text summary for lab runs."""

    return "\n".join(
        [
            "Random Baseline: The Drunk Microbe",
            f"episodes: {summary.episodes}",
            f"seed: {summary.seed}",
            f"grid: {summary.grid_size}x{summary.grid_size}",
            f"average reward: {summary.average_reward:.3f}",
            f"average lifespan: {summary.average_lifespan:.2f} steps",
            f"food eaten: {summary.food_eaten}",
            f"poison collisions: {summary.poison_collisions}",
            f"wasted moves: {summary.wasted_moves}",
            f"repeated positions: {summary.repeated_positions}",
            f"unique tiles visited: {summary.unique_tiles_visited}",
            f"loop detections: {summary.loop_detections}",
            f"revisit ratio: {summary.revisit_ratio:.3f}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--grid-size", type=int, default=10)
    args = parser.parse_args()

    _, summary = evaluate_random(
        seed=args.seed,
        episodes=args.episodes,
        grid_size=args.grid_size,
    )
    print(format_summary(summary))


if __name__ == "__main__":
    main()
