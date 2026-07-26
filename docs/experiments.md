# Experiments

## 2026-05-11: Phase 1 Random Baseline

Command:

```powershell
python -m abiogenesis.training.train_random --seed 13 --episodes 10 --grid-size 10
```

Results:

| Metric | Value |
| --- | ---: |
| Episodes | 10 |
| Seed | 13 |
| Grid | 10x10 |
| Average reward | -0.467 |
| Average lifespan | 16.70 steps |
| Food eaten | 3 |
| Poison collisions | 6 |
| Wasted moves | 50 |

Conclusion: random behavior gives a measurable baseline and fails messily enough to be useful.

## 2026-05-11: Phase 2A Q-Learning Comparison

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --train-episodes 1000 --eval-episodes 50 --grid-size 10
```

Results:

| Metric | Random | Q-learning |
| --- | ---: | ---: |
| Average reward | 0.166 | 1.263 |
| Average lifespan | 21.40 steps | 27.70 steps |
| Food eaten | 39 | 77 |
| Poison collisions | 20 | 0 |

Conclusion: a small tabular learner can outperform the random baseline in this local-sensor world. The important result is not grand intelligence; it is measured improvement under the same evaluation conditions.

## 2026-05-12: Phase 2B Scent Gradient Comparison

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --compare-scent
```

Results:

| Metric | Random | Local Q-learning | Scent Q-learning |
| --- | ---: | ---: | ---: |
| Average reward | 0.166 | 1.263 | 1.684 |
| Average lifespan | 21.40 steps | 27.70 steps | 29.56 steps |
| Food eaten | 39 | 77 | 109 |
| Poison collisions | 20 | 0 | 10 |

Conclusion: directional scent improves food-seeking and lifespan compared with the local-tile table on this run. The poison result is mixed: scent-aware learning still outperforms random on collisions, but does not match the local-tile policy's zero-collision evaluation here.

## 2026-05-12: Phase 2C Poison Discipline, Default Rewards

Question: does the Phase 2B scent tradeoff hold across multiple seeds?

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 5 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --multi-seed
```

Settings:

- seeds: 21 through 25
- training episodes per Q-learning agent: 1000
- evaluation episodes per seed: 50
- reward settings: default environment values

Mean results across seed-level summaries:

| Metric | Random | Local Q-learning | Scent Q-learning |
| --- | ---: | ---: | ---: |
| Average reward | 0.200 | 1.184 | 1.514 |
| Average lifespan | 21.588 steps | 27.240 steps | 28.592 steps |
| Food eaten | 42.200 | 74.200 | 102.000 |
| Poison collisions | 21.400 | 1.400 | 12.000 |
| Wasted moves | 298.200 | 202.600 | 155.800 |

Conclusion: the one-seed Phase 2B result was not a fluke. Scent-aware Q-learning collected more food, earned more reward, lived longer, and wasted fewer moves than local Q-learning on this five-seed run. It also hit substantially more poison than local Q-learning. The result is a tradeoff, not a clean win.

## 2026-05-12: Phase 2C Poison Discipline, Harsher Poison

Question: does making poison more costly teach the scent-aware learner better poison discipline?

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 5 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --multi-seed --poison-penalty -2.0 --poison-energy-cost 12
```

Settings:

- seeds: 21 through 25
- training episodes per Q-learning agent: 1000
- evaluation episodes per seed: 50
- poison reward penalty: -2.0
- poison energy cost: 12

Mean results across seed-level summaries:

| Metric | Random | Local Q-learning | Scent Q-learning |
| --- | ---: | ---: | ---: |
| Average reward | -0.238 | 1.653 | 1.066 |
| Average lifespan | 20.612 steps | 29.948 steps | 26.972 steps |
| Food eaten | 41.200 | 100.800 | 92.800 |
| Poison collisions | 21.400 | 1.600 | 13.000 |
| Wasted moves | 289.000 | 191.800 | 137.000 |

Conclusion: harsher poison consequences did not solve the scent-aware collision problem in this setup. Local Q-learning benefited more from the stronger discipline signal, while scent-aware Q-learning still took many poison hits. This suggests the current scent state may need better conflict handling or more training/hyperparameter exploration before it can keep its food-seeking advantage without stepping on rakes.

## 2026-05-12: Phase 2D Conflict-Aware Scent

Question: can a compact directional conflict signal reduce the raw scent agent's poison collisions while keeping some of its food-seeking advantage?

Encoder:

