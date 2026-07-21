# Lab Notes

## 2026-05-11: Phase 0, The Petri Dish

Bacterium-0 has its first dish: a 10x10 Gymnasium grid-world with one organism, food, poison, energy, and a hard episode limit.

Rules are intentionally small and measurable. The organism can move north, south, east, west, or wait. Every tick costs energy and a tiny reward penalty. Food restores energy and gives a positive reward. Poison drains energy and gives a negative reward. An episode ends when the organism runs out of energy or reaches the maximum step count.

No learning has been added yet. Today the microbe crawls.

## 2026-05-11: Phase 1, The Drunk Microbe

Bacterium-0 now has a random baseline agent and a repeatable evaluation script.

Command:

```powershell
python -m abiogenesis.training.train_random --seed 13 --episodes 10 --grid-size 10
```

Results:

- episodes: 10
- seed: 13
- grid: 10x10
- average reward: -0.467
- average lifespan: 16.70 steps
- food eaten: 3
- poison collisions: 6
- wasted moves: 50

Interpretation: the baseline is alive enough to fail in measurable ways. It bumps, waits, eats occasionally, hits poison too often, and gives us something future learning runs must beat.

## 2026-05-11: Phase 2A, The Slightly Less Stupid Microbe

Bacterium-0 now has a small tabular Q-learning agent. Its state is deliberately limited: the contents of the north, south, east, and west neighboring tiles, plus a coarse energy bucket. This is not a neural net and not a planner. It is a little table of remembered consequences.

Comparison command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --train-episodes 1000 --eval-episodes 50 --grid-size 10
```

Results:

- evaluation episodes: 50
- evaluation seed: 100021
- grid: 10x10
- random average reward: 0.166
- random average lifespan: 21.40 steps
- random food eaten: 39
- random poison collisions: 20
- Q-learning average reward: 1.263
- Q-learning average lifespan: 27.70 steps
- Q-learning food eaten: 77
- Q-learning poison collisions: 0

Interpretation: the table-brain learned a useful local rule set. It still does not understand the whole dish, but in this run it found more food, lived longer, and avoided poison entirely during evaluation.

## 2026-05-12: Phase 2B, The Microbe Gets A Nose

Bacterium-0 now has primitive directional scent. For each cardinal direction, the sensor reports the nearest food signal and nearest poison signal as a tiny discrete value: 0 for none, 1 for weak, and 2 for strong. Adjacent objects smell strong; farther objects smell weak.

The old local-tile Q-learning encoder is still available for comparison. The new scent-aware encoder keeps the adjacent tile codes and energy bucket, then adds directional food scent and directional poison scent.

Comparison command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --compare-scent
```

Results:

- evaluation episodes: 50
- evaluation seed: 100021
- grid: 10x10
- random average reward: 0.166
- random average lifespan: 21.40 steps
- random food eaten: 39
- random poison collisions: 20
- local Q-learning average reward: 1.263
- local Q-learning average lifespan: 27.70 steps
- local Q-learning food eaten: 77
- local Q-learning poison collisions: 0
- scent Q-learning average reward: 1.684
- scent Q-learning average lifespan: 29.56 steps
- scent Q-learning food eaten: 109
- scent Q-learning poison collisions: 10

Interpretation: scent helped the table-brain find more food and live longer under the same evaluation worlds. The tradeoff in this run is that the scent-aware policy accepted more poison collisions than the local-tile learner. Useful nose, imperfect judgment.

## 2026-05-12: Visual Intermission, The Observation Window

Before adding new learning behavior, the lab now has a way to watch Bacterium-0 move through the dish.

The ASCII renderer now draws bordered grids with clear marks for organism, food, poison, and empty space. Playback frames include step count, energy, last reward, total reward, food eaten, and poison collisions.

ASCII command:

```powershell
python -m abiogenesis.render.play_episode --agent random --renderer ascii --seed 7 --delay 0.2
```

There is also an optional pygame renderer for a small colored-tile viewing window. It shows the same core HUD metrics and supports space to pause, `r` to reset, and `q` or escape to quit.

