# Project State

Last reconciled: 2026-07-21

## Current Phase

**R0: Rebaseline and engineering retool, implemented and automatically verified.**
Bacterium-0 is conceptually frozen as the legacy benchmark organism. R0 changed the
engineering control plane, not organism behavior. Manual pygame verification remains Joe's
explicit boundary. The next implementation-ready packet is R1A in `NEXT_WORK_PACKET.md`.

## Canonical Repository

- GitHub repository: `https://github.com/Inzania2016/digital-abiogenesis`
- Default branch: `main`
- Local `main` tracks `origin/main`.
- The owner-created remote `LICENSE` commit `2306243a94ef2030936ca0f63991dadcc4d9b995`
  is preserved as the root of history.
- The completed R0 baseline was published directly to `main` as
  `dcc8f69f60f225040610ebd896dcc16b8f4e8512` under the authorized initialization packet.
- Publication details are recorded in
  `docs/verification/2026-07-21-git-publication.md`.
- Future feature commits remain subject to the explicit commit gate in `AGENTS.md`.

## Implemented Capabilities

- A deterministic, Gymnasium-compatible rectangular grid environment with food, poison,
  energy, movement boundaries, five actions, and episode termination/truncation.
- A deterministic random baseline and tabular Q-learning with save/load support.
- Local, raw scent, conflict-scent, tiny-memory, visit-memory, loop-scent, and
  directional-novelty encoders; optional loop and novelty reward shaping default to zero.
- Single- and multi-seed training/evaluation, Q-learning sweeps, and aggregate metrics for
  reward, lifespan, food, poison, movement, coverage, loops, and novelty.
- ASCII replay and a pygame observation window with controls, overlays, screenshots,
  optional PNG sprites, and shape fallbacks.
- A Pillow-based sprite transparency conversion tool.

Historical experiment results—including mixed and negative memory/novelty findings—are
preserved in `docs/experiments.md` and `docs/lab-notes.md`.

## Supported Runtime

- Supported development runtime: Python 3.13.
- Current observed local runtime: Python 3.13.13 in `.venv`.
- Package metadata permits Python 3.10 through 3.13 (`>=3.10,<3.14`) so the core library
  remains usable on its existing range while preventing unsupported Python 3.14 setup.
- Renderer dependency: pygame via the `render` extra.

See `DECISIONS.md` for the runtime decision and `OPEN_QUESTIONS.md` for the unresolved
long-term compatibility policy.

## Architecture Summary

The environment owns world dynamics; agents own policy and learning; sensors and encoders
translate observations and episode memory; training/evaluation orchestrate deterministic
runs; metrics summarize outcomes; renderers observe state without changing it. See
`docs/architecture/CURRENT_ARCHITECTURE.md` for the inventory and data flow.

## Verification Status

- Pre-R0 baseline on 2026-07-20: 87 tests collected; 77 passed and 10 errored during
  fixture setup because the machine-level pytest temp root was inaccessible.
- `scripts/bootstrap.ps1`: passed on Python 3.13.13 and installed `.[dev,render]`.
- `scripts/check.ps1`: passed with 87 tests, Ruff lint, and Ruff formatting checks.
- `scripts/run-benchmark.ps1`: passed; its 3-seed Phase 3D metrics reproduced the existing
  documented table.
- `scripts/package-source.ps1`: passed; final archive inspection found 77 entries and zero
  forbidden local/generated entries.
- Clean-source audit on 2026-07-21: the filtered archive bootstrapped a new Python 3.13.13
  `.venv`, installed `.[dev,render]` including pygame, and passed all 87 tests plus both Ruff
  gates in an isolated extracted copy. The audit copy was removed afterward.
- `scripts/clean.ps1`: removed bytecode, egg metadata, and other caches but returned an
  incomplete-clean error for the pre-existing permission-locked `.pytest_cache`.
- Pygame visual verification: not performed by Codex and not claimed.
- Git initialization, remote reconciliation, and R0 publication: complete. Local `main` and
  `origin/main` matched the published R0 commit at final verification.

The exact R0 engineering verification and publication histories are recorded in
`docs/verification/2026-07-20-r0.md` and
`docs/verification/2026-07-21-git-publication.md`.


## Known Limitations

- No named canonical benchmark scenarios or standard run artifact writer yet.
- Experiment comparisons are driven by large command surfaces rather than manifests.
- The tabular state space grows quickly for memory-rich encoders; recorded results show
  that several variants do not outperform the local baseline under tested budgets.
- No reproduction, inheritance, population model, environmental regime changes, or
  multi-agent ecology is implemented.
- Pygame behavior requires a human-visible manual check.

## Known Technical Debt

- `evaluate_q_learning.py` is oversized and mixes variant registration, training,
  evaluation, reward shaping, aggregation, formatting, and CLI work.
- `memory.py` is a growing collection of trackers and encoders.
- Experiment configuration is distributed across code defaults and CLI flags.
- Historical phase language drifted away from the current R0-R6 research ladder.
- Source archives have repeatedly included ignored local artifacts.

The bounded debt inventory is in `docs/architecture/TECHNICAL_DEBT.md`; R0 intentionally
does not refactor these runtime modules.
