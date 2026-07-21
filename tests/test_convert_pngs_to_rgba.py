from pathlib import Path
import importlib.util
import sys

import pytest
from PIL import Image

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "convert_pngs_to_rgba.py"
SPEC = importlib.util.spec_from_file_location("convert_pngs_to_rgba", MODULE_PATH)
assert SPEC is not None
converter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = converter
SPEC.loader.exec_module(converter)

DEFAULT_BG = converter.DEFAULT_BG
DEFAULT_TOLERANCE = converter.DEFAULT_TOLERANCE
convert_png = converter.convert_png
convert_pngs = converter.convert_pngs
destination_for = converter.destination_for
matches_background = converter.matches_background
parse_hex_color = converter.parse_hex_color


def test_default_background_and_tolerance() -> None:
    assert parse_hex_color(DEFAULT_BG) == (255, 255, 255)
    assert DEFAULT_TOLERANCE == 10


def test_matches_background_uses_per_channel_tolerance() -> None:
    assert matches_background((250, 255, 246, 17), background=(255, 255, 255), tolerance=10)
    assert not matches_background((244, 255, 255, 17), background=(255, 255, 255), tolerance=10)


def test_destination_preserves_relative_path_without_overwrite(tmp_path: Path) -> None:
    input_dir = tmp_path / "assets" / "sprites"
    output_dir = tmp_path / "converted"
    source = input_dir / "nested" / "food.png"

    destination = destination_for(
        source,
        input_dir=input_dir,
        output_dir=output_dir,
        overwrite=False,
    )

    assert destination == output_dir / "nested" / "food.png"


def test_convert_png_sets_background_alpha_zero_and_others_opaque(tmp_path: Path) -> None:
    input_dir = tmp_path / "assets" / "sprites"
    output_dir = tmp_path / "out"
    source = input_dir / "bug.png"
    input_dir.mkdir(parents=True)
    image = Image.new("RGB", (2, 1))
    image.putdata([(255, 255, 250), (12, 34, 56)])
    image.save(source)

    result = convert_png(
        source,
        input_dir=input_dir,
        output_dir=output_dir,
        background=(255, 255, 255),
        tolerance=10,
        overwrite=False,
    )

    assert result.converted
    with Image.open(output_dir / "bug.png") as converted:
        assert converted.mode == "RGBA"
        pixels = converted.load()
        assert pixels[0, 0] == (255, 255, 250, 0)
        assert pixels[1, 0] == (12, 34, 56, 255)


def test_convert_png_overwrite_writes_source_path(tmp_path: Path) -> None:
    input_dir = tmp_path / "assets" / "sprites"
    source = input_dir / "bug.png"
    input_dir.mkdir(parents=True)
    Image.new("RGB", (1, 1), color=(255, 255, 255)).save(source)

    result = convert_png(
        source,
        input_dir=input_dir,
        output_dir=tmp_path / "ignored",
        background=(255, 255, 255),
        tolerance=10,
        overwrite=True,
    )

    assert result.converted
    assert result.destination == source
    with Image.open(source) as converted:
        assert converted.mode == "RGBA"
        assert converted.load()[0, 0] == (255, 255, 255, 0)


def test_unreadable_image_returns_error(tmp_path: Path) -> None:
    input_dir = tmp_path / "assets" / "sprites"
    source = input_dir / "broken.png"
    input_dir.mkdir(parents=True)
    source.write_text("not a png")

    result = convert_png(
        source,
        input_dir=input_dir,
        output_dir=tmp_path / "out",
        background=(255, 255, 255),
        tolerance=10,
        overwrite=False,
    )

    assert not result.converted
    assert result.error


def test_convert_pngs_rejects_negative_tolerance(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="tolerance"):
        convert_pngs(
            input_dir=tmp_path,
            output_dir=tmp_path / "out",
            background=(255, 255, 255),
            tolerance=-1,
            overwrite=False,
        )
