# Decision Log

## 2026-07-20 — Bacterium-0 remains tabular for the current benchmark

Bacterium-0 is frozen conceptually as the legacy tabular benchmark. R0 and R1 do not add
neural networks, PyTorch, Stable-Baselines3, PettingZoo, or LLM integration.

## 2026-07-20 — Experiment claims require metrics

Behavioral improvement is claimed only when fair, reproducible measurements support the
specific claim. Human-visible anecdotes supplement metrics but do not replace them.

## 2026-07-20 — Mixed and negative results are preserved

Historical results remain evidence, including the poison tradeoffs and the mixed-to-negative
memory, loop, and novelty findings. They are not removed to simplify the narrative.

## 2026-07-20 — Rendering must not alter behavior

ASCII and pygame are observation surfaces. Rendering, sprites, controls, overlays, and
screenshots must not change environment state, rewards, agent policy, or encoder semantics.

## 2026-07-20 — Python 3.13 is the known-good development runtime

Development and bootstrap use `py -3.13`; `.python-version` contains `3.13`. Package
metadata uses `requires-python = ">=3.10,<3.14"`. This is the smallest safe R0 change that
prevents accidental Python 3.14 setup while retaining the existing core-library range.
Whether all support should become 3.13-only remains open in `OPEN_QUESTIONS.md`.

## 2026-07-20 — Obsidian is navigation, not authority

The repository root may remain an Obsidian vault, and `HOME.md` is its navigation page.
Authoritative project state stays in the ordered Markdown control plane defined by
`AGENTS.md`. `.obsidian/workspace.json` is ignored because it is user-specific and
churn-prone; existing shared app, appearance, and core-plugin files are preserved.

## 2026-07-20 — Commits require explicit owner approval

Codex does not commit, push, tag, publish, or open a pull request unless Joe explicitly
approves that action for the current work.

## 2026-07-20 — Visual behavior requires Joe's verification

Codex may test non-graphical rendering helpers and verify that pygame imports or starts only
when a task calls for those checks. Human-visible behavior is not verified unless Joe runs
the manual procedure and records the result.

## 2026-07-20 — Pytest uses repository-local temporary storage in project scripts

The machine-level temp root observed during R0 was inaccessible. `scripts/test.ps1` directs
pytest temporary files to ignored `.pytest-tmp/`, keeping the test command reproducible
without changing application or test behavior.

## 2026-07-21 — GitHub is the canonical source repository

`https://github.com/Inzania2016/digital-abiogenesis` is the canonical source repository and
`main` is its default branch. The remote was created with one owner-authored `LICENSE`
commit; Joe explicitly authorized preserving that commit and publishing the completed R0
baseline on top of it without force-pushing.

Generated environments, caches, runs, models, packaged archives, screenshots, secrets, and
personal editor/vault state are excluded from Git. Intentional source, tests, documentation,
scripts, shared project configuration, historical experiment evidence, and renderer assets
are included. The R0 publication is authorized directly to `main`; future feature work must
continue to follow the explicit commit gate in `AGENTS.md`.

## 2026-07-23 — Bacterium-0 benchmark v1 uses JSON artifacts

Canonical manifests use `manifest.json`; metrics use `metrics.json`; interpretation uses
`summary.md`. JSON requires no new dependency, matches existing machine-readable output,
and keeps the v1 artifact set on one serialization format. TOML is not selected for v1.

The contract is versioned as `1.0`, the benchmark as `bacterium-0-v1`, and run IDs use
`YYYYMMDDTHHMMSSZ_<scenario-id>_<suite-id>_<four-hex-suffix>`.

## 2026-07-23 — Quick and full suites have fixed seed lists and budgets

`b0-quick-v1` uses ordered replicate roots `[21, 22, 23]`, 200 training episodes per
learned policy and seed, and 20 evaluation episodes per policy and seed.

`b0-full-v1` uses ordered replicate roots `[21, 22, 23, 24, 25, 26, 27, 28, 29, 30]`,
1000 training episodes per learned policy and seed, and 100 evaluation episodes per policy
and seed. R1A does not run or claim the full suite.

Evaluation roots preserve the current `seed + 100000` derivation. Adjacent replicate roots
produce overlapping episode-seed windows under current behavior; the benchmark documents
that limitation instead of presenting the roots as statistically independent worlds.

## 2026-07-23 — Bacterium-0 v1 has five canonical policy variants

Canonical runs compare `random`, `local-q`, `conflict-scent-q`, `novelty-scent-q`, and
`novelty-scent-q-rewarded`. The rewarded variant uses the historically recorded novelty
reward `0.02`. Other existing encoders remain available for research without becoming
mandatory benchmark policies.

