# Open Questions

These items are unresolved. They are not owner decisions until Joe explicitly resolves
them and the outcome is added to `DECISIONS.md`.

| ID | Question | Why it matters | Needed by |
| --- | --- | --- | --- |
| OQ-001 | Should supported development remain Python 3.13 only, while the core package permits Python 3.10-3.13, or should all support be restricted to the 3.13 line? | The current `>=3.10,<3.14` constraint blocks unsupported 3.14 renderer setup without unnecessarily dropping existing core-library compatibility, but it creates separate development and library contracts. | Before publishing a stable package policy |
| OQ-004 | Should curated model or policy artifacts ever be committed, and under what size/reproducibility rules? | Current model output is ignored, but a benchmark may benefit from a small reviewed policy artifact. | Before committing any model |
| OQ-005 | Should GitHub Actions be introduced during R1 or after the benchmark contract stabilizes? | CI can enforce checks, but adding it before commands and runtime policy settle may create churn. | R1 planning |
| OQ-006 | Which root Obsidian settings should be shared beyond `app.json`, `appearance.json`, and `core-plugins.json`? | `workspace.json` is now ignored as user-specific; sync/plugin preferences may still deserve an explicit policy. | Before Git hygiene changes |
| OQ-008 | What stronger statistical treatment, if any, should follow v1 population dispersion fields? | Confidence intervals or paired analyses should be chosen after the runner exists, the seed schedule is revisited, and full-suite cost is measured. | After R1C evidence and timing |
| OQ-009 | Should the overlapping episode-seed windows produced by adjacent replicate roots be redesigned in a future benchmark version? | Benchmark v1 preserves existing seed derivation and documents the overlap; changing it now would invalidate direct v1 agreement, while leaving it indefinitely limits independence claims. | After R1C evidence audit |
| OQ-010 | Should a future Godot simulation plane live in this repository or a sibling repository? | One repository simplifies versioning; a sibling may isolate engine artifacts and release cadence. | Before L1 |
| OQ-011 | Should Godot simulation orchestration use C# or GDScript? | The likely engine is the Mono build, while reviewed 4.2.1 examples use GDScript; API ergonomics, headless tests, and ownership differ. | L1 design |
| OQ-012 | Should Python control Godot only through per-run files, stdin/stdout, or later local sockets? | The narrow file protocol is easiest to audit, but measured throughput may justify IPC. | After L1 timing |
| OQ-013 | Should `.npy` little-endian float32 remain the cross-plane field format? | NumPy compatibility is convenient, but Godot parsing cost and multi-channel evolution may favor another defined binary layout. | L0/L1 boundary |
| OQ-014 | What measured CPU/GPU error tolerances define Lenia parity? | Exact float equality is inappropriate, but thresholds must be evidence-based rather than invented. | L1 acceptance |
| OQ-015 | Which optimizer should tune fixed Lenia parameters? | CMA-ES is the current likely starting point, with differential evolution and random search as alternatives; objective shape and failure modes should decide. | L3 |
| OQ-016 | Is recurrent NEAT worth testing after the feed-forward feasibility spike? | Recurrence adds temporal memory and determinism/debugging cost; a concrete limitation should justify it. | Before another Bacterium-0 NEAT packet or L4 |
| OQ-017 | What evidence would make an experimental NEAT policy eligible for a future canonical benchmark version? | Eligibility needs fair budgets, stable artifacts, repeatability, cost reporting, and an owner-approved contract change; RS-01 cannot promote it. | Future benchmark version |
| OQ-018 | How is phenotype identity defined through motion, deformation, split, merge, and regeneration? | Identity affects trajectories, holdout outcomes, and lineage claims. | L2 |
| OQ-019 | What constitutes phenotype death, and when does fragmentation produce multiple entities rather than one damaged entity? | Fitness and ecological claims depend on explicit non-anthropomorphic rules. | L2/L7 |
| OQ-020 | Should the continuous substrate begin with multi-channel Lenia or defer Flow-Lenia and other variants? | Variants change mathematics, telemetry, compute cost, and provenance; premature generality risks losing a reference contract. | After L1 |
| OQ-021 | What source-code adaptation and attribution policy should apply to external Lenia/Godot implementations? | Some sources are permissive, while others have no detected license; research inspiration must remain distinct from copied code. | Before any adaptation |
| OQ-022 | What candidate evaluation budget and safe parallelism model are affordable? | GPU context ownership, process startup, deterministic assignment, timeouts, and failure attribution affect valid evolutionary evidence. | L3 |
| OQ-023 | Which measured phenotype descriptors should define a future MAP-Elites archive? | Arbitrary or redundant bins can manufacture apparent diversity. | L6 |
