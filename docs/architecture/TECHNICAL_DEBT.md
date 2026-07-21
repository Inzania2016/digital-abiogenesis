# Technical Debt Inventory

Last reviewed: 2026-07-20

This file records debt without authorizing broad R0 refactoring. Priority should be set by
future work packets and evidence needs.

## TD-001: Oversized Evaluation Module

`src/abiogenesis/training/evaluate_q_learning.py` is roughly 900 lines and owns too many
concerns: training invocation, evaluation loops, reward shaping, variant registration,
multi-seed aggregation, formatting, and CLI parsing. This makes benchmark contracts harder
to isolate and increases the risk of inconsistent variants.

Likely future direction: separate scenario specification, execution, aggregation, and
presentation after R1 defines stable artifacts. Do not refactor ahead of that contract.

## TD-002: Training and Evaluation Responsibilities Are Entangled

Training functions, evaluation helpers, reward-shaping behavior, encoder registration,
aggregate models, report formatting, and command interfaces reach across several modules.
The current system works, but adding named benchmarks or new organisms could multiply
branching logic.

Likely future direction: introduce narrow data contracts first, then extract orchestration
in behavior-preserving steps with characterization tests.

## TD-003: Memory Module Growth

`src/abiogenesis/agents/memory.py` has become a large collection of independent trackers,
encoder adapters, constants, and lifecycle helpers. The contents remain understandable,
but ownership will blur as internal-state research grows.

Likely future direction: organize by tracker/encoder family only when a work packet needs
it; preserve encoder semantics and comparison availability.

## TD-004: Distributed Experiment Configuration

Experiment configuration is spread across dataclass defaults, function parameters, parser
flags, and command documentation. Exact runs depend on long command lines and implicit code
defaults.

R1 response: named scenarios and the experiment artifact contract should establish an
explicit versioned source before changing runtime orchestration.

## TD-005: README Command Catalog Growth

The old README accumulated phase history and a large command catalog, making current state
hard to find. R0 makes it a landing page and preserves detailed commands in
`docs/COMMANDS.md`.

## TD-006: Phase History Drift

The old `AGENTS.md` embedded a Phase 0-6 roadmap that drifted from the actual Phase 3D
implementation and the new R0-R6 direction. R0 replaces it with a stable constitution and
makes `ROADMAP.md` authoritative.

## TD-007: Polluted Source Archives

Shared source archives have repeatedly included ignored virtual environments, caches, and
local outputs. `.gitignore` cannot protect ad hoc zip tools.

R0 mitigation: `scripts/package-source.ps1` filters archive entries independently of Git.
The broader artifact retention policy remains an owner decision.

## TD-008: No Machine-Readable Benchmark Contract

Historical commands and Markdown results are useful but do not emit standardized manifests,
metrics files, or versioned summaries. They should not be retroactively presented as if they
did.

R1 response: finalize and implement the provisional contract in
`docs/experiments/EXPERIMENT_ARTIFACT_CONTRACT.md`.
