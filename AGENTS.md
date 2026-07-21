# Digital Abiogenesis Collaboration Constitution

## Purpose and Non-goals

Digital Abiogenesis is an open-source artificial-life workbench for demonstrating,
measuring, and visualizing adaptive behavior within lifetimes and across generations.
The current organism, Bacterium-0, is the legacy tabular benchmark.

The project does not claim consciousness, sentience, self-awareness, or biological
life. Do not turn the organism into a chatbot, introduce cloud dependencies, or add
neural-network frameworks unless an approved work packet explicitly requires them.

## Authority Order

When instructions conflict, use this order:

1. User instructions for the current task.
2. `AGENTS.md`.
3. `PROJECT_STATE.md`.
4. `NEXT_WORK_PACKET.md`.
5. `DECISIONS.md`.
6. Architecture and experiment documentation.
7. Historical lab notes.

`VISION.md` defines the north star and `ROADMAP.md` owns the research ladder. Do not
embed a second roadmap here. Obsidian and `HOME.md` provide navigation; they do not
override authoritative Markdown files.

## Engineering Principles

- Inspect the repository and current state before editing.
- Make the smallest coherent change that satisfies the active packet.
- Prefer readable Python, explicit configuration, deterministic seeds, small functions,
  useful type hints, and tests for rules.
- Keep dependencies minimal and open source. Do not add cloud services by default.
- Do not combine behavior changes with cleanup or broad refactoring.
- Preserve the runnable baseline and historical evidence.
- Treat Python 3.13 as the supported development runtime; follow `DECISIONS.md` for the
  package compatibility range.

## Experiment Integrity

- Every experiment must state a question, configuration, agent, encoder, seeds,
  training/evaluation duration, metrics, interpretation, and next step.
- Claims of learning or improvement require measured evidence under fair conditions.
- Preserve mixed and negative findings. Never tune until a preferred result appears and
  describe that result as natural.
- Use deterministic seeds where practical and record exact commands.
- Do not change recorded results unless correcting a demonstrated error, and document any
  correction explicitly.

## Separation of Concerns

- Environment: owns world state, movement, rewards, energy, reset/step, and termination.
- Agents: own action selection, learning updates, policy state, and persistence.
- Sensors/encoders: convert observations and episode memory into agent state.
- Metrics: record and aggregate behavior without influencing it.
- Rendering: observes state and presents ASCII or pygame views; it must not alter behavior.

Do not let agents mutate the environment directly, do not hide learning state inside the
environment, and do not couple rendering to training or world dynamics.

## Tests and Verification

- Add or update tests for behavior changes before reporting completion.
- Run `./scripts/check.ps1` for the current automated quality gate and record the exact
  outcome. Run the relevant smoke test or benchmark when practical.
- Follow `VERIFICATION.md` for automated and manual procedures.
- Codex may verify commands and non-graphical outputs it actually runs. Only Joe may
  verify human-visible pygame behavior.
- Never invent a passing command, metric, or visual observation.

## Commit Gate

Do not commit, push, tag, publish, or open a pull request without Joe's explicit approval
for that action. Report the working-tree scope before any approved commit. If Git metadata
is unavailable, say so rather than inferring status.

## Generated Artifacts

Generated data belongs in predictable ignored locations such as `runs/`, `artifacts/`,
`models/`, or `dist/`. Do not commit virtual environments, caches, bytecode, build output,
screenshots, large run output, or model files by default. Curated artifacts require an
explicit owner decision. Preserve intentional source assets and historical experiment
records.

## Required Codex Final Report

For change tasks, report:

1. Summary.
2. Files created and modified.
3. Behavior-change statement.
4. Exact commands run and results.
5. Failures, skipped checks, and verification boundaries.
6. Git status summary and commit status.
7. Recommended next task.
8. Recommended model and reasoning level for that task, including when a higher level is
   worthwhile.
