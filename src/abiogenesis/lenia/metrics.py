"""Small field metrics used by CPU verification and future parity work."""

from __future__ import annotations

import math

import numpy as np

from abiogenesis.lenia.reference import validate_field


def field_mass(field: np.ndarray) -> float:
    """Return field mass using float64 scalar accumulation."""

    validate_field(field)
    return float(np.sum(field, dtype=np.float64))


def _circular_coordinate(weights: np.ndarray, *, ambiguity_tolerance: float) -> float | None:
    mass = float(np.sum(weights, dtype=np.float64))
    if mass == 0.0:
        return None
    indexes = np.arange(weights.size, dtype=np.float64)
    angles = (2.0 * math.pi / weights.size) * indexes
    cosine = float(np.sum(weights * np.cos(angles), dtype=np.float64))
    sine = float(np.sum(weights * np.sin(angles), dtype=np.float64))
    if math.hypot(cosine, sine) / mass <= ambiguity_tolerance:
        return None
    angle = math.atan2(sine, cosine) % (2.0 * math.pi)
    return angle * weights.size / (2.0 * math.pi)


def toroidal_centroid(
    field: np.ndarray,
    *,
    ambiguity_tolerance: float = 1e-12,
) -> tuple[float, float] | None:
    """Return ``(x, y)`` circular means, or ``None`` for empty/ambiguous fields."""

    validate_field(field)
    if not math.isfinite(ambiguity_tolerance) or ambiguity_tolerance < 0.0:
        raise ValueError("ambiguity_tolerance must be finite and non-negative")
    column_weights = np.sum(field, axis=0, dtype=np.float64)
    row_weights = np.sum(field, axis=1, dtype=np.float64)
    x = _circular_coordinate(column_weights, ambiguity_tolerance=ambiguity_tolerance)
    y = _circular_coordinate(row_weights, ambiguity_tolerance=ambiguity_tolerance)
    if x is None or y is None:
        return None
    return x, y
