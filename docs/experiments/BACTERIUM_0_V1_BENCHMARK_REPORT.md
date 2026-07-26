# Bacterium-0 v1 Benchmark Report

Status: **Frozen R1 benchmark report**

Evidence date: 2026-07-26  
Source commit: `7164e571810deac67042b87e3a5eacddfc24f6f0`

## Executive Summary

All five `b0-quick-v1` and all five `b0-full-v1` scenario runs completed from
the same clean source commit, passed independent contract validation, and
declared no deviations. Generated policies were not retained. The ignored
canonical run directories remain the numerical source of truth.

The full evidence supports bounded, descriptive findings:

- `local-q` had the highest unshaped mean return in every distinct tested
  environment and the lowest mean poison-collision count.
- `conflict-scent-q` usually collected more food than `local-q`, but its
  additional poison contact reduced the advantage to a tradeoff.
- unshaped `novelty-scent-q` exceeded random mean return in every scenario but
  remained below `local-q` and `conflict-scent-q`.
- shaped `novelty-scent-q-rewarded` produced the highest coverage and lowest
  revisit ratio in every scenario, with more poison contact and lower
  unshaped-outcome performance than the strongest cautious policies.
- the approved default-to-sparse shift produced mixed evidence: local and
  conflict-scent policies lost mean return relative to policies trained
  directly under sparse food, while unshaped novelty improved descriptively.
- `unseen-seeds-v1` and `stable-default-v1` produced identical quick and full
  policy payloads. Both use the same default environment and the same
  `+100000` evaluation-root derivation, so the named unseen-seed scenario adds
  no distinct contrast in benchmark v1.

These are not claims of statistical significance, intelligence, generality,
adaptation, ecological fitness, or independent replicate worlds.

## Benchmark Identity

| Field | Value |
| --- | --- |
| Benchmark | `bacterium-0-v1` |
| Artifact contract | `1.0` |
| Quick suite | roots 21-23; 200 training and 20 evaluation episodes |
| Full suite | roots 21-30; 1000 training and 100 evaluation episodes |
| Evaluation roots | replicate root + 100000 |
| Policies | `random`, `local-q`, `conflict-scent-q`, `novelty-scent-q`, `novelty-scent-q-rewarded` |
| Shaped policy | `novelty-scent-q-rewarded`, `novelty_reward=0.02` |
| Source state | clean Git commit |
| Visual verification | not performed |

Learned-policy evaluation was greedy and did not update Q values. All
aggregates below use seed records; dispersion is population standard
deviation.

## Evidence Inventory

Every row has terminal status `completed`, validation `passed`, artifact hashes
`passed`, zero deviations, and no retained policy artifacts.

| Suite | Scenario | Run ID | Wall clock | Ignored artifact location |
| --- | --- | --- | ---: | --- |
| quick | `stable-default-v1` | `20260726T204532Z_stable-default-v1_b0-quick-v1_9886` | 5.867 s | `runs/r1c/quick/20260726T204532Z_stable-default-v1_b0-quick-v1_9886` |
| quick | `sparse-food-v1` | `20260726T204621Z_sparse-food-v1_b0-quick-v1_1a3d` | 5.273 s | `runs/r1c/quick/20260726T204621Z_sparse-food-v1_b0-quick-v1_1a3d` |
| quick | `poison-rich-v1` | `20260726T204704Z_poison-rich-v1_b0-quick-v1_8273` | 4.961 s | `runs/r1c/quick/20260726T204704Z_poison-rich-v1_b0-quick-v1_8273` |
| quick | `resource-shift-v1` | `20260726T204730Z_resource-shift-v1_b0-quick-v1_6dd2` | 5.766 s | `runs/r1c/quick/20260726T204730Z_resource-shift-v1_b0-quick-v1_6dd2` |
| quick | `unseen-seeds-v1` | `20260726T204757Z_unseen-seeds-v1_b0-quick-v1_940c` | 5.789 s | `runs/r1c/quick/20260726T204757Z_unseen-seeds-v1_b0-quick-v1_940c` |
| full | `stable-default-v1` | `20260726T204940Z_stable-default-v1_b0-full-v1_ef82` | 103.361 s | `runs/r1c/full/20260726T204940Z_stable-default-v1_b0-full-v1_ef82` |
| full | `sparse-food-v1` | `20260726T205148Z_sparse-food-v1_b0-full-v1_724b` | 92.100 s | `runs/r1c/full/20260726T205148Z_sparse-food-v1_b0-full-v1_724b` |
| full | `poison-rich-v1` | `20260726T205344Z_poison-rich-v1_b0-full-v1_ba0c` | 86.589 s | `runs/r1c/full/20260726T205344Z_poison-rich-v1_b0-full-v1_ba0c` |
| full | `resource-shift-v1` | `20260726T205534Z_resource-shift-v1_b0-full-v1_c859` | 104.291 s | `runs/r1c/full/20260726T205534Z_resource-shift-v1_b0-full-v1_c859` |
| full | `unseen-seeds-v1` | `20260726T205743Z_unseen-seeds-v1_b0-full-v1_ea9c` | 103.484 s | `runs/r1c/full/20260726T205743Z_unseen-seeds-v1_b0-full-v1_ea9c` |

