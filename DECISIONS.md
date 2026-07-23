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
