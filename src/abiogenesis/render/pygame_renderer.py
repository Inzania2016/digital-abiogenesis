"""Optional pygame renderer for watching Bacterium-0."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from abiogenesis.core.types import Position
from abiogenesis.render.debug_overlay import format_scent_lines
from abiogenesis.render.pygame_theme import DEFAULT_THEME, PygameTheme
from abiogenesis.render.sprite_assets import SpriteAssets, SpriteConfig


@dataclass(frozen=True)
class PygameFrame:
    """State needed to draw one visual frame."""

    organism: Position
    food: np.ndarray
    poison: np.ndarray
    step: int
    max_steps: int
    energy: int
    last_reward: float
    total_reward: float
    food_eaten: int
    poison_collisions: int
    wasted_moves: int = 0
    repeated_positions: int = 0
    agent_type: str = "random"
    encoder_name: str = "local"
    seed: int = 0
    paused: bool = False
    delay: float = 0.2
    show_hud: bool = True
    show_trail: bool = False
    show_scent: bool = False
    trail: tuple[Position, ...] = ()
    encoded_state: tuple[int, ...] | None = None


class PygameRenderer:
    """A lightweight artificial-life lab dish renderer."""

    def __init__(
        self,
        *,
        width: int,
        height: int,
        tile_size: int = 48,
        theme: PygameTheme = DEFAULT_THEME,
        sprite_config: SpriteConfig | None = None,
    ) -> None:
        try:
            import pygame
        except ImportError as exc:
            raise RuntimeError(
                "pygame is not installed. Install the render extra with "
                '`python -m pip install -e ".[render]"`.'
            ) from exc

        self.pygame = pygame
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.theme = theme
        self.sprite_config = sprite_config or SpriteConfig()
        self.margin = 18
        self.panel_width = 320
        self.grid_width = width * tile_size
        self.grid_height = height * tile_size
        self.window_width = self.grid_width + self.panel_width + self.margin * 3
        self.window_height = max(self.grid_height + self.margin * 2, 520)
        pygame.init()
        pygame.display.set_caption("Digital Abiogenesis: Bacterium-0")
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.font = pygame.font.SysFont("consolas", 17)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self.title_font = pygame.font.SysFont("consolas", 20, bold=True)
        self.sprites = SpriteAssets(pygame=pygame, config=self.sprite_config)

    def draw(self, frame: PygameFrame) -> None:
        """Draw one frame."""

        pygame = self.pygame
        t = pygame.time.get_ticks() / 1000.0
        self.screen.fill(self.theme.background)
        grid_origin = (self.margin, self.margin)
        self._draw_dish_background(grid_origin)

        for y in range(self.height):
            for x in range(self.width):
                rect = self._cell_rect(x, y, grid_origin)
                self._draw_tile_background(rect=rect, x=x, y=y)

        if frame.show_trail:
            self._draw_trail(frame=frame, grid_origin=grid_origin)

        for y in range(self.height):
            for x in range(self.width):
                rect = self._cell_rect(x, y, grid_origin)
                self._draw_tile_contents(rect=rect, x=x, y=y, frame=frame, t=t)

        self._draw_grid_lines(grid_origin)
        self._draw_organism(frame=frame, grid_origin=grid_origin, t=t)

        if frame.show_scent and frame.encoded_state is not None:
            self._draw_scent_overlay(frame=frame, grid_origin=grid_origin)

        if frame.show_hud:
            self._draw_hud(frame)

        pygame.display.flip()

    def save_screenshot(self, path: str) -> None:
        """Save the current screen to an image."""

        self.pygame.image.save(self.screen, path)

    def close(self) -> None:
        """Close the pygame window."""

        self.pygame.quit()

    def _cell_rect(self, x: int, y: int, origin: tuple[int, int]):
        return self.pygame.Rect(
            origin[0] + x * self.tile_size,
            origin[1] + y * self.tile_size,
            self.tile_size,
            self.tile_size,
        )

    def _draw_dish_background(self, origin: tuple[int, int]) -> None:
        pygame = self.pygame
        rect = pygame.Rect(
            origin[0] - 6,
            origin[1] - 6,
            self.grid_width + 12,
            self.grid_height + 12,
        )
        pygame.draw.rect(self.screen, (15, 19, 22), rect, border_radius=10)
        pygame.draw.rect(self.screen, self.theme.panel_edge, rect, width=2, border_radius=10)

    def _draw_tile_background(
        self,
        *,
        rect,
        x: int,
        y: int,
    ) -> None:
        pygame = self.pygame
        fill = self.theme.empty_alt if (x + y) % 2 else self.theme.empty
        pygame.draw.rect(self.screen, fill, rect)

    def _draw_tile_contents(
        self,
        *,
        rect,
        x: int,
        y: int,
        frame: PygameFrame,
        t: float,
    ) -> None:
        if frame.food[y, x]:
            self._draw_food(rect=rect, t=t, phase=x + y)
        elif frame.poison[y, x]:
            self._draw_poison(rect=rect, t=t)

    def _draw_food(self, *, rect, t: float, phase: int) -> None:
        pygame = self.pygame
        sprite = self.sprites.surface("food", tile_size=self.tile_size)
        pulse = int(35 + 25 * math.sin(t * 5 + phase))
        inner = rect.inflate(-self.tile_size * 0.36, -self.tile_size * 0.36)
        pygame.draw.ellipse(self.screen, _brighten(self.theme.food_glow, pulse // 2), inner)
        if sprite is None:
            pygame.draw.rect(self.screen, _brighten(self.theme.food, pulse), rect)
            inner = rect.inflate(-self.tile_size * 0.42, -self.tile_size * 0.42)
            pygame.draw.ellipse(self.screen, self.theme.food_glow, inner)
            return

        bob = int(math.sin(t * 4 + phase) * max(1, self.tile_size * 0.04))
        self.screen.blit(sprite, sprite.get_rect(center=(rect.centerx, rect.centery + bob)))

    def _draw_poison(self, *, rect, t: float) -> None:
        pygame = self.pygame
        sprite = self.sprites.surface("poison", tile_size=self.tile_size)
        glow_size = int(self.tile_size * (0.62 + 0.04 * math.sin(t * 4)))
        glow_rect = pygame.Rect(0, 0, glow_size, glow_size)
        glow_rect.center = rect.center
        pygame.draw.ellipse(self.screen, self.theme.poison_glow, glow_rect, width=2)
        if sprite is None:
            pygame.draw.rect(self.screen, self.theme.poison, rect)
            pad = max(5, self.tile_size // 5)
            pygame.draw.line(
                self.screen,
                self.theme.poison_glow,
                (rect.left + pad, rect.top + pad),
                (rect.right - pad, rect.bottom - pad),
                width=3,
            )
            pygame.draw.line(
                self.screen,
                self.theme.poison_glow,
                (rect.right - pad, rect.top + pad),
                (rect.left + pad, rect.bottom - pad),
                width=3,
            )
            return

        self.screen.blit(sprite, sprite.get_rect(center=rect.center))

    def _draw_grid_lines(self, origin: tuple[int, int]) -> None:
        pygame = self.pygame
        for x in range(self.width + 1):
            px = origin[0] + x * self.tile_size
            pygame.draw.line(
                self.screen,
                self.theme.grid,
                (px, origin[1]),
                (px, origin[1] + self.grid_height),
            )
        for y in range(self.height + 1):
            py = origin[1] + y * self.tile_size
            pygame.draw.line(
                self.screen,
                self.theme.grid,
                (origin[0], py),
                (origin[0] + self.grid_width, py),
            )

    def _draw_organism(
        self,
        *,
        frame: PygameFrame,
        grid_origin: tuple[int, int],
        t: float,
    ) -> None:
        pygame = self.pygame
        x, y = frame.organism
        rect = self._cell_rect(x, y, grid_origin)
        center = rect.center
        sprite = self.sprites.surface("organism", tile_size=self.tile_size)
        if sprite is not None:
            scale = 1.0 + 0.04 * math.sin(t * 6)
            size = max(8, int(sprite.get_width() * scale))
            pulsed = pygame.transform.smoothscale(sprite, (size, size))
            pygame.draw.circle(
                self.screen,
                (23, 72, 104),
                center,
                max(8, int(size * 0.48)),
                width=2,
            )
            self.screen.blit(pulsed, pulsed.get_rect(center=center))
            return

        radius = max(8, int(self.tile_size * (0.28 + 0.04 * math.sin(t * 6))))
        pygame.draw.circle(self.screen, self.theme.organism, center, radius)
        pygame.draw.circle(self.screen, self.theme.organism_core, center, max(4, radius // 2))
        pygame.draw.circle(self.screen, (23, 72, 104), center, radius + 3, width=2)

    def _draw_trail(self, *, frame: PygameFrame, grid_origin: tuple[int, int]) -> None:
        pygame = self.pygame
        if not frame.trail:
            return
        max_alpha_steps = max(1, len(frame.trail))
        for index, (x, y) in enumerate(frame.trail[-80:]):
            rect = self._cell_rect(x, y, grid_origin).inflate(
                -self.tile_size * 0.58, -self.tile_size * 0.58
            )
            shade = int(50 + 100 * (index + 1) / max_alpha_steps)
            color = _brighten(self.theme.trail, shade // 5)
            pygame.draw.ellipse(self.screen, color, rect)

    def _draw_scent_overlay(self, *, frame: PygameFrame, grid_origin: tuple[int, int]) -> None:
        lines = format_scent_lines(
            state=frame.encoded_state or (),
            encoder_name=frame.encoder_name,
        )
        if not lines:
            return
        x, y = frame.organism
        center = self._cell_rect(x, y, grid_origin).center
        offsets = {
            "north": (0, -self.tile_size),
            "south": (0, self.tile_size),
            "east": (self.tile_size, 0),
            "west": (-self.tile_size, 0),
        }
        values = _direction_overlay_values(lines)
        for direction, label in values.items():
            dx, dy = offsets[direction]
            end = (center[0] + dx, center[1] + dy)
            color = self._scent_color(label)
            self.pygame.draw.line(self.screen, color, center, end, width=3)
            text = self.small_font.render(label, True, color)
            self.screen.blit(
                text, (end[0] - text.get_width() // 2, end[1] - text.get_height() // 2)
            )

    def _draw_hud(self, frame: PygameFrame) -> None:
        pygame = self.pygame
        x = self.margin * 2 + self.grid_width
        rect = pygame.Rect(x, self.margin, self.panel_width, self.window_height - self.margin * 2)
        pygame.draw.rect(self.screen, self.theme.panel, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.theme.panel_edge, rect, width=1, border_radius=8)

        lines = [
            ("Bacterium-0", self.title_font, self.theme.text),
            (f"agent: {frame.agent_type}", self.font, self.theme.text),
            (f"encoder: {frame.encoder_name}", self.font, self.theme.text),
            (f"seed: {frame.seed}", self.font, self.theme.text),
            (f"step: {frame.step}/{frame.max_steps}", self.font, self.theme.text),
            (f"energy: {frame.energy}", self.font, self.theme.text),
            (f"last reward: {frame.last_reward:.2f}", self.font, self.theme.text),
            (f"total reward: {frame.total_reward:.2f}", self.font, self.theme.text),
            (f"food eaten: {frame.food_eaten}", self.font, self.theme.text),
            (f"poison hits: {frame.poison_collisions}", self.font, self.theme.text),
            (f"wasted moves: {frame.wasted_moves}", self.font, self.theme.text),
            (f"repeats: {frame.repeated_positions}", self.font, self.theme.text),
            (f"delay: {frame.delay:.2f}s", self.font, self.theme.muted_text),
            (
                "paused" if frame.paused else "running",
                self.font,
                self.theme.warning_text if frame.paused else self.theme.muted_text,
            ),
            ("", self.font, self.theme.text),
            ("space pause  r reset", self.small_font, self.theme.muted_text),
            ("up/down or +/- speed", self.small_font, self.theme.muted_text),
            ("t trail  s scent  h hud", self.small_font, self.theme.muted_text),
            ("p/f12 screenshot  q quit", self.small_font, self.theme.muted_text),
        ]
        y = rect.top + 16
        for text, font, color in lines:
            if text:
                surface = font.render(text, True, color)
                self.screen.blit(surface, (rect.left + 16, y))
            y += 24

    def _scent_color(self, label: str) -> tuple[int, int, int]:
        if "both" in label or "adjacent" in label:
            return self.theme.scent_conflict
        if "poison" in label:
            return self.theme.scent_poison
        if "food" in label or "strong" in label or "weak" in label:
            return self.theme.scent_food
        return self.theme.muted_text


def frame_from_observation(
    *,
    observation: dict[str, Any],
    max_steps: int,
    last_reward: float,
    total_reward: float,
    food_eaten: int,
    poison_collisions: int,
    wasted_moves: int = 0,
    repeated_positions: int = 0,
    agent_type: str = "random",
    encoder_name: str = "local",
    seed: int = 0,
    paused: bool = False,
    delay: float = 0.2,
    show_hud: bool = True,
    show_trail: bool = False,
    show_scent: bool = False,
    trail: tuple[Position, ...] = (),
    encoded_state: tuple[int, ...] | None = None,
) -> PygameFrame:
    """Create a drawable pygame frame from an environment observation."""

    return PygameFrame(
        organism=tuple(int(value) for value in observation["organism"]),
        food=observation["food"],
        poison=observation["poison"],
        step=int(observation["steps"][0]),
        max_steps=max_steps,
        energy=int(observation["energy"][0]),
        last_reward=last_reward,
        total_reward=total_reward,
        food_eaten=food_eaten,
        poison_collisions=poison_collisions,
        wasted_moves=wasted_moves,
        repeated_positions=repeated_positions,
        agent_type=agent_type,
        encoder_name=encoder_name,
        seed=seed,
        paused=paused,
        delay=delay,
        show_hud=show_hud,
        show_trail=show_trail,
        show_scent=show_scent,
        trail=trail,
        encoded_state=encoded_state,
    )


def _brighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, channel + amount) for channel in color)


def _direction_overlay_values(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            continue
        _, rest = line.split(":", 1)
        for chunk in rest.split(","):
            if "=" not in chunk:
                continue
            direction, value = chunk.strip().split("=", 1)
            if direction in {"north", "south", "east", "west"} and value != "none":
                values[direction] = value
    return values
