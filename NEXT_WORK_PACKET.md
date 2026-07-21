# Next Work Packet: R1A

## Title

**R1A: Define Bacterium-0 benchmark scenarios and experiment artifact contract.**

## Goal

Turn the current multi-seed evaluation surface into a small, named, reproducible benchmark
specification and finalize the run-artifact contract before implementing a general runner.

## In Scope

- Define named **quick** and **full** Bacterium-0 benchmark scenarios.
- Select existing agents/encoders and unchanged environment defaults for each scenario.
- Define scenario IDs, seed lists, episode budgets, expected artifact fields, and exact
  comparison questions.
- Resolve JSON versus TOML for manifests and quick/full seed counts with Joe.
- Refine `docs/experiments/EXPERIMENT_ARTIFACT_CONTRACT.md` into an implementation-ready
  version, including schema examples and validation rules.
- Update relevant control-plane, architecture, command, and verification documentation.
- Add documentation/schema tests only if a concrete machine-readable schema is introduced.

## Out of Scope

- Changing environment dynamics, rewards, default configuration, learning logic, or encoder
  semantics.
- Implementing Bacterium-1, homeostasis, reproduction, ecology, neural networks, or LLMs.
- Retrofitting historical experiment folders or changing historical metrics.
- Broadly refactoring `evaluate_q_learning.py` or `memory.py`.
- Committing model artifacts, adding CI, or committing/pushing without owner approval.

## Files Likely Involved

- `docs/experiments/EXPERIMENT_ARTIFACT_CONTRACT.md`
- a new benchmark specification under `docs/experiments/`
- `PROJECT_STATE.md`, `DECISIONS.md`, `OPEN_QUESTIONS.md`, and `VERIFICATION.md`
- `docs/COMMANDS.md` and `docs/architecture/CURRENT_ARCHITECTURE.md`
- `pyproject.toml` or `tests/` only if a schema dependency-free validator/test is justified

## Acceptance Criteria

- Quick and full suites have stable names, purposes, agents/encoders, seed lists, episode
  counts, and exact commands.
- Every scenario states the claim it can and cannot support.
- The artifact contract has required/optional fields, types, naming rules, and one complete
  example for `manifest`, `metrics`, and `summary`.
- Owner decisions are recorded without rewriting historical results.
- No organism behavior changes.
- Documentation checks and the existing quality gate pass, or failures are recorded.

## Verification Commands

```powershell
.\scripts\check.ps1
.\scripts\run-benchmark.ps1
```

If R1A adds a schema validator, also run its focused tests with
`.\.venv\Scripts\python.exe -m pytest <test-path>`.

## Open Owner Decisions

Joe must decide before the specification is finalized:

- JSON or TOML for the canonical experiment manifest.
- The canonical seed counts for quick and full suites.
- Whether R1A should define an exact metrics schema now or only required metric names and
  semantic rules.
