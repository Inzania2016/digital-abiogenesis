from pathlib import Path

import numpy as np
import pytest

import abiogenesis.lenia.kernel as kernel_module
from abiogenesis.lenia.config import load_config
from abiogenesis.lenia.kernel import build_kernel, polynomial_core

CONFIG = load_config(Path("configs/lenia/lenia-single-channel-cpu-v1.json"))


def test_polynomial_core_has_expected_support_and_peak() -> None:
    radii = np.array([-0.1, 0.0, 0.25, 0.5, 0.75, 1.0, 1.1])

    values = polynomial_core(radii, alpha=4)

    assert values[0] == 0.0
    assert values[1] == 0.0
    assert values[3] == 1.0
    assert values[5] == 0.0
    assert values[6] == 0.0
    assert values[2] == values[4]


def test_kernel_contract_symmetry_support_normalization_and_determinism() -> None:
    first = build_kernel(CONFIG)
    second = build_kernel(CONFIG)
    radius = CONFIG.kernel_radius
    coordinates = np.arange(-radius, radius + 1)
    rows, columns = np.meshgrid(coordinates, coordinates, indexing="ij")
    outside = np.sqrt(rows * rows + columns * columns) >= radius

    assert first.shape == (11, 11)
    assert first.dtype.str == "<f4"
    assert first.flags.c_contiguous
    assert np.all(np.isfinite(first))
    assert np.all(first >= 0.0)
    assert np.all(first[outside] == 0.0)
    assert np.array_equal(first, np.flip(first, axis=0))
    assert np.array_equal(first, np.flip(first, axis=1))
    assert np.array_equal(first, first.T)
    assert abs(float(np.sum(first, dtype=np.float64)) - 1.0) <= 1e-6
    assert np.array_equal(first, second)


def test_zero_kernel_normalization_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(
        kernel_module,
        "polynomial_core",
        lambda radius_fraction, alpha: np.zeros_like(radius_fraction),
    )

    with pytest.raises(ValueError, match="normalization"):
        build_kernel(CONFIG)
