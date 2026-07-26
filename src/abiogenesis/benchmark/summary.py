"""Deterministic Markdown summaries derived from benchmark metrics."""

from __future__ import annotations

from abiogenesis.benchmark.models import (
    Deviation,
    PolicyDefinition,
    ScenarioDefinition,
    SuiteDefinition,
)


def _mean(policy: dict[str, object], metric: str) -> float | None:
    aggregate = policy["aggregate"]
    assert isinstance(aggregate, dict)
    value = aggregate[metric]
    if value is None:
        return None
    assert isinstance(value, dict)
    return float(value["mean"])


def _format(value: float | None) -> str:
    return "null" if value is None else f"{value:.6g}"


def render_summary(
    *,
    run_id: str,
    scenario: ScenarioDefinition,
    suite: SuiteDefinition,
    policies: tuple[PolicyDefinition, ...],
    metrics: dict[str, object],
    source: dict[str, object],
    deviations: tuple[Deviation, ...],
) -> str:
    """Render only direct, machine-derived comparisons and contract boundaries."""

    policy_records = metrics["policies"]
    assert isinstance(policy_records, list)
    record_by_id = {record["policy_id"]: record for record in policy_records}
    rows = []
    for policy in policies:
        record = record_by_id[policy.policy_id]
        rows.append(
            "| "
            + " | ".join(
                (
                    f"`{policy.policy_id}`",
                    _format(_mean(record, "average_reward")),
                    _format(_mean(record, "food_eaten")),
                    _format(_mean(record, "poison_collisions")),
                    _format(_mean(record, "unique_tiles_visited")),
                )
            )
            + " |"
        )

    reward_values = [
        (policy.policy_id, _mean(record_by_id[policy.policy_id], "average_reward"))
        for policy in policies
    ]
    observed_rewards = [
        (policy_id, value) for policy_id, value in reward_values if value is not None
    ]
    if observed_rewards:
        highest_policy, highest_reward = max(observed_rewards, key=lambda item: item[1])
        interpretation = (
            f"`{highest_policy}` has the highest recorded mean evaluation reward "
            f"({_format(highest_reward)}) in this artifact."
        )
    else:
        interpretation = "No non-null aggregate reward is available for comparison."

    if any(policy.novelty_reward != 0.0 for policy in policies):
        interpretation += (
            " Rewarded novelty return includes declared shaping and must be interpreted "
            "with food, poison, lifespan, movement, and coverage metrics."
        )

    if deviations:
        deviation_lines = [
            f"- `{deviation.code}`: {deviation.message} Effect: {deviation.effect}"
            for deviation in deviations
        ]
    else:
        deviation_lines = ["- None recorded."]

    source_commit = source.get("commit")
    source_dirty = source.get("dirty")
    policy_text = ", ".join(f"`{policy.policy_id}`" for policy in policies)

    lines = [
        f"# Bacterium-0 Benchmark Run: {run_id}",
        "",
        "## Question",
        "",
        scenario.question,
        "",
        "## Hypothesis",
        "",
        scenario.hypothesis,
        "",
        "## Scenario and Suite",
        "",
        f"- Scenario: `{scenario.scenario_id}`",
        f"- Suite: `{suite.suite_id}`",
        f"- Evidence label: {suite.evidence_label}",
        f"- Run ID: `{run_id}`",
        "",
        "## Artifacts",
        "",
        "- [manifest.json](manifest.json)",
        "- [metrics.json](metrics.json)",
        "",
        "## Policy Comparison",
        "",
        policy_text,
        "",
        "## Settings",
        "",
        f"- Source commit: `{source_commit}`",
        f"- Source dirty: `{str(source_dirty).lower()}`",
        f"- Replicate roots: `{list(suite.replicate_roots)}`",
        f"- Evaluation roots: `{list(suite.evaluation_roots)}`",
        (
            "- Episodes: "
            f"{suite.training_episodes} training per learned policy/seed; "
            f"{suite.evaluation_episodes} evaluation per policy/seed"
        ),
        (
            "- Training/evaluation environment equal: "
            f"`{scenario.training_config == scenario.evaluation_config}`"
        ),
        "",
        "## Results",
        "",
        "Aggregate `count` is the number of contributing seed records.",
        "",
        "| Policy | Mean reward | Mean food total | Mean poison total | Mean unique-tile total |",
        "| --- | ---: | ---: | ---: | ---: |",
        *rows,
        "",
        "## Interpretation",
        "",
        interpretation,
        "",
        "## Regressions and Mixed Outcomes",
        "",
        (
            "No policy is promoted by this summary. Inspect reward, food, poison, movement, "
            "loop, and coverage metrics together; mixed outcomes remain material."
        ),
        "",
        "## Failures and Deviations",
        "",
        *deviation_lines,
        "",
        "## Claims Supported",
        "",
        *(f"- {claim}" for claim in scenario.claims_supported),
        "",
        "## Claims Not Supported",
        "",
        *(f"- {claim}" for claim in scenario.claims_not_supported),
        "",
        "## Next Experiment",
        "",
        "Validate this artifact, inspect per-seed spread, and compare it only with compatible runs.",
        "",
    ]
    return "\n".join(lines)