The ignored operational ledger is
`runs/r1c/r1c-execution-ledger.json`.

## Quick Evidence

Quick evidence was used only for configuration, gross-regression, artifact,
and runtime checks. It is not statistically stable canonical evidence.

Mean return by policy:

| Scenario | Random | Local Q | Conflict scent Q | Novelty scent Q | Shaped novelty scent Q |
| --- | ---: | ---: | ---: | ---: | ---: |
| stable default | 0.2265 | 1.7040 | 0.5638 | 0.1367 | 0.5698 |
| sparse food | -0.0520 | 0.4978 | -0.1345 | -0.2858 | 0.0855 |
| poison rich | -0.9270 | 0.9445 | -0.7423 | -0.4347 | -0.4322 |
| resource shift | -0.0520 | 0.4832 | -0.0698 | -0.2437 | 0.0105 |
| unseen seeds | 0.2265 | 1.7040 | 0.5638 | 0.1367 | 0.5698 |

The shaped column uses a different reward definition and is not ranked against
the four unshaped columns. Quick/full changes were material for some policies:
for example, poison-rich conflict-scent mean return moved from `-0.7423` in
quick evidence to `0.4017` in full evidence. This confirms the specification's
warning that three quick roots are unsuitable for stable conclusions.

## Full Evidence

Reward values for `novelty-scent-q-rewarded` include shaping and are not
directly comparable with unshaped reward. Food, poison, coverage, and revisit
metrics remain shared behavioral measurements. Values are aggregate mean plus
or minus population standard deviation across 10 seed records.

### `stable-default-v1`

| Policy | Reward | Food | Poison | Unique tiles | Revisit ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `random` | 0.0947 ± 0.0070 | 82.2 ± 0.4 | 52.0 ± 0.8 | 991.1 ± 2.4 | 0.5623 ± 0.0018 |
| `local-q` | 1.3754 ± 0.3012 | 167.5 ± 31.6 | 1.7 ± 1.3 | 1027.9 ± 240.8 | 0.6810 ± 0.0677 |
| `conflict-scent-q` | 1.2621 ± 0.1833 | 174.7 ± 19.8 | 21.0 ± 3.8 | 1075.9 ± 66.5 | 0.6502 ± 0.0124 |
| `novelty-scent-q` | 0.4444 ± 0.0932 | 112.6 ± 9.4 | 45.5 ± 4.4 | 1006.5 ± 48.5 | 0.5923 ± 0.0166 |
| `novelty-scent-q-rewarded` | 0.9385 ± 0.1627 | 130.7 ± 10.4 | 47.0 ± 7.7 | 1785.4 ± 72.2 | 0.2800 ± 0.0173 |

Supported: local Q had the highest unshaped mean return and lowest poison
contact; conflict scent collected slightly more food but hit more poison.
Shaped novelty had the highest coverage and lowest revisit ratio.

Not supported: a statistical-significance claim, superiority beyond the
default world, or a direct shaped-versus-unshaped reward ranking.

### `sparse-food-v1`

