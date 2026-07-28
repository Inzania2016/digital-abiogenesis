"""Polynomial single-ring kernel construction for the RS-02 reference."""

from __future__ import annotations

import numpy as np

from abiogenesis.lenia.config import CANONICAL_DTYPE_STRING, LeniaConfig

CANONICAL_DTYPE = np.dtype(CANONICAL_DTYPE_STRING)


def polynomial_core(radius_fraction: np.ndarray, alpha: int) -> np.ndarray:
    """Evaluate ``(4 r (1-r))**alpha`` on ``0 <= r < 1`` and zero elsewhere."""

    values = np.asarray(radius_fraction, dtype=np.float64)
    output = np.zeros(values.shape, dtype=np.float64)
    supported = (values >= 0.0) & (values < 1.0)
    supported_values = values[supported]
    output[supported] = (4.0 * supported_values * (1.0 - supported_values)) ** alpha
    return output


def build_kernel(config: LeniaConfig) -> np.ndarray:
    """Build, normalize in float64, and return a C-contiguous ``<f4`` kernel."""

    radius = config.kernel_radius
    coordinates = np.arange(-radius, radius + 1, dtype=np.float64)
    rows, columns = np.meshgrid(coordinates, coordinates, indexing="ij")
    radial_fraction = np.sqrt(rows * rows + columns * columns) / float(radius)
    shell = polynomial_core(radial_fraction, config.kernel_alpha)
    shell *= config.kernel_beta[0]
    normalization = float(np.sum(shell, dtype=np.float64))
    if not np.isfinite(normalization) or normalization <= 0.0:
        raise ValueError("kernel normalization sum must be finite and positive")
    kernel = np.asarray(shell / normalization, dtype=CANONICAL_DTYPE, order="C")
    if not np.all(np.isfinite(kernel)) or np.any(kernel < 0):
        raise ValueError("normalized kernel must be finite and nonnegative")
    return kernel
