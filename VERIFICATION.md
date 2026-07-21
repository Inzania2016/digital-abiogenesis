# Verification Contract

## Automated Verification

Bootstrap or refresh the Python 3.13 environment:

```powershell
.\scripts\bootstrap.ps1
```

Run the complete quality gate:

```powershell
.\scripts\check.ps1
```

`check.ps1` runs, in order:

1. pytest through `.venv\Scripts\python.exe`, with repository-local temporary storage;
2. `ruff check .`;
3. `ruff format --check .`.

Run the current R0 deterministic benchmark wrapper:

```powershell
.\scripts\run-benchmark.ps1
```

R1 will replace this wrapper's generic multi-seed command with named scenarios.

## Manual Pygame Verification

Only Joe records this as human-visible verification:

1. Complete bootstrap and automated checks.
2. Run:

   ```powershell
   .\.venv\Scripts\python.exe -m abiogenesis.render.play_episode --agent q-learning --renderer pygame --seed 21 --train-episodes 500 --encoder conflict-scent --tile-size 56 --debug-overlay
   ```

3. Confirm that the window opens, the sprite-based organism/food/poison render (or documented
   shape fallbacks appear), the organism advances, the HUD updates, and pause/reset/speed,
   trail, scent, HUD, screenshot, and quit controls behave as documented.
4. Confirm that visual observation does not itself establish a learning claim.
5. Record date, runtime, command, observed outcome, and failures in a verification record.

## Verification Authority

Codex may verify:

- commands it actually runs and their exit codes;
- automated tests, lint, formatting, imports, deterministic CLI output, archive contents,
  and non-graphical renderer helpers;
- filesystem and configuration facts visible in the workspace.

Only Joe may verify:

- the human-visible correctness or quality of the pygame window;
- subjective animation, sprite appearance, responsiveness, and interactive control feel.

Codex must not convert an import check, unit test, screenshot file, or unseen window launch
into a claim of visual success.

## Verification Records

Store milestone records in `docs/verification/` using a dated descriptive filename, such as
`2026-07-20-r0.md`. Include environment/runtime, exact commands, exit codes, relevant output
summaries, skipped manual steps, and known limitations. Append experiment results only to
the historical experiment documents when an actual experiment was run and interpreted.

Never invent or backfill a verification result. A failed or skipped check remains explicit
until a later dated record supersedes it.
