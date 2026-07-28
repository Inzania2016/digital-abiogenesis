import numpy as np
import pytest

from abiogenesis.lenia.metrics import field_mass, toroidal_centroid


def field_with_points(shape: tuple[int, int], points: list[tuple[int, int, float]]) -> np.ndarray:
    field = np.zeros(shape, dtype="<f4")
    for y, x, value in points:
        field[y, x] = value
    return field


def test_mass_uses_float64_scalar_accumulation() -> None:
    field = np.full((32, 32), np.float32(0.1), dtype="<f4")

    result = field_mass(field)

    assert type(result) is float
    assert result == float(np.sum(field, dtype=np.float64))


def test_centered_and_translated_toroidal_centroids() -> None:
    centered = field_with_points(
        (9, 9),
        [(y, x, 1.0) for y in range(3, 6) for x in range(3, 6)],
    )
    translated = np.roll(centered, shift=(2, 3), axis=(0, 1))

    assert toroidal_centroid(centered) == pytest.approx((4.0, 4.0), abs=1e-12)
    assert toroidal_centroid(translated) == pytest.approx((7.0, 6.0), abs=1e-12)


def test_wraparound_centroid_uses_circular_not_arithmetic_mean() -> None:
    field = field_with_points((8, 8), [(2, 0, 1.0), (2, 7, 1.0)])

    centroid = toroidal_centroid(field)

    assert centroid is not None
    assert centroid[0] == pytest.approx(7.5, abs=1e-12)
    assert centroid[1] == pytest.approx(2.0, abs=1e-12)


def test_empty_and_ambiguous_centroids_return_none() -> None:
    empty = np.zeros((8, 8), dtype="<f4")
    ambiguous = field_with_points((8, 8), [(2, 0, 1.0), (2, 4, 1.0)])

    assert toroidal_centroid(empty) is None
    assert toroidal_centroid(ambiguous) is None