| Policy | Reward | Food | Poison | Unique tiles | Revisit ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `random` | -0.2941 ± 0.0470 | 33.0 ± 2.4 | 43.5 ± 2.7 | 899.3 ± 12.3 | 0.5638 ± 0.0044 |
| `local-q` | 0.6601 ± 0.1932 | 94.2 ± 20.3 | 3.7 ± 1.1 | 1174.3 ± 189.6 | 0.5673 ± 0.0610 |
| `conflict-scent-q` | 0.5356 ± 0.1060 | 99.0 ± 11.1 | 21.8 ± 3.7 | 1001.9 ± 92.0 | 0.6266 ± 0.0311 |
| `novelty-scent-q` | -0.0718 ± 0.0687 | 47.5 ± 5.5 | 34.6 ± 3.4 | 829.9 ± 27.6 | 0.6284 ± 0.0127 |
| `novelty-scent-q-rewarded` | 0.3520 ± 0.0736 | 62.4 ± 6.0 | 38.2 ± 4.9 | 1690.0 ± 51.4 | 0.2350 ± 0.0192 |

Supported: all learned unshaped policies exceeded random mean return. Local Q
had the highest unshaped mean return and lowest poison contact; conflict scent
collected slightly more food. Shaped novelty had the highest coverage.

Not supported: adaptation to scarcity, behavior under arbitrary densities, or
a claim that more exploration produced the strongest unshaped outcome.

### `poison-rich-v1`

| Policy | Reward | Food | Poison | Unique tiles | Revisit ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `random` | -0.7008 ± 0.0106 | 48.6 ± 0.8 | 103.1 ± 0.5 | 796.3 ± 5.8 | 0.5182 ± 0.0035 |
| `local-q` | 1.4552 ± 0.2255 | 182.9 ± 23.8 | 8.8 ± 1.9 | 1094.9 ± 157.4 | 0.6580 ± 0.0416 |
| `conflict-scent-q` | 0.4017 ± 0.1263 | 118.6 ± 14.5 | 56.2 ± 6.1 | 836.9 ± 56.1 | 0.6548 ± 0.0212 |
| `novelty-scent-q` | -0.2757 ± 0.1038 | 77.4 ± 7.7 | 86.9 ± 6.4 | 841.1 ± 30.4 | 0.5668 ± 0.0162 |
| `novelty-scent-q-rewarded` | 0.1475 ± 0.0550 | 94.5 ± 6.6 | 85.0 ± 5.1 | 1326.8 ± 26.7 | 0.3538 ± 0.0141 |

Supported: local Q had the highest unshaped mean return, most food, and far
fewer poison collisions. Shaped novelty increased coverage but retained high
poison contact. Full evidence reversed the negative quick mean for conflict
scent, demonstrating quick instability.

Not supported: toxin homeostasis, robustness to other poison settings, or
general danger avoidance.

### `resource-shift-v1`

| Policy | Reward | Food | Poison | Unique tiles | Revisit ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| `random` | -0.2941 ± 0.0470 | 33.0 ± 2.4 | 43.5 ± 2.7 | 899.3 ± 12.3 | 0.5638 ± 0.0044 |
| `local-q` | 0.5175 ± 0.1338 | 78.1 ± 13.8 | 2.6 ± 1.2 | 925.0 ± 206.7 | 0.6584 ± 0.0753 |
| `conflict-scent-q` | 0.4594 ± 0.1492 | 86.2 ± 15.1 | 16.9 ± 3.3 | 973.9 ± 84.7 | 0.6310 ± 0.0241 |
| `novelty-scent-q` | 0.0007 ± 0.0931 | 56.0 ± 8.8 | 35.4 ± 4.3 | 915.3 ± 43.5 | 0.5978 ± 0.0179 |
| `novelty-scent-q-rewarded` | 0.3529 ± 0.0774 | 60.6 ± 8.9 | 37.0 ± 5.6 | 1724.6 ± 39.9 | 0.2172 ± 0.0164 |

The matched comparison is against `sparse-food-v1`, because both evaluate
under sparse food. Training on stable defaults rather than sparse food changed:

- local Q mean return from `0.6601` to `0.5175` and food from `94.2` to `78.1`;
- conflict-scent mean return from `0.5356` to `0.4594` and food from `99.0` to `86.2`;
- unshaped novelty mean return from `-0.0718` to `0.0007` and food from `47.5` to `56.0`;
- shaped novelty return from `0.3520` to `0.3529`, with similar shared outcomes.

Supported: the approved shift produced policy-dependent mixed changes; it did
not uniformly degrade every metric or policy.