- 0 = no directional signal
- 1 = food only
- 2 = poison only
- 3 = both food and poison
- 4 = adjacent poison

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 5 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --multi-seed
```

Settings:

- seeds: 21 through 25
- training episodes per Q-learning agent: 1000
- evaluation episodes per seed: 50
- reward settings: default environment values

Mean results across seed-level summaries:

| Metric | Random | Local Q-learning | Raw scent Q-learning | Conflict-scent Q-learning |
| --- | ---: | ---: | ---: | ---: |
| Average reward | 0.200 | 1.184 | 1.514 | 1.401 |
| Average lifespan | 21.588 steps | 27.240 steps | 28.592 steps | 28.332 steps |
| Food eaten | 42.200 | 74.200 | 102.000 | 94.000 |
| Poison collisions | 21.400 | 1.400 | 12.000 | 9.800 |
| Wasted moves | 298.200 | 202.600 | 155.800 | 181.800 |

Conclusion: conflict-aware scent improved poison discipline compared with raw scent, reducing mean poison collisions from 12.000 to 9.800. It also reduced food eaten and average reward compared with raw scent. The compact conflict signal is a better danger hint, but it is not yet enough to match local Q-learning's caution.

## 2026-05-12: Phase 2E Learning Sweep and Behavior Replay

Question: can raw scent or conflict-scent behavior improve through Q-learning settings before adding new organism features?

Default sweep dimensions:

- encoders: `scent`, `conflict-scent`
- alpha: 0.2
- gamma: 0.9, 0.95
- epsilon decay: 0.99, 0.995
- minimum epsilon: 0.05
- training episodes: 300, 600
- seeds: 21 through 23
- evaluation episodes per seed: 20
- reward settings: default environment values

Command:

```powershell
python -m abiogenesis.training.sweep_q_learning --seed 21 --seeds 3 --eval-episodes 20 --grid-size 10 --save-best-path models/phase-2e-best-q.json
```

Top sweep results by mean average reward:

| Encoder | Alpha | Gamma | Epsilon decay | Min epsilon | Train episodes | Average reward | Average lifespan | Food eaten | Poison collisions | Wasted moves |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| conflict-scent | 0.20 | 0.90 | 0.990 | 0.050 | 600 | 1.337 | 28.017 | 36.0 | 3.7 | 96.7 |
| scent | 0.20 | 0.95 | 0.995 | 0.050 | 600 | 1.310 | 27.300 | 40.3 | 8.7 | 98.7 |
| scent | 0.20 | 0.90 | 0.990 | 0.050 | 600 | 1.308 | 27.517 | 38.0 | 6.3 | 99.7 |
| conflict-scent | 0.20 | 0.90 | 0.995 | 0.050 | 600 | 1.296 | 27.050 | 38.7 | 7.3 | 72.3 |

Saved table:

- path: `models/phase-2e-best-q.json`
- encoder: `conflict-scent`
- selected seed: 22
- selected metric: average reward

Replay smoke command:

```powershell
python -m abiogenesis.render.play_episode --agent q-learning --renderer ascii --q-path models/phase-2e-best-q.json --encoder conflict-scent --seed 100022 --grid-size 10 --delay 0
```

Replay observation: the saved table found four food tiles with zero poison collisions on the inspected episode, then spent its remaining energy in a small repeated movement pattern. That is useful behavior, but not full discipline.

Conclusion: tuning helped. The best default sweep result was conflict-scent with gamma 0.90, epsilon decay 0.990, and 600 training episodes. It improved poison discipline compared with the earlier raw scent behavior while preserving useful food seeking. The repeated late-episode wandering suggests the table still lacks memory or a richer signal for depleted areas.

## 2026-05-13: Phase 3A Tiny Memory

Question: does a minimal memory signal help Q-learning distinguish repeated looping from useful movement?

Memory signal:

- base features: existing `conflict-scent` state
- previous action
- whether the organism is at the same position as the previous step
- repeat-position bucket:
  - 0 = no repeat
  - 1 = repeated once
  - 2 = repeated multiple times

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 500 --eval-episodes 30 --grid-size 10 --multi-seed
```

Settings:

- encoders compared: `local`, `scent`, `conflict-scent`, `memory-scent`
- seeds: 21 through 23
- training episodes per Q-learning agent: 500
- evaluation episodes per seed: 30
- reward settings: default environment values

Mean results across seed-level summaries:

| Metric | Random | Local Q-learning | Raw scent Q-learning | Conflict-scent Q-learning | Memory-scent Q-learning |
| --- | ---: | ---: | ---: | ---: | ---: |
| Average reward | 0.319 | 1.932 | 1.218 | 1.060 | 0.347 |
| Average lifespan | 22.522 steps | 31.211 steps | 27.067 steps | 26.233 steps | 21.944 steps |
| Food eaten | 28.333 | 69.000 | 56.667 | 49.667 | 32.000 |
| Poison collisions | 12.000 | 1.667 | 12.000 | 10.000 | 15.000 |
| Wasted moves | 184.667 | 123.000 | 115.667 | 170.667 | 171.000 |
| Repeated positions | 184.667 | 123.000 | 115.667 | 170.667 | 171.000 |

