# Artificial Cell and Computational Metabolism Hypothesis

Status: conceptual research direction. Not a milestone, not an approved work packet, and
not authorization to implement anything.

Recorded: 2026-08-08.

## Purpose

This document records a research hypothesis so that it can be examined, criticized, and
either earned or discarded later. It is deliberately not a roadmap. `ROADMAP.md` owns the
R0-R6 ladder and `docs/research/lenia/IMPLEMENTATION_ROADMAP.md` owns the RS-01/L0-L7 side
track; neither is changed by this document.

The purpose is to state clearly:

- what the hypothesis claims;
- what it explicitly does not claim;
- which existing project questions it touches;
- what evidence would be required before any part of it is believed.

## Hypothesis

> Organism-like computation may emerge from populations of locally autonomous,
> energy-constrained artificial cells, rather than requiring that the organism or the
> intelligent agent be supplied as a primitive.

Two subordinate propositions make the hypothesis testable in principle:

1. **Resource-constrained selection.** If sensing, computation, signaling, maintenance,
   growth, repair, and reproduction each consume a finite local resource, then wasteful
   organization may become less viable through the simulated rules themselves, without an
   explicit efficiency term in any reward or fitness function. This is a
   computational-metabolism hypothesis, not demonstrated metabolism.
2. **Emergent boundary.** If no organism object is declared, then any persistent,
   self-maintaining, differentiated structure that appears is an experimental result to be
   measured rather than an assumption built into the simulation.

Both propositions are currently unsupported by any evidence in this repository.

## Relationship to Digital Abiogenesis

The project already runs a top-down track and a bottom-up track. This hypothesis names the
bottom-up track's long-term motivation without displacing the top-down one.

```text
TOP-DOWN                          BOTTOM-UP

defined organism                  local units
    |                                 |
policy / regulation               energy + interaction
    |                                 |
adaptation                        self-organization
    |                                 |
inheritance                       persistent structures
    |                                 |
ecology                           organism-like organization
                                      |
                                  adaptation / cognition?
```

Neither direction is currently assumed to be superior. The eventual value of keeping both
is that they can be compared under shared evidence standards: a defined organism gives a
controlled, measurable baseline, and an emergent structure — if one ever appears — must be
measured against that baseline rather than praised on its own terms.

The conceptual progression under investigation is:

```text
artificial cell -> local interaction -> persistent structure
    -> specialization / differentiation -> self-maintaining organization
    -> organism-like entity -> adaptation / learning -> possible higher-order cognition
```

Each arrow is a research question, not a predicted outcome. The project should expect the
chain to break at an early arrow and should record that honestly when it does.

## The Artificial Cell Concept

A future artificial cell would carry only enough state and rules to survive and interact
locally. Candidate ingredients, none of them fixed:

- local state;
- an energy or resource store;
- local sensing of a bounded neighborhood;
- local computation;
- local communication or signaling;
- maintenance requirements that must be paid to persist;
- optionally, local memory or adaptive state.

No concrete data structure, class, tensor layout, or update order is defined here, and
none should be until an approved packet requires one. Fixing a representation early is the
main way this direction could quietly become an implementation with a hypothesis attached
to it after the fact.

The load-bearing idea is that **the cell itself need not be intelligent**. Whatever
capability appears is expected to be a property of organization among many simple units,
not a capability installed in any single unit.

## Computational-Metabolism Hypothesis

Metabolism-inspired resource accounting is treated as a candidate experimental mechanism
rather than as another reward channel. Activities that might carry a cost include
maintenance, sensing, computation, signaling, movement or state change, growth, repair,
and reproduction. A resource ledger must causally change an entity's future reachable
state and ability to maintain, sense, compute, signal, repair, grow, or reproduce inside
the simulated world. By contrast, reward shaping adds or subtracts an evaluator's score
because a behavior is preferred.

The governing principle:

> Where possible, make computational efficiency a consequence of viability constraints
> rather than an externally awarded efficiency score.

A structure that performs unnecessary work should spend more resources and become less
viable because of the simulated resource rules, not because an `efficiency_bonus` term was
added to a reward function. Rewarding efficiency directly makes efficiency a target that
can be gamed; charging for work can make it a constraint that changes later viability. This
principle does not establish that efficient behavior will emerge or that any chosen costs
are biologically correct.

This has an obvious failure mode that the project should watch for: a cost table is itself
a designed object, and different tables may produce different evolutionary outcomes. An
arbitrary table tuned toward a desired behavior can become reward shaping in disguise.
Cost structures will therefore need the same treatment as scenario definitions —
preregistered, reported, and tested for sensitivity across deliberately varied tables, as
recorded in OQ-027.

