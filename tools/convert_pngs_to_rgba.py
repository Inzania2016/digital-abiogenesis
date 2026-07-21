"""Convert sprite PNGs to RGBA and key out a flat background color."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image, UnidentifiedImageError
except ImportError as exc:  # pragma: no cover - exercised by users without dev deps.
    raise SystemExit(
        "Pillow is required for this tool. Install dev dependencies with "
        '`python -m pip install -e ".[dev]"`.'
    ) from exc


DEFAULT_INPUT = Path("assets") / "sprites"
DEFAULT_OUTPUT = Path("assets") / "sprites_rgba"
DEFAULT_BG = "#FFFFFF"
DEFAULT_TOLERANCE = 10


@dataclass(frozen=True)
class ConversionResult:
    """Summary for one conversion attempt."""

    source: Path
    destination: Path
    converted: bool
    error: str | None = None


def parse_hex_color(value: str) -> tuple[int, int, int]:
    """Parse a #RRGGBB color string."""

    if len(value) != 7 or not value.startswith("#"):
        raise argparse.ArgumentTypeError("background color must use #RRGGBB")
    try:
        return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("background color must use #RRGGBB") from exc


def matches_background(
    pixel: tuple[int, int, int, int],
    *,
    background: tuple[int, int, int],
    tolerance: int,
) -> bool:
    """Return True when a pixel is within tolerance of the background color."""

    return all(abs(pixel[index] - background[index]) <= tolerance for index in range(3))


def transparent_background_image(
    image: Image.Image,
    *,
    background: tuple[int, int, int],
    tolerance: int,
) -> Image.Image:
    """Return an RGBA copy with matching background pixels made transparent."""

    rgba = image.convert("RGBA")
    converted_pixels = []
    pixel_data = getattr(rgba, "get_flattened_data", rgba.getdata)
    for pixel in pixel_data():
        red, green, blue, _alpha = pixel
        alpha = 0 if matches_background(pixel, background=background, tolerance=tolerance) else 255
        converted_pixels.append((red, green, blue, alpha))
    rgba.putdata(converted_pixels)
    return rgba


def iter_pngs(input_dir: Path) -> list[Path]:
    """Return PNG files under an input directory in predictable order."""

    return sorted(path for path in input_dir.rglob("*.png") if path.is_file())


def destination_for(
    source: Path,
    *,
    input_dir: Path,
    output_dir: Path,
    overwrite: bool,
) -> Path:
    """Return the destination path for a source PNG."""

    if overwrite:
        return source
    return output_dir / source.relative_to(input_dir)


def convert_png(
    source: Path,
    *,
    input_dir: Path,
    output_dir: Path,
    background: tuple[int, int, int],
    tolerance: int,
    overwrite: bool,
) -> ConversionResult:
    """Convert one PNG to RGBA with a transparent keyed background."""

    destination = destination_for(
        source,
        input_dir=input_dir,
        output_dir=output_dir,
        overwrite=overwrite,
    )
    if source.resolve() == destination.resolve() and not overwrite:
        return ConversionResult(
            source=source,
            destination=destination,
            converted=False,
            error="refusing to overwrite original without --overwrite",
        )

    try:
        with Image.open(source) as image:
            converted = transparent_background_image(
                image,
                background=background,
                tolerance=tolerance,
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        converted.save(destination)
    except (OSError, UnidentifiedImageError) as exc:
        return ConversionResult(
            source=source,
            destination=destination,
            converted=False,
            error=str(exc),
        )

    return ConversionResult(source=source, destination=destination, converted=True)


def convert_pngs(
    *,
    input_dir: Path,
    output_dir: Path,
    background: tuple[int, int, int],
    tolerance: int,
    overwrite: bool,
) -> list[ConversionResult]:
    """Convert all PNGs under an input directory."""

    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    if not input_dir.exists():
        raise FileNotFoundError(f"input folder does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"input path is not a folder: {input_dir}")

    return [
        convert_png(
            path,
            input_dir=input_dir,
            output_dir=output_dir,
            background=background,
            tolerance=tolerance,
            overwrite=overwrite,
        )
        for path in iter_pngs(input_dir)
    ]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Folder to scan recursively for PNG files.",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="Output folder for converted PNG files."
    )
    parser.add_argument(
        "--bg",
        type=parse_hex_color,
        default=parse_hex_color(DEFAULT_BG),
        help='Background color to key out, such as "#FFFFFF".',
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=DEFAULT_TOLERANCE,
        help="Per-channel background match tolerance.",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Write converted PNGs over the originals."
    )
    return parser


def print_summary(results: list[ConversionResult]) -> None:
    """Print a compact conversion summary."""

    converted = [result for result in results if result.converted]
    failed = [result for result in results if result.error]
    for result in converted:
        print(f"converted: {result.source} -> {result.destination}")
    for result in failed:
        print(f"error: {result.source}: {result.error}")
    print(f"summary: scanned={len(results)} converted={len(converted)} errors={len(failed)}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    results = convert_pngs(
        input_dir=args.input,
        output_dir=args.output,
        background=args.bg,
        tolerance=args.tolerance,
        overwrite=args.overwrite,
    )
    print_summary(results)


if __name__ == "__main__":
    main()
