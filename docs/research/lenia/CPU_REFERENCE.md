# Single-Channel Lenia CPU Reference

Status: RS-02 implemented and automatically verified on 2026-07-27.

## Scope and Non-goals

This is a finite, discrete, two-dimensional, single-channel NumPy reference for the standard
additive Lenia update. It exists to make equations, serialization, fixtures, and future
CPU/GPU parity auditable. It is not a continuous-space simulation, discovered organism,
stable morphology, biological-life claim, self-replicator, evolutionary system, Godot
backend, or GPU-equivalence result.

No multi-kernel, multi-channel, asymptotic, mass-conserving, reaction-diffusion, neural, or
extended Lenia variant is implemented.

## Mathematical and Operational Authority

Primary authority is Bert Wang-Chak Chan, “Lenia: Biology of Artificial Life,”
arXiv:1812.05433v3, *Complex Systems* 28(3), 2019, 251-286,
DOI `10.25088/ComplexSystems.28.3.251`.

The implementation freezes paper equations 7-13 and 15-18:

```text
potential U_t(x) = sum_n K(n) A_t(x + n)
growth G(u; mu, sigma) = 2 exp(-((u - mu)^2) / (2 sigma^2)) - 1
A_(t+dt)(x) = clip(A_t(x) + dt G(U_t(x)), 0, 1)
core(r) = (4 r (1-r))^alpha for 0 <= r < 1, else 0
shell(r; beta=[1]) = core(r)
K = shell / finite discrete shell sum
```

The paper notes that DFT/FFT convolution automatically gives periodic boundaries. RS-02
uses direct periodic convolution instead of FFT so accumulation order is visible.

The author's `Chakazul/Lenia` repository was inspected only to cross-check the operational
order at commit `adfc542939266de7f4bb7ebb552e8499701ee107`, file
`Python/old/Lenia.py`: normalize kernel, compute potential, map growth, add `dt` growth to
the unchanged current field, clip, optionally quantize, then replace state. The exact
checkout contains `LICENSE.md` with an MIT license, contrary to the packet's preliminary
“no license detected” note. The stricter no-copy boundary was retained.

## Frozen Configuration

`configs/lenia/lenia-single-channel-cpu-v1.json` defines:

| Field | Value |
| --- | --- |
| `config_id` | `lenia-single-channel-cpu-v1` |
| radius / alpha / beta | `5` / `4` / `[1.0]` |
| growth mean / width | `0.15` / `0.015` |
| `T` / `dt` | `10` / `0.1` |
| boundary | `periodic` |
| dtype | little-endian IEEE-754 float32, NumPy `<f4` |
| convolution | `direct-row-major` |

The immutable configuration rejects missing/unknown fields, nonfinite parameters, invalid
radius/alpha/sigma, any other beta, dtype, boundary, convolution, or disagreement between
`dt` and `1/T`. Its JSON serialization is deterministic.

## Boundary, State, and Update Contract

Fields are finite, C-contiguous, two-dimensional `<f4` arrays with values in `[0,1]`.
Inputs are never mutated. Every public step returns a new C-contiguous `<f4` array.

The entire current field is validated and remains unchanged while potential and growth are
calculated. Only then is `field + float32(dt) * growth` clipped to `[0,1]`. There is no
in-place partial update, soft clipping, state quantization, backend selection, parallelism,
SciPy, FFT, or GPU operation.

## Kernel and Direct Convolution

The stored kernel is an 11×11 `<f4` array representing offsets `-5..5` on each axis.
Euclidean distance divided by radius supplies `r`. The center is zero because `core(0)=0`;
offsets with `r >= 1` are zero. The discrete shell is normalized in float64, then cast once
to canonical `<f4`. The observed float64 accumulation of the stored float32 kernel is
`1.000000011175871`, within the `1e-6` normalization tolerance.

Convolution visits kernel rows, then columns, in deterministic order. For kernel offset
`(dy, dx)`, `numpy.roll(field, (-dy, -dx))` makes output `(y,x)` read input
`(y+dy,x+dx)` with toroidal wrapping. Each nonzero float32 weighted roll is added to a
float32 accumulator. A test-only nested scalar oracle independently implements the same
mathematical indexing and agrees within `rtol=0, atol=1e-6`.

## Conway Learning Anchor

