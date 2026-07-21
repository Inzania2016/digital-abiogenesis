# Digital Abiogenesis: Project Context

This project explores primitive artificial life through small, testable software organisms.

The first goal is not intelligence in the human sense.

The first goal is adaptive survival behavior.

We start with a tiny grid-world creature called Bacterium-0. It lives in a simple world with food, poison, energy, and death. It should begin as a random actor, then become a learning actor.

The project should grow through experiments, not declarations.

A behavior counts only if it can be measured.

## Design Premise

A useful primitive AI organism needs:

- an environment
- sensors
- actions
- internal state
- consequences
- memory or adaptation
- measurable improvement

The project deliberately starts below language.

Language may be added later, but only after the creature can behave.

## First Research Question

Can a simple software organism improve survival behavior in a toy world through repeated experience?

## Initial Success Criteria

Bacterium-0 succeeds when:

- the environment runs
- the random baseline runs
- metrics are recorded
- a learning agent can eventually outperform the baseline

## Long-Term Direction

Possible future branches:

- reinforcement learning
- evolutionary algorithms
- memory systems
- multi-agent ecology
- symbolic planning
- local LLM-assisted narration or reasoning
- artificial chemistry
- cellular automata
- neural cellular automata
- genetic programming

## Current Visualization

The pygame observation window is renderer-only. It can draw Bacterium-0,
food, and poison with optional PNG sprites from `assets/sprites/`, while
falling back to the original shape-based drawing when sprites are disabled or
missing. Rendering must not change environment rules, rewards, encoders,
training, or evaluation behavior.

## Current Memory Direction

Phase 3D adds directional novelty for tabular learning. The `novelty-scent`
encoder keeps conflict-scent features and appends north/south/east/west
novelty buckets: blocked, visited, or unvisited. This tells the table-brain
which neighboring directions may lead somewhere new, unlike Phase 3C loop
detection, which only says that a cycle is happening. Environment movement and
default reward values remain unchanged.
