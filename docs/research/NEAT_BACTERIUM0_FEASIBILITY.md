# NEAT Feasibility on Bacterium-0

Status: RS-01 exploratory research, not canonical benchmark evidence.

## Policy Contract

`neat-feedforward-experimental` wraps a NEAT-Python feed-forward network around the
existing novelty-scent encoder. It does not register as one of the five Bacterium-0 v1
policies.

| Ordered input | Existing discrete range | Network value |
| --- | ---: | ---: |
| north, south, east, west local tile | 0-3 | value / 3 |
| north, south, east, west conflict scent | 0-4 | value / 4 |
| energy bucket | 0-2 | value / 2 |
| north, south, east, west directional novelty | 0-2 | value / 2 |

The adapter reads only the observation passed through the existing encoder and updates its
existing episode memory explicitly after steps. The 13-value order is fixed in artifacts.

The five outputs are north, south, east, west, and wait in the existing `Action` enum order.
The largest finite score wins; an exact tie selects the first action in that order.

## Fitness and Seed Roles

Primary fitness is only mean unmodified environment reward over each ordered fitness root
and its `root + episode_index` episodes. Lifespan, food, poison, wasted/repeated movement,
unique tiles, revisit ratio, loops, and zero-valued novelty diagnostics are recorded but
never shape fitness.

- Experiment seed 21 controls Python, NumPy, and NEAT population randomness.
- Fitness roots `[21, 22, 23]` are visible during selection.
- Disjoint holdout roots `[31, 32, 33]` run only after the winner is selected.
- Genome and episode evaluation is serial (`workers=1`) and order-preserving.

Tests show that the same NEAT-Python version, effective config, seed, and runtime reproduce
the initial population, and a different experiment seed changes it. Cross-platform
bit-for-bit evolution is not claimed. Floating-point/library differences may alter later
generations. Run IDs and the portable exporter timestamp use wall-clock data but do not
affect selection or evaluation.

## Default Configuration Rationale

`configs/neat/bacterium0-feedforward.ini` is project-authored using NEAT-Python's documented
configuration keys:

- `pop_size = 30` and 10 CLI generations bound the feasibility cost; the trainer safely
  writes the selected population and seed into each run's effective copy.
- `no_fitness_termination = True` ensures the requested bounded generation count runs;
  the unreachable `fitness_threshold = 1000` is therefore not a performance claim.
- `feed_forward = True`, 13 inputs, 5 outputs, and `full_direct` match the adapter contract
  and give every action access to every input at initialization.
- `tanh` activation and `sum` aggregation are fixed to avoid activation-family search in
  the spike.
- Standard Gaussian bias/weight initialization and bounded mutation provide a modest,
  inspectable starting search. Response values are fixed at 1.0.
- Node/connection add and delete probabilities allow topology evolution without recurrence.
- Compatibility threshold 3.0, max stagnation 20, survival threshold 0.2, and elitism 1
  are conservative feasibility settings, not tuned claims.
- `min_species_size = 1` supports the tiny 4-genome test; the real default remains 30.

These values have not been optimized. Poor results must not trigger budget escalation or
post hoc tuning inside RS-01.

## Artifacts and Replay

Runs use provisional `neat-research-0.1` beneath ignored `runs/neat/`. They store lifecycle
and source/runtime identity, hashes, exact configuration, generation and holdout metrics,
summary, portable network JSON, and a pickled winner. The pickle must be loaded only from a
trusted local run. The validator checks hashes before replay.

Replay uses:

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.neuroevolution.replay --neat-run <run-directory> --seed 31 --debug-overlay
```

A dedicated ASCII module avoids widening the existing renderer CLI's random/Q-learning
type and lifecycle logic during a bounded spike. Pygame wiring is deferred and no visual
success is claimed.

## Bounded Result

Run `20260726T153027Z_neat-feedforward-experimental_19fa` selected genome 40. Evolutionary
fitness was `1.1953333333333345`; holdout mean reward was `-0.686`. The noncanonical
comparison reported random `-0.067333333333333`, local-Q `0.758`, and novelty-scent-Q
`-0.0673333333333334`. The result is mixed/negative generalization evidence and does not
support NEAT promotion.
