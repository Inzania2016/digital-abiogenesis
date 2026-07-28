# RS-02: Conway-to-Lenia CPU Reference

Status: completed and automatically verified 2026-07-27; awaiting owner commit approval.

## Goal

Implement a deterministic, headless NumPy reference that makes the initial Lenia
mathematics and field format testable before any Godot or GPU work.

## In Scope

- Define boundary, kernel, growth, time-step, clipping, dtype, and update-order contracts.
- Implement the smallest Conway-to-continuous-to-Lenia learning sequence needed to audit
  the final update.
- Add deterministic 32x32 and 64x64 fixtures and `.npy` serialization.
- Test kernel normalization, updates, invalid values, repeatability, mass, and centroid.
- Record exact source provenance and benchmark CPU step cost.

## Out of Scope

- Godot, shaders, GPU dependencies, rendering claims, NEAT or other optimization, phenotype
  search, neural cellular automata, reproduction, resources, and ecology.

## Likely Files

```text
src/abiogenesis/lenia/
configs/lenia/
tests/test_lenia_*.py
docs/research/lenia/CPU_REFERENCE.md
docs/verification/<date>-rs-02.md
```

## Acceptance Criteria

- Equations and implementation order are explicit and source-grounded.
- Same fixture, seed, dtype, and parameters reproduce the same CPU result locally.
- 32x32 and 64x64 fixture tests pass without a renderer.
- No existing Bacterium-0 behavior or R1 contract changes.
- Outputs are finite or fail with attributable validation errors.
- The result defines inputs for, but does not begin, a Godot parity spike.

## Verification Commands

```powershell
.\scripts\check.ps1
.\scripts\test.ps1 tests -k lenia -q
git diff --check
git status --short
```

## Frozen RS-02 Decisions

- Mathematical authority: Chan paper arXiv `1812.05433v3`.
- Periodic boundary and direct serial row-major convolution.
- Runtime and persisted state/kernel dtype: `<f4`.
- Project-authored analytic 32×32 and 64×64 fixtures are source-controlled.
- Same-environment outputs are bitwise repeatable; cross-environment goldens use
  `rtol=0, atol=1e-6` without a bitwise promise.

## Recommended Model

GPT-5.6 Sol Medium is sufficient once the equations and decisions are fixed. Use High for
the initial packet if sources disagree, the update order remains ambiguous, or numerical
drift requires deeper reconciliation.
