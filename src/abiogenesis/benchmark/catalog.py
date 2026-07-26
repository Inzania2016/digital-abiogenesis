"""Immutable Bacterium-0 benchmark catalog approved in R1A."""

from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType

from abiogenesis.benchmark.models import (
    PolicyDefinition,
    ScenarioDefinition,
    SuiteDefinition,
)
from abiogenesis.core.config import BacteriaWorldConfig

CONTRACT_VERSION = "1.0"
BENCHMARK_VERSION = "bacterium-0-v1"
SEED_DERIVATION = (
    "training episode seed = training root + episode index; "
    "evaluation root = replicate root + 100000; "
    "evaluation episode seed = evaluation root + episode index"
)

_DEFAULT = BacteriaWorldConfig()
_SPARSE_FOOD = replace(_DEFAULT, food_count=4)
_POISON_RICH = replace(_DEFAULT, poison_count=12)

_DEFAULT_SUPPORTED = (
    "relative performance under the specified world",
    "reward, food, poison, movement, loop, and exploration tradeoffs",
)
_DEFAULT_UNSUPPORTED = (
    "general intelligence or transfer outside the specified world",
    "ecological, evolutionary, conscious, or sentient behavior",
)

SCENARIOS = MappingProxyType(
    {
        "stable-default-v1": ScenarioDefinition(
            scenario_id="stable-default-v1",
            question=(
                "Under the unchanged default environment, how do canonical "
                "Bacterium-0 policies compare?"
            ),
            hypothesis=(
                "Learned policies will differ from the random baseline while exposing "
                "reward, danger, and exploration tradeoffs."
            ),
            training_config=_DEFAULT,
            evaluation_config=_DEFAULT,
            claims_supported=_DEFAULT_SUPPORTED
            + ("regression comparison against the frozen default configuration",),
            claims_not_supported=_DEFAULT_UNSUPPORTED + ("robustness to environmental change",),
        ),
        "sparse-food-v1": ScenarioDefinition(
            scenario_id="sparse-food-v1",
            question="How do policies behave when useful resources are harder to encounter?",
            hypothesis=(
                "Directional novelty may alter resource encounters when food count is "
                "reduced from eight to four."
            ),
            training_config=_SPARSE_FOOD,
            evaluation_config=_SPARSE_FOOD,
            claims_supported=_DEFAULT_SUPPORTED
            + ("behavior under the specified food_count=4 resource scarcity",),
            claims_not_supported=_DEFAULT_UNSUPPORTED
            + ("adaptation during a run or long-term ecological carrying capacity",),
        ),
        "poison-rich-v1": ScenarioDefinition(
            scenario_id="poison-rich-v1",
            question=(
                "How do policies trade food collection against danger when poison is "
                "more prevalent?"
            ),
            hypothesis=(
                "Increasing poison count from six to twelve will expose different "
                "risk and survival tradeoffs."
            ),
            training_config=_POISON_RICH,
            evaluation_config=_POISON_RICH,
            claims_supported=_DEFAULT_SUPPORTED
            + ("poison avoidance under the specified poison_count=12 world",),
            claims_not_supported=_DEFAULT_UNSUPPORTED
            + ("toxin homeostasis or learning under changing toxicity",),
        ),
        "resource-shift-v1": ScenarioDefinition(
            scenario_id="resource-shift-v1",
            question=(
                "How does a frozen trained policy respond when evaluation conditions "
                "differ from training conditions?"
            ),
            hypothesis=(
                "Policies trained under stable defaults will show measurable changes "
                "when evaluated without further learning at food_count=4."
            ),
            training_config=_DEFAULT,
            evaluation_config=_SPARSE_FOOD,
            claims_supported=(
                "robustness of a frozen policy to the default-to-sparse shift",
                "metric degradation or improvement after the specified shift",
            ),
            claims_not_supported=_DEFAULT_UNSUPPORTED
            + ("online adaptation, recovery, or lifetime learning after the shift",),
        ),
        "unseen-seeds-v1": ScenarioDefinition(
            scenario_id="unseen-seeds-v1",
            question=(
                "Does a trained policy retain its behavior on evaluation roots not used "
                "as training roots?"
            ),
            hypothesis=(
                "Frozen learned policies will retain measurable behavior on the "
                "specified +100000 evaluation roots."
            ),
            training_config=_DEFAULT,
            evaluation_config=_DEFAULT,
            claims_supported=(
                "basic behavior on evaluation roots not used as training roots",
                "reduced risk of reporting only the exact training-root world",
            ),
            claims_not_supported=_DEFAULT_UNSUPPORTED
            + (
                "independence between all episode-seed windows",
                "generalization to different environment dynamics",
            ),
        ),
    }
)

SUITES = MappingProxyType(
    {
        "b0-quick-v1": SuiteDefinition(
            suite_id="b0-quick-v1",
            replicate_roots=(21, 22, 23),
            training_episodes=200,
            evaluation_episodes=20,
            evidence_label="quick evidence only; not statistical stability",
        ),
        "b0-full-v1": SuiteDefinition(
            suite_id="b0-full-v1",
            replicate_roots=tuple(range(21, 31)),
            training_episodes=1000,
            evaluation_episodes=100,
            evidence_label="canonical Bacterium-0 evidence",
        ),
    }
)

POLICIES = MappingProxyType(
    {
        "random": PolicyDefinition(
            policy_id="random",
            agent_type="RandomAgent",
            encoder=None,
            learned=False,
        ),
        "local-q": PolicyDefinition(
            policy_id="local-q",
            agent_type="QLearningAgent",
            encoder="local",
            learned=True,
        ),
        "conflict-scent-q": PolicyDefinition(
            policy_id="conflict-scent-q",
            agent_type="QLearningAgent",
            encoder="conflict-scent",
            learned=True,
        ),
        "novelty-scent-q": PolicyDefinition(
            policy_id="novelty-scent-q",
            agent_type="QLearningAgent",
            encoder="novelty-scent",
            learned=True,
        ),
        "novelty-scent-q-rewarded": PolicyDefinition(
            policy_id="novelty-scent-q-rewarded",
            agent_type="QLearningAgent",
            encoder="novelty-scent",
            learned=True,
            novelty_reward=0.02,
        ),
    }
)

CANONICAL_POLICY_IDS = tuple(POLICIES)


def _resolve(mapping, identifier: str, label: str):
    try:
        return mapping[identifier]
    except KeyError as error:
        available = ", ".join(mapping)
        raise ValueError(f"Unknown {label} {identifier!r}. Available: {available}") from error


def resolve_scenario(scenario_id: str) -> ScenarioDefinition:
    return _resolve(SCENARIOS, scenario_id, "scenario")


def resolve_suite(suite_id: str) -> SuiteDefinition:
    return _resolve(SUITES, suite_id, "suite")


def resolve_policies(policy_ids: tuple[str, ...] | None = None) -> tuple[PolicyDefinition, ...]:
    if policy_ids is None:
        policy_ids = CANONICAL_POLICY_IDS
    if not policy_ids:
        raise ValueError("At least one policy is required.")
    if len(set(policy_ids)) != len(policy_ids):
        raise ValueError("Policy IDs must not be repeated.")
    resolved = tuple(_resolve(POLICIES, policy_id, "policy") for policy_id in policy_ids)
    canonical_positions = [CANONICAL_POLICY_IDS.index(policy.policy_id) for policy in resolved]
    if canonical_positions != sorted(canonical_positions):
        raise ValueError("Policies must follow canonical order.")
    return resolved
