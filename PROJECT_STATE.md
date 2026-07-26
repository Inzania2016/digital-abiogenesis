# Project State

Last reconciled: 2026-07-26

## Current Phase

**R1B: Bacterium-0 benchmark runner and artifact writer, implemented and automatically
verified.** Bacterium-0 remains conceptually frozen as the legacy benchmark organism. R1B
implements the approved R1A scenario/suite catalog, narrow execution layer, contract-v1
artifact writer, deterministic summary, optional policy persistence, and dependency-free
validator without changing organism behavior. Manual pygame verification remains Joe's
explicit boundary. The next implementation-ready packet is R1C in `NEXT_WORK_PACKET.md`.

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
- An approved `bacterium-0-v1` specification with quick/full suite profiles, five named
  scenarios, five canonical policies, exact seed/budget rules, and contract-v1 artifact
  examples.
- An immutable benchmark catalog and CLI runner covering stable, sparse-food, poison-rich,
  resource-shift, and unseen-seed scenarios through existing training/evaluation seams.
- Atomic contract-v1 manifest, metrics, summary, and optional learned-policy output under
  collision-safe ignored run directories.
- Dependency-free validation of registry agreement, lifecycle status, seeds/budgets,
  metrics and population aggregates, hashes, declared inventory, policy metadata, paths,
  and summary headings.

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
- R1A on 2026-07-23: example manifest and metrics JSON parsed; declared example hashes
  matched; all metric keys, sample counts, and aggregate population statistics were
  recomputed successfully.
- R1A `scripts/check.ps1`: passed with 87 tests, Ruff lint, and Ruff formatting checks.
- R1A `scripts/run-benchmark.ps1`: passed for seeds 21-23, 200 training episodes, and 20
  evaluation episodes; it reproduced the historical Phase 3D metrics.
- R1A full `b0-full-v1` suite: not run, as required by the specification packet.
- R1B focused benchmark tests: passed with 24 tests after formatting; the complete quality
  gate passed with 111 tests plus Ruff lint and formatting checks.
- R1B canonical dry run: passed and resolved `stable-default-v1`, `b0-quick-v1`, roots
  21-23, 200/20 episode budgets, and the five approved policies without writing artifacts.
- R1B tiny retained-policy smoke: produced a valid `partial` run containing five policy
  result sets and four learned Q-table artifacts. The validator passed its hashes,
  aggregate arithmetic, declarations, and file inventory. It correctly declared
  `test-smoke-profile` and `source-not-clean` deviations.
- R1B explicit legacy wrapper: passed and reproduced the deterministic Phase 3D comparison.
- R1B canonical quick and full evidence suites: not run; execution and audit belong to R1C.

The exact R0 engineering verification and publication histories are recorded in
`docs/verification/2026-07-20-r0.md` and
`docs/verification/2026-07-21-git-publication.md`. R1A evidence is in
`docs/verification/2026-07-23-r1a.md`; R1B evidence is in
`docs/verification/2026-07-26-r1b.md`.


## Known Limitations

- Canonical quick/full benchmark evidence has not yet been executed, audited, or frozen
  into an R1 report.
- Adjacent replicate roots preserve overlapping episode-seed windows; benchmark v1
  documents this limitation and does not establish statistically independent worlds.
- The new benchmark path and legacy evaluator share behavior through public function seams
  rather than a consolidated execution core, so characterization tests remain important.
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

The bounded debt inventory is in `docs/architecture/TECHNICAL_DEBT.md`; R1B intentionally
does not broadly refactor the legacy runtime modules.
