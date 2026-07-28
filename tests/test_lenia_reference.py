from pathlib import Path

import numpy as np
import pytest

from abiogenesis.lenia.config import load_config
from abiogenesis.lenia.kernel import build_kernel
from abiogenesis.lenia.reference import (
    direct_periodic_convolution,
    growth_mapping,
    load_field,
    save_field,
    step,
    step_many,
    validate_field,
)

CONFIG = load_config(Path("configs/lenia/lenia-single-channel-cpu-v1.json"))
KERNEL = build_kernel(CONFIG)


def scalar_periodic_convolution(field: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    height, width = field.shape
    center = kernel.shape[0] // 2
    output = np.zeros_like(field)
    for y in range(height):
        for x in range(width):
            accumulator = np.float32(0.0)
            for kernel_y in range(kernel.shape[0]):
                for kernel_x in range(kernel.shape[1]):
                    weight = kernel[kernel_y, kernel_x]
                    if weight == 0.0:
                        continue
                    offset_y = kernel_y - center
                    offset_x = kernel_x - center
                    product = np.float32(
                        weight * field[(y + offset_y) % height, (x + offset_x) % width]
                    )
                    accumulator = np.float32(accumulator + product)
            output[y, x] = accumulator
    return output


def test_direct_convolution_matches_independent_scalar_oracle() -> None:
    field = np.arange(49, dtype=np.float32).reshape(7, 7) / np.float32(48.0)
    field = np.ascontiguousarray(field, dtype="<f4")

    actual = direct_periodic_convolution(field, KERNEL)
    expected = scalar_periodic_convolution(field, KERNEL)

    assert actual.dtype.str == "<f4"
    assert actual.flags.c_contiguous
    assert np.allclose(actual, expected, rtol=0.0, atol=1e-6)
    assert np.array_equal(actual, direct_periodic_convolution(field, KERNEL))


def test_impulse_response_and_periodic_wrap_match_kernel_offsets() -> None:
    field = np.zeros((8, 8), dtype="<f4")
    field[0, 0] = 1.0

    potential = direct_periodic_convolution(field, KERNEL)
    center = KERNEL.shape[0] // 2

    assert potential[0, 1] == KERNEL[center, center - 1]
    assert potential[0, -1] == KERNEL[center, center + 1]
    assert potential[1, 0] == KERNEL[center - 1, center]
    assert potential[-1, 0] == KERNEL[center + 1, center]


def test_direct_convolution_rejects_unnormalized_kernel() -> None:
    field = np.zeros((8, 8), dtype="<f4")
    kernel = np.zeros((3, 3), dtype="<f4")
    kernel[1, 1] = np.float32(0.5)

    with pytest.raises(ValueError, match="normalized"):
        direct_periodic_convolution(field, kernel)


def test_growth_mapping_peak_range_tail_and_repeatability() -> None:
    potential = np.linspace(0.0, 1.0, 101, dtype=np.float32).reshape(1, 101)
    at_mu = np.full((2, 2), CONFIG.growth_mu, dtype="<f4")

    growth = growth_mapping(
        potential,
        mu=CONFIG.growth_mu,
        sigma=CONFIG.growth_sigma,
    )

    assert growth_mapping(
        at_mu,
        mu=CONFIG.growth_mu,
        sigma=CONFIG.growth_sigma,
    )[0, 0] == pytest.approx(1.0, abs=1e-6)
    assert np.min(growth) >= -1.0
    assert np.max(growth) <= 1.0
    assert growth[0, -1] == pytest.approx(-1.0, abs=1e-6)
    assert np.array_equal(
        growth,
        growth_mapping(
            potential,
            mu=CONFIG.growth_mu,
            sigma=CONFIG.growth_sigma,
        ),
    )


@pytest.mark.parametrize("sigma", [0.0, -0.1, float("nan"), float("inf")])
def test_invalid_growth_sigma_fails(sigma: float) -> None:
    with pytest.raises(ValueError, match="sigma"):
        growth_mapping(
            np.zeros((2, 2), dtype="<f4"),
            mu=CONFIG.growth_mu,
            sigma=sigma,
        )


def test_step_is_new_clipped_synchronous_float32_and_repeatable() -> None:
    field = np.load("tests/fixtures/lenia/field_32_initial.npy", allow_pickle=False)
    original = field.copy()

    first = step(field, kernel=KERNEL, config=CONFIG)
    repeated = step(field, kernel=KERNEL, config=CONFIG)
    ten_a = step_many(field, kernel=KERNEL, config=CONFIG, steps=10)
    ten_b = step_many(field, kernel=KERNEL, config=CONFIG, steps=10)

    assert np.array_equal(field, original)
    assert first is not field
    assert first.dtype.str == "<f4"
    assert first.flags.c_contiguous
    assert np.all(np.isfinite(first))
    assert np.all((first >= 0.0) & (first <= 1.0))
    assert np.array_equal(first, repeated)
    assert np.array_equal(ten_a, ten_b)


@pytest.mark.parametrize(
    "field",
    [
        np.zeros(4, dtype="<f4"),
        np.zeros((4, 4), dtype="<f8"),
        np.full((4, 4), np.nan, dtype="<f4"),
        np.full((4, 4), -0.1, dtype="<f4"),
        np.full((4, 4), 1.1, dtype="<f4"),
        np.zeros((4, 8), dtype="<f4")[:, ::2],
    ],
)
def test_invalid_lenia_fields_fail(field: np.ndarray) -> None:
    with pytest.raises(ValueError):
        validate_field(field)
    with pytest.raises(ValueError):
        step(field, kernel=KERNEL, config=CONFIG)


def test_step_rejects_kernel_shape_inconsistent_with_config() -> None:
    field = np.zeros((32, 32), dtype="<f4")
    kernel = np.full((3, 3), np.float32(1.0 / 9.0), dtype="<f4")

    with pytest.raises(ValueError, match="shape"):
        step(field, kernel=kernel, config=CONFIG)


def test_field_serialization_round_trip_disables_object_data(tmp_path: Path) -> None:
    field = np.load("tests/fixtures/lenia/field_32_initial.npy", allow_pickle=False)
    output = tmp_path / "field.npy"

    save_field(output, field)

    assert np.array_equal(load_field(output), field)
    object_path = tmp_path / "objects.npy"
    np.save(object_path, np.array([{"unsafe": True}], dtype=object), allow_pickle=True)
    with pytest.raises(ValueError, match="allow_pickle=False"):
        load_field(object_path)
