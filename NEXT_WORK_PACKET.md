# Next Work Packet: R1B

## Title

**R1B: Implement the benchmark runner and artifact writer.**

## Goal

Implement the narrow orchestration layer specified by
`docs/experiments/BACTERIUM_0_BENCHMARK_V1.md` and
`docs/experiments/EXPERIMENT_ARTIFACT_CONTRACT.md`. Run named Bacterium-0 scenarios through
existing training/evaluation behavior and emit dependency-free contract-v1 artifacts.

## In Scope

- Add an explicit scenario registry for:
  - `stable-default-v1`;
  - `sparse-food-v1`;
  - `poison-rich-v1`;
  - `resource-shift-v1`;
  - `unseen-seeds-v1`.
- Add immutable suite profiles for `b0-quick-v1` and `b0-full-v1`.
- Add a runner CLI with explicit scenario, suite, output root, and optional policy-output
  arguments.
- Execute exactly the five canonical policy variants.
- Reuse existing environment, agent, encoder, training, evaluation, and episode metric
  semantics.
- Support separate training/evaluation configurations for `resource-shift-v1` without
  continuing learning during evaluation.
- Write `manifest.json`, `metrics.json`, and `summary.md` under an immutable run ID.
- Calculate per-seed values plus count, mean, population standard deviation, minimum, and
  maximum.
- Add SHA-256 declarations and optional policy artifact metadata.
- Add a dependency-free validator for structure, registry agreement, hashes, counts,
  aggregate arithmetic, and required summary headings.
- Replace or extend `scripts/run-benchmark.ps1` only after retaining an explicit legacy
  regression path.
- Add focused unit and integration tests, including a tiny-budget smoke profile used only
  by tests.
- Update command, architecture, verification, and project-state documentation.

## Out of Scope

- Changing environment dynamics, rewards, defaults, Q-learning, encoder semantics, or
  existing metric collection.
- Running or publishing the full ten-seed suite as part of implementation.
- Broadly rewriting `evaluate_q_learning.py` or `memory.py`.
- Retrofitting historical experiment folders.
- Adding third-party schema, statistics, CLI, or persistence dependencies.
- Adding CI, Bacterium-1, homeostasis, reproduction, ecology, neural networks, or LLMs.
- Committing or pushing without explicit owner approval.

## Likely Files

- New modules under `src/abiogenesis/benchmarks/` for registry, runner, aggregation,
  artifacts, and validation.
- Narrow characterization or extraction changes in
  `src/abiogenesis/training/evaluate_q_learning.py` only where required to reuse existing
  behavior.
- `scripts/run-benchmark.ps1`.
- Focused tests under `tests/`.
- `PROJECT_STATE.md`, `VERIFICATION.md`, `docs/COMMANDS.md`, and
  `docs/architecture/CURRENT_ARCHITECTURE.md`.

## Implementation Constraints

- Treat the R1A documents as the behavior-neutral contract.
- Prefer small adapters around existing functions before extracting evaluator internals.
- Any evaluator extraction must have characterization tests demonstrating unchanged
  outputs for the legacy quick command.
- Evaluation must be greedy and must not update learned policy state.
- Resolved values, not only CLI inputs, go into the manifest.
- Completed run directories are immutable.
- A failed run must become an honest terminal or recoverable partial artifact, never a
  fabricated completion.

## Acceptance Criteria

- Named quick scenario runs select exactly five canonical policies.
- Scenario registry values exactly match R1A.
- Quick/full profiles expose the approved ordered roots and budgets.
- Sparse-food and poison-rich configurations alter only their declared count.
- Resource-shift trains on stable defaults and evaluates a frozen policy on sparse food.
- Unseen-seed roots and episode derivation match the specification.
- A tiny integration run emits all required files and passes the validator.
- Metrics preserve current per-seed meanings and calculate required population dispersion.
- Optional policies are hashed and declared when requested; `policy/` is absent otherwise.
- Legacy quick output remains reproducible within deterministic behavior.
- Existing quality gates pass.
- No intentional organism behavior change.

## Verification Commands

Exact new CLI/test paths should be finalized during implementation. At minimum run:

```powershell
.\scripts\check.ps1
.\scripts\run-benchmark.ps1
.\.venv\Scripts\python.exe -m pytest <focused-benchmark-tests>
.\.venv\Scripts\python.exe -m abiogenesis.benchmarks.run --scenario stable-default-v1 --suite <test-smoke-suite>
.\.venv\Scripts\python.exe -m abiogenesis.benchmarks.validate <generated-run-directory>
git diff --check
git status --short
```

Do not run the full `b0-full-v1` suite during R1B implementation unless Joe explicitly asks
for that evidence run.

## Open Owner Decisions

None are required to begin R1B. Stop and request direction only if implementation would
require changing a frozen R1A semantic, adding a dependency, or broadly decomposing the
legacy evaluator beyond narrow tested seams.
