"""Experimental NEAT integration for the isolated RS-01 research track."""

from abiogenesis.neuroevolution.observation import (
    ACTION_ORDER,
    FEATURE_NAMES,
    ObservationAdapter,
)
from abiogenesis.neuroevolution.policy import NeatPolicy

POLICY_ID = "neat-feedforward-experimental"

__all__ = [
    "ACTION_ORDER",
    "FEATURE_NAMES",
    "NeatPolicy",
    "ObservationAdapter",
    "POLICY_ID",
]
