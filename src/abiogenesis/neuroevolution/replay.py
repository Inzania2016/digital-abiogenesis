"""Replay a trusted local NEAT winner through the existing ASCII renderer."""

from __future__ import annotations

import argparse
import pickle
import time
from pathlib import Path

from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.neuroevolution import ACTION_ORDER, NeatPolicy, POLICY_ID
from abiogenesis.neuroevolution.config import load_neat_config, require_neat
from abiogenesis.neuroevolution.validation import validate_run
from abiogenesis.render.ascii_renderer import render_observation_ascii


def load_replay_policy(run_directory: Path) -> tuple[dict[str, object], NeatPolicy]:
    """Validate, then load a locally trusted pickle and its effective configuration."""

    manifest = validate_run(run_directory)
    neat = require_neat()
    config = load_neat_config(neat, run_directory / "neat-config.ini")
    with (run_directory / "winner_genome.pkl").open("rb") as handle:
        winner = pickle.load(handle)  # noqa: S301 - contract warns that only trusted local runs load.
    expected_id = manifest["winner"]["genome_id"]
    if int(winner.key) != expected_id:
        raise ValueError("Winner genome ID differs from the validated manifest.")
    network = neat.nn.FeedForwardNetwork.create(winner, config)
    return manifest, NeatPolicy(network)


def replay(
    *,
    run_directory: Path,
    seed: int,
    debug_overlay: bool = False,
    delay: float = 0.0,
    max_frames: int | None = None,
) -> int:
    """Render an episode to text and return the number of actions taken."""

    if delay < 0:
        raise ValueError("delay must be non-negative")
    if max_frames is not None and max_frames < 1:
        raise ValueError("max-frames must be at least 1")
    manifest, policy = load_replay_policy(run_directory)
    environment = manifest["environment"]
    if not isinstance(environment, dict):
        raise ValueError("Manifest environment must be an object.")
    config = BacteriaWorldConfig(**environment)
    env = BacteriaWorldEnv(config)
    observation, _ = env.reset(seed=seed)
    policy.reset(observation)
    total_reward = 0.0
    last_reward = 0.0
    food_eaten = 0
    poison_collisions = 0
    frames = 0

    while True:
        print(
            render_observation_ascii(
                observation=observation,
                max_steps=config.max_steps,
                last_reward=last_reward,
                total_reward=total_reward,
                food_eaten=food_eaten,
                poison_collisions=poison_collisions,
            )
        )
        if max_frames is not None and frames >= max_frames:
            break
        if env.energy <= 0 or env.steps >= config.max_steps:
            break
        action = policy.act(observation)
        if debug_overlay:
            print(
                "\n".join(
                    [
                        f"policy={POLICY_ID}",
                        f"run_id={manifest['run_id']}",
                        f"winner_genome_id={manifest['winner']['genome_id']}",
                        f"input_vector={policy.last_input}",
                        f"output_scores={policy.last_scores}",
                        f"action={ACTION_ORDER[action]} ({action})",
                    ]
                )
            )
        observation, last_reward, terminated, truncated, info = env.step(action)
        policy.update(action=action, observation=observation)
        total_reward += last_reward
        food_eaten += int(info["ate_food"])
        poison_collisions += int(info["hit_poison"])
        frames += 1
        if delay:
            time.sleep(delay)
        if terminated or truncated:
            print(
                render_observation_ascii(
                    observation=observation,
                    max_steps=config.max_steps,
                    last_reward=last_reward,
                    total_reward=total_reward,
                    food_eaten=food_eaten,
                    poison_collisions=poison_collisions,
                )
            )
            break
    return frames


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--neat-run", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--debug-overlay", action="store_true")
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--max-frames", type=int)
    args = parser.parse_args()
    replay(
        run_directory=args.neat_run,
        seed=args.seed,
        debug_overlay=args.debug_overlay,
        delay=args.delay,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    main()
