# Comparative Artificial-Life References

Reviewed: 2026-07-27

This is a bounded research checkpoint for later L2-L7 design. Neither project changes
RS-02 scope, is a dependency, or is being ported. No external code or assets were copied.

## BioSim4

- Repository: `https://github.com/davidrmiller/biosim4`
- Inspected commit: `45e808cc86e24bae941b60ddebbedd53e874cbd5`
- License: MIT, copyright David R. Miller and contributors.
- Additional provenance warning: `src/genome-compare.cpp` says its Jaro-Winkler function
  was adapted from a separately GNU GPL v3-licensed source. That file is not used or copied.
- Status: comparative reference only.

Useful later principles are explicit genotype-to-controller compilation, a transparent
direct-connection genome baseline, generational population selection, population diversity
and sensor/action prevalence metrics, shared-world intent with deferred movement/death
resolution, and generation-indexed environmental changes.

## Evolving Protozoa

- Repository: `https://github.com/DylanCope/Evolving-Protozoa`
- Inspected commit: `c10d43879ad8873c68f113195785ccd1d9507d9b`
- License: MIT, copyright Dylan Cope 2023.
- Status: comparative reference only.

Useful later principles are brain/morphology coevolution, capabilities with construction
and maintenance costs, developmental invalidity distinct from lifetime failure, overlapping
generations and resource-driven reproduction, evolvable sensing, and adhesion with resource
or signal exchange as a multicellularity concept. Its current genome parent references use
runtime hash values; a future Digital Abiogenesis lineage contract should instead use
durable explicit identifiers.

## Relevance Boundary

BioSim4 and Evolving Protozoa may inform later phenotype measurement, optimization,
controller, quality-diversity, reproduction, and ecology packets. They do not authorize any
of those features in RS-02. This packet implements only a deterministic single-channel
Lenia CPU mathematical reference.
