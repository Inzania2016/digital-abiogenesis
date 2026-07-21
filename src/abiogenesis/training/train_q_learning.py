"""Train the tabular Q-learning microbe."""

import argparse
from pathlib import Path

from abiogenesis.agents import (
    LoopScentEncoder,
    MemoryScentEncoder,
    NoveltyScentEncoder,
    QLearningAgent,
    VisitScentEncoder,
    encode_conflict_scent_observation,
    encode_observation,
    encode_scent_observation,
)
from abiogenesis.agents.memory import reset_encoder_memory, update_encoder_memory
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.metrics.recorder import EpisodeRecord, RunSummary

ENCODERS = {
    "conflict-scent": encode_conflict_scent_observation,
    "local": encode_observation,
    "loop-scent": LoopScentEncoder,
    "memory-scent": MemoryScentEncoder,
    "novelty-scent": NoveltyScentEncoder,
    "scent": encode_scent_observation,
    "visit-scent": VisitScentEncoder,
}


def build_encoder(encoder_name: str):
    """Create a fresh encoder by name."""

    if encoder_name not in ENCODERS:
        raise ValueError(f"Unknown encoder: {encoder_name}")
    encoder = ENCODERS[encoder_name]
    return encoder() if isinstance(encoder, type) else encoder


def novelty_bonus_for_position(
    *,
    position: tuple[int, int],
    visited_positions: set[tuple[int, int]],
    novelty_reward: float,
) -> float:
    """Return the novelty reward for entering a previously unseen tile."""

    if novelty_reward == 0.0 or position in visited_positions:
        return 0.0
    return novelty_reward


def train_q_learning(
    *,
    seed: int = 0,
    episodes: int = 500,
    grid_size: int = 10,
    alpha: float = 0.2,
    gamma: float = 0.95,
    epsilon: float = 1.0,
    epsilon_decay: float = 0.995,
    min_epsilon: float = 0.05,
    encoder_name: str = "local",
    config: BacteriaWorldConfig | None = None,
    loop_penalty: float = 0.0,
    novelty_reward: float = 0.0,
) -> tuple[QLearningAgent, list[EpisodeRecord], RunSummary]:
    """Train a tabular Q-learning agent and return training records."""

    if episodes < 1:
        raise ValueError("episodes must be at least 1")
    if grid_size < 2:
        raise ValueError("grid_size must be at least 2")
    encoder = build_encoder(encoder_name)

    world_config = config or BacteriaWorldConfig(width=grid_size, height=grid_size)
    env = BacteriaWorldEnv(world_config)
    agent = QLearningAgent(
        env.action_space,
        alpha=alpha,
        gamma=gamma,
        epsilon=epsilon,
        epsilon_decay=epsilon_decay,
        min_epsilon=min_epsilon,
        seed=seed,
        encoder=encoder,
    )

    records: list[EpisodeRecord] = []
    for episode_index in range(episodes):
        observation, _ = env.reset(seed=seed + episode_index)
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
        terminated = False
        truncated = False

        while not (terminated or truncated):
            state = agent.encoder(observation)
            action = agent.act(observation, explore=True)
            next_observation, reward, terminated, truncated, info = env.step(action)
            update_encoder_memory(
                agent.encoder,
                action=action,
                observation=next_observation,
            )
            loop_memory = getattr(agent.encoder, "memory", None)
            loop_detected = bool(getattr(loop_memory, "loop_detected", False))
            next_position = tuple(int(value) for value in next_observation["organism"])
            novelty_bonus = novelty_bonus_for_position(
                position=next_position,
                visited_positions=visited_positions,
                novelty_reward=novelty_reward,
            )
            shaped_reward = reward + (loop_penalty if loop_detected else 0.0) + novelty_bonus
            next_state = agent.encoder(next_observation)
            agent.update(
                state,
                action,
                shaped_reward,
                next_state,
                done=terminated or truncated,
            )
            observation = next_observation
            total_reward += shaped_reward
            food_eaten += int(info["ate_food"])
            poison_collisions += int(info["hit_poison"])
            wasted_moves += int(info["wasted_move"])
            repeated_positions += int(info["wasted_move"])
            if loop_detected:
                loop_detections += 1
                loop_bucket = int(getattr(loop_memory, "loop_bucket", 0))
                short_loops += int(loop_bucket == 1)
                medium_loops += int(loop_bucket == 2)
                long_loops += int(loop_bucket == 3)
            if novelty_bonus != 0.0:
                novelty_bonuses += 1
                novelty_reward_total += novelty_bonus
            visited_positions.add(next_position)

        agent.decay_epsilon()
        records.append(
            EpisodeRecord(
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
        )

    summary = RunSummary.from_records(records=records, seed=seed, grid_size=grid_size)
    return agent, records, summary


def format_training_summary(summary: RunSummary, agent: QLearningAgent) -> str:
    """Create a clear text summary for training."""

    return "\n".join(
        [
            "Q-Learning Training: The Slightly Less Stupid Microbe",
            f"episodes: {summary.episodes}",
            f"seed: {summary.seed}",
            f"grid: {summary.grid_size}x{summary.grid_size}",
            f"average reward: {summary.average_reward:.3f}",
            f"average lifespan: {summary.average_lifespan:.2f} steps",
            f"food eaten: {summary.food_eaten}",
            f"poison collisions: {summary.poison_collisions}",
            f"repeated positions: {summary.repeated_positions}",
            f"unique tiles visited: {summary.unique_tiles_visited}",
            f"loop detections: {summary.loop_detections}",
            f"novelty bonuses: {summary.novelty_bonuses}",
            f"novelty reward total: {summary.novelty_reward_total:.3f}",
            f"final epsilon: {agent.epsilon:.3f}",
            f"q-table states: {len(agent.q_table)}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--grid-size", type=int, default=10)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--gamma", type=float, default=0.95)
    parser.add_argument("--epsilon", type=float, default=1.0)
    parser.add_argument("--epsilon-decay", type=float, default=0.995)
    parser.add_argument("--min-epsilon", type=float, default=0.05)
    parser.add_argument("--encoder", choices=sorted(ENCODERS), default="local")
    parser.add_argument("--loop-penalty", type=float, default=0.0)
    parser.add_argument("--novelty-reward", type=float, default=0.0)
    parser.add_argument("--save-path", type=Path)
    args = parser.parse_args()

    agent, _, summary = train_q_learning(
        seed=args.seed,
        episodes=args.episodes,
        grid_size=args.grid_size,
        alpha=args.alpha,
        gamma=args.gamma,
        epsilon=args.epsilon,
        epsilon_decay=args.epsilon_decay,
        min_epsilon=args.min_epsilon,
        encoder_name=args.encoder,
        loop_penalty=args.loop_penalty,
        novelty_reward=args.novelty_reward,
    )
    if args.save_path is not None:
        args.save_path.parent.mkdir(parents=True, exist_ok=True)
        agent.save(args.save_path)

    print(format_training_summary(summary, agent))


if __name__ == "__main__":
    main()
