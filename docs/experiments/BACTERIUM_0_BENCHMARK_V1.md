# Bacterium-0 Benchmark v1

Status: **approved R1A specification; runner implementation belongs to R1B**

## Identity and Purpose

- Benchmark name: **Bacterium-0 Benchmark**
- Benchmark version: `bacterium-0-v1`
- Artifact contract version: `1.0`

The benchmark freezes a small, representative comparison surface for the legacy tabular
organism. It supports reproducible regression evidence and bounded claims about behavior in
the existing grid world. It does not turn every historical encoder into a permanent
baseline.

## Frozen Organism Boundary

R1 does not change environment dynamics, rewards, default configuration, Q-learning,
encoders, or rendering. Unless a scenario explicitly overrides a field, the resolved world
configuration is:

| Field | Value |
| --- | ---: |
| `width` | 10 |
| `height` | 10 |
| `food_count` | 8 |
| `poison_count` | 6 |
| `initial_energy` | 20 |
| `max_steps` | 100 |
| `step_energy_cost` | 1 |
| `food_energy` | 5 |
| `poison_energy_cost` | 8 |
| `food_reward` | 1.0 |
| `poison_penalty` | -1.0 |
| `step_penalty` | -0.01 |

Learned policies use the existing tabular defaults: `alpha=0.2`, `gamma=0.95`,
`epsilon=1.0`, `epsilon_decay=0.995`, and `min_epsilon=0.05`. Evaluation is greedy and does
not update the Q table.

## Canonical Policy Variants

| Policy ID | Agent | Encoder | Reward shaping | Role |
| --- | --- | --- | --- | --- |
| `random` | `RandomAgent` | none | none | Non-learning baseline |
| `local-q` | `QLearningAgent` | `local` | none | Compact tabular learning baseline |
| `conflict-scent-q` | `QLearningAgent` | `conflict-scent` | none | Directional food/poison perception |
| `novelty-scent-q` | `QLearningAgent` | `novelty-scent` | none | Directional novelty signal without shaping |
| `novelty-scent-q-rewarded` | `QLearningAgent` | `novelty-scent` | `novelty_reward=0.02` | Existing shaped novelty comparison |

The rewarded novelty value is not new: `0.02` is the documented Phase 3D value. It is
applied during both training and evaluation by orchestration code when entering a tile not
previously visited in that episode. It does not change `BacteriaWorldEnv`.

Raw scent, memory-scent, visit-scent, loop-scent, and loop-penalty variants remain available
for historical or exploratory research, but are not required in canonical v1 runs.

## Suite Profiles

| Suite ID | Ordered replicate seeds | Training episodes per learned policy and seed | Evaluation episodes per policy and seed | Purpose |
| --- | --- | ---: | ---: | --- |
| `b0-quick-v1` | `[21, 22, 23]` | 200 | 20 | Developer smoke comparison, gross regression detection, and artifact validation |
| `b0-full-v1` | `[21, 22, 23, 24, 25, 26, 27, 28, 29, 30]` | 1000 | 100 | Canonical Bacterium-0 evidence and milestone acceptance |

The quick budget deliberately matches the R0 wrapper and documented Phase 3D short run. It
is quick evidence only and does not support a claim of statistical stability.

The full budget is the approved starting budget. Existing functions accept these episode
counts, and historical commands used 1000 training episodes, but the canonical
five-policy, ten-seed suite has not been timed or run. R1A must not claim its runtime or
results. R1B should measure runtime without silently reducing the budget.

Every scenario runs all five policies. `random` has no training phase; its training episode
count is `0`.

## Seed Policy

Suite seed lists are ordered **replicate root seeds**, not an enumeration of every
environment reset.

For replicate root `s`, current behavior derives:

- Q-agent initialization seed: `s`;
- training episode environment seeds: `s + episode_index`, starting at index `0`;
- evaluation root seed: `s + 100000`;
- evaluation episode environment seeds: `s + 100000 + episode_index`;
- random action seed for an evaluation episode: that episode's environment seed.

Thus the exact evaluation root lists are:

- quick: `[100021, 100022, 100023]`;
- full: `[100021, 100022, 100023, 100024, 100025, 100026, 100027, 100028, 100029, 100030]`.

Training and evaluation roots do not overlap. Adjacent replicate roots do produce
overlapping episode-seed windows under the legacy derivation. This is a documented
limitation, not hidden independence. Changing the derivation would change the benchmark
schedule and requires a new scenario or benchmark version plus an explicit decision.

Policy variants within a replicate must receive matched evaluation episode seeds. Seed
order must be preserved in the manifest and metrics.

## Scenario Catalog

### `stable-default-v1`