Pygame setup and command:

```powershell
python -m pip install -e ".[render]"
python -m abiogenesis.render.play_episode --agent q-learning --renderer pygame --seed 21 --train-episodes 500 --encoder scent
```

No new learning behavior was added here. This is a viewport into the existing creature, useful for noticing patterns the aggregate metrics flatten away.

## 2026-05-12: Phase 2C, Poison Discipline

Goal: analyze the Phase 2B tradeoff where scent-aware Q-learning finds more food but accepts more poison collisions than local-tile Q-learning.

The evaluator now has a multi-seed mode that keeps the three-way comparison intact: random baseline, local Q-learning, and scent-aware Q-learning. It also accepts reward and energy knobs for poison penalty, poison energy cost, food reward, and step penalty. Defaults are unchanged unless a command passes overrides.

Default command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 5 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --multi-seed
```

Default five-seed mean results:

- random average reward: 0.200
- local Q-learning average reward: 1.184
- scent Q-learning average reward: 1.514
- random poison collisions: 21.400
- local Q-learning poison collisions: 1.400
- scent Q-learning poison collisions: 12.000
- random wasted moves: 298.200
- local Q-learning wasted moves: 202.600
- scent Q-learning wasted moves: 155.800

Harsher poison command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 5 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --multi-seed --poison-penalty -2.0 --poison-energy-cost 12
```

Harsher poison five-seed mean results:

- random average reward: -0.238
- local Q-learning average reward: 1.653
- scent Q-learning average reward: 1.066
- random poison collisions: 21.400
- local Q-learning poison collisions: 1.600
- scent Q-learning poison collisions: 13.000

Interpretation: scent remains useful for food seeking and movement efficiency under the default reward scheme, but the poison-discipline problem is real across seeds. Simply making poison harsher did not teach the scent-aware table to avoid it; it mostly made local Q-learning look better. Next likely experiment: improve the scent state representation around food/poison conflicts, or sweep Q-learning hyperparameters across multiple seeds before changing the organism again.

## 2026-05-12: Phase 2D, Conflict-Aware Scent

Goal: give the scent-aware table a more compact way to notice when a direction contains attraction, danger, or both.

The original local encoder and raw scent encoder remain available. A new `conflict-scent` encoder adds four directional values after the adjacent tile codes:

- 0 = no signal
- 1 = food only
- 2 = poison only
- 3 = both food and poison
- 4 = adjacent poison

