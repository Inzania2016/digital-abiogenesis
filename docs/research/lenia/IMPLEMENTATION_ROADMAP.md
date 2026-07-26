# Lenia Research Side-Track Ladder

This ladder is subordinate to the main R0-R6 roadmap. Advancing a side-track stage requires
a separately approved work packet.

## RS-01 — NEAT Feasibility on Bacterium-0

- **Question:** Can optional NEAT plumbing work in the understood legacy environment?
- **Deliverables:** feed-forward adapter, raw-reward evaluator, serial trainer, provisional
  artifacts/validator, trusted-local ASCII replay, provenance and architecture documents.
- **Evidence/exit:** focused tests and a bounded run validate; winner reload selects an
  action; no existing behavior or canonical contract changes.
- **Risks:** accidental benchmark promotion, pickle safety, weak one-run interpretation.
- **Model:** GPT-5.6 Sol High; cross-cutting reproducibility and architecture justified High.

## L0 — Conway-to-Lenia CPU Reference

- **Question:** Can the continuous update be specified and reproduced without a renderer?
- **Deliverables:** NumPy CPU reference, 32x32/64x64 fixtures, explicit math/serialization,
  deterministic tests, timing baseline.
- **Evidence/exit:** repeated fixtures match; kernel mass, update rules, and invariants have
  tests; no unexplained NaNs or platform drift.
- **Risks:** ambiguous equations, boundary/order mistakes, reference overengineering.
- **Model:** GPT-5.6 Sol Medium for the bounded implementation; High if reconciling multiple
  conflicting mathematical sources or unexplained numerical drift.

## L1 — Godot GPU Lenia Parity Spike

- **Question:** Can Godot 4.7.1 reproduce the CPU contract with useful throughput?
- **Deliverables:** minimal headless-capable project, compute backend, fixture protocol,
  parity/timing report, documented 4.2.1-to-4.7.1 API review.
- **Evidence/exit:** named fixtures meet owner-approved error tolerances; transfer,
  synchronization, and step costs are measured; failures are attributable.
- **Risks:** driver/API differences, hidden synchronization, readback cost, unavailable
  headless compute.
- **Model:** GPT-5.6 Sol High for shader/API/parity reasoning; Medium only for narrow
  follow-up fixes after the contract is stable.

## L2 — Phenotype Measurement

- **Question:** Which measurements describe persistent, moving, damaged, or fragmented forms?
- **Deliverables:** mass, centroid, velocity, component, symmetry/rotation, and regeneration
  definitions; CPU/GPU telemetry parity; edge-case fixtures.
- **Evidence/exit:** metrics are deterministic, unit-tested, and meaningful on preregistered
  examples; identity/death conventions are owner-approved.
- **Risks:** anthropomorphic labels, unstable component tracking, metric gaming.
- **Model:** GPT-5.6 Sol High for metric semantics and edge cases; Medium for implementation
  after definitions are fixed.

## L3 — Numerical Lenia Parameter Evolution

- **Question:** Can a bounded numerical optimizer find reproducible parameter sets for an
  explicit phenotype objective?
- **Deliverables:** random baseline, likely CMA-ES or justified alternative, candidate
  contract, budget/cost accounting, holdout perturbations.
- **Evidence/exit:** optimizer exceeds its baseline across approved seeds without invalid
  simulation exploitation; artifacts replay.
- **Risks:** objective hacking, collapse, excessive evaluations, overfitting.
- **Model:** GPT-5.6 Sol High for optimizer/experimental design; Medium for a preregistered
  runner once choices are closed.

## L4 — NEAT-Controlled Lenia

- **Question:** Can a global evolved controller improve adaptation under perturbation?
- **Deliverables:** bounded telemetry/action interface, feed-forward baseline, fixed-policy
  controls, artifact/replay support, ablations.
- **Evidence/exit:** holdout adaptation evidence exceeds appropriate fixed and numerical
  controls at recorded cost.
- **Risks:** hidden state leakage, unstable control cadence, unfair baselines, opaque policy.
- **Model:** GPT-5.6 Sol High.

## L5 — Shared Local Neural Rule

- **Question:** Can one evolved local rule sustain coherent field-level behavior?
- **Deliverables:** local observation/update contract, CPU reference, GPU parity,
  mathematical-Lenia control, bounded evolutionary run.
- **Evidence/exit:** reproducible coherent behavior survives holdout perturbations and is not
  an artifact of rendering, precision, or a single initial field.
- **Risks:** neural cellular-automata scope explosion, GPU cost, uninterpretable failure.
- **Model:** GPT-5.6 Sol High; use the highest available reasoning for initial design/parity.

## L6 — Quality-Diversity Archive

- **Question:** Can validated descriptors reveal multiple high-quality behavioral niches?
- **Deliverables:** descriptor decision, archive algorithm, coverage/quality statistics,
  lineage and replayable elites.
- **Evidence/exit:** archive reproducibly fills distinct valid niches and survives descriptor
  sensitivity checks.
- **Risks:** arbitrary bins, redundant descriptors, archive artifacts mistaken for ecology.
- **Model:** GPT-5.6 Sol High.

## L7 — Resources, Reproduction, and Ecology

- **Question:** What population effects arise when validated phenotypes consume resources,
  reproduce, vary, and interact?
- **Deliverables:** explicit resource/reproduction/death rules, inheritance and lineage
  records, population controls, ecological scenarios.
- **Evidence/exit:** controlled multi-generation evidence distinguishes inheritance and
  interaction effects from independent dynamics.
- **Risks:** uncontrolled complexity, narrative overclaiming, compute growth, lineage bugs.
- **Model:** GPT-5.6 Sol High; split into narrow High-design and Medium-implementation packets.