No numeric costs, rates, budgets, or conservation rules are proposed here. Inventing
plausible-looking energy values before there is a substrate would be premature precision.
Nor does subtracting an energy scalar demonstrate metabolism. That claim would require an
operationally defined process involving some combination of resource acquisition,
transformation, storage of usable capacity, expenditure on maintenance, work, or
construction, and depletion or waste. Until then, this document concerns resource-
constrained artificial cells and a computational-metabolism hypothesis.

## Locality and Self-Organization

The direction prefers investigating local interaction over assuming centralized control:

- cells primarily observe bounded local neighborhoods;
- signals may propagate through neighbors rather than through a broadcast channel;
- specialization may depend on local conditions;
- global behavior should not automatically require a global controller.

This is a research preference, not a retroactive architecture mandate. Global controllers
remain legitimate in existing and future comparative experiments — L4's global evolved
controller is explicitly a valid comparison arm, and the value of a locality claim depends
on having a centralized control to measure it against.

## Emergent Organism Boundary

Existing experiments define the organism before the simulation begins. Bacterium-0 is one
organism because the environment says so. This direction allows the alternative: that the
boundary is a measurement, not a declaration.

Open questions in this area:

- When is a collection of cells one organism rather than several, or none?
- Can persistent structures arise without an explicitly declared organism object?
- Can such structures specialize internally?
- Can they maintain or repair themselves after damage?
- Can reproduction occur at the cell level, the collective level, or both?
- Can an organization persist despite complete turnover of its constituent cells?

These connect directly to unresolved Lenia-side identity questions. OQ-018 (identity
through motion, deformation, split, merge, and regeneration) and OQ-019 (what constitutes
death, and when fragmentation yields multiple entities rather than one damaged entity) are
the same problem reached from the continuous-field side. Artificial-cell claims about
boundary, persistence, split, merge, death, and reproduction must use the identity and
death conventions eventually settled by L2. OQ-029 records the dependency; it does not
establish a competing identity convention.

## Differentiation and Development

A future system might grow or organize its structure rather than having that structure
specified. The question is whether initially similar cells can adopt different functional
roles based on local state, environment, history, or signaling.

Roles such as "memory cell", "sensor cell", or "planning cell" are examples of what
differentiation could look like if it occurred. They are not an implementation
specification, and assigning them in advance would answer the research question by
construction.

Differentiation is also one of the easiest properties to see where none exists. A
measurable definition — a persistent, reproducible difference in behavior or state between
cells with the same rules, attributable to local history rather than to initialization
noise — is a prerequisite for using the word at all.

## Inheritance, Evolution, and Ecology

The project's existing emphasis on measurable inheritance and selection carries over. What
this direction adds is the recognition that biological evolution is not equivalent to
optimizing a single static benchmark.

Long-term experiments in this direction may need variation, inheritance, competition,
cooperation, resource scarcity, environmental change, ecological interaction, neutral or
non-beneficial variation, and historical path dependence. Stochastic evolutionary dynamics
and reproducibility are compatible: a deterministic experiment seed can define one
replayable stochastic history containing mutation, neutral variation, ecological
randomness, historical contingency, births, deaths, and resource fluctuations, while
different seeds sample alternative histories. How those histories should be seeded,
replicated, and recorded remains unresolved in OQ-031.

No evolutionary algorithm, mutation operator, selection scheme, or population model is
designed in this document.

## Relationship to Bacterium-0

Bacterium-0 is unaffected. It remains conceptually frozen as the legacy benchmark organism,
its behavior is unchanged, and the `bacterium-0-v1` contract, scenarios, seeds, budgets,
and frozen R1 evidence are untouched by this hypothesis.

Its role in this direction is as the control. Bacterium-0 is the clearest case of a
declared organism with declared sensing, declared actions, and an external reward: exactly
the assumption set this hypothesis proposes to eventually relax. If an emergent structure
is ever claimed to do something interesting, a Bacterium-0-style defined organism under
matched conditions is the honest thing to compare it against.

The hypothesis also gives R2 homeostasis a question to keep in view: whether regulation of
internal variables is best expressed as an organism-level policy objective or as a
consequence of local viability constraints. R2 is not obliged to answer it.

## Relationship to Lenia

The Lenia side track is the closest existing substrate to this hypothesis, and the nearest
thing the project has to locally governed dynamics with no declared organism. RS-02's
completed CPU reference already exhibits the relevant shape: a single local rule applied
uniformly, with any persistent structure being a consequence rather than a declaration.

What Lenia currently lacks relative to the hypothesis is resource accounting. Its update is
a local growth rule, not a metabolism; nothing is spent, and nothing becomes unviable for
having done unnecessary work. L7 (resources, reproduction, ecology) is where that gap would
first be addressed, and L2 (phenotype measurement) owns the identity conventions any
boundary claim would depend on.

