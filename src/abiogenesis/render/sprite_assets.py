"""Sprite asset helpers for the optional pygame Petri dish renderer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

SPRITE_FILENAMES = {
    "organism": "bacteria_tardigrade.png",
    "food": "food_drumstick.png",
    "poison": "poison_mushrooms.png",
}


def find_project_root(start: Path | None = None) -> Path:
    """Find the nearest project root, falling back to the current directory."""

    current = (start or Path.cwd()).resolve()
    candidates = (current, *current.parents)
    for candidate in candidates:
        if (candidate / "pyproject.toml").exists() or (candidate / "AGENTS.md").exists():
            return candidate
    return current


def resolve_sprite_dir(sprite_dir: Path, *, project_root: Path | None = None) -> Path:
    """Resolve a sprite directory relative to the project root when needed."""

    if sprite_dir.is_absolute():
        return sprite_dir
    return (project_root or find_project_root()) / sprite_dir


@dataclass(frozen=True)
class SpriteConfig:
    """Configuration for optional sprite rendering."""

    sprite_dir: Path = Path("assets") / "sprites"
    enabled: bool = True

    @classmethod
    def from_directory(cls, sprite_dir: Path | str, *, enabled: bool = True) -> "SpriteConfig":
        """Build a sprite config from a path-like directory."""

        return cls(sprite_dir=Path(sprite_dir), enabled=enabled)

    def resolved_dir(self, *, project_root: Path | None = None) -> Path:
        """Return the absolute sprite directory."""

        return resolve_sprite_dir(self.sprite_dir, project_root=project_root)

    def paths(self, *, project_root: Path | None = None) -> dict[str, Path]:
        """Return expected sprite paths keyed by renderer role."""

        base = self.resolved_dir(project_root=project_root)
        return {name: base / filename for name, filename in SPRITE_FILENAMES.items()}


class SpriteAssets:
    """Lazy pygame sprite loader with per-tile-size surface caching."""

    def __init__(
        self,
        *,
        pygame: Any,
        config: SpriteConfig | None = None,
        project_root: Path | None = None,
    ) -> None:
        self.pygame = pygame
        self.config = config or SpriteConfig()
        self.project_root = project_root
        self._cache: dict[tuple[str, int], Any | None] = {}

    def surface(self, name: str, *, tile_size: int) -> Any | None:
        """Return a scaled sprite surface, or None when disabled/missing."""

        if not self.config.enabled:
            return None
        key = (name, tile_size)
        if key not in self._cache:
            self._cache[key] = self._load_scaled(name=name, tile_size=tile_size)
        return self._cache[key]

    def _load_scaled(self, *, name: str, tile_size: int) -> Any | None:
        paths = self.config.paths(project_root=self.project_root)
        path = paths.get(name)
        if path is None or not path.exists():
            return None

        surface = self.pygame.image.load(path).convert_alpha()
        target_size = max(8, int(tile_size * 0.82))
        return self.pygame.transform.smoothscale(surface, (target_size, target_size))
