<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase N — <name>

> **Owner:** <Agent Name + icon + (Role)>
> **Pre:** <what must be true / completed before this phase begins>
> **Reads:** <files / MCP responses / artifacts this phase consumes>
> **Writes:** <files / artifacts this phase produces>

## Steps

1. <One shell command or one file edit — be explicit, no paraphrasing>
2. <Next command or edit>
3. <Continue as needed — every step must be independently executable>

## Output

- **Artifact:** `<path/to/output/file>`
- **Schema / shape:** <what the file must contain or look like>

## Verify commands

<!-- REQUIRED. One canonical table with exactly these two columns. Each command is paired with exactly one declared executor; the validator enforces declared traceability and phase review audits executor authority. -->

| Executor | Command |
|---|---|
| <Name Emoji (Role)> | `<shell command>` |

- Python `test_*.py` edits in reviewed discovery areas: declare the project's approved whole-suite command (AICore uses `uv run --frozen --group dev pytest -q`), assign Crucible 🔥 (Test Architect) as executor, record Bastion 🧱 (Backend & Scripts Architect) `[PASS]`, and require Crucible 🔥 (Test Architect) `[PASS]` or `[FAIL]` — `[UNCERTAIN]` is not acceptable for this scope.

## Gate

- ⬜ <Condition that must be true before next phase begins>
- ⬜ <Second condition if applicable>
- Python `test_*.py` phases: the gate passes only when Crucible 🔥 (Test Architect) ran the declared project-approved whole-suite command with exit 0, Bastion 🧱 (Backend & Scripts Architect) returned `[PASS]`, and Crucible 🔥 (Test Architect) returned `[PASS]` on test architecture; `[FAIL]` or `[UNCERTAIN]` blocks completion.

## Abort conditions

- <Halt if X — describe exactly what constitutes a blocking failure>
- <Halt if Y>

## Tool whitelist / blacklist

<!-- OPTIONAL — include this section ONLY for read-only phases touching external systems -->
<!-- Example: -->
<!-- Whitelist: the data-query tool (read-only queries only) -->
<!-- Blacklist: the ticket-mutation tool (no ticket writes in this phase) -->
