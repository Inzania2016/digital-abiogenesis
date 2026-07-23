# Documentation Example: Bacterium-0 Quick Comparison

> Synthetic structural example only. These numbers are not experiment evidence.

## Question

Under the unchanged default environment, how do the five canonical Bacterium-0 policies
compare?

## Hypothesis

The learned policies will differ from the random baseline, and novelty reward shaping may
increase coverage or food contact while worsening poison discipline.

## Scenario and Suite

- Scenario: `stable-default-v1`
- Suite: `b0-quick-v1`
- Run: `20260723T184502Z_stable-default-v1_b0-quick-v1_a7f3`
- Evidence class: documentation example; not evidence

## Artifacts

- [manifest.json](manifest.json)
- [metrics.json](metrics.json)
- No policy artifacts were requested.

## Policy Comparison

`random`, `local-q`, `conflict-scent-q`, `novelty-scent-q`, and
`novelty-scent-q-rewarded` are compared on matched synthetic seed records.

## Settings

- Source: clean example Git state shown in `manifest.json`
- Environment: unchanged 10x10 defaults for training and evaluation
- Replicate roots: `[21, 22, 23]`
- Evaluation roots: `[100021, 100022, 100023]`
- Training: 200 episodes per learned policy and replicate
- Evaluation: 20 episodes per policy and replicate
- Learned-policy defaults: alpha 0.2, gamma 0.95, epsilon 1.0, decay 0.995, minimum 0.05
- Reward shaping: zero except `novelty-scent-q-rewarded`, which uses novelty reward 0.02

## Results

Aggregate `count` is the number of seed records. The table is a view of the synthetic
machine-readable example, not a recorded run.

| Policy | Mean reward | Food total per seed | Poison total per seed | Unique-tile total per seed |
| --- | ---: | ---: | ---: | ---: |
| `random` | 0.2 | 15.0 | 9.0 | 200.0 |
| `local-q` | 1.7 | 40.0 | 5.0 | 270.0 |
| `conflict-scent-q` | 0.6 | 26.0 | 10.0 | 190.0 |
| `novelty-scent-q` | 0.1 | 15.0 | 8.0 | 192.0 |
| `novelty-scent-q-rewarded` | 0.6 | 23.0 | 12.0 | 257.0 |

## Interpretation

If these were real measurements, they would suggest tradeoffs rather than a universal
winner. Because this is a synthetic example, no behavioral conclusion is permitted.

## Regressions and Mixed Outcomes

The example deliberately shows higher coverage and poison collisions for the rewarded
novelty policy. This illustrates how a summary should preserve mixed outcomes.

## Failures and Deviations

The manifest declares a `documentation-example` deviation. There are no execution failures
because no experiment was executed.

## Claims Supported

- The three artifact formats can express the canonical quick-suite structure.

## Claims Not Supported

- Any claim about learning, policy quality, regression, visual behavior, or statistical
  stability.

## Next Experiment

Implement the R1B runner and execute `stable-default-v1` under `b0-quick-v1`.
