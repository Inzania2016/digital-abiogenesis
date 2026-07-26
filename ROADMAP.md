# Research Roadmap

This roadmap owns the R0-R6 research ladder. Milestones are evidence gates, not calendar
promises. A later milestone may be refined into smaller work packets without changing its
research question.

## R0: Rebaseline and Engineering Retool

- **Research question:** Can the existing project be made durable and navigable without
  changing the legacy organism?
- **Intended deliverables:** authoritative control-plane documents, Python 3.13 runtime
  contract, deterministic development scripts, quality gates, architecture/debt inventory,
  artifact-contract design, concise README, and Obsidian navigation.
- **Exit criteria:** documents agree; bootstrap/check/benchmark outcomes are recorded
  honestly; historical evidence and renderer remain intact; no intentional behavior change.
- **Major risks:** documentation drift, accidental runtime edits, lost historical findings,
  and packaging local artifacts.

## R1: Bacterium-0 Benchmark v1

- **Research question:** What stable scenarios and artifact schema make Bacterium-0 a
  reproducible legacy benchmark?
- **Intended deliverables:** named quick/full benchmark scenarios, versioned configuration,
  standardized run artifacts, baseline comparisons, and benchmark documentation.
- **Exit criteria:** canonical scenarios run across approved seeds, emit contract-compliant
  artifacts, and reproduce documented metrics within defined interpretation rules.
- **Major risks:** overfitting scenarios, excessive runtime, ambiguous seed policy, and
  retrofitting old results as if they used the new contract.

## R2: Bacterium-1 Homeostasis

- **Research question:** Can an organism regulate explicit internal needs under pressure?
- **Intended deliverables:** Bacterium-1 specification, internal state and sensing, fair
  Bacterium-0 comparison, regulation metrics, tests, and visualization overlays.
- **Exit criteria:** at least one preregistered scenario shows reproducible regulation of a
  viability variable beyond an appropriate baseline.
- **Major risks:** reward proxies masquerading as regulation, too many internal variables,
  and unfair comparisons.

## R3: Adaptation Under Environmental Change

- **Research question:** Can behavior adjust when resource or hazard regimes change within
  or between lifetimes?
- **Intended deliverables:** explicit change regimes, adaptation-rate and recovery metrics,
  controls, and repeatable comparisons.
- **Exit criteria:** measured post-change adjustment outperforms a fixed-policy/control
  baseline across approved seeds.
- **Major risks:** data leakage, nonstationarity hiding poor performance, and confusing
  exploration with adaptation.

## R4: Reproduction and Inheritance

- **Research question:** Can useful variation propagate across generations under selection?
- **Intended deliverables:** reproduction rules, inherited parameters/traits, mutation,
  lineage records, population metrics, and deterministic small-population experiments.
- **Exit criteria:** lineage-aware evidence shows a heritable trait distribution and fitness
  changing across generations under defined selection pressure.
- **Major risks:** uncontrolled randomness, trivial fitness hacks, population collapse, and
  irreproducible lineage state.

## R5: Ecology and Emergence

- **Research question:** What measurable population-level behaviors arise from organism and
  resource interactions?
- **Intended deliverables:** multi-organism environment, competition/cooperation scenarios,
  individual and population metrics, and observation tooling.
- **Exit criteria:** interactions measurably alter both individual and population outcomes,
  with controls distinguishing interaction effects from independent behavior.
- **Major risks:** combinatorial complexity, unstable simulations, anthropomorphic stories,
  and insufficient causal controls.

## R6: Comparative Intelligence Architectures

- **Research question:** Which architectures best support adaptation, regulation, and
  inheritance under the established benchmark suite?
- **Intended deliverables:** comparable tabular, evolutionary, and other justified local
  architectures; shared interfaces; cost/complexity metrics; and evidence-based synthesis.
- **Exit criteria:** multiple architectures are evaluated under the same contracts with
  transparent capability, cost, and failure tradeoffs.
- **Major risks:** incompatible comparisons, premature neural/LLM scope, compute growth,
  and mistaking complexity for intelligence.

## Isolated Research Side Tracks

RS-01 proves optional neuroevolution plumbing on Bacterium-0 and proposes a CPU-first
Lenia/Godot path. It does not replace or advance the R0-R6 mainline. The separate
RS-01/L0-L7 research ladder, evidence gates, and model recommendations are maintained in
`docs/research/lenia/IMPLEMENTATION_ROADMAP.md`; any stage requires its own approved packet.
