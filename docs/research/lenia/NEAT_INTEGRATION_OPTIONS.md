# Ranked Neuroevolution and Lenia Integration Options

The ranking reflects dependency order and research value, not a commitment to implement
every option.

## 1. Option A — Evolve the Bacterium-0 Controller

Status: implemented as `neat-feedforward-experimental` in RS-01.

This is the smallest debugging surface for NEAT configuration, fixed observation/action
contracts, raw-reward fitness, seed roles, artifacts, reload, and replay. It remains outside
the five canonical Bacterium-0 policies. One bounded result cannot establish superiority or
benchmark eligibility.

## 2. Option B — Tune Fixed Lenia Parameters

For a small fixed vector such as kernel radii/weights, growth mean/width, time step, or
channel coupling, NEAT is not the first choice: topology growth adds representation and
search complexity without a neural controller to discover.

- A simple genetic algorithm is transparent but may require more tuning and evaluations.
- Differential evolution is a strong bounded black-box baseline and tolerates irregular
  objectives.
- CMA-ES is the likely first choice for a modest, correlated, continuous parameter vector
  when the objective is reasonably smooth.
- MAP-Elites is appropriate after phenotype descriptors are stable and diversity itself is
  the research question; it is not the first numerical optimizer.

Recommendation: begin with CMA-ES plus a random-search sanity baseline; prefer differential
evolution if discontinuities, constraints, or collapse make covariance adaptation brittle.
Do not implement either until CPU fixtures and phenotype metrics exist.

## 3. Option C — NEAT-Controlled Lenia Phenotype

A single global feed-forward or recurrent controller can observe phenotype/environment
telemetry and periodically modulate a bounded set of Lenia controls.

Candidate observations include mass, centroid and velocity, fragmentation, angular
velocity, nutrient/toxin gradients, damage, recent growth, and recent parameter changes.
Candidate actions include bounded growth-mean or growth-width adjustment, kernel/channel
selection, directional bias, signaling, and metabolic control.

This option needs defined observation cadence, safe action bounds, causally useful
perturbation scenarios, ablations against fixed parameters, and penalties for invalid
simulation—not hidden reward shaping. Recurrent NEAT remains an open question until a
feed-forward temporal telemetry baseline shows a specific memory limitation.

## 4. Option D — Shared Local Neural Rule

Every cell or region executes the same evolved neural update rule. This is closer to a
neural cellular automaton and is explicitly advanced work. It must wait for CPU/GPU parity,
stable phenotype telemetry, reproducible snapshots, bounded execution cost, and a clear
comparison against mathematical Lenia rules. It risks opaque dynamics, enormous candidate
cost, and GPU implementation complexity.

## 5. Option E — NEAT plus Quality Diversity

NEAT could evolve controller structure within a MAP-Elites-style archive. Possible archive
descriptors include speed, body size, symmetry, rotation, regeneration, fragmentation,
resource efficiency, and number of components. Descriptors must be stable, nonredundant,
bounded, and measurable before archive design. Quality diversity is a later research
instrument, not evidence of open-ended evolution.

## Decision Sequence

```text
RS-01 controller plumbing
        |
        v
CPU mathematical reference -> GPU parity -> phenotype metrics
        |                                      |
        v                                      v
fixed numeric optimization              global NEAT controller
                                                |
                                  shared local rule / QD archive
```
