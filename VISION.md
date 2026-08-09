# Vision

## North Star

> Build a minimal artificial-life workbench that can demonstrate, measure, and visualize
> adaptive behavior across an organism's lifetime and across generations.

The project begins with small organisms and controlled worlds because mechanisms should
remain inspectable and claims should remain testable. Bacterium-0 is the legacy benchmark,
not the final architecture.

## Working Definitions

- **Adaptation**: a reproducible change in policy or behavior that improves or materially
  changes measured outcomes under defined conditions, within a lifetime or across trials.
- **Homeostasis**: regulation of explicit internal variables around viable ranges despite
  environmental pressure; survival time alone is not sufficient evidence.
- **Inheritance**: transfer of specified traits, parameters, or structures from parent to
  offspring with measurable variation and consequences across generations.
- **Ecology**: interacting organisms and resources whose individual actions alter the
  conditions and outcomes of other organisms or populations.

These are engineering definitions for experiments. The project is not claiming
consciousness, sentience, self-awareness, subjective experience, or biological life.

## Design Pillars

1. **Inspectable organisms**: begin with mechanisms small enough to understand.
2. **Separation of concerns**: keep world dynamics, policy, sensing, metrics, and rendering
   independently testable.
3. **Reproducible experiments**: use explicit configuration, deterministic seeds, exact
   commands, and preserved artifacts.
4. **Evidence before narrative**: behavioral claims require fair comparisons and metrics.
5. **Honest history**: retain negative, mixed, and failed results.
6. **Progressive complexity**: earn homeostasis, inheritance, and ecology before adding
   larger intelligence architectures.
7. **Observable behavior**: combine quantitative metrics with a renderer that cannot alter
   the experiment.
8. **Do not assume the organism boundary**: controlled benchmarks may define an organism
   explicitly, but later research should permit organism-like structures to emerge from
   lower-level interacting units where that is experimentally justified. Where no organism
   is declared, the boundary is a measurement rather than an assumption.
9. **Energetic accountability**: where appropriate, sensing, computation, communication,
   maintenance, growth, repair, and reproduction should carry explicit resource
   consequences rather than depending exclusively on external task reward. Prefer letting
   viability create selection pressure over adding an efficiency term to a reward function.

Pillars 8 and 9 describe a research direction, not a retroactive mandate. They do not
change Bacterium-0, the benchmark contracts, or any active milestone. The reasoning,
unknowns, and explicit non-claims are recorded in
`docs/research/alife/ARTIFICIAL_CELL_HYPOTHESIS.md`.

## Evidence Standards

- Every experiment answers a stated question and records its configuration and seed set.
- Comparisons use matched conditions and distinguish training from evaluation.
- Claims identify which metrics improved, regressed, or remained mixed.
- Important results should reproduce across multiple seeds before becoming benchmark
  expectations.
- Human-visible observations are labeled separately from automated results.
- Missing artifacts, failed commands, and contradictory results remain visible.
- Words such as organism, cooperation, specialization, memory, repair, adaptation, and
  learning require an operational definition and a measurement before use as a claim. A
  suggestive visualization may motivate a measurement but never replaces one.

## Non-goals

- Building a chatbot or treating language as the organism.
- Claiming consciousness, sentience, self-awareness, or biological life.
- Adding neural networks, LLMs, cloud services, or multi-agent frameworks before the
  relevant research milestone justifies them.
- Simulating biology at high fidelity.
- Building a large UI or general-purpose RL framework.
- Optimizing for impressive demos at the expense of reproducibility or interpretability.