## 2026-07-23 — Scenario resource counts are explicit

`stable-default-v1` uses unchanged defaults. `sparse-food-v1` changes only `food_count` from
8 to 4. `poison-rich-v1` changes only `poison_count` from 6 to 12.
`resource-shift-v1` trains under stable defaults and evaluates the frozen policy under
`sparse-food-v1`. These count changes are benchmark configuration, not new environment
behavior, and require runner support in R1B because the legacy CLI does not expose them.

## 2026-07-23 — Metrics v1 preserves implementation semantics and requires dispersion

Per-seed reward, lifespan, and revisit ratio are episode means. Count and coverage metrics
are totals across the seed record's evaluation episodes. Cross-seed aggregates require
`count`, `mean`, population standard deviation, `min`, and `max`; confidence intervals are
deferred until runner cost is measured.

Schema-defined fields remain present. Measured zero is distinct from `null`, which means
inapplicable or uncollected. The existing machine name `novelty_reward_total` is retained
instead of adding the proposed alias `novelty_bonus_total`.

## 2026-07-23 — Generated policy artifacts remain optional and ignored

A policy artifact is emitted only when requested. Its policy ID, format, path, SHA-256,
byte count, and load command must be declared. Otherwise the run has no `policy/`
directory. R1A does not authorize curated policy commits or change the owner commit gate.

## 2026-07-26 — R1B is a narrow orchestration layer

The benchmark runner reuses the existing public training, greedy evaluation, random
evaluation, environment configuration, and `RunSummary` seams. It does not refactor
`evaluate_q_learning.py` or change environment, reward, agent, encoder, or episode-metric
semantics. Scenario selection, suite resolution, cross-seed aggregation, artifact writing,
and validation live under `abiogenesis.benchmark`.

`resource-shift-v1` is implemented by training under the stable configuration and
evaluating the frozen greedy policy under the sparse-food configuration. Evaluation does
not update Q values.

## 2026-07-26 — Noncanonical execution cannot claim completion

A run using the implementation-only `--test-smoke` profile, a policy subset, or a dirty
source tree records explicit deviations and terminates as `partial`, even when its files
validate. Only an undeviated canonical policy set, seed schedule, budget, clean source
state, complete metrics, and verified artifacts may terminate as `completed`.

The PowerShell wrapper now defaults to the named contract-v1 runner. The historical Phase
3D command remains available explicitly as `scripts/run-benchmark.ps1 -Mode Legacy`.

## 2026-07-26 — NEAT-Python 2.x is an optional research dependency

RS-01 uses `neat-python>=2.0,<3` only through the `neat` extra. Stable 2.0.0 was reviewed:
it is BSD-3-Clause, declares Python 3.13 support, provides deterministic population seeding,
and can export feed-forward networks to JSON. The upper bound excludes the next breaking
major; unreleased 2.1 repository state is not the minimum. NEAT remains absent from default,
development, and rendering dependencies.

## 2026-07-26 — NEAT remains experimental and has a separate artifact contract

The policy ID is `neat-feedforward-experimental`. It does not join the five canonical
Bacterium-0 policies or change benchmark contract `1.0`. Evolution runs use provisional
`artifact_type: neuroevolution-research` and `artifact_contract: neat-research-0.1` under
ignored `runs/neat/` directories. Pickled genomes are trusted-local artifacts; portable
network JSON, exact effective configuration, hashes, and lifecycle state are also required.

## 2026-07-26 — Experimental NEAT reuses novelty-scent without shaping fitness

The fixed 13-value input vector is the existing novelty-scent state normalized by each
documented discrete maximum. Outputs follow the existing action enumeration exactly:
north, south, east, west, wait. The first maximum wins ties. Fitness is mean unmodified
environment reward over ordered fitness roots and episodes; all other measures remain
secondary diagnostics.

## 2026-07-26 — RS-01 evaluation is serial with isolated seed roles

Python, NumPy, and NEAT population initialization use `experiment_seed`. Ordered fitness
roots `[21, 22, 23]` select the winner; disjoint holdout roots `[31, 32, 33]` are used only
after selection. Environment episode seeds are root plus zero-based episode index. Workers
remain one until deterministic Windows parallel behavior and ordering are separately
proved. Cross-platform bit-for-bit reproducibility is not claimed.
The strongest tested guarantee is repeatable NEAT initial populations under the same
version, configuration, seed, and runtime; a different experiment seed changes that
population. Wall-clock run IDs and NEAT's exported JSON timestamp are intentionally not
bit-identical and do not influence fitness.