Conclusion: this first tiny-memory encoding did not improve behavior under the small default comparison. It performed only slightly above random on reward, had the most poison collisions, and did not reduce repeated-position counts compared with raw scent. The result suggests that simply appending previous action and repeat status increases state space faster than 500 training episodes can exploit it.

## 2026-05-13: Phase 3B Visit Memory

Question: does a tiny visited-tile memory help the tabular learner avoid loops better than previous-action memory?

Visit memory signal:

- base features: existing `conflict-scent` state
- current tile visited before:
  - 0 = not visited before
  - 1 = visited before
- adjacent visited flags:
  - north visited
  - south visited
  - east visited
  - west visited

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 500 --eval-episodes 30 --grid-size 10 --multi-seed
```

Settings:

- encoders compared: `local`, `scent`, `conflict-scent`, `memory-scent`, `visit-scent`
- seeds: 21 through 23
- training episodes per Q-learning agent: 500
- evaluation episodes per seed: 30
- reward settings: default environment values

Mean results across seed-level summaries:

| Metric | Random | Local Q-learning | Raw scent Q-learning | Conflict-scent Q-learning | Memory-scent Q-learning | Visit-scent Q-learning |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Average reward | 0.319 | 1.932 | 1.218 | 1.060 | 0.347 | 0.306 |
| Average lifespan | 22.522 steps | 31.211 steps | 27.067 steps | 26.233 steps | 21.944 steps | 21.644 steps |
| Food eaten | 28.333 | 69.000 | 56.667 | 49.667 | 32.000 | 29.000 |
| Poison collisions | 12.000 | 1.667 | 12.000 | 10.000 | 15.000 | 13.333 |
| Wasted moves | 184.667 | 123.000 | 115.667 | 170.667 | 171.000 | 177.667 |
| Repeated positions | 184.667 | 123.000 | 115.667 | 170.667 | 171.000 | 177.667 |
| Unique tiles visited | 323.000 | 384.667 | 337.333 | 307.667 | 320.333 | 313.333 |

Conclusion: visit memory is wired correctly, but this first training setup did not use it well. Visit-scent scored slightly below memory-scent, visited fewer unique tiles than local and raw scent, and did not reduce repeated positions. Like Phase 3A, this points toward state-space growth outpacing the small training budget.

## 2026-05-14: Phase 3C Loop Detection

Question: does adding an explicit loop signal help the tabular learner notice
small movement cycles, and does an optional loop penalty improve the tradeoff?

Loop signal:

- base features: existing `conflict-scent` state
- previous action
- loop bucket:
  - 0 = no loop
  - 1 = two-position loop
  - 2 = three-position loop
  - 3 = longer repeated loop

No-penalty command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed
```

Settings:

- encoders compared: `local`, `scent`, `conflict-scent`, `memory-scent`, `visit-scent`, `loop-scent`
- seeds: 21 through 23
- training episodes per Q-learning agent: 200
- evaluation episodes per seed: 20
- loop penalty: 0.0

Mean results across seed-level summaries:

| Metric | Random | Local Q-learning | Raw scent | Conflict-scent | Memory-scent | Visit-scent | Loop-scent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Average reward | 0.227 | 1.704 | 0.378 | 0.564 | 0.192 | 0.213 | 0.319 |
| Average lifespan | 22.350 | 29.600 | 22.183 | 23.617 | 20.800 | 22.017 | 21.433 |
| Food eaten | 18.333 | 44.333 | 20.667 | 26.333 | 20.333 | 16.000 | 21.000 |
| Poison collisions | 9.333 | 4.333 | 8.667 | 10.333 | 12.333 | 7.333 | 10.333 |
| Wasted moves | 121.667 | 11.333 | 128.333 | 139.333 | 111.667 | 132.000 | 124.000 |
| Unique tiles visited | 219.667 | 271.667 | 183.667 | 186.000 | 196.000 | 193.333 | 199.333 |
| Loop detections | 36.000 | 217.333 | 119.000 | 116.667 | 33.000 | 30.667 | 34.000 |
| Revisit ratio | 0.546 | 0.582 | 0.630 | 0.646 | 0.570 | 0.599 | 0.573 |

