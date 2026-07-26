# Current Architecture

Last inventoried: 2026-07-26

## Scope

This is the implemented Bacterium-0 architecture through the R1B benchmark control layer.
It inventories existing behavior; it does not prescribe Bacterium-1 or refactor the
legacy evaluator.

## Environment

`src/abiogenesis/envs/bacteria_world.py` provides `BacteriaWorldEnv`, a Gymnasium
environment with deterministic seeded placement. `BacteriaWorldConfig` in `core/config.py`
owns explicit defaults for dimensions, food, poison, energy, episode length, rewards, and
costs. The environment exposes north, south, east, west, and wait actions, clamps movement
at boundaries, applies consequences, and returns copied observations plus step information.

`envs/sensors.py` calculates discrete cardinal food or poison scent: none, weak, or strong.

## Agents

- `RandomAgent` samples deterministic pseudorandom actions from a discrete action space and
  supplies the baseline.
- `QLearningAgent` owns epsilon-greedy selection, tabular Q updates, epsilon decay, and JSON
  table save/load. It accepts an observation encoder and never mutates the environment.

## Encoders and Memory Trackers

`q_learning_agent.py` contains stateless encoders:

- `local`: adjacent tiles plus a coarse energy bucket.
- `scent`: local state plus raw directional food and poison scent.
- `conflict-scent`: local state plus compact directional attraction/danger conflicts.

`agents/memory.py` contains episode-scoped trackers and encoders:

- `memory-scent`: previous action and repeated-position state.
- `visit-scent`: current/adjacent visited flags.
- `loop-scent`: recent-position cycle detection plus previous action.
- `novelty-scent`: blocked/visited/unvisited state for cardinal neighbors.

Training and playback reset/update encoder memory explicitly around environment steps. The
environment remains unaware of learning memory.

## Training

- `training/train_random.py` runs and summarizes the random baseline.
- `training/train_q_learning.py` registers encoders, trains Q tables, applies optional loop
  or novelty shaping outside the environment, and emits episode records.
- `training/sweep_q_learning.py` performs deterministic small hyperparameter grids and can
  save the representative best table.

All reward-shaping command defaults remain zero. No R0 tooling changes their semantics.

## Evaluation

`training/evaluate_q_learning.py` evaluates greedy trained policies against matched random
worlds, compares all current encoder variants, supports multi-seed aggregation, exposes
reward/energy experiment overrides, and formats CLI reports. It is the command wrapped by
the legacy benchmark script.

R1A defines named suites, scenarios, canonical policy IDs, seed policy, and artifact
schemas in `docs/experiments/BACTERIUM_0_BENCHMARK_V1.md` and
`docs/experiments/EXPERIMENT_ARTIFACT_CONTRACT.md`. R1B implements those definitions in
`abiogenesis.benchmark` without widening the legacy evaluator CLI. The runner can select
the canonical policy set, resolve explicit food/poison counts, and use separate training
and frozen evaluation configurations for `resource-shift-v1`.

## Metrics

`metrics/recorder.py` defines immutable episode and run summaries. Current measurements
cover total/average reward, lifespan, food, poison, wasted/repeated movement, unique tiles,
loop categories, novelty bonuses, and revisit ratio.

Current `RunSummary` semantics matter to R1: reward, lifespan, and revisit ratio are episode
means, while count and coverage fields are totals over evaluation episodes. The benchmark
runner preserves those per-seed meanings and adds count, mean, population standard
deviation, minimum, and maximum across replicate roots.

## Benchmark Control Layer

`src/abiogenesis/benchmark/` contains:

- `catalog.py`: immutable scenario, suite, and canonical-policy definitions;
- `models.py`: benchmark value objects, status values, metric names, and headings;
- `runner.py`: CLI resolution and narrow orchestration over existing training/evaluation
  functions;
- `artifacts.py`: collision-safe run directories, atomic writes, and SHA-256 metadata;
- `summary.py`: deterministic human-readable summaries;
- `validation.py`: dependency-free cross-file, registry, arithmetic, hash, and inventory
  validation.

Canonical runs contain all five policies. Test-smoke runs, policy subsets, and dirty-source
runs record deviations and cannot be marked `completed`. Optional learned Q tables are
written only when requested.

## Rendering

- `render/ascii_renderer.py` produces bordered observation and status text.
- `render/play_episode.py` orchestrates one ASCII or pygame replay using existing agents.
- `render/pygame_renderer.py` draws the dish, HUD, trail, scent overlay, and entity sprites.
- `render/sprite_assets.py` lazily resolves, loads, scales, and caches optional sprites from
  `assets/sprites/`; missing files fall back to shape rendering.
- `render/pygame_controls.py` keeps pause/reset/speed/overlay/screenshot/quit controls
  separate from world rules.

Rendering reads observations and playback counters. It is not part of the learning update
or environment dynamics.

## Tools and Engineering Scripts

- `tools/convert_pngs_to_rgba.py` prepares transparent PNG sprite copies using Pillow.
- `scripts/bootstrap.ps1` creates/refreshes the Python 3.13 development environment.
- `scripts/test.ps1` runs pytest with project-local temporary storage.
- `scripts/check.ps1` runs pytest and Ruff gates.
- `scripts/clean.ps1` removes safe generated caches and optionally output folders.
- `scripts/package-source.ps1` creates a filtered source archive.
- `scripts/run-benchmark.ps1` defaults to the contract-v1 runner and retains an explicit
  `-Mode Legacy` regression path.

The R1A example artifacts under `docs/experiments/examples/b0-quick-v1/` are synthetic
documentation, not generated results. Runtime artifacts are written under ignored `runs/`
directories and validated against the implemented registry.

## Documentation

Root control-plane files own current intent, decisions, state, verification, and next work.
`docs/lab-notes.md` and `docs/experiments.md` preserve chronological evidence. `HOME.md`
provides Obsidian navigation without becoming a competing source of truth.

## Data Flow

```text
explicit config + seed
        |
        v
 BacteriaWorldEnv.reset() -----> observation ----------------------+
        ^                            |                              |
        |                            v                              v
        |                    sensor / encoder                 ASCII / pygame
        |                            |                         observation
        |                            v
        |                    agent selects action
        |                            |
        +---- BacteriaWorldEnv.step(action)
                         |
                         +--> next observation + reward + info + done
                                      |
                          +-----------+-----------+
                          v                       v
                 optional training update   episode metrics
                                                  |
                                                  v
                                     run summary / comparison
```

R1B adds this behavior-neutral orchestration layer around the existing flow:

```text
scenario registry + suite profile
               |
               v
     existing train/evaluate seams
               |
               v
 per-seed evaluation records + aggregates
               |
               v
 manifest.json + metrics.json + summary.md
```