**Question:** Under the unchanged default environment, how do canonical Bacterium-0
policies compare?

Configuration: the frozen defaults above for training and evaluation.

Supported claims:

- relative performance under the default world;
- regression comparison against the frozen configuration;
- reward, food, poison, movement, loop, and exploration tradeoffs.

Unsupported claims:

- robustness to environmental change;
- general intelligence or transfer outside this world;
- ecological, evolutionary, conscious, or sentient behavior.

Implementation status: the legacy evaluator can express the underlying configuration and
budgets, but R1B must implement canonical policy selection and artifacts.

### `sparse-food-v1`

**Question:** How do policies behave when useful resources are harder to encounter?

Configuration: set `food_count=4`; retain every other frozen default for both training and
evaluation. Four is a deliberate half-density count relative to the default eight, using
the environment's existing explicit count field.

Supported claims:

- behavior under this defined resource scarcity;
- exploration, food encounter, reward, and survival tradeoffs;
- whether novelty-related behavior helps encounter sparse resources.

Unsupported claims:

- adaptation during a run;
- long-term carrying capacity or ecological scarcity;
- general performance under arbitrary food densities.

Implementation status: **specified in R1A; implementation required in R1B**. The
environment accepts the configuration programmatically, but the legacy evaluator CLI has
no food-count flag.

### `poison-rich-v1`

**Question:** How do policies trade food collection against danger when poison is more
prevalent?

Configuration: set `poison_count=12`; retain every other frozen default for both training
and evaluation. Twelve is a deliberate doubling of the default six and fits the existing
10x10 placement constraint.

Supported claims:

- poison avoidance in this defined elevated-danger world;
- food/risk/reward tradeoffs;
- survival under the specified poison prevalence.

Unsupported claims:

- toxin homeostasis;
- learning under changing toxicity;
- robustness to other poison counts or penalty values.

Implementation status: **specified in R1A; implementation required in R1B**. The
environment accepts the configuration programmatically, but the legacy evaluator CLI has
no poison-count flag.

### `resource-shift-v1`

**Question:** How does a frozen trained policy respond when evaluation conditions differ
from training conditions?

Configuration:

- train learned policies with `stable-default-v1`;
- freeze the resulting Q table;
- evaluate with the `sparse-food-v1` configuration (`food_count=4`);
- do not explore, update Q values, decay epsilon, or continue learning during evaluation;
- evaluate `random` on the shifted world as a matched non-learning reference.

Supported claims:

- robustness of a frozen policy to this known default-to-sparse distribution shift;
- metric degradation or improvement after the specified shift.

Unsupported claims:

- online adaptation, recovery, or lifetime learning after the shift;
- robustness to arbitrary distribution changes.

Implementation status: **specified in R1A; implementation required in R1B**. The current
evaluator uses one configuration for both training and evaluation.

### `unseen-seeds-v1`

**Question:** Does a trained policy retain its behavior on evaluation roots not used as
training roots?

This is a seed policy layered over `stable-default-v1`, not a distinct environment.

- quick training roots: `[21, 22, 23]`;
- quick evaluation roots: `[100021, 100022, 100023]`;
- full training roots: `[21, 22, 23, 24, 25, 26, 27, 28, 29, 30]`;
- full evaluation roots:
  `[100021, 100022, 100023, 100024, 100025, 100026, 100027, 100028, 100029, 100030]`;
- episode seeds expand from each root according to the seed policy above;
- learned policies are frozen and greedy throughout evaluation.

Supported claims:

- basic behavior on evaluation seed roots not used as training roots;
- reduced risk of reporting only the exact training-root world.

Unsupported claims:

- independence between all episode-seed windows;
- generalization to different dynamics;
- transfer learning or online adaptation.

Implementation status: the legacy evaluator already uses the `+100000` evaluation-root
derivation, but R1B must expose the named scenario and artifacts.

## Canonical Evaluation Metrics

Per-seed records preserve current `RunSummary` semantics. `average_reward`,
`average_lifespan`, and `revisit_ratio` are episode means. Count and coverage fields are
totals across that seed record's evaluation episodes. Full-run aggregates operate on those
seed-level values, not on training records.

