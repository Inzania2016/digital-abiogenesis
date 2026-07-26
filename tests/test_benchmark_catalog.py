from datetime import UTC, datetime

import pytest

from abiogenesis.benchmark.artifacts import generate_run_id
from abiogenesis.benchmark.catalog import (
    CANONICAL_POLICY_IDS,
    resolve_policies,
    resolve_scenario,
    resolve_suite,
)


def test_quick_and_full_suites_match_r1a() -> None:
    quick = resolve_suite("b0-quick-v1")
    full = resolve_suite("b0-full-v1")

    assert quick.replicate_roots == (21, 22, 23)
    assert quick.evaluation_roots == (100021, 100022, 100023)
    assert (quick.training_episodes, quick.evaluation_episodes) == (200, 20)
    assert full.replicate_roots == tuple(range(21, 31))
    assert full.evaluation_roots == tuple(range(100021, 100031))
    assert (full.training_episodes, full.evaluation_episodes) == (1000, 100)


def test_scenario_configs_preserve_frozen_changes() -> None:
    stable = resolve_scenario("stable-default-v1")
    sparse = resolve_scenario("sparse-food-v1")
    poison = resolve_scenario("poison-rich-v1")
    shift = resolve_scenario("resource-shift-v1")

    assert stable.training_config.food_count == 8
    assert stable.training_config.poison_count == 6
    assert sparse.training_config.food_count == 4
    assert sparse.training_config.poison_count == stable.training_config.poison_count
    assert poison.training_config.poison_count == 12
    assert poison.training_config.food_count == stable.training_config.food_count
    assert shift.training_config == stable.training_config
    assert shift.evaluation_config == sparse.evaluation_config


def test_canonical_policies_and_novelty_reward_match_r1a() -> None:
    policies = resolve_policies()

    assert tuple(policy.policy_id for policy in policies) == CANONICAL_POLICY_IDS
    assert policies[-1].policy_id == "novelty-scent-q-rewarded"
    assert policies[-1].encoder == "novelty-scent"
    assert policies[-1].novelty_reward == 0.02


def test_catalog_rejects_unknown_and_misordered_ids() -> None:
    with pytest.raises(ValueError, match="Unknown scenario"):
        resolve_scenario("swamp-hype-v1")
    with pytest.raises(ValueError, match="Unknown suite"):
        resolve_suite("b0-maybe-v1")
    with pytest.raises(ValueError, match="Unknown policy"):
        resolve_policies(("missing",))
    with pytest.raises(ValueError, match="canonical order"):
        resolve_policies(("local-q", "random"))


def test_run_id_is_sortable_and_filesystem_safe() -> None:
    run_id = generate_run_id(
        resolve_scenario("stable-default-v1"),
        resolve_suite("b0-quick-v1"),
        now=datetime(2026, 7, 26, 12, 34, 56, tzinfo=UTC),
        suffix="a7f3",
    )

    assert run_id == "20260726T123456Z_stable-default-v1_b0-quick-v1_a7f3"
    assert all(character.isalnum() or character in "-_" for character in run_id)


def test_run_id_rejects_invalid_suffix() -> None:
    with pytest.raises(ValueError, match="four lowercase hexadecimal"):
        generate_run_id(
            resolve_scenario("stable-default-v1"),
            resolve_suite("b0-quick-v1"),
            suffix="NOPE",
        )
