# Lenia and Godot Architecture Proposal

Status: RS-01 proposal only. No Lenia runtime or Godot project exists.

## Boundary and Ownership

```text
Python research plane                    Godot simulation plane
---------------------                    ----------------------
experiment orchestration    request      continuous cellular field
evolution / NEAT / optimizers ---------> CPU or GPU step backend
metrics and statistics                   visualization and perturbations
artifact contracts           <--------- phenotype telemetry and snapshots
candidate generation          result     deterministic replay
quality-diversity archives
```

Python should own research schedules, candidates, evidence aggregation, and immutable run
artifacts. Godot should own field stepping, GPU resources, interactive visualization,
perturbation tools, and replay. Neither side should silently redefine the other side's
parameters or metrics.

## First Protocol

Start with a short-lived local process and files, not a persistent service:

```text
request/
  command.json
  initial-field.npy
result/
  metrics.json
  optional-final-field.npy
  optional-snapshots/
```

`command.json` should include a protocol version, candidate ID, seed, grid shape, dtype,
channel layout, boundary rule, kernel/growth parameters, time step, step count, requested
metrics, input/output paths, and exact simulator identity. Array files should initially use
NumPy `.npy` with C-order little-endian `float32`, explicit shape, and named channel order.
This is easy for Python to inspect and sufficiently defined for a Godot reader. Whether
`.npy` remains the cross-engine format is an open owner decision.

Godot should write `metrics.json` atomically with status, timings, backend, device, numeric
summary, errors, and output hashes. Python should validate identity and hashes before using
the result as fitness. A later measured need may justify stdin/stdout IPC or a local socket;
RS-01 does not prescribe persistent networking.

## Deterministic CPU Reference First

The first Lenia implementation must be a small Python/NumPy CPU reference on 32x32 and
64x64 grids. It owns the mathematical contract: boundary behavior, kernel construction and
normalization, growth function, update order, clipping, time step, dtype, and snapshot
layout. Each fixture records parameters, seed, starting field, step count, and expected
metrics or field hash.

CPU repeatability should be checked independently before comparing a GPU backend. CPU/GPU
parity should measure:

- maximum absolute cell error;
- mean absolute cell error;
- total mass difference;
- centroid distance, with an explicit zero-mass convention.

Exact floating-point equality across CPU and GPU is not required. Numeric tolerances must
be selected from observed error on named fixtures and recorded as an owner decision; this
document does not invent them.

## Godot 4.7.1 Review Gate

The likely local engine is
`C:\dev\tools\Godot_v4.7.1-stable_mono_win64`; reviewed references target Godot 4.2.1.
Before creating a project, RS-03/L1 must explicitly verify:

- RenderingDevice and shader-language changes between 4.2.1 and 4.7.1;
- storage texture/buffer formats, workgroup sizing, dispatch limits, and barriers;
- headless RenderingDevice availability on supported Windows and CI hosts;
- C# versus GDScript ownership of resource creation, dispatch, and lifecycle;
- the cost of CPU-to-GPU upload, GPU-to-CPU telemetry/readback, and snapshots;
- synchronization points such as submit/sync that can serialize every step;
- deterministic fixture loading and automated parity output without a visible window;
- device loss, shader compilation failure, unsupported GPU, and CPU fallback reporting.

The reviewed compute example performs explicit buffer/texture setup, dispatch,
synchronization, and CPU readback. That is useful evidence of the risk boundary, not a
template to copy. The first GPU spike should keep visualization decoupled from simulation
stepping and avoid full-field readback every rendered frame unless profiling justifies it.

## Verification Layers

1. Unit-test kernel, growth, clipping, boundary, serialization, and phenotype metrics on CPU.
2. Re-run named CPU fixtures and confirm deterministic fields/metrics.
3. Run headless Godot fixtures against identical inputs.
4. Evaluate parity measures and recorded tolerances.
5. Measure step time, transfer time, synchronization time, and snapshot overhead.
6. Only then perform human-visible Godot review; automated parity does not prove visual
   quality, and visual review does not prove numerical parity.

## Failure and Artifact Discipline

Every evaluation must preserve its request, result, simulator/runtime identity, timing,
backend, deviations, and hashes. Timeouts, invalid fields, NaNs, zero mass, fragmentation,
and simulator crashes need explicit machine-readable outcomes. Evolution must not turn
infrastructure failure into an attractive fitness value.
