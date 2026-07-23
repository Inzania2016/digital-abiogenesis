# Experiment Artifact Contract v1

Status: **approved R1A specification; writer and validator implementation belong to R1B**

## Purpose and Authority

Contract version `1.0` defines the durable shape of a Bacterium-0 benchmark run. It
separates resolved configuration, machine-readable evaluation results, human
interpretation, and optional learned policy state.

This contract applies prospectively. Historical Markdown experiments are not silently
retrofitted or represented as v1 artifacts. Metric semantics and benchmark settings are
defined jointly with `BACTERIUM_0_BENCHMARK_V1.md`; that benchmark document is
authoritative for scenario meaning.

## Run Shape

```text
runs/<run-id>/
  manifest.json
  metrics.json
  summary.md
  policy/
    <optional policy artifact>
```

`policy/` exists only when policy output was explicitly requested. Generated runs and
policies remain ignored and uncommitted by default.

## Run Identifier

Format:

```text
YYYYMMDDTHHMMSSZ_<scenario-id>_<suite-id>_<suffix>
```

Example:

```text
20260723T184502Z_stable-default-v1_b0-quick-v1_a7f3
```

Rules:

- timestamp is UTC with literal `T` and `Z`;
- scenario and suite IDs are included verbatim;
- suffix is four lowercase hexadecimal characters;
- only ASCII letters, digits, hyphens, and underscores are permitted;
- the identifier is filesystem-safe and lexically sortable by creation time;
- the run ID identifies an execution, not a code version;
- a completed run directory is immutable and must never be reused.

Collision handling generates a new suffix. It does not overwrite or append to an existing
completed directory.

## Versioning

- `contract_version` is `"1.0"`.
- `benchmark_version` is `"bacterium-0-v1"`.
- Additive optional fields may appear in a compatible minor contract revision.
- Removing fields or changing required fields, types, missing-value rules, or semantics
  requires a new major contract version.
- Changing benchmark policies, scenario configuration, seed derivation, metric meaning, or
  canonical budgets requires a new scenario, suite, or benchmark version.
- Historical artifacts remain byte-stable and are never silently upgraded.

Consumers must reject unsupported major contract versions. They may accept an unknown
minor revision only when unknown optional fields can be safely ignored.

## Common Types

- **UTC timestamp:** string matching `YYYY-MM-DDTHH:MM:SSZ`; fractional seconds may be
  added in a compatible minor revision.
- **SHA-256:** 64-character lowercase hexadecimal string.
- **Git commit:** 40-character lowercase hexadecimal object ID, or `null` when Git metadata
  is unavailable.
- **Path:** repository- or run-relative path using `/`; never an absolute machine path.
- **Command:** one exact PowerShell command string as invoked from the repository root.
- **Notes:** ordered array of strings; empty is `[]`, not `null`.
- **Deviation:** object with required `code`, `message`, and `effect` strings.

## Status Lifecycle

Allowed manifest status values:

- `planned`: directory and resolved plan may exist; execution has not started;
- `running`: execution started and is not terminal;
- `completed`: every canonical policy, seed, episode, metric, and required artifact passed;
- `partial`: usable output exists, but a declared requirement is missing or deviated;
- `failed`: the run did not produce usable canonical metrics;
- `interrupted`: execution stopped before a normal terminal outcome.

Terminal states are `completed`, `partial`, `failed`, and `interrupted`. A terminal
manifest requires `completed_at`. Only `completed` is canonical evidence without
qualification.

## Manifest Schema

Every schema-defined top-level key is required. Nullable values are explicit.

| Field | Type | Rules |
| --- | --- | --- |
| `contract_version` | string | Must be `"1.0"` |
| `benchmark_version` | string | Must be `"bacterium-0-v1"` |
| `run_id` | string | Must match the containing directory |
| `status` | string enum | One lifecycle value above |
| `started_at` | UTC timestamp or null | Required and non-null after `planned` |
| `completed_at` | UTC timestamp or null | Non-null for terminal states |
| `scenario_id` | string | Registered scenario ID |
| `suite_id` | string | `b0-quick-v1` or `b0-full-v1` |
| `source` | object | Required source identity |
| `runtime` | object | Required runtime and platform data |
| `environment` | object | Fully resolved training and evaluation configurations |
| `policies` | array | Ordered policy declarations |
| `seeds` | object | Ordered roots and derivation |
| `budgets` | object | Explicit episode counts |
| `invocation` | object | Exact command and working-directory rule |
| `artifacts` | object | Final output declarations and hashes |
| `verification` | object | Automated and visual states |
| `deviations` | array | Empty for a canonical completed run |
| `notes` | array | Human-readable non-normative notes |

