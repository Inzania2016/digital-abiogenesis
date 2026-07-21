# Current Architecture

Last inventoried: 2026-07-20

## Scope

This is the implemented Bacterium-0 architecture at R0. It inventories existing behavior;
it does not prescribe Bacterium-1 or refactor the runtime.

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
the R0 benchmark script.

## Metrics

`metrics/recorder.py` defines immutable episode and run summaries. Current measurements
cover total/average reward, lifespan, food, poison, wasted/repeated movement, unique tiles,
loop categories, novelty bonuses, and revisit ratio.

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
- `scripts/run-benchmark.ps1` wraps the current deterministic multi-seed evaluation.

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
