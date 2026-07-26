# Next Work Packet: RS-02

## Title

**RS-02: Conway-to-Lenia CPU Reference**

## Status

Active next packet after completed R1C. Not started.

## Authoritative Packet

Use:

```text
docs/work-packets/RS-02_CONWAY_TO_LENIA_CPU_REFERENCE.md
```

## Goal

Implement a deterministic, headless NumPy reference that makes the initial
Lenia mathematics and field format testable before any Godot or GPU work.

## Required Decisions Before Implementation

- exact mathematical source and version;
- boundary rule and internal dtype;
- update order and clipping semantics;
- initial 32x32 and 64x64 fixtures;
- whether small `.npy` fixtures may be committed;
- numerical repeatability expectations across supported Python/NumPy versions.

## Boundaries

RS-02 does not begin Godot, shaders, GPU work, rendering claims, optimization,
phenotype search, reproduction, resources, or ecology. It must not change
Bacterium-0 behavior or the R1 artifact contract.

## Recommended Model

Use GPT-5.6 Sol Medium after the equations and decisions are fixed. Escalate to
High only if sources conflict, update ordering is ambiguous, or numerical
parity fixtures expose unresolved interpretation.