### Source

| Field | Type | Rules |
| --- | --- | --- |
| `kind` | string enum | `git`, `archive`, or `unknown` |
| `repository_url` | string or null | Canonical URL when known |
| `commit` | Git commit or null | Exact source commit |
| `dirty` | boolean or null | `null` only when state cannot be determined |

A canonical completed run requires `kind="git"`, a non-null commit, and `dirty=false`.
Unknown or dirty source must be declared as a deviation.

### Runtime

| Field | Type |
| --- | --- |
| `python_version` | string |
| `python_implementation` | string |
| `platform_system` | string |
| `platform_release` | string |
| `machine` | string |

Values are observed at execution time, not inferred from package metadata.

### Environment

`environment.training` and `environment.evaluation` each contain every
`BacteriaWorldConfig` field:

`width`, `height`, `food_count`, `poison_count`, `initial_energy`, `max_steps`,
`step_energy_cost`, `food_energy`, `poison_energy_cost`, `food_reward`,
`poison_penalty`, and `step_penalty`.

Counts and energy fields are integers; rewards and penalties are JSON numbers. Separate
training and evaluation objects are required even when identical so distribution shifts
cannot be hidden.

### Policy Declaration

Each ordered `policies` element contains:

| Field | Type | Rules |
| --- | --- | --- |
| `policy_id` | string | Canonical policy ID |
| `agent_type` | string | Implemented class or stable agent identifier |
| `encoder` | string or null | `null` for `random` |
| `learning` | object or null | `null` for non-learning policies |
| `reward_shaping` | object | Explicit `loop_penalty` and `novelty_reward` numbers |
| `evaluation_exploration` | boolean | Must be `false` for learned canonical policies |
| `policy_artifact_requested` | boolean | Controls optional output |

Learning objects contain numeric `alpha`, `gamma`, `epsilon_initial`, `epsilon_decay`, and
`epsilon_min`. Policy declarations are configuration, not result records.

### Seeds and Budgets

`seeds` contains ordered integer arrays:

- `replicate_roots`;
- `training_roots`;
- `evaluation_roots`;

and a required `derivation` string. For v1, the derivation states that training episode
seed is `training_root + episode_index` and evaluation episode seed is
`evaluation_root + episode_index`, with evaluation root equal to replicate root plus
100000.

`budgets` contains:

- `training_episodes_per_learned_policy_per_seed` integer;
- `evaluation_episodes_per_policy_per_seed` integer;
- `policy_count` integer;
- `learned_policy_count` integer.

### Invocation

`invocation.command` is the exact command with resolved scenario and suite arguments.
`invocation.working_directory` must be `"repository-root"`. Secrets must never be placed in
the command.

### Artifacts

`artifacts.metrics` and `artifacts.summary` are required objects with `path`, `media_type`,
and non-null `sha256` in a terminal run. The manifest does not hash itself because a
self-hash is recursive.

`artifacts.policies` is an array. It is empty when no policy output was requested. Each
policy artifact declaration requires:

- `policy_id`;
- run-relative `path` under `policy/`;
- `format`;
- `sha256`;
- `load_command`;
- `byte_count`.

If any policy artifact is declared, `policy/` exists. Undeclared files in a completed run
directory violate the contract.

### Verification

`verification.automated` contains:

- `status`: `passed`, `failed`, `partial`, or `not_run`;
- `commands`: ordered array of exact commands;
- `notes`: ordered array of strings.

`verification.visual` contains:

- `status`: `passed`, `failed`, or `not_performed`;
- `verified_by`: string or null;
- `notes`: ordered array of strings.

Only Joe may record a human-visible pygame result. Artifact creation never implies visual
success.

## Metrics Schema

Every top-level field is required:

| Field | Type | Rules |
| --- | --- | --- |
| `contract_version` | string | Must match manifest |
| `benchmark_version` | string | Must match manifest |
| `run_id` | string | Must match manifest and directory |
| `scenario_id` | string | Must match manifest |
| `suite_id` | string | Must match manifest |
| `example_only` | boolean | `false` for real runs; documentation examples use `true` |
| `policies` | array | One record per declared policy, in manifest order |

Each policy record contains:

- `policy_id`: matching manifest policy;
- `status`: `completed`, `partial`, `failed`, or `interrupted`;
- `per_seed`: ordered seed result array;
- `aggregate`: object with every canonical metric key.

Each per-seed result contains:

