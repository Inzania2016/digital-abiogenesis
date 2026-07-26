# RS-02: Conway-to-Lenia CPU Reference

Status: next active packet after completed R1C; not executed.

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
.\.venv\Scripts\python.exe -m pytest tests/test_lenia_*.py -q
git diff --check
git status --short
```

## Open Owner Decisions

- Exact mathematical source/version to freeze.
- Boundary rule and internal dtype.
- Initial fixture set and whether small `.npy` fixtures may be committed.
- Numeric repeatability expectations across supported Python/NumPy versions.

## Recommended Model

GPT-5.6 Sol Medium is sufficient once the equations and decisions are fixed. Use High for
the initial packet if sources disagree, the update order remains ambiguous, or numerical
drift requires deeper reconciliation.
