# L1: Godot GPU Lenia Parity Spike

Status: proposed next side-track packet; not approved or started.

## Goal

Determine whether Godot 4.7.1 can reproduce the frozen RS-02 CPU update within explicit
numeric tolerances and useful measured cost.

## Required Inputs

- `configs/lenia/lenia-single-channel-cpu-v1.json`
- all files and hashes in `tests/fixtures/lenia/manifest.json`
- periodic boundary and synchronous update order from `CPU_REFERENCE.md`
- C-contiguous little-endian float32 field serialization
- CPU golden comparison rule `rtol=0, atol=1e-6`
- mass and toroidal-centroid primitives

## In Scope

- Review RenderingDevice and compute-shader differences from reference Godot 4.2.1 projects
  to the local Godot 4.7.1 Mono target.
- Create the smallest headless-capable simulation/compute project.
- Load the committed fixtures and execute the exact single-channel update.
- Measure maximum/mean cell error, mass difference, centroid difference, upload, dispatch,
  synchronization, readback, and total step time.
- Record device/runtime/shader identity and attributable failures.

## Out of Scope

Visualization quality claims, NEAT, numerical optimization, multi-channel/Flow-Lenia,
neural cellular automata, resources, reproduction, and ecology.

## Owner Decisions Required

- Repository versus sibling-project placement.
- C# versus GDScript orchestration.
- Owner-approved CPU/GPU parity tolerances.
- Headless fallback policy when compute is unavailable.

## Acceptance Boundary

Automated shader parity does not verify visual quality. A visible Godot review, if later
requested, remains a separate human-verification boundary.

## Recommended Model

Use GPT-5.6 Sol High for the initial packet because shader semantics, synchronization,
transfer cost, API-version changes, headless behavior, and numerical parity cross several
systems. Medium is suitable only for narrow follow-ups after the backend contract is stable.
