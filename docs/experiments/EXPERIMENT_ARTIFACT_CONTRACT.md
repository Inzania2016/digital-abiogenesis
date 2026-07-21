# Experiment Artifact Contract

Status: **provisional R0 design; implementation begins after R1A approval**

## Purpose

Each future benchmark run should be inspectable without reconstructing a long command from
memory. The artifact set must distinguish configuration, machine-readable outcomes, human
interpretation, and optional learned policy state.

R0 does not retrofit historical experiments or claim that old Markdown records satisfy this
contract.

## Provisional Run Shape

```text
runs/<run-id>/
  manifest.json
  metrics.json
  summary.md
  optional policy artifact
```

`manifest.json` is the provisional filename requested for the initial design. Whether the
canonical manifest remains JSON or becomes TOML is an explicit R1A owner decision. Metrics
remain JSON unless R1A records a different decision.

## Run Identifier

A run ID should be unique, filesystem-safe, and sortable. The exact format is unresolved;
a likely structure combines a UTC timestamp, scenario ID, and short collision-resistant
suffix. A run ID is an identifier, not evidence of code version.

## Manifest Responsibilities

The manifest should eventually capture:

- contract/schema version;
- run ID and named benchmark scenario/version;
- code or version-control identifier when available, plus dirty/unknown state;
- UTC timestamp and supported runtime version;
- exact environment configuration, including dimensions, counts, energy, steps, rewards,
  and costs;
- agent type and implementation identifier;
- encoder type and memory-tracker configuration;
- learning hyperparameters;
- ordered training and evaluation seed lists;
- training and evaluation episode counts;
- reward shaping and whether each value is an environment or orchestration concern;
- exact invocation command and working-directory assumptions;
- declared output/policy artifacts;
- verification status and known omissions.

No field should silently rely on the current Python default if that default affects the run.

## Metrics Responsibilities

`metrics.json` should contain contract version, run/scenario ID, per-seed summaries, aggregate
statistics, and metric units/semantics. At minimum the current benchmark needs reward,
lifespan, food eaten, poison collisions, wasted/repeated movement, unique coverage, loops,
novelty metrics when applicable, and sample counts.

R1A must decide whether aggregate values include only means or also spread/interval measures.
Absent metrics should be null or omitted according to an explicit schema rule, never encoded
as a misleading zero.

## Summary Responsibilities

`summary.md` is the human-readable experiment record. It should state:

- question and hypothesis;
- scenario and artifact links;
- concise settings and exact comparison;
- results table;
- interpretation, including regressions and mixed outcomes;
- failures, deviations, and unverified observations;
- next proposed experiment.

The summary may explain machine-readable values but must not contradict them.

## Optional Policy Artifact

A learned Q table or future policy artifact may be stored within the run directory when
explicitly requested. Its filename, format, producing agent/encoder, hash, and load command
must appear in the manifest. Committing curated policies remains an unresolved owner decision;
generated `runs/` and `models/` stay ignored by default.

## Integrity Rules

- Write a manifest from resolved values, not just user-supplied flags.
- Preserve ordered seed lists and exact commands.
- Do not overwrite a completed run directory.
- Mark interrupted or partial runs explicitly.
- Keep training metrics separate from evaluation metrics.
- Store enough context to identify reward shaping outside the environment.
- Never manufacture code identifiers when Git metadata is unavailable.
- Never retrofit historical Markdown into synthetic run artifacts without labeling the
  conversion and provenance.

## Deferred R1A Decisions

- JSON versus TOML manifest.
- Canonical quick/full seed lists and episode budgets.
- Exact schema and validation mechanism.
- Run-ID format.
- Required dispersion statistics.
- Policy artifact retention and commit rules.
