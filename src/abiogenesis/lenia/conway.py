"""Minimal synchronous Conway anchor with explicit toroidal boundaries."""

from __future__ import annotations

import numpy as np


def conway_step(field: np.ndarray) -> np.ndarray:
    """Return one periodic Moore-neighborhood update without mutating ``field``."""

    if not isinstance(field, np.ndarray) or field.ndim != 2:
        raise ValueError("Conway field must be a two-dimensional NumPy array")
    if field.dtype not in (np.dtype(np.bool_), np.dtype(np.uint8)):
        raise ValueError("Conway field dtype must be bool or uint8")
    if field.dtype == np.dtype(np.uint8) and not np.all((field == 0) | (field == 1)):
        raise ValueError("uint8 Conway fields must contain only 0 and 1")

    alive = field.astype(np.uint8, copy=False)
    neighbors = np.zeros(field.shape, dtype=np.uint8)
    for row_shift in (-1, 0, 1):
        for column_shift in (-1, 0, 1):
            if row_shift == 0 and column_shift == 0:
                continue
            neighbors += np.roll(
                alive,
                shift=(row_shift, column_shift),
                axis=(0, 1),
            )
    next_alive = (neighbors == 3) | ((alive == 1) & (neighbors == 2))
    return np.ascontiguousarray(next_alive.astype(field.dtype, copy=False))