The multi-seed evaluator now compares random, local Q-learning, raw scent Q-learning, and conflict-scent Q-learning in the same run.

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 5 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --multi-seed
```

Default five-seed mean results:

- random average reward: 0.200
- local Q-learning average reward: 1.184
- raw scent Q-learning average reward: 1.514
- conflict-scent Q-learning average reward: 1.401
- random poison collisions: 21.400
- local Q-learning poison collisions: 1.400
- raw scent Q-learning poison collisions: 12.000
- conflict-scent Q-learning poison collisions: 9.800
- raw scent food eaten: 102.000
- conflict-scent food eaten: 94.000

Interpretation: conflict-aware scent did what it was designed to do, but only partially. It reduced poison collisions compared with raw scent while preserving much of the food-seeking advantage. The cost was lower reward, less food, and more wasted movement than raw scent. The nose is more cautious now, but not yet disciplined enough to beat local Q-learning on poison avoidance.

## 2026-05-12: Phase 2E, Learning Sweep and Behavior Replay

Goal: tune the tabular learner before adding new organism features or bigger model machinery.

A new sweep script compares Q-learning settings across multiple seeds. It can sweep:

- alpha
- gamma
- epsilon decay
- minimum epsilon
- training episodes
- encoder choice

Default command:

```powershell
python -m abiogenesis.training.sweep_q_learning --seed 21 --seeds 3 --eval-episodes 20 --grid-size 10 --save-best-path models/phase-2e-best-q.json
```

Best result by mean average reward:

- encoder: conflict-scent
- alpha: 0.20
- gamma: 0.90
- epsilon decay: 0.990
- minimum epsilon: 0.050
- training episodes: 600
- average reward: 1.337
- average lifespan: 28.017
- food eaten: 36.0
- poison collisions: 3.7
- wasted moves: 96.7

The sweep saved the best representative table to `models/phase-2e-best-q.json`. Replay command:

```powershell
python -m abiogenesis.render.play_episode --agent q-learning --renderer ascii --q-path models/phase-2e-best-q.json --encoder conflict-scent --seed 100022 --grid-size 10 --delay 0
```

Replay interpretation: the saved table collected four food items and avoided poison in the inspected episode, then fell into repeated movement until energy ran out. This suggests the tuned table-brain has useful danger discipline, but still has no memory of exhausted territory or broader search plan.

Next step: run a slightly wider sweep or add a minimal memory signal only after the table-brain tuning plateau is better understood.

## 2026-05-12: Phase 2F, Sensor and Action Overlay

Goal: make replay more useful without changing the organism, rewards, or learning.

ASCII replay now has a `--debug-overlay` flag for Q-learning agents. The overlay shows:

- encoder name
- encoded state tuple
- chosen action for the current frame
- best action by the current Q-table values
- Q-values for north, south, east, west, and wait
- raw scent or conflict-scent direction labels when the encoder includes scent

Example command:

```powershell
python -m abiogenesis.render.play_episode --agent q-learning --renderer ascii --q-path models/phase-2e-best-q.json --encoder conflict-scent --seed 100022 --grid-size 10 --delay 0.1 --debug-overlay
```

Smoke-test observation: the overlay makes tie-heavy or undertrained tables obvious. In the quick check, many states had all-zero Q-values, so the chosen action could differ from the first best table action because tie-breaking still comes from the agent policy. That is useful microscope data, not a behavior change.

Interpretation: this gives us a way to watch what the table-brain can and cannot distinguish before adding memory or a larger learning system.

## 2026-05-13: Phase 3A, Tiny Memory

Goal: give Bacterium-0 a minimal episode memory signal without changing environment rules, rewards, or movement.

Added a `memory-scent` encoder. It keeps the existing conflict-scent features and appends:

- previous action
- same-position flag from the previous step
- repeat-position bucket:
  - 0 = no repeat
  - 1 = repeated once
  - 2 = repeated multiple times

The memory tracker resets at the start of each episode and updates after each environment step. The environment itself remains stateless with respect to learning memory.

Comparison command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 500 --eval-episodes 30 --grid-size 10 --multi-seed
```

Results:

- local Q-learning average reward: 1.932
- raw scent Q-learning average reward: 1.218
- conflict-scent Q-learning average reward: 1.060
- memory-scent Q-learning average reward: 0.347
- local repeated positions: 123.000
- raw scent repeated positions: 115.667
- conflict-scent repeated positions: 170.667
- memory-scent repeated positions: 171.000
- memory-scent poison collisions: 15.000

Interpretation: the crumb of memory is wired in, but the first measured behavior is poor. The memory-scent state did not reduce loops in this small comparison, and it increased poison collisions. Likely cause: the extra memory dimensions enlarge the table enough that 500 episodes is too little, or the current repeat signal is too crude. Next step should be either a small Phase 3A sweep for `memory-scent` specifically or a simpler memory feature before adding any larger brain.

## 2026-05-13: Phase 3B, Visit Memory

Goal: give Bacterium-0 a tiny chalk-mark memory of visited tiles, without changing environment rules.

Added a `visit-scent` encoder. It keeps the existing conflict-scent features and appends:

- current tile visited before
- north tile visited
- south tile visited
- east tile visited
- west tile visited

The visited set resets at the start of each episode and updates after each environment step. Metrics now include unique tiles visited when summaries are built from episode records.