Loop-penalty command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed --loop-penalty -0.05
```

Loop-scent with penalty:

| Metric | Value |
| --- | ---: |
| Average reward | 0.177 |
| Average lifespan | 21.500 |
| Food eaten | 18.333 |
| Poison collisions | 9.000 |
| Loop detections | 30.000 |
| Unique tiles visited | 196.667 |
| Revisit ratio | 0.586 |

Conclusion: loop detection is measurable and exposes behavior that the older
blocked-move repeat metric missed. In this short comparison, `loop-scent`
reduced loop detections compared with raw scent and conflict-scent, but it did
not beat local Q-learning on reward, lifespan, food, or unique coverage. A
small loop penalty reduced loop detections slightly further, but also reduced
reward and food collection. The result is a cautionary tradeoff, not evidence
that loop awareness is broadly better yet.

## 2026-05-15: Phase 3D Directional Novelty

Question: does telling the agent which adjacent directions are blocked,
visited, or unvisited improve exploration compared with only detecting loops?

Novelty signal:

- base features: existing `conflict-scent` state
- north/south/east/west novelty:
  - 0 = blocked
  - 1 = visited
  - 2 = unvisited

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed
```

Settings:

- encoders compared: `local`, `scent`, `conflict-scent`, `memory-scent`, `visit-scent`, `loop-scent`, `novelty-scent`
- seeds: 21 through 23
- training episodes per Q-learning agent: 200
- evaluation episodes per seed: 20
- reward settings: default environment values

Mean results across seed-level summaries:

| Metric | Random | Local Q-learning | Raw scent | Conflict-scent | Memory-scent | Visit-scent | Loop-scent | Novelty-scent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Average reward | 0.227 | 1.704 | 0.378 | 0.564 | 0.192 | 0.213 | 0.319 | 0.137 |
| Average lifespan | 22.350 | 29.600 | 22.183 | 23.617 | 20.800 | 22.017 | 21.433 | 21.333 |
| Food eaten | 18.333 | 44.333 | 20.667 | 26.333 | 20.333 | 16.000 | 21.000 | 15.000 |
| Poison collisions | 9.333 | 4.333 | 8.667 | 10.333 | 12.333 | 7.333 | 10.333 | 8.000 |
| Wasted moves | 121.667 | 11.333 | 128.333 | 139.333 | 111.667 | 132.000 | 124.000 | 151.667 |
| Unique tiles visited | 219.667 | 271.667 | 183.667 | 186.000 | 196.000 | 193.333 | 199.333 | 191.667 |
| Loop detections | 36.000 | 217.333 | 119.000 | 116.667 | 33.000 | 30.667 | 34.000 | 46.333 |
| Revisit ratio | 0.546 | 0.582 | 0.630 | 0.646 | 0.570 | 0.599 | 0.573 | 0.585 |

Conclusion: directional novelty did not improve exploration in this small run.
It reduced poison collisions compared with `loop-scent`, but collected less
food, had lower reward, wasted more moves, visited fewer unique tiles, and had
more loop detections. The directional signal is now measurable and available
for future sweeps, but the first result is mixed-to-negative rather than a
behavioral improvement.

## 2026-05-15: Phase 3D Optional Novelty Reward

Question: does directional novelty become useful when entering a new tile earns
a small explicit bonus?

Reward shaping:

- `--novelty-reward 0.02`
- applied in training/evaluation loops, not in `BacteriaWorldEnv`
- awarded only when entering a tile not previously visited in the same episode

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed --novelty-reward 0.02
```

Settings:

- seeds: 21 through 23
- training episodes per Q-learning agent: 200
- evaluation episodes per seed: 20
- reward settings: default environment values plus novelty shaping for the explicit novelty-reward comparison

Mean result for shaped novelty-scent:

| Metric | Novelty-scent | Novelty-scent reward 0.02 |
| --- | ---: | ---: |
| Average reward | 0.137 | 0.570 |
| Average lifespan | 21.333 | 21.750 |
| Food eaten | 15.000 | 23.000 |
| Poison collisions | 8.000 | 12.000 |
| Unique tiles visited | 191.667 | 257.333 |
| Loop detections | 46.333 | 28.000 |
| Revisit ratio | 0.585 | 0.436 |
| Novelty bonuses | 0.000 | 237.333 |
| Novelty reward total | 0.000 | 4.747 |

Conclusion: novelty reward made the directional novelty signal more useful for
coverage and food seeking in this small run. The shaped agent visited many more
unique tiles and collected more food than unshaped novelty-scent, and its
average reward rose. The cost was worse poison discipline. This is a promising
exploration-pressure tradeoff, not a complete improvement.

## 2026-07-26: Canonical Bacterium-0 Benchmark v1

All five quick and all five full named scenarios completed from clean commit
`7164e571810deac67042b87e3a5eacddfc24f6f0` and passed contract validation. The frozen
report preserves the full machine-derived tables, shaped/unshaped boundary, runtime cost,
mixed resource-shift result, and the redundant unseen-seed finding:

- `docs/experiments/BACTERIUM_0_V1_BENCHMARK_REPORT.md`

Generated run artifacts remain ignored and no policies were retained. This chronology entry
does not duplicate or reinterpret the frozen numerical tables.
