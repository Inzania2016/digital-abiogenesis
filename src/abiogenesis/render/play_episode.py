"""Play one visible Bacterium-0 episode."""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from abiogenesis.agents import QLearningAgent, RandomAgent
from abiogenesis.core.config import BacteriaWorldConfig
from abiogenesis.envs import BacteriaWorldEnv
from abiogenesis.render import format_q_debug_overlay, render_observation_ascii
from abiogenesis.render.pygame_controls import (
    ViewerControls,
    apply_key,
    consume_transient_flags,
    screenshot_path,
)
from abiogenesis.render.pygame_renderer import PygameRenderer, frame_from_observation
from abiogenesis.render.sprite_assets import SpriteConfig
from abiogenesis.agents.memory import reset_encoder_memory, update_encoder_memory
from abiogenesis.training.train_q_learning import ENCODERS, build_encoder, train_q_learning


class Agent(Protocol):
    """Shared action interface for playback agents."""

    def act(self, observation, *, explore: bool = False) -> int:
        """Choose one action."""


@dataclass
class PlaybackStats:
    """Mutable counters for one watched episode."""

    last_reward: float = 0.0
    total_reward: float = 0.0
    food_eaten: int = 0
    poison_collisions: int = 0
    wasted_moves: int = 0
    repeated_positions: int = 0

    def record_step(
        self,
        *,
        reward: float,
        ate_food: bool,
        hit_poison: bool,
        wasted_move: bool,
    ) -> None:
        self.last_reward = reward
        self.total_reward += reward
        self.food_eaten += int(ate_food)
        self.poison_collisions += int(hit_poison)
        self.wasted_moves += int(wasted_move)
        self.repeated_positions += int(wasted_move)


def build_agent(
    *,
    agent_name: str,
    env: BacteriaWorldEnv,
    seed: int,
    q_path: Path | None,
    train_episodes: int,
    encoder_name: str,
) -> RandomAgent | QLearningAgent:
    """Create the selected playback agent."""

    if agent_name == "random":
        return RandomAgent(env.action_space, seed=seed)

    if encoder_name not in ENCODERS:
        raise ValueError(f"Unknown encoder: {encoder_name}")

    if q_path is None:
        agent, _, _ = train_q_learning(
            seed=seed,
            episodes=train_episodes,
            grid_size=env.config.width,
            encoder_name=encoder_name,
        )
        return agent

    agent = QLearningAgent(
        env.action_space,
        seed=seed,
        encoder=build_encoder(encoder_name),
    )
    agent.load(q_path)
    return agent


def choose_action(agent: RandomAgent | QLearningAgent, observation) -> int:
    """Choose one action without requiring both agent classes to share kwargs."""

    if isinstance(agent, QLearningAgent):
        return agent.act(observation, explore=False)
    return agent.act(observation)


def clear_terminal() -> None:
    """Clear the terminal for frame-by-frame playback."""

    os.system("cls" if os.name == "nt" else "clear")


def play_ascii(
    *,
    env: BacteriaWorldEnv,
    agent: RandomAgent | QLearningAgent,
    seed: int,
    delay: float,
    encoder_name: str,
    debug_overlay: bool = False,
) -> None:
    """Run one episode in terminal ASCII."""

    observation, _ = env.reset(seed=seed)
    if isinstance(agent, QLearningAgent):
        reset_encoder_memory(agent.encoder, observation)
    stats = PlaybackStats()
    terminated = False
    truncated = False

    while True:
        action = None
        if not (terminated or truncated):
            action = choose_action(agent, observation)

        clear_terminal()
        print(
            render_observation_ascii(
                observation=observation,
                max_steps=env.config.max_steps,
                last_reward=stats.last_reward,
                total_reward=stats.total_reward,
                food_eaten=stats.food_eaten,
                poison_collisions=stats.poison_collisions,
            )
        )
        if debug_overlay and isinstance(agent, QLearningAgent) and action is not None:
            print()
            print(
                format_q_debug_overlay(
                    agent=agent,
                    observation=observation,
                    encoder_name=encoder_name,
                    chosen_action=action,
                )
            )
        if terminated or truncated:
            break

        time.sleep(delay)
        observation, reward, terminated, truncated, info = env.step(action)
        if isinstance(agent, QLearningAgent):
            update_encoder_memory(
                agent.encoder,
                action=action,
                observation=observation,
            )
        stats.record_step(
            reward=reward,
            ate_food=info["ate_food"],
            hit_poison=info["hit_poison"],
            wasted_move=info["wasted_move"],
        )


