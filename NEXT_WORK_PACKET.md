# Next Work Packet: R1C

## Title

**R1C: Execute and publish the canonical Bacterium-0 benchmark report.**

## Goal

Use the R1B runner to execute, validate, and audit the approved Bacterium-0 v1 benchmark
scenarios. Produce a frozen evidence report that distinguishes quick evidence from full
evidence, records runtime cost, and makes only metric-supported claims.

## In Scope

- Execute and validate `b0-quick-v1` for all five named scenarios.
- Record wall-clock cost and artifact locations for each quick run.
- Review quick artifacts for configuration agreement, status, deviations, hashes, metric
  completeness, and summary accuracy.
- If quick evidence and runtime cost support proceeding, execute and validate
  `b0-full-v1` for all five scenarios.
- Produce a frozen R1 benchmark report comparing the five canonical policies within each
  scenario and distinguishing shaped from unshaped returns.
- Record mixed and negative findings without selecting only favorable comparisons.
- Update project state, verification evidence, and owner questions from the completed
  audit.

## Out of Scope

- Changing environment dynamics, reward definitions, defaults, Q-learning, encoder
  semantics, seed derivation, scenario definitions, or metric semantics.
- Modifying the runner or validator except for a demonstrated blocking defect covered by
  a focused regression test.
- Retrofitting historical Markdown results into contract-v1 artifacts.
- Statistical redesign, hyperparameter tuning, or adding confidence intervals.
- Bacterium-1, homeostasis, environmental adaptation beyond the approved resource-shift
  scenario, reproduction, inheritance, ecology, neural networks, or LLMs.
- Committing generated run or policy artifacts by default.
- Committing or pushing without explicit owner approval.

## Likely Files

- Ignored run directories under `runs/`.
- A new frozen report under `docs/experiments/`.
- A dated record under `docs/verification/`.
- `PROJECT_STATE.md`, `OPEN_QUESTIONS.md`, and `NEXT_WORK_PACKET.md`.
- `docs/experiments.md` or `docs/lab-notes.md` only when the new evidence belongs in their
  historical chronology.

## Implementation Constraints

- Start from a clean source state so canonical runs may reach `completed`.
- Treat completed run directories as immutable.
- Validate every run before interpreting it.
- Do not compare reward-shaped and unshaped returns as though their reward definitions are
  identical.
- Do not promote a winning architecture beyond what the scenario metrics support.
- Stop and preserve evidence if a run is partial, failed, interrupted, or non-reproducible.

## Acceptance Criteria

- All five quick scenario runs exist, validate, and have no undeclared deviations.
- Full scenario runs are either completed and validated or explicitly deferred with a
  documented evidence-based reason.
- The report cites exact run IDs, suite IDs, scenario IDs, policy IDs, seed schedules,
  budgets, runtime costs, and relevant metrics.
- Conclusions preserve mixed and negative findings and honor shaped-return boundaries.
- Generated artifacts remain ignored and their retention status is explicit.
- Existing quality gates pass with no intentional organism behavior change.

## Verification Commands

```powershell
.\scripts\check.ps1
.\scripts\run-benchmark.ps1 -Scenario stable-default-v1 -Suite b0-quick-v1
.\scripts\run-benchmark.ps1 -Scenario sparse-food-v1 -Suite b0-quick-v1
.\scripts\run-benchmark.ps1 -Scenario poison-rich-v1 -Suite b0-quick-v1
.\scripts\run-benchmark.ps1 -Scenario resource-shift-v1 -Suite b0-quick-v1
.\scripts\run-benchmark.ps1 -Scenario unseen-seeds-v1 -Suite b0-quick-v1
.\.venv\Scripts\python.exe -m abiogenesis.benchmark.runner --validate-only <run-directory>
git diff --check
git status --short
```

Run the same five commands with `-Suite b0-full-v1` only after the quick audit confirms
configuration and cost are acceptable for the evidence packet.

## Open Owner Decisions

- Whether adjacent replicate-root episode-seed windows are acceptable for benchmark v1 or
  should be redesigned only in a future benchmark version.
- Whether any generated policy artifacts should be retained locally after the audit.
- Whether the full-suite runtime cost warrants executing every scenario in one packet.