Comparison command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 500 --eval-episodes 30 --grid-size 10 --multi-seed
```

Results:

- local Q-learning average reward: 1.932
- raw scent Q-learning average reward: 1.218
- conflict-scent Q-learning average reward: 1.060
- memory-scent Q-learning average reward: 0.347
- visit-scent Q-learning average reward: 0.306
- local unique tiles visited: 384.667
- raw scent unique tiles visited: 337.333
- memory-scent unique tiles visited: 320.333
- visit-scent unique tiles visited: 313.333
- visit-scent repeated positions: 177.667

Interpretation: the chalk marks exist, but the table-brain did not turn them into better behavior under this small training budget. Visit memory slightly underperformed the previous tiny-memory encoder and did not reduce repeated positions. This is another sign that adding state features is cheap, but making the tabular learner use them may require more training, a sweep, or a simpler feature design.

## 2026-05-13: Phase 3A.5, Fancy Petri Dish Viewer

Goal: improve the pygame observation window without changing environment behavior, rewards, learning, or agent policy.

The pygame renderer now presents the dish as a clearer artificial-life lab view:

- configurable tile size
- darker dish background
- visible grid lines
- pulsing organism
- glowing food
- danger-marked poison
- subtle empty tiles
- optional trail overlay
- optional scent/debug overlay
- HUD panel with agent, encoder, seed, step, energy, rewards, food, poison, wasted moves, and repeated positions

Example command:

```powershell
python -m abiogenesis.render.play_episode --agent q-learning --renderer pygame --seed 21 --train-episodes 500 --encoder conflict-scent --tile-size 56 --debug-overlay
```

Controls:

- Space: pause/unpause
- R: reset episode
- Escape or Q: quit
- Up/Down or +/-: increase/decrease playback speed
- T: toggle trail overlay
- S: toggle scent overlay
- H: toggle HUD
- P or F12: save a screenshot to `artifacts/screenshots/`

Interpretation: this is a microscope upgrade only. The creature moves under the same policies and receives the same consequences; the viewer just makes its movement, sensed directions, and repeated paths easier to inspect.

## 2026-05-14: Phase 3A.6, Sprite-Based Petri Dish Viewer

Goal: make the pygame dish prettier without changing environment behavior,
rewards, movement, Q-learning, encoders, training, evaluation, or ASCII
rendering.

The pygame renderer now looks for optional sprites in `assets/sprites/`:

- `bacteria_tardigrade.png`
- `food_drumstick.png`
- `poison_mushrooms.png`

Sprites are loaded lazily, scaled to the tile size, cached, and drawn with
transparency preserved. Missing sprites fall back to the previous shape-based
tile drawing, and `--no-sprites` forces shape rendering. A custom sprite
directory can be passed with `--sprite-dir`.

Example command:

```powershell
python -m abiogenesis.render.play_episode --agent q-learning --renderer pygame --seed 21 --train-episodes 500 --encoder conflict-scent --tile-size 56 --debug-overlay
```

Interpretation: this is visualization-only. No experiment metrics were updated
because the organism's behavior and consequences did not change.

## 2026-05-14: Sprite Asset Pipeline

Goal: make sprite preparation repeatable without changing runtime behavior.

Added `tools/convert_pngs_to_rgba.py`, a Pillow-based utility that recursively
scans PNG sprite folders, converts images to RGBA, and turns pixels matching a
configured background color transparent. Defaults key out white (`#FFFFFF`) with
tolerance `10`.

Non-destructive example:

```powershell
python tools/convert_pngs_to_rgba.py --input assets/sprites --output assets/sprites_rgba --bg "#FFFFFF" --tolerance 10
```

Intentional overwrite example:

```powershell
python tools/convert_pngs_to_rgba.py --input assets/sprites --bg "#FFFFFF" --tolerance 10 --overwrite
```

Interpretation: this is asset tooling only. The environment, agents, rewards,
encoders, training, evaluation, ASCII renderer, and pygame controls are
unchanged.

## 2026-05-14: Phase 3C, Loop Detection and Exploration Pressure

Goal: give Bacterium-0 a tiny signal for repeated movement cycles without
adding neural networks or changing environment rules.

Added a recent-position loop tracker that detects simple cycles such as
A-B-A-B and A-B-C-A-B-C. Added a `loop-scent` encoder that keeps the existing
conflict-scent features and appends:

