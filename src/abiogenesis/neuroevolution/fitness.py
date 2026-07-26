"""Raw-reward fitness and diagnostic evaluation for experimental NEAT policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable

from abiogenesis.agents.memory import LoopMemoryTracker
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.metrics.recorder import EpisodeRecord, RunSummary
from abiogenesis.neuroevolution.policy import ActivatingNetwork, NeatPolicy


@dataclass(frozen=True)
class EvaluationBatch:
    """Ordered episode records and summaries for one seed role."""

    root_seeds: tuple[int, ...]
    episodes_per_seed: int
    records: tuple[EpisodeRecord, ...]
    seed_summaries: tuple[RunSummary, ...]
    summary: RunSummary

    @property
    def mean_reward(self) -> float:
        return self.summary.average_reward

    def as_dict(self) -> dict[str, object]:
        return {
            "root_seeds": list(self.root_seeds),
            "episodes_per_seed": self.episodes_per_seed,
            "fitness": self.mean_reward,
            "aggregate": asdict(self.summary),
            "per_seed": [
                {"root_seed": seed, "metrics": asdict(summary)}
                for seed, summary in zip(self.root_seeds, self.seed_summaries, strict=True)
            ],
            "episodes": [asdict(record) for record in self.records],
        }


def validate_seed_roles(
    fitness_seeds: tuple[int, ...],
    holdout_seeds: tuple[int, ...],
) -> None:
    """Require ordered, unique, disjoint non-negative seed lists."""

    for label, seeds in (("fitness", fitness_seeds), ("holdout", holdout_seeds)):
        if not seeds:
            raise ValueError(f"{label} seeds must not be empty")
        if any(seed < 0 for seed in seeds):
            raise ValueError(f"{label} seeds must be non-negative")
        if len(set(seeds)) != len(seeds):
            raise ValueError(f"{label} seeds must be unique")
    overlap = set(fitness_seeds).intersection(holdout_seeds)
    if overlap:
        raise ValueError(f"fitness and holdout seeds overlap: {sorted(overlap)}")


def run_policy_episode(
    *,
    network: ActivatingNetwork,
    seed: int,
    config: BacteriaWorldConfig | None = None,
) -> EpisodeRecord:
    """Evaluate one policy using only the environment's unmodified reward."""

    world_config = config or BacteriaWorldConfig()
    env = BacteriaWorldEnv(world_config)
    policy = NeatPolicy(network)
    observation, _ = env.reset(seed=seed)
    policy.reset(observation)
    loop_memory = LoopMemoryTracker()
    loop_memory.reset(observation)
    visited_positions = {tuple(int(value) for value in observation["organism"])}
    total_reward = 0.0
    food_eaten = 0
    poison_collisions = 0
    wasted_moves = 0
    loop_detections = 0
    short_loops = 0
    medium_loops = 0
    long_loops = 0
    terminated = False
    truncated = False

    while not (terminated or truncated):
        action = policy.act(observation)
        observation, reward, terminated, truncated, info = env.step(action)
        policy.update(action=action, observation=observation)
        loop_memory.update_after_step(action=action, observation=observation)
        total_reward += reward
        food_eaten += int(info["ate_food"])
        poison_collisions += int(info["hit_poison"])
        wasted_moves += int(info["wasted_move"])
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
        repeated_positions=wasted_moves,
        unique_tiles_visited=len(visited_positions),
        loop_detections=loop_detections,
        short_loops=short_loops,
        medium_loops=medium_loops,
        long_loops=long_loops,
        novelty_bonuses=0,
        novelty_reward_total=0.0,
    )


def evaluate_network(
    *,
    network: ActivatingNetwork,
    root_seeds: tuple[int, ...],
    episodes_per_seed: int,
    config: BacteriaWorldConfig | None = None,
    episode_runner: Callable[..., EpisodeRecord] = run_policy_episode,
) -> EvaluationBatch:
    """Evaluate roots in their supplied order and average all raw-reward episodes."""

    if not root_seeds:
        raise ValueError("root seeds must not be empty")
    if episodes_per_seed < 1:
        raise ValueError("episodes-per-seed must be at least 1")
    world_config = config or BacteriaWorldConfig()
    records: list[EpisodeRecord] = []
    seed_summaries: list[RunSummary] = []
    for root_seed in root_seeds:
        seed_records = [
            episode_runner(
                network=network,
                seed=root_seed + episode_index,
                config=world_config,
            )
            for episode_index in range(episodes_per_seed)
        ]
        records.extend(seed_records)
        seed_summaries.append(
            RunSummary.from_records(
                records=seed_records,
                seed=root_seed,
                grid_size=world_config.width,
            )
        )
    summary = RunSummary.from_records(
        records=records,
        seed=root_seeds[0],
        grid_size=world_config.width,
    )
    return EvaluationBatch(
        root_seeds=root_seeds,
        episodes_per_seed=episodes_per_seed,
        records=tuple(records),
        seed_summaries=tuple(seed_summaries),
        summary=summary,
    )
