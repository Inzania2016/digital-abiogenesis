# Next Work Packet: L1

## Title

**L1: Godot GPU Lenia Parity Spike**

## Status

Proposed after completed RS-02. Not approved or started.

## Authoritative Packet

Use:

```text
docs/work-packets/L1_GODOT_GPU_LENIA_PARITY_SPIKE.md
```

## Goal

Measure whether a minimal Godot 4.7.1 compute backend reproduces the frozen RS-02 CPU
reference within owner-approved numeric tolerances and useful measured cost.

## Required Inputs

- canonical `lenia-single-channel-cpu-v1` configuration;
- committed 32x32 and 64x64 inputs and CPU outputs;
- `<f4`, C-order, `.npy`, periodic-boundary, and synchronous-update contracts;
- fixture hashes, mass, centroid, and CPU golden tolerance;
- explicit owner decisions on project placement, orchestration language, and GPU tolerance.

## Boundaries

L1 must remain a parity spike. It does not begin visual-quality claims, evolution,
optimization, multi-channel/Flow-Lenia, neural cellular automata, resources,
reproduction, or ecology. It must not change Bacterium-0, NEAT, or R1 contracts.

## Recommended Model

Use GPT-5.6 Sol High because shader semantics, GPU synchronization and transfer,
Godot API-version differences, headless execution, and numerical parity cross systems.