| Machine name | Per-seed type | Unit and semantics | Direction | Applicability |
| --- | --- | --- | --- | --- |
| `average_reward` | number | Mean evaluation episode return, including declared orchestration shaping | Context-dependent; higher is usually better only within compatible reward definitions | universal |
| `average_lifespan` | number | Mean evaluation steps per episode | Context-dependent | universal |
| `food_eaten` | integer | Total food contacts across evaluation episodes | Usually higher | universal |
| `poison_collisions` | integer | Total poison contacts across evaluation episodes | Usually lower | universal |
| `wasted_moves` | integer | Total steps where position did not change, including wait and blocked movement | Usually lower | universal |
| `repeated_positions` | integer | Current compatibility metric; identical to `wasted_moves` in Bacterium-0 | Usually lower | universal |
| `unique_tiles_visited` | integer | Sum of per-episode unique-position counts, including each starting tile | Context-dependent; higher indicates coverage | universal |
| `revisit_ratio` | number | Mean of `(steps + 1 - unique_tiles_visited) / steps` per episode, clamped at zero revisits | Usually lower for exploration | universal |
| `loop_detections` | integer | Total steps on which a repeated cycle of length 2-4 is detected | Usually lower | universal |
| `short_loops` | integer | Loop detections with cycle length 2 | Usually lower | universal |
| `medium_loops` | integer | Loop detections with cycle length 3 | Usually lower | universal |
| `long_loops` | integer | Loop detections with cycle length 4 | Usually lower | universal |
| `novelty_bonuses` | integer | Count of nonzero novelty rewards across evaluation episodes | Descriptive | universal when instrumentation ran |
| `novelty_reward_total` | number | Sum of novelty reward values across evaluation episodes | Descriptive; not comparable across reward definitions | universal when instrumentation ran |
| `episode_count` | integer | Number of completed evaluation episodes represented by the seed record | Completeness measure | universal |

The packet's proposed label `novelty_bonus_total` maps to the existing implementation
metric `novelty_reward_total`. V1 keeps the implemented machine name rather than creating a
historical alias.

For unshaped policies, `novelty_bonuses=0` and `novelty_reward_total=0.0` are valid measured
zeros when instrumentation ran. A metric is `null`, not zero, when it was inapplicable or
not collected. Every schema-defined metric key remains present in per-seed and aggregate
records. A completed canonical run has no `null` universal metrics.

## Aggregate Rules

Each aggregate metric is either `null` or:

```json
{
  "count": 3,
  "mean": 1.234,
  "population_stddev": 0.123,
  "min": 1.0,
  "max": 1.4
}
```

- `count` is the number of non-null **seed records**, not episodes.
- `population_stddev` divides by `count`, not `count - 1`.
- `sample_count` in a per-seed record is its number of completed evaluation episodes and
  must equal `episode_count`.
- Aggregates exclude failed/null seed metrics and expose the reduced `count`; the run must
  be `partial` and declare the deviation.
- Training metrics never enter evaluation aggregates.
- Stronger statistical treatment, including confidence intervals, is deferred until the
  runner exists and full-suite cost is measured.

## Comparison Questions

Every scenario summary must, at minimum, compare:

1. Does each learned policy outperform `random` on compatible reward and outcome metrics?
2. What changes relative to `local-q` when directional scent or novelty is added?
3. Does `novelty-scent-q-rewarded` improve coverage or food contact at a poison or reward
   cost?
4. Are conclusions consistent across seed records, or driven by one replicate?
5. Did any configuration, seed, budget, policy, or verification step deviate from the
   specification?

Reward comparisons involving `novelty-scent-q-rewarded` must state that its reported return
includes shaping. Food, poison, lifespan, movement, and coverage metrics are required to
interpret that comparison.

## Reproducibility and Integrity

A conforming run must:

- use a named scenario and suite without hidden defaults;
- record the fully resolved configuration and learning hyperparameters;
- preserve ordered seeds and deterministic derivation rules;
- record the exact command, repository-root working-directory rule, runtime, Git state,
  and artifact hashes;
- evaluate frozen learned policies without exploration or updates;
- keep random and learned policies on matched evaluation worlds;
- emit contract-compliant `manifest.json`, `metrics.json`, and `summary.md`;
- keep generated policies optional and ignored by default;
- never overwrite a completed run directory.

## Failure and Deviation Rules

- A missing canonical policy, seed, episode, universal metric, or required artifact makes
  the run `partial` or `failed`, never `completed`.
- A process failure records the last durable state, error, and missing artifacts.
- Any noncanonical seed, budget, configuration, hyperparameter, or reward shaping value
  must appear in `deviations`; the output is not canonical v1 evidence.
- Dirty or unknown source state must be explicit. It cannot be presented as the frozen
  canonical benchmark report.
- Quick results must be labeled quick evidence only.
- No visual claim may be inferred from artifact creation or non-graphical checks.

## Future Extensions

Additive artifact fields may use a compatible contract minor revision. Changing a scenario
configuration, seed schedule, metric meaning, policy set, or required budget requires a new
scenario, suite, or benchmark version as appropriate. Historical artifacts remain
immutable and are never silently rewritten. New organisms receive new benchmark versions;
they do not redefine Bacterium-0 v1.