`abiogenesis.lenia.conway.conway_step` is an independent, minimal periodic Game of Life
anchor. It accepts 2-D boolean or binary uint8 fields, sums the eight Moore neighbors, and
returns a synchronous non-mutating update. Stable block, period-two blinker, and toroidal
edge tests make synchronous and periodic semantics explicit. It is not an attempt to
emulate every Game of Life feature or reproduce GoL through Lenia parameters.

## Fixtures and Serialization

Committed NumPy `.npy` fixtures use `allow_pickle=False`, C order, and `<f4`:

| File | Project-authored recipe | Steps | SHA-256 |
| --- | --- | ---: | --- |
| `field_32_initial.npy` | centered Gaussian-like blob plus smaller offset blob | 0 | `b3d933cd8d42c01339062f0644db2d06244d13a83bf578aaee036e35743d2480` |
| `field_32_step1.npy` | expected output from the 32×32 input | 1 | `380c7181d6706d5d42d007fa8a79fceae6c42cfce28dbceb9cb4907cbed70c4f` |
| `field_64_initial.npy` | centered annulus plus asymmetric low-amplitude lobe | 0 | `9dc534a7cd0679e89269699b79bfe2f2cc34f33a36ce5455ab3a4558e04d791d` |
| `field_64_step10.npy` | expected output from the 64×64 input | 10 | `034398266a4f25c9bc49fc31ad6df6e3583f6a151880b82e1eb4cd8c3642afa9` |

The manifest records contract/config identity, boundary, convolution, role, recipe, shape,
dtype, step count, and hash. No random source, external pattern, “species,” or lifeform asset
is used. Goldens are regression records, not independent mathematical proof.

## Repeatability and Tolerances

In the verified Python 3.13.13, NumPy 2.4.4, Windows 11 AMD64 environment:

- repeated in-memory fixture generation was bitwise identical;
- regenerated `.npy` files and manifest were byte-identical;
- repeated steps from identical inputs were bitwise identical;
- both CLI replay outputs had the same SHA-256 as their committed goldens.

Across Python, NumPy, CPU, architecture, or operating-system changes, bitwise equality is
not promised. Golden numeric comparison uses `rtol=0, atol=1e-6`. Drift above that threshold
is a blocking investigation; goldens must not be silently refreshed.

## Mass and Toroidal Centroid

Mass is `sum(field)` with float64 accumulation.

Centroid uses a weighted circular mean independently for columns and rows, returned as
`(x,y)` in each axis's half-open index range. Empty fields or an axis whose normalized
circular resultant is at most `1e-12` return `None`; no arithmetic centroid is substituted.
This is a parity primitive, not phenotype identity.

## Commands

Generate or verify fixtures:

```powershell
.\.venv\Scripts\python.exe scripts\generate-lenia-fixtures.py
.\.venv\Scripts\python.exe scripts\generate-lenia-fixtures.py --check
```

Execute a fixed run:

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.lenia.reference `
  --config configs\lenia\lenia-single-channel-cpu-v1.json `
  --input tests\fixtures\lenia\field_64_initial.npy `
  --steps 10 `
  --output runs\lenia\field_64_step10.npy
```

Measure serial step cost:

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.lenia.reference `
  --config configs\lenia\lenia-single-channel-cpu-v1.json `
  --benchmark --sizes 32 64 --warmup 5 --steps 100
```

## Measured CPU Cost

One serial wall-clock measurement used five warmup steps and 100 measured steps per size on
an Intel Core i7-9700F, Windows 11 Home `10.0.26200`, Python 3.13.13, NumPy 2.4.4:

| Shape | Total | Per step |
| --- | ---: | ---: |
| 32×32 | 0.356740 s | 0.003567 s |
| 64×64 | 0.389294 s | 0.003893 s |

This is a local engineering measurement, not a cross-machine performance benchmark.

## Godot Parity Inputs

L1 must consume the exact configuration JSON, four fixture arrays, expected hashes,
`<f4`/C-order serialization, periodic indexing, row-major accumulation contract, synchronous
update order, and `rtol=0, atol=1e-6` CPU-golden comparison rule. CPU/GPU parity tolerances
for shader output remain an explicit L1 decision and need not equal the CPU-golden tolerance.

## Provenance and Limitations

The implementation was independently authored from the paper equations and project packet.
No external Python, JavaScript, Java, C++, pattern array, lifeform asset, shader, or Godot
source was copied or adapted. Direct float32 accumulation is intentionally slow and
auditable. FFT, GPU parity, visualization, phenotype interpretation, evolution, resources,
reproduction, and ecology remain future work.
