# Open Questions

These items are unresolved. They are not owner decisions until Joe explicitly resolves
them and the outcome is added to `DECISIONS.md`.

| ID | Question | Why it matters | Needed by |
| --- | --- | --- | --- |
| OQ-001 | Should supported development remain Python 3.13 only, while the core package permits Python 3.10-3.13, or should all support be restricted to the 3.13 line? | The current `>=3.10,<3.14` constraint blocks unsupported 3.14 renderer setup without unnecessarily dropping existing core-library compatibility, but it creates separate development and library contracts. | Before publishing a stable package policy |
| OQ-002 | Should standard experiment manifests use JSON or TOML? | JSON matches existing model serialization and is ubiquitous; TOML is easier for hand-authored configuration. | R1A |
| OQ-003 | How many seeds define the canonical quick and full benchmark suites? | Runtime and statistical confidence must be balanced and named explicitly. | R1A |
| OQ-004 | Should curated model or policy artifacts ever be committed, and under what size/reproducibility rules? | Current model output is ignored, but a benchmark may benefit from a small reviewed policy artifact. | Before committing any model |
| OQ-005 | Should GitHub Actions be introduced during R1 or after the benchmark contract stabilizes? | CI can enforce checks, but adding it before commands and runtime policy settle may create churn. | R1 planning |
| OQ-006 | Which root Obsidian settings should be shared beyond `app.json`, `appearance.json`, and `core-plugins.json`? | `workspace.json` is now ignored as user-specific; sync/plugin preferences may still deserve an explicit policy. | Before Git hygiene changes |
| OQ-007 | Should R1 define an exact metrics JSON schema or a versioned semantic contract first? | A rigid early schema may encode current evaluator debt; a loose contract may be hard to validate. | R1A |
