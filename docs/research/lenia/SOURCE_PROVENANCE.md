# Lenia and Neuroevolution Source Provenance

Reviewed: 2026-07-26; RS-02 sources added 2026-07-27

RS-01 used these sources for research and interface design. No external repository was
vendored, and no external Python, GDScript, shader, notebook, or Godot project code was
copied or adapted. Project code in RS-01 was authored against documented NEAT-Python APIs
and the existing Digital Abiogenesis seams.

| Source | Inspected identity | Detected license | RS-01 use |
| --- | --- | --- | --- |
| [NEAT-Python documentation](https://neat-python.readthedocs.io/en/latest/neat_overview.html) and [repository](https://github.com/CodeReclaimers/neat-python) | PyPI `2.0.0`; tag commit `f1a993190fea8c8f9c7c2a72fbf6c10cb4c870ea`; repository head also inspected at `7d9acae0a1e5d7ed6199ffbd525dd15c5c87a86f` | BSD-3-Clause | API, deterministic population seed, feed-forward configuration keys, and portable network JSON export. The project-selected configuration values are original to this spike. |
| Stanley and Miikkulainen, [“Evolving Neural Networks through Augmenting Topologies”](https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf) | 2002 paper | Publication/citation source; no source-code license inferred | Algorithmic background and terminology only. |
| [OpenLenia/Lenia-Tutorial](https://github.com/OpenLenia/Lenia-Tutorial) | `2642cf995b90f4f37788aba440450098e36aa798` | MIT, copyright Open Science Lenia 2021 | Mathematical learning sequence from Conway-style rules through continuous state, kernel, growth, and time. No notebook code copied. |
| [OpenLenia tutorial in Colab](https://colab.research.google.com/github/OpenLenia/Lenia-Tutorial/blob/main/Tutorial_From_Conway_to_Lenia.ipynb) | Notebook at the OpenLenia commit above | Same MIT-licensed repository content | Browser-hosted view of the same tutorial; no separate implementation authority. |
| Bert Wang-Chak Chan, [“Lenia: Biology of Artificial Life”](https://arxiv.org/abs/1812.05433) | arXiv `1812.05433` | Research paper; no source-code license inferred | Mathematical and historical research source only. |
| [Complexity Explorables Lenia](https://chakazul.github.io/lenia-CE/lenia.html) | Live page retrieved 2026-07-26 | No clear source-code license detected during review | Research-only orientation and interactive terminology. Nothing copied or adapted. |
| [Wikipedia: Lenia](https://en.wikipedia.org/wiki/Lenia) | Live article retrieved 2026-07-26 | CC BY-SA 4.0 article content | Orientation only, not implementation authority. |
| [ConwayLife Wiki](https://conwaylife.com/wiki/) | Retrieval returned HTTP 403 on 2026-07-26 | Not determined | Listed for future orientation; no content used as implementation authority. |
| [ThePathfindersCodex/lenia-godot-compute-shader](https://github.com/ThePathfindersCodex/lenia-godot-compute-shader) | `5a0cbab3b6ea53500b5cd5d59330c2684edbcee3` | MIT, copyright 2024 | Architecture review of a Godot 4.2.1 RenderingDevice/GLSL compute path, buffer and texture transfer, dispatch, synchronization, and CPU readback. No code copied. |
| [ThePathfindersCodex/game-of-life-2-lenia](https://github.com/ThePathfindersCodex/game-of-life-2-lenia) | `3f6f88db7dfd3d2bcd96f0fd13aa6cea63db5929` | MIT, copyright 2023 | Review of a Godot 4.2.1 stepwise Conway-to-Lenia teaching implementation. No code copied. |
| [Ludmuterol/lenia_godot](https://github.com/Ludmuterol/lenia_godot) | `5efcf05b55c592791babedf5cb14b830e31ba351` | No license file detected | Transitive research-only provenance noted by a reviewed reference. No adaptation is permitted without a clarified license. |

## RS-02 Mathematical and Comparative Sources

| Source | Inspected identity | Detected license | RS-02 use |
| --- | --- | --- | --- |
| Bert Wang-Chak Chan, [“Lenia: Biology of Artificial Life”](https://arxiv.org/abs/1812.05433) | arXiv `1812.05433v3`; *Complex Systems* 28(3), 2019; DOI `10.25088/ComplexSystems.28.3.251` | Research publication; no source-code license inferred | Primary authority for equations 7-13 and 15-18, periodic FFT discussion, and finite numerical interpretation. |
| [Chakazul/Lenia](https://github.com/Chakazul/Lenia) | `adfc542939266de7f4bb7ebb552e8499701ee107`; `Python/old/Lenia.py` | `LICENSE.md` contains MIT, copyright Bert Chan 2018 | Operational-order cross-check only. The exact checkout corrects the packet's preliminary “no license detected” statement. No code, patterns, or assets copied. |
| [davidrmiller/biosim4](https://github.com/davidrmiller/biosim4) | `45e808cc86e24bae941b60ddebbedd53e874cbd5` | MIT; `src/genome-compare.cpp` separately warns of GPL v3 provenance for one adapted function | Comparative reference only for later L2-L7 design. No code copied. |
| [DylanCope/Evolving-Protozoa](https://github.com/DylanCope/Evolving-Protozoa) | `c10d43879ad8873c68f113195785ccd1d9507d9b` | MIT, copyright Dylan Cope 2023 | Comparative reference only for later L2-L7 design. No code or assets copied. |

## Future Adaptation Rule

Before adapting source rather than ideas, record the exact file and commit, confirm that
its license covers the intended use, preserve its notices, identify the adapted lines in
the change report, and add any required attribution. Sources without a clear license remain
research-only. MIT or BSD status is not permission to omit attribution.
