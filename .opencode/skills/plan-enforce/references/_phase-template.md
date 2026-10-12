<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase N — <name>

> **Owner:** <Agent Name + icon + (Role)>
> **Pre:** <what must be true / completed before this phase begins>
> **Reads:** <files / MCP responses / artifacts this phase consumes>
> **Writes:** <files / artifacts this phase produces>

> Contract-sized: one coherent responsibility, with its interfaces, allowed writes, outputs, and gates. Size by responsibility, never by an arbitrary file count. State behavior and contracts — never prewrite private implementation. If the plan ships a behavior-visible change, this phase's `**Writes:**` includes the affected documentation paths.

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

- Python `test_*.py` edits in reviewed discovery areas: declare the project's approved whole-suite command, assign Crucible 🔥 (Test Architect) as executor, record Bastion 🧱 (Backend & Scripts Architect) `[PASS]`, and require Crucible 🔥 (Test Architect) `[PASS]` or `[FAIL]` — `[UNCERTAIN]` is not acceptable for this scope.
- A behavior slice may record an expected red checkpoint: the designated executor runs the new failing test through its authorized command and records the red result. Expected red is never a goal `✅`, a phase gate PASS, or an acceptance `✅`; it only proves the test can fail.

## Gate

- ⬜ <Condition that must be true before next phase begins>
- ⬜ <Second condition if applicable>
- ⬜ If this phase replaces, supersedes, or newly wires behavior: a recorded legacy/dead-code sweep with no dead symbol, inert field, or stale mapping.
- ⬜ If this phase ships a behavior-visible change: the affected documentation is written in the same change and reviewed against the delivered behavior (not the plan's description of it).
- ⬜ Expected red is never the gate PASS: the phase requires final green (the executor's command exits 0), the applicable architecture verdicts (Atrium 🏛️ (Frontend Architect) / Bastion 🧱 (Backend & Scripts Architect) / Crucible 🔥 (Test Architect)), and the reviewed whole-suite gate.
- Python `test_*.py` phases: the gate passes only when Crucible 🔥 (Test Architect) ran the declared project-approved whole-suite command with exit 0, Bastion 🧱 (Backend & Scripts Architect) returned `[PASS]`, and Crucible 🔥 (Test Architect) returned `[PASS]` on test architecture; `[FAIL]` or `[UNCERTAIN]` blocks completion.

## Abort conditions

- <Halt if X — describe exactly what constitutes a blocking failure>
- <Halt if Y>

## Tool whitelist / blacklist

<!-- OPTIONAL — include this section ONLY for read-only phases touching external systems -->
<!-- Example: -->
<!-- Whitelist: the data-query tool (read-only queries only) -->
<!-- Blacklist: the ticket-mutation tool (no ticket writes in this phase) -->