## 2026-07-26 — Lenia must have a deterministic CPU reference before Godot GPU work

The proposed continuous substrate begins with a small NumPy CPU mathematical reference and
32x32/64x64 fixtures. A future Godot 4.7.1 backend must be compared using measured maximum
and mean cell error, mass difference, and centroid difference under owner-approved
tolerances. RS-01 adds no Lenia runtime or Godot project and copies no external code.

## 2026-07-26 — R1C accepts benchmark-v1 seed overlap and retains no policies

R1C accepts the adjacent replicate-root episode-window overlap as a documented benchmark-v1
limitation. It does not imply complete independence or redesign the schedule. Any redesign
requires a future scenario or benchmark version.

Canonical R1C runs omit generated policy artifacts. All ten quick/full run directories and
the execution ledger remain local and ignored. This packet does not decide whether a future
small curated policy may be committed.

## 2026-07-26 — Full canonical evidence passed the measured runtime gate

Five validated quick runs totaled 27.656 seconds. Scaling the measured variable time by the
quick/full episode-work ratio and adding a 20% margin projected 506.820 seconds for the full
suite, below both approved thresholds. All five full runs therefore executed sequentially,
validated, and totaled 489.825 seconds.

The frozen report separates shaped and unshaped return, preserves mixed and negative
findings, and records that `unseen-seeds-v1` duplicates `stable-default-v1` under the
benchmark-v1 environment and seed definitions. R1C changes no organism behavior.

## 2026-07-27 — Lenia paper v3 is the RS-02 mathematical authority

RS-02 freezes Bert Wang-Chak Chan, “Lenia: Biology of Artificial Life,”
arXiv `1812.05433v3`, equations 7-13 and 15-18. The implementation is a finite discrete
numerical reference and does not claim the continuous-space limit.

The author's repository at `adfc542939266de7f4bb7ebb552e8499701ee107` was used only to
cross-check operational order. Contrary to the packet's preliminary license note, that
exact tree contains an MIT `LICENSE.md`. No code, patterns, or assets were copied.

## 2026-07-27 — The CPU reference uses one direct periodic float32 update

The canonical model is two-dimensional, single-channel, additive Lenia with one normalized
radial polynomial kernel: radius 5, alpha 4, beta `[1.0]`; exponential growth uses
`mu=0.15`, `sigma=0.015`; `T=10` and `dt=0.1`. The boundary is periodic.

Runtime fields, stored fields, and stored kernels use C-contiguous little-endian IEEE-754
float32 (`<f4`). Kernel normalization and metric accumulation may use documented float64
temporaries. Convolution uses a float32 accumulator and deterministic row-major kernel
offsets with explicit `numpy.roll`; no FFT, SciPy, parallelism, backend selection, or GPU is
part of RS-02. Updates are synchronous, non-mutating, and clipped only after adding growth
to the unchanged current field.

## 2026-07-27 — Small deterministic Lenia fixtures are source-controlled

The project-authored 32x32 Gaussian-pair and 64x64 annulus/lobe recipes use no random source
or external lifeform pattern. Initial and expected `.npy` arrays plus a hash manifest are
committed as regression and future parity inputs. Loading always uses `allow_pickle=False`.

Within the same Python, NumPy, OS, architecture, configuration, and implementation,
regeneration and repeated steps must be bitwise identical. Across environments bitwise
identity is not promised; CPU golden comparisons use `rtol=0, atol=1e-6`, and unexplained
larger drift blocks rather than refreshes the goldens.

## 2026-07-27 — Comparative repositories remain reference-only

BioSim4 at `45e808cc86e24bae941b60ddebbedd53e874cbd5` and Evolving Protozoa at
`c10d43879ad8873c68f113195785ccd1d9507d9b` inform later L2-L7 questions only. Neither is a
dependency or port, and no code or assets were copied. BioSim4 is MIT but carries a
file-level GPL provenance warning in its genome-comparison source; Evolving Protozoa is MIT.

## 2026-08-09 — The artificial-cell hypothesis is a research direction, not a milestone

The project recognizes a bottom-up artificial-cell hypothesis alongside its top-down
organism track. This conceptual direction does not add, reorder, replace, or advance any
R0-R6 milestone; change the Lenia L0-L7 ladder or L1; or authorize implementation of
artificial cells, metabolism, reproduction, ecology, or cognition. Its claims remain subject
to the project's evidence standards, and substrate choice remains unresolved.
