# Digital Abiogenesis

Digital Abiogenesis is a minimal artificial-life workbench for measuring and visualizing
adaptive behavior. Its current organism, **Bacterium-0**, is a Gymnasium-compatible grid
microbe with energy, food, poison, tabular Q-learning, deterministic evaluation, and ASCII
and sprite-based pygame observation windows.

The project is currently at **R0: Rebaseline and engineering retool**. Bacterium-0 is being
preserved as the legacy benchmark before named benchmark scenarios are defined in R1.

## Quick Setup

Python 3.13 is the supported development runtime.

```powershell
py -3.13 -m venv .venv
.\scripts\bootstrap.ps1
```

The bootstrap script uses `.venv\Scripts\python.exe` directly and installs the development
and renderer extras.

## Verify

Run the canonical quality gate:

```powershell
.\scripts\check.ps1
```

Run the current deterministic multi-seed benchmark wrapper:

```powershell
.\scripts\run-benchmark.ps1
```

## Observe Bacterium-0

The canonical sprite-capable pygame viewer command is:

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.render.play_episode --agent q-learning --renderer pygame --seed 21 --train-episodes 500 --encoder conflict-scent --tile-size 56 --debug-overlay
```

The renderer falls back to shape drawing if a sprite is missing. Visual behavior is only
considered verified after Joe performs the manual procedure in `VERIFICATION.md`.

## Project Control Plane

- [Home](HOME.md)
- [Current project state](PROJECT_STATE.md)
- [Vision](VISION.md)
- [Roadmap](ROADMAP.md)
- [Next work packet](NEXT_WORK_PACKET.md)
- [Verification](VERIFICATION.md)

Detailed development and experiment commands are preserved in
[docs/COMMANDS.md](docs/COMMANDS.md). Historical results remain in
[docs/experiments.md](docs/experiments.md) and [docs/lab-notes.md](docs/lab-notes.md).
