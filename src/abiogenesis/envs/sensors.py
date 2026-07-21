"""Primitive directional sensors for Bacterium-0."""

from __future__ import annotations

from typing import Literal

import numpy as np

from abiogenesis.core.types import Position

Direction = Literal["north", "south", "east", "west"]
ScentSignal = int

DIRECTIONS: tuple[Direction, Direction, Direction, Direction] = (
    "north",
    "south",
    "east",
    "west",
)

NO_SCENT = 0
WEAK_SCENT = 1
STRONG_SCENT = 2


def directional_scent(
    *,
    organism: Position,
    targets: np.ndarray,
    direction: Direction,
) -> ScentSignal:
    """Return a discrete signal for the nearest target in one cardinal direction."""

    x, y = organism
    height, width = targets.shape

    if direction == "north":
        distances = range(1, y + 1)
        cells = ((x, y - distance) for distance in distances)
    elif direction == "south":
        distances = range(1, height - y)
        cells = ((x, y + distance) for distance in distances)
    elif direction == "east":
        distances = range(1, width - x)
        cells = ((x + distance, y) for distance in distances)
    else:
        distances = range(1, x + 1)
        cells = ((x - distance, y) for distance in distances)

    for distance, (target_x, target_y) in zip(distances, cells, strict=True):
        if targets[target_y, target_x]:
            return STRONG_SCENT if distance == 1 else WEAK_SCENT
    return NO_SCENT


def directional_scents(
    *,
    organism: Position,
    targets: np.ndarray,
) -> tuple[ScentSignal, ScentSignal, ScentSignal, ScentSignal]:
    """Return north, south, east, west scent signals for a target grid."""

    return tuple(
        directional_scent(
            organism=organism,
            targets=targets,
            direction=direction,
        )
        for direction in DIRECTIONS
    )
