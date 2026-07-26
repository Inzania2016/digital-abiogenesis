# Technical Debt Inventory

Last reviewed: 2026-07-26

This file records debt without authorizing broad R0 refactoring. Priority should be set by
future work packets and evidence needs.

## TD-001: Oversized Evaluation Module

`src/abiogenesis/training/evaluate_q_learning.py` is roughly 900 lines and owns too many
concerns: training invocation, evaluation loops, reward shaping, variant registration,
multi-seed aggregation, formatting, and CLI parsing. This makes benchmark contracts harder
to isolate and increases the risk of inconsistent variants.

R1B adds a separate benchmark control layer around public evaluator/training seams rather
than refactoring this module. Likely future direction: characterize and extract shared
evaluation responsibilities after R1 evidence establishes which seams need to remain
stable.

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

R1B mitigation: the benchmark catalog and resolved manifest provide an explicit versioned
source for canonical runs. Legacy exploratory CLIs still retain distributed configuration.

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

## TD-008: Machine-Readable Benchmark Contract Is New and Unaudited at Scale

Historical commands and Markdown results remain useful but do not emit standardized
manifests, metrics files, or versioned summaries. They should not be retroactively
presented as if they did.

R1B implements the v1 writer and validator. R1C still needs to execute and audit canonical
quick/full evidence, measure cost, and expose any scale or usability problems.

## TD-009: Benchmark and Legacy Evaluation Paths Share Behavior Indirectly

The benchmark runner deliberately calls existing public training and evaluation functions
instead of extracting common evaluator internals. This minimizes R1B behavior risk but
leaves two orchestration paths that could drift.

Likely future direction: retain deterministic characterization tests and consolidate only
after the v1 evidence run identifies a concrete maintenance need.

## TD-010: Adjacent Replicate Roots Overlap Evaluation Windows

The preserved `root + 100000` episode-seed derivation means adjacent replicate roots
produce overlapping evaluation episode seeds. Benchmark v1 documents this limitation and
must not imply independent worlds.

Likely future direction: decide after R1C whether a future benchmark version should use
non-overlapping windows. Do not change v1 seed semantics in place.

## TD-011: Experimental Evaluation Loops Duplicate Legacy Metric Collection

The NEAT raw-reward evaluator deliberately avoids refactoring the oversized legacy
evaluator, but both collect similar episode diagnostics. This minimizes RS-01 behavior
risk while creating another path that could drift.

Likely future direction: use characterization evidence to extract a policy-neutral episode
recorder only when a narrow packet can prove semantic equivalence.

## TD-012: Winning Genomes Use Trusted-Local Pickle

NEAT-Python genomes are saved with pickle for exact reload. Pickle is Python/version
sensitive and unsafe for untrusted input. The same run also stores portable network JSON,
effective configuration, versions, and hashes, but the JSON path is not yet a native
Digital Abiogenesis loader.

Likely future direction: keep generated pickles ignored; evaluate a safe project-owned
network loader only if curated or cross-version policy artifacts are approved.

## TD-013: Neuroevolution Reproducibility Is Bounded, Not Bit-Exact Across Platforms

RS-01 seeds Python, NumPy, NEAT, environment resets, and serial ordering. Floating-point,
dependency, and platform changes may still alter evolution. A dirty source run is labeled
partial.

Likely future direction: repeat clean-source experiments before research claims, record
dependency locks when justified, and test Windows parallelism before adding workers.

## TD-014: Future Python/Godot Boundary Is Unimplemented

The Lenia architecture defines a file-first protocol and CPU/GPU parity measures, but
field serialization performance, Godot 4.7.1 APIs, headless compute, synchronization, and
numeric tolerances remain unverified.

Likely future direction: implement L0 CPU reference before selecting or building the L1
Godot boundary.