- previous action
- loop bucket:
  - 0 = no loop
  - 1 = length-2 loop
  - 2 = length-3 loop
  - 3 = longer loop

Metrics now include loop detections, short/medium/long loop counts, unique
tiles, and revisit ratio. A `--loop-penalty` option applies optional reward
pressure in training/evaluation loops; its default is `0.0`.

No-penalty comparison command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed
```

Mean results:

- local Q-learning average reward: 1.704
- local loop detections: 217.333
- loop-scent average reward: 0.319
- loop-scent loop detections: 34.000
- loop-scent unique tiles visited: 199.333

Loop-penalty command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed --loop-penalty -0.05
```

Loop-scent with penalty:

- average reward: 0.177
- food eaten: 18.333
- poison collisions: 9.000
- loop detections: 30.000
- unique tiles visited: 196.667
- revisit ratio: 0.586

Interpretation: loop awareness is wired and measurable, but this short
comparison does not show a clean behavioral improvement. The penalty reduced
loop detections slightly compared with loop-scent without penalty, but it also
reduced reward and food collection. This is a tradeoff, not a win.

## 2026-05-15: Phase 3D, Directional Novelty Pressure

Goal: give Bacterium-0 directional information about nearby novelty, rather
than only telling it that a loop is happening.

Added a `novelty-scent` encoder. It keeps the existing conflict-scent features
and appends north/south/east/west novelty buckets:

- 0 = blocked
- 1 = visited
- 2 = unvisited

Example command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed
```

Mean results for the new encoder in the small comparison:

- novelty-scent average reward: 0.137
- novelty-scent average lifespan: 21.333
- novelty-scent food eaten: 15.000
- novelty-scent poison collisions: 8.000
- novelty-scent unique tiles visited: 191.667
- novelty-scent loop detections: 46.333
- novelty-scent revisit ratio: 0.585

Interpretation: directional novelty is wired and visible in the debug overlay,
but this first short run did not improve behavior. It reduced poison collisions
relative to loop-scent in the same comparison, but reward, food collection,
wasted movement, and loop detections were worse. The result suggests the signal
may need more training, a smaller representation, or reward shaping before it
becomes useful.

## 2026-05-15: Phase 3D, Optional Novelty Reward

Goal: test whether the directional novelty signal becomes useful when the
agent has a small reason to enter new tiles.

Added `--novelty-reward`, defaulting to `0.0`. The reward is applied outside
`BacteriaWorldEnv` in the training/evaluation loops, and only when the organism
enters a tile that has not been visited earlier in the same episode. Metrics
now track novelty bonus count and total novelty reward.

Command:

```powershell
python -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed --novelty-reward 0.02
```

Novelty-reward result:

- novelty-scent-reward-0.02 average reward: 0.570
- average lifespan: 21.750
- food eaten: 23.000
- poison collisions: 12.000
- novelty bonuses: 237.333
- novelty reward total: 4.747
- loop detections: 28.000
- unique tiles visited: 257.333
- revisit ratio: 0.436

Interpretation: the curiosity compass started to matter, but it is still a
tradeoff. Compared with unshaped novelty-scent, the reward improved average
reward, food collection, unique tile coverage, and revisit ratio. It also
increased poison collisions. This suggests exploration pressure is useful, but
needs poison discipline or tuning before it is a clean improvement.

## 2026-07-20: R0 Rebaseline and Engineering Retool

Goal: preserve Bacterium-0 as the legacy benchmark while installing a durable project
control plane, explicit Python 3.13 development contract, deterministic PowerShell tooling,
quality gates, architecture inventory, artifact-contract design, and Obsidian navigation.

The R0 implementation intentionally leaves environment rules, reward defaults, agent
learning, encoder semantics, metrics, historical results, and the sprite-based pygame viewer
unchanged. Detailed command outcomes and manual-verification boundaries are recorded in the
dated R0 verification record rather than repeated here.

Interpretation: this is an engineering rebaseline, not a new organism experiment. The next
research task is R1A: define named Bacterium-0 benchmark scenarios and finalize the future
run-artifact contract.
