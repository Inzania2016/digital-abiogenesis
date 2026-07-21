# R0 Git Publication Record — 2026-07-21

## Scope

This record covers initialization of the local Git repository, reconciliation with the
existing GitHub history, and publication of the verified R0 baseline. Joe explicitly
authorized committing and publishing directly to `main` for this packet. No pull request
was requested or created.

## Repository and History

- Canonical remote: `https://github.com/Inzania2016/digital-abiogenesis.git`
- Default branch: `main`
- Preserved owner-created root commit: `2306243a94ef2030936ca0f63991dadcc4d9b995`
  (`Initial commit`, containing `LICENSE`)
- Published R0 commit: `dcc8f69f60f225040610ebd896dcc16b8f4e8512`
- R0 commit message: `Establish Digital Abiogenesis R0 baseline`
- Published scope: 77 added files, 8,605 inserted lines, approximately 7.54 MiB in the
  working-tree representation; no individual file exceeded 10 MiB.
- Final branch relationship before this record: local `main` and `origin/main` both pointed
  to the published R0 commit.

The existing remote commit was retained as the parent of the R0 commit. No history rewrite
or force update was used.

## Baseline Selection and Hygiene

The committed baseline includes source, tests, deterministic PowerShell scripts,
authoritative and historical documentation, shared Codex configuration, portable Obsidian
configuration, and the intentional pygame sprite assets.

The baseline excludes virtual environments, Python and test caches, bytecode, build and
distribution output, local model/run/artifact output, screenshots, logs, secrets and local
environment files, user-specific VS Code state, and Obsidian workspace/cache state.
`LICENSE` was already tracked and remained unchanged.

Secret-name and credential-pattern checks found no project secret files selected for the
baseline. The only certificate encountered by an earlier broad scan was pip's certificate
bundle inside the ignored `.venv`. Machine-specific absolute paths in the R0 verification
record were replaced with portable descriptions before publication.

## Commands and Results

- `git init -b r0-reconcile`: passed.
- `git remote add origin https://github.com/Inzania2016/digital-abiogenesis.git`: passed.
- `git fetch origin --prune`: passed.
- `git switch -c main --track origin/main`: passed.
- `./scripts/clean.ps1`: removed normal generated output but reported the known
  permission-locked `.pytest_cache`; `.venv` was intentionally preserved.
- Ignore, staged-scope, size, secret-name, and large-file checks: passed for the selected
  baseline.
- `git diff --cached --check`: passed before the R0 commit.
- `./scripts/check.ps1`: passed on Python 3.13.13; 87 tests passed, Ruff lint passed, and 39
  Python files passed the Ruff formatting check.
- `./scripts/run-benchmark.ps1`: passed for seeds 21 through 23 with 200 training episodes
  per Q agent and 20 evaluation episodes per seed. The output reproduced the documented
  Phase 3D metrics; local Q-learning remained the strongest average-reward variant in this
  run at `1.704` versus random at `0.227`.
- `git commit -m "Establish Digital Abiogenesis R0 baseline"`: created the local baseline
  commit successfully.
- `git push origin main`: did not run because the execution environment required an
  interactive approval while its approval policy was disabled.
- Authenticated GitHub Git Data API fallback: uploaded and hash-verified all 77 new blobs,
  reproduced the local tree `4ffbf276befe79b601e4a4aa896930ab80a1437a`, created the R0
  commit, and advanced `refs/heads/main` without force.
- `git fetch origin main`: passed after publication and synchronized the tracking ref.

GitHub's Git Data API retained the original `-05:00` author and committer offset but omitted
the conventional trailing newline in the submitted one-line commit message. The repository
parent, tree, displayed message, author, committer, and instant were unchanged. The fetched
GitHub commit is therefore the canonical published object identified above.

## Benchmark Summary

The canonical wrapper completed successfully. Selected average rewards were:

| Variant | Average reward |
| --- | ---: |
| random | 0.227 |
| local-q | 1.704 |
| raw-scent | 0.378 |
| conflict | 0.564 |
| memory | 0.192 |
| visit | 0.213 |
| loop | 0.319 |
| novelty | 0.137 |

These are verification results, not new experiment claims. The full historical result and
its mixed and negative findings remain in `docs/experiments.md`.

## Verification Boundary

- No organism behavior, rewards, defaults, learning logic, encoder semantics, or recorded
  experiment results were intentionally changed for Git publication.
- The pygame viewer was not run for this packet, and Codex makes no visual-verification
  claim. Human-visible pygame behavior remains Joe's verification boundary.
- No commit was force-pushed, no history was rewritten, and no pull request was created.