Not supported: online adaptation, recovery, transfer to arbitrary shifts, or
statistical significance.

### `unseen-seeds-v1`

The aggregate table is identical to `stable-default-v1`, and the complete
quick and full policy payloads are byte-for-byte equivalent after excluding
top-level run/scenario identity. This is expected from the implemented
benchmark-v1 definitions: both scenarios use stable defaults and the same
training and `+100000` evaluation roots.

Supported: evaluation used roots distinct from training roots.

Not supported: an additional contrast beyond stable default, independence of
adjacent episode windows, or broader generalization.

## Scenario Findings

The scenario-local findings above preserve the strongest and weakest evidence:

- caution from `local-q` translated into high return and low poison contact;
- conflict scent often improved food seeking relative to local Q, but with a
  poison tradeoff and no consistent return lead;
- unshaped directional novelty did not surpass either established learned
  baseline on mean return;
- shaped novelty reliably changed exploration behavior, but the shaped return
  cannot establish superiority over unshaped policies;
- quick rankings were not stable enough to replace the full suite;
- the named unseen-seed scenario was redundant with stable default in v1.

## Cross-Scenario Synthesis

Raw reward is not treated as a common difficulty scale across scenarios.
Within each scenario, local Q led the unshaped mean-return ordering. Across
scenarios, the most consistent behavioral contrast was local Q's low poison
contact versus shaped novelty's high coverage and low revisit ratio.

The sparse-trained/resource-shift comparison is the one approved
cross-scenario return comparison because evaluation conditions match. It
showed mixed policy-dependent changes, not a universal robustness result.

## Runtime and Cost

Quick runs totaled `27.656` seconds. Fixed command overhead was estimated as
the median of three dry-run measurements (`0.493`, `2.389`, and `0.469`
seconds): `0.493` seconds.

The quick suite represents 2700 policy episodes; the full suite represents
45000, a `16.6667` workload ratio. For each scenario, the projection subtracted
fixed overhead, scaled variable time by the workload ratio, restored overhead,
and added a 20% safety margin. This produced:

| Scenario | Projected full | Actual full |
| --- | ---: | ---: |
| stable default | 108.080 s | 103.361 s |
| sparse food | 96.200 s | 92.100 s |
| poison rich | 89.960 s | 86.589 s |
| resource shift | 106.060 s | 104.291 s |
| unseen seeds | 106.520 s | 103.484 s |
| **Aggregate** | **506.820 s** | **489.825 s** |

The 8.447-minute projected aggregate and 1.801-minute maximum scenario passed
the approved 8-hour and 2-hour gates. Actual full execution took 8.164 minutes.
The projection assumes episode cost scales approximately with work; the safety
margin covered observed variation here but is not a universal runtime model.

## Limitations

- Quick evidence has only 3 roots; full evidence has 10.
- Aggregates use population standard deviation only.
- No confidence intervals, hypothesis tests, or significance claims exist.
- Adjacent replicate roots create overlapping episode-seed windows and do not
  establish complete statistical independence.
- Hyperparameters and environment definitions are fixed.
- The shaped-return boundary prevents direct reward ranking of
  `novelty-scent-q-rewarded` against unshaped policies.
- Results cover one implementation and local runtime context.
- Generated policies were not retained.
- No pygame visual verification was performed.
- `unseen-seeds-v1` duplicates stable-default evidence under the current v1
  seed and environment definitions.

## Frozen Conclusions

Benchmark v1 establishes reproducible contract-compliant evidence, not a
winner for future architectures. Under these scenarios, compact local Q
learning remained the strongest cautious unshaped baseline. Conflict scent
preserved a food-seeking/poison tradeoff. Directional novelty without shaping
did not displace either baseline. Explicit novelty shaping strongly altered
coverage and revisit behavior while preserving a poison cost and a separate
return definition.

The resource-shift result is mixed, and the unseen-seed scenario adds no
distinct contrast. Both negative findings are part of the frozen result.

## Next Research Direction

R1C is complete. The next packet is
`docs/work-packets/RS-02_CONWAY_TO_LENIA_CPU_REFERENCE.md`. RS-02 must begin
with explicit equation, boundary, dtype, update-order, provenance, and fixture
decisions; this report does not execute it.