This document changes nothing about Lenia. The equations, configuration, fixtures, hashes,
and tolerances frozen by RS-02 are untouched, L2-L7 remain unstarted, and the proposed L1
packet remains a **GPU numerical parity spike** — not a visualization task and not an
artificial-cell implementation task.

## Evidence Requirements

The project's `evidence before narrative` pillar applies with unusual force here.
Artificial-life systems are especially vulnerable to anthropomorphic interpretation,
because a field of moving pixels will reliably look purposeful to a human observer.

Before any of the following words are used as a claim in this project, it needs an
operational definition, a measurement, a control, and reproduction across seeds:

- organism;
- cooperation;
- specialization;
- memory;
- repair;
- adaptation;
- learning.

Specific standards that should apply to any future work in this direction:

- A visualization that looks suggestive is not evidence. Renderings may motivate a
  measurement; they may never substitute for one.
- Every structural claim needs a stated negative: what observation would have falsified it.
- Persistence claims need a control showing the structure does not appear under a matched
  condition that should not produce it — for example under shuffled neighborhoods, removed
  signaling, or absent resource constraint.
- Energetic claims need the cost table reported alongside the result, since the result is
  partly a property of the cost table.
- Mixed and negative findings are preserved, as everywhere else in this project.

## Major Unknowns

- Whether energetic viability alone produces any useful selection pressure, or whether it
  merely produces extinction and stasis.
- Whether persistent structures can arise at all in a system with maintenance costs and no
  declared organism.
- Whether an organism boundary can be defined non-arbitrarily, or whether every candidate
  definition turns out to encode the answer it was meant to measure.
- Whether cell-level and collective-level reproduction are alternatives, complements, or
  the same mechanism observed at two scales.
- Whether any of this is computationally affordable on the project's local hardware at a
  population size large enough to be interesting.
- Whether the appropriate substrate is discrete entities, a continuous field, or something
  else entirely.
- How stochastic evolutionary histories should be seeded, replicated, and recorded under
  the project's reproducibility contract.

## Non-Claims and Non-Goals

This document does not claim, and no future work should be read as claiming without
evidence, that this architecture will produce:

- intelligence;
- consciousness, sentience, self-awareness, or subjective experience;
- biological life;
- superior AI, or an advantage over any existing method.

It also does not:

- authorize implementation of artificial cells, metabolism, reproduction, ecology, neural
  cellular automata, or new learning algorithms;
- add, reorder, replace, or reprioritize any R0-R6 milestone;
- change the L0-L7 side-track ladder or begin L2-L7;
- expand the proposed L1 Godot GPU parity spike;
- modify Bacterium-0, benchmark contracts, Lenia equations, or committed fixtures;
- prescribe a substrate, data structure, energy value, or cost table;
- ban global controllers from comparative experiments.

## Substrate Independence

The eventual substrate is not assumed to be Python objects, a neural network, Lenia,
cellular automata, silicon nanotechnology, biological cells, or molecular computing. The
current software workbench is an experimental platform, and the hypothesis concerns
organization and resource-constrained local computation rather than any particular physical
realization.

This matters practically: an early implementation choice should be treated as one probe of
the hypothesis, not as the hypothesis itself. The first substrate must be chosen later
against explicit probe requirements, not merely because one implementation is convenient.

## Candidate Future Research Questions

Recorded for later selection. None is approved, scheduled, or scoped.

- What is the minimum cell state that still permits any persistent multi-cell structure?
- Does a maintenance cost alone produce structure, or is a spatial resource gradient
  required?
- Under a fixed cost table, does any organization arise that outlasts the lifetime of its
  constituent cells?
- Can a structure recover measured state after localized damage, and does recovery depend
  on signaling?
- Do initially identical cells develop reproducible, locally attributable behavioral
  differences?
- Does removing signaling while holding costs fixed measurably degrade a persistent
  structure?
- How do outcomes vary across several deliberately different cost tables, and which
  conclusions survive all of them?
- Under matched compute budgets, how does an emergent structure compare against a
  Bacterium-0-style defined organism on a shared task?
- Can Lenia's existing local rule be extended with explicit resource accounting without
  losing its deterministic reference contract?

## Related Documents

- `VISION.md` — north star, design pillars, and evidence standards.
- `ROADMAP.md` — the authoritative R0-R6 ladder.
- `OPEN_QUESTIONS.md` — OQ-018, OQ-019, and OQ-025 through OQ-031.
- `docs/research/lenia/IMPLEMENTATION_ROADMAP.md` — the RS-01/L0-L7 side track.
- `docs/research/lenia/CPU_REFERENCE.md` — the frozen deterministic Lenia CPU reference.
- `COMPARATIVE_REFERENCES.md` — reviewed external systems with related mechanisms.
