"""Lightweight immutable models for benchmark orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from abiogenesis.core.config import BacteriaWorldConfig


class RunStatus(StrEnum):
    """Artifact lifecycle states from contract 1.0."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class ScenarioDefinition:
    """A named training/evaluation environment contract."""

    scenario_id: str
    question: str
    hypothesis: str
    training_config: BacteriaWorldConfig
    evaluation_config: BacteriaWorldConfig
    claims_supported: tuple[str, ...]
    claims_not_supported: tuple[str, ...]


@dataclass(frozen=True)
class SuiteDefinition:
    """Ordered replicate roots and episode budgets."""

    suite_id: str
    replicate_roots: tuple[int, ...]
    training_episodes: int
    evaluation_episodes: int
    evidence_label: str
    canonical: bool = True

    @property
    def training_roots(self) -> tuple[int, ...]:
        return self.replicate_roots

    @property
    def evaluation_roots(self) -> tuple[int, ...]:
        return tuple(seed + 100_000 for seed in self.replicate_roots)


@dataclass(frozen=True)
class PolicyDefinition:
    """One canonical policy and its existing implementation settings."""

    policy_id: str
    agent_type: str
    encoder: str | None
    learned: bool
    novelty_reward: float = 0.0
    loop_penalty: float = 0.0


@dataclass(frozen=True)
class Deviation:
    """A machine-readable reason a run is not canonical evidence."""

    code: str
    message: str
    effect: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "effect": self.effect,
        }


METRIC_KEYS = (
    "average_reward",
    "average_lifespan",
    "food_eaten",
    "poison_collisions",
    "wasted_moves",
    "repeated_positions",
    "unique_tiles_visited",
    "revisit_ratio",
    "loop_detections",
    "short_loops",
    "medium_loops",
    "long_loops",
    "novelty_bonuses",
    "novelty_reward_total",
    "episode_count",
)

SUMMARY_HEADINGS = (
    "Question",
    "Hypothesis",
    "Scenario and Suite",
    "Artifacts",
    "Policy Comparison",
    "Settings",
    "Results",
    "Interpretation",
    "Regressions and Mixed Outcomes",
    "Failures and Deviations",
    "Claims Supported",
    "Claims Not Supported",
    "Next Experiment",
)