def play_pygame(
    *,
    env: BacteriaWorldEnv,
    agent: RandomAgent | QLearningAgent,
    seed: int,
    delay: float,
    agent_name: str,
    encoder_name: str,
    tile_size: int,
    debug_overlay: bool = False,
    sprite_config: SpriteConfig | None = None,
) -> None:
    """Run one episode in a pygame window."""

    renderer = PygameRenderer(
        width=env.config.width,
        height=env.config.height,
        tile_size=tile_size,
        sprite_config=sprite_config,
    )
    clock = renderer.pygame.time.Clock()
    observation, _ = env.reset(seed=seed)
    if isinstance(agent, QLearningAgent):
        reset_encoder_memory(agent.encoder, observation)
    stats = PlaybackStats()
    controls = ViewerControls(delay=delay, show_scent=debug_overlay)
    trail: list[tuple[int, int]] = [tuple(int(value) for value in observation["organism"])]
    terminated = False
    truncated = False
    last_tick = 0.0

    try:
        running = True
        while running:
            for event in renderer.pygame.event.get():
                if event.type == renderer.pygame.QUIT:
                    running = False
                elif event.type == renderer.pygame.KEYDOWN:
                    controls = apply_key(
                        controls,
                        _pygame_key_name(renderer.pygame, event.key),
                    )

            if controls.should_quit:
                running = False

            if controls.should_reset:
                observation, _ = env.reset(seed=seed)
                if isinstance(agent, QLearningAgent):
                    reset_encoder_memory(agent.encoder, observation)
                stats = PlaybackStats()
                trail = [tuple(int(value) for value in observation["organism"])]
                terminated = False
                truncated = False
                last_tick = 0.0

            now = time.monotonic()
            if (
                not controls.paused
                and not (terminated or truncated)
                and now - last_tick >= controls.delay
            ):
                action = choose_action(agent, observation)
                observation, reward, terminated, truncated, info = env.step(action)
                if isinstance(agent, QLearningAgent):
                    update_encoder_memory(
                        agent.encoder,
                        action=action,
                        observation=observation,
                    )
                stats.record_step(
                    reward=reward,
                    ate_food=info["ate_food"],
                    hit_poison=info["hit_poison"],
                    wasted_move=info["wasted_move"],
                )
                trail.append(tuple(int(value) for value in observation["organism"]))
                last_tick = now

            encoded_state = (
                agent.encoder(observation) if isinstance(agent, QLearningAgent) else None
            )
            renderer.draw(
                frame_from_observation(
                    observation=observation,
                    max_steps=env.config.max_steps,
                    last_reward=stats.last_reward,
                    total_reward=stats.total_reward,
                    food_eaten=stats.food_eaten,
                    poison_collisions=stats.poison_collisions,
                    wasted_moves=stats.wasted_moves,
                    repeated_positions=stats.repeated_positions,
                    agent_type=agent_name,
                    encoder_name=encoder_name,
                    seed=seed,
                    paused=controls.paused,
                    delay=controls.delay,
                    show_hud=controls.show_hud,
                    show_trail=controls.show_trail,
                    show_scent=controls.show_scent,
                    trail=tuple(trail),
                    encoded_state=encoded_state,
                )
            )
            if controls.should_screenshot:
                path = screenshot_path(
                    directory=Path("artifacts") / "screenshots",
                    seed=seed,
                    step=int(observation["steps"][0]),
                )
                path.parent.mkdir(parents=True, exist_ok=True)
                renderer.save_screenshot(str(path))
            controls = consume_transient_flags(controls)
            clock.tick(30)
    finally:
        renderer.close()


def _pygame_key_name(pygame, key: int) -> str:
    if key == pygame.K_ESCAPE:
        return "escape"
    if key == pygame.K_F12:
        return "f12"
    if key == pygame.K_UP:
        return "up"
    if key == pygame.K_DOWN:
        return "down"
    if key == pygame.K_SPACE:
        return "space"
    if key in (pygame.K_PLUS, pygame.K_KP_PLUS):
        return "+"
    if key in (pygame.K_MINUS, pygame.K_KP_MINUS):
        return "-"
    return pygame.key.name(key)


def build_parser() -> argparse.ArgumentParser:
    """Build the playback CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=["random", "q-learning"], default="random")
    parser.add_argument("--renderer", choices=["ascii", "pygame"], default="ascii")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--grid-size", type=int, default=10)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--tile-size", type=int, default=48)
    parser.add_argument("--q-path", type=Path)
    parser.add_argument("--train-episodes", type=int, default=500)
    parser.add_argument("--encoder", choices=sorted(ENCODERS), default="local")
    parser.add_argument(
        "--debug-overlay",
        action="store_true",
        help="Show Q-learning state/scent details in ASCII, or scent overlay in pygame.",
    )
    parser.add_argument(
        "--sprite-dir",
        type=Path,
        default=Path("assets") / "sprites",
        help="Directory containing pygame sprite PNGs.",
    )
    parser.add_argument(
        "--no-sprites",
        action="store_true",
        help="Force the pygame renderer to use shape-based drawing.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.delay < 0:
        raise ValueError("delay must be non-negative")
    if args.tile_size < 20:
        raise ValueError("tile-size must be at least 20")

    env = BacteriaWorldEnv(BacteriaWorldConfig(width=args.grid_size, height=args.grid_size))
    agent = build_agent(
        agent_name=args.agent,
        env=env,
        seed=args.seed,
        q_path=args.q_path,
        train_episodes=args.train_episodes,
        encoder_name=args.encoder,
    )

    if args.renderer == "pygame":
        play_pygame(
            env=env,
            agent=agent,
            seed=args.seed,
            delay=args.delay,
            agent_name=args.agent,
            encoder_name=args.encoder,
            tile_size=args.tile_size,
            debug_overlay=args.debug_overlay,
            sprite_config=SpriteConfig.from_directory(
                args.sprite_dir,
                enabled=not args.no_sprites,
            ),
        )
    else:
        play_ascii(
            env=env,
            agent=agent,
            seed=args.seed,
            delay=args.delay,
            encoder_name=args.encoder,
            debug_overlay=args.debug_overlay,
        )


if __name__ == "__main__":
    main()
