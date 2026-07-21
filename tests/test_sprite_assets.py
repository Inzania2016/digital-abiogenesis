from pathlib import Path

from abiogenesis.render.play_episode import build_parser
from abiogenesis.render.sprite_assets import (
    SPRITE_FILENAMES,
    SpriteAssets,
    SpriteConfig,
    resolve_sprite_dir,
)


class FakeSurface:
    def convert_alpha(self) -> "FakeSurface":
        return self


class FakeImage:
    def __init__(self) -> None:
        self.loads: list[Path] = []

    def load(self, path: Path) -> FakeSurface:
        self.loads.append(path)
        return FakeSurface()


class FakeTransform:
    def __init__(self) -> None:
        self.scales: list[tuple[int, int]] = []

    def smoothscale(
        self, surface: FakeSurface, size: tuple[int, int]
    ) -> tuple[FakeSurface, tuple[int, int]]:
        self.scales.append(size)
        return surface, size


class FakePygame:
    def __init__(self) -> None:
        self.image = FakeImage()
        self.transform = FakeTransform()


def test_default_sprite_paths_are_expected(tmp_path: Path) -> None:
    config = SpriteConfig()

    paths = config.paths(project_root=tmp_path)

    assert paths == {
        name: tmp_path / "assets" / "sprites" / filename
        for name, filename in SPRITE_FILENAMES.items()
    }


def test_resolve_sprite_dir_uses_project_root_for_relative_paths(tmp_path: Path) -> None:
    resolved = resolve_sprite_dir(Path("custom/sprites"), project_root=tmp_path)

    assert resolved == tmp_path / "custom" / "sprites"


def test_sprite_config_from_directory_controls_enabled_flag() -> None:
    config = SpriteConfig.from_directory("stage/makeup", enabled=False)

    assert config.sprite_dir == Path("stage/makeup")
    assert not config.enabled


def test_missing_sprite_returns_none_without_loading(tmp_path: Path) -> None:
    pygame = FakePygame()
    assets = SpriteAssets(
        pygame=pygame,
        config=SpriteConfig(sprite_dir=Path("missing")),
        project_root=tmp_path,
    )

    assert assets.surface("organism", tile_size=56) is None
    assert pygame.image.loads == []


def test_sprite_surface_is_loaded_scaled_and_cached(tmp_path: Path) -> None:
    sprite_dir = tmp_path / "assets" / "sprites"
    sprite_dir.mkdir(parents=True)
    (sprite_dir / "bacteria_tardigrade.png").write_bytes(b"not-a-real-png")
    pygame = FakePygame()
    assets = SpriteAssets(
        pygame=pygame,
        config=SpriteConfig(),
        project_root=tmp_path,
    )

    first = assets.surface("organism", tile_size=56)
    second = assets.surface("organism", tile_size=56)

    assert first is second
    assert pygame.image.loads == [sprite_dir / "bacteria_tardigrade.png"]
    assert pygame.transform.scales == [(45, 45)]


def test_play_episode_parser_accepts_sprite_flags() -> None:
    args = build_parser().parse_args(
        [
            "--renderer",
            "pygame",
            "--no-sprites",
            "--sprite-dir",
            "custom/sprites",
        ]
    )

    assert args.no_sprites
    assert args.sprite_dir == Path("custom/sprites")