| Field | Type | Rules |
| --- | --- | --- |
| `replicate_seed` | integer | Suite replicate root |
| `training_seed` | integer or null | `null` for `random` |
| `evaluation_seed` | integer | Evaluation root |
| `training_episode_count` | integer | `0` for `random` |
| `evaluation_episode_count` | integer | Requested evaluation episodes |
| `sample_count` | integer | Successfully completed evaluation episodes |
| `status` | string enum | `completed`, `partial`, `failed`, or `interrupted` |
| `deviations` | array | Ordered deviation objects |
| `metrics` | object | Every canonical metric key |

The required metric keys and exact semantics are defined in
`BACTERIUM_0_BENCHMARK_V1.md`:

- `average_reward`;
- `average_lifespan`;
- `food_eaten`;
- `poison_collisions`;
- `wasted_moves`;
- `repeated_positions`;
- `unique_tiles_visited`;
- `revisit_ratio`;
- `loop_detections`;
- `short_loops`;
- `medium_loops`;
- `long_loops`;
- `novelty_bonuses`;
- `novelty_reward_total`;
- `episode_count`.

Metric values are JSON numbers or `null`. Integer-semantic fields must be JSON integers in
per-seed records. `episode_count` must equal `sample_count`. A zero means measured zero;
uncollected or inapplicable means `null`.

Each aggregate metric is either `null` or an object with exactly:

```json
{
  "count": 3,
  "mean": 1.234,
  "population_stddev": 0.123,
  "min": 1.0,
  "max": 1.4
}
```

`count` is the number of non-null seed values. Population standard deviation uses the seed
values and divides by `count`. It is `0.0` for one contributing value. Aggregates never
combine training and evaluation values or silently substitute zero for missing data.

## Missing, Partial, and Failed Data

- Schema-defined keys are never omitted.
- A per-seed failed metric object contains all metric keys with `null`.
- A partial metric may be numeric only if it summarizes the declared `sample_count`.
- Aggregates use non-null seed values and reveal the contributing seed count.
- Any reduced sample or aggregate count requires `status="partial"` and a deviation.
- A completed policy requires every expected seed and evaluation episode.
- A completed run requires every canonical policy to be completed.

## Summary Contract

`summary.md` is required and contains these headings:

1. `Question`
2. `Hypothesis`
3. `Scenario and Suite`
4. `Artifacts`
5. `Policy Comparison`
6. `Settings`
7. `Results`
8. `Interpretation`
9. `Regressions and Mixed Outcomes`
10. `Failures and Deviations`
11. `Claims Supported`
12. `Claims Not Supported`
13. `Next Experiment`

The settings identify source commit, environment differences, seeds, budgets, learning
hyperparameters, and reward shaping. Results state whether aggregate `count` refers to
seeds and link to machine-readable metrics. Interpretation may add context but may not
change, round into contradiction, or omit material failures from the machine-readable
artifacts.

## Complete Documentation Examples

The complete, valid JSON and Markdown examples are stored under:

```text
docs/experiments/examples/b0-quick-v1/
  manifest.json
  metrics.json
  summary.md
```

They are synthetic structural examples, explicitly marked `example_only`, and are not
experiment evidence. Their run ID, policy set, fields, artifact paths, and result structure
are complete. Hashes in the example manifest must match the example `metrics.json` and
`summary.md` whenever those files change.

## Integrity and Validation Rules

A dependency-free R1B validator must check at least:

- required keys, types, enums, ID/version agreement, and run-ID format;
- manifest scenario, suite, policy, seed, and budget agreement with the benchmark registry;
- status/timestamp consistency;
- source-state requirements for canonical completion;
- per-seed ordering, counts, metric presence, null rules, and aggregate arithmetic;
- SHA-256 hashes and declared file inventory;
- policy directory absence or declaration consistency;
- summary headings and links;
- no absolute machine paths;
- immutability/no overwrite for completed runs.

JSON Schema files are not added in R1A. Cross-file arithmetic, hashes, policy ordering, and
scenario-registry rules require executable validation, so an incomplete schema would create
false confidence. R1B should implement the small structural and integrity validator with
the Python standard library.

## Optional Policy Artifacts

Policy output is opt-in per policy. When requested, the writer records format, hash, byte
count, and exact load command. When not requested, no `policy/` directory is created.
Generated policy artifacts remain ignored by Git. This contract does not authorize curated
models or change the commit gate.

## Historical and Claim Boundaries

- Historical Markdown remains historical and is not converted during R1A.
- `example_only=true` artifacts cannot support behavior claims.
- Quick-suite artifacts are quick evidence only.
- Reward-shaped and unshaped returns are not treated as identical reward definitions.
- A visual verification state is independent from automated benchmark completion.
- No artifact may claim consciousness, sentience, general intelligence, homeostasis,
  inheritance, or ecology.
