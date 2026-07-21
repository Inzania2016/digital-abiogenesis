# Development and Experiment Commands

These commands preserve the useful R0 command catalog. Use
`.venv\Scripts\python.exe` directly so commands cannot drift to a global interpreter.

## Environment and Quality Gate

```powershell
py -3.13 -m venv .venv
.\scripts\bootstrap.ps1
.\scripts\test.ps1
.\scripts\check.ps1
.\scripts\clean.ps1
.\scripts\package-source.ps1
```

Remove ignored run/artifact output only when intentional:

```powershell
.\scripts\clean.ps1 -Generated
```

## Random Baseline

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.training.train_random --seed 13 --episodes 10 --grid-size 10
```

## Train and Compare Q-learning

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.training.train_q_learning --seed 21 --episodes 1000 --grid-size 10 --save-path models/bacterium-0-q.json
.\.venv\Scripts\python.exe -m abiogenesis.training.evaluate_q_learning --seed 21 --train-episodes 1000 --eval-episodes 50 --grid-size 10
.\.venv\Scripts\python.exe -m abiogenesis.training.evaluate_q_learning --seed 21 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --compare-scent
```

## Multi-seed and Reward Experiments

The current R0 wrapper uses the latest small documented comparison:

```powershell
.\scripts\run-benchmark.ps1
```

Direct forms:

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed
.\.venv\Scripts\python.exe -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 5 --train-episodes 1000 --eval-episodes 50 --grid-size 10 --multi-seed --poison-penalty -2.0 --poison-energy-cost 12
.\.venv\Scripts\python.exe -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed --loop-penalty -0.05
.\.venv\Scripts\python.exe -m abiogenesis.training.evaluate_q_learning --seed 21 --seeds 3 --train-episodes 200 --eval-episodes 20 --grid-size 10 --multi-seed --novelty-reward 0.02
```

## Encoder Variants

Available encoder names are `local`, `scent`, `conflict-scent`, `memory-scent`,
`visit-scent`, `loop-scent`, and `novelty-scent`.

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.training.train_q_learning --seed 21 --episodes 500 --grid-size 10 --encoder memory-scent
.\.venv\Scripts\python.exe -m abiogenesis.training.train_q_learning --seed 21 --episodes 500 --grid-size 10 --encoder visit-scent
.\.venv\Scripts\python.exe -m abiogenesis.training.train_q_learning --seed 21 --episodes 500 --grid-size 10 --encoder loop-scent
.\.venv\Scripts\python.exe -m abiogenesis.training.train_q_learning --seed 21 --episodes 500 --grid-size 10 --encoder novelty-scent --novelty-reward 0.02
```

## Hyperparameter Sweep

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.training.sweep_q_learning --seed 21 --seeds 3 --eval-episodes 20 --grid-size 10
.\.venv\Scripts\python.exe -m abiogenesis.training.sweep_q_learning --seed 21 --seeds 3 --eval-episodes 20 --grid-size 10 --save-best-path models/phase-2e-best-q.json
```

## ASCII Playback

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.render.play_episode --agent random --renderer ascii --seed 7 --delay 0.2
.\.venv\Scripts\python.exe -m abiogenesis.render.play_episode --agent q-learning --renderer ascii --q-path models/phase-2e-best-q.json --encoder conflict-scent --seed 100022 --grid-size 10 --delay 0.1 --debug-overlay
```

## Pygame Observation Window

```powershell
.\.venv\Scripts\python.exe -m abiogenesis.render.play_episode --agent q-learning --renderer pygame --seed 21 --train-episodes 500 --encoder conflict-scent --tile-size 56 --debug-overlay
.\.venv\Scripts\python.exe -m abiogenesis.render.play_episode --agent q-learning --renderer pygame --encoder conflict-scent --sprite-dir assets/sprites
```

Use `--no-sprites` to force shape rendering. Pygame controls:

- Space: pause/unpause.
- R: reset.
- Escape or Q: quit.
- Up/Down or +/-: playback speed.
- T: trail overlay.
- S: scent overlay.
- H: HUD.
- P or F12: screenshot under `artifacts/screenshots/`.

Follow `VERIFICATION.md`; Codex does not claim visual success.

## Sprite Preparation

```powershell
.\.venv\Scripts\python.exe tools/convert_pngs_to_rgba.py --input assets/sprites --output assets_rgba/sprites --bg "#FFFFFF" --tolerance 10
.\.venv\Scripts\python.exe tools/convert_pngs_to_rgba.py --input assets/sprites --bg "#FFFFFF" --tolerance 10 --overwrite
```

The overwrite form is destructive and should be used only intentionally.
