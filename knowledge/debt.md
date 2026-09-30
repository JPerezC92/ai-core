# Accepted Debt Register

Records of deferred technical or process debt that are **non-blocking** for release.

## Entry format

Each entry MUST include:

- **ID** — unique identifier (e.g. `DEBT-001`)
- **Date** — when the deferral decision was made
- **Description** — what is deferred
- **Direct evidence** — the evidence that justifies deferral
- **Resolution criteria** — what must be true for the debt to be cleared
- **Explicit deferral decision** — who decided, and when

## Rules

- An accepted debt is nonblocking only when its record here carries direct evidence, resolution criteria, and an explicit deferral decision (see Herald 📯 (Release Manager) spec).
- Disclose the ID and unresolved criteria in any operation report that touches it.
- Clear and retire a debt in the same PR: the PR that clears a debt deletes its entry from this register, and its body and commit carry the Resolution evidence (criteria met, validation and audit results). Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one PR: its clearing PR.

## Register

### DEBT-001 — PR test-evidence observed output is unstandardized

- **ID:** DEBT-001
- **Date:** 2026-09-27
- **Description:** `## Test evidence` Observed output has no human-readable contract. Agents paste full runner stdout (pytest `-q` progress dots, traces, dumps). The useful signal is the verdict line.
- **Direct evidence:** PR #44 Test evidence for pytest at `c89a6e6698a52948cfbf3f62c8eb41f04383482e` recorded `........................................................................ [ 97%]` / `.. [100%]` plus `74 passed in 0.11s`. User rejected the dots as unhelpful. `git-pr` SKILL.md Post-PR evidence contract requires `<literal observed output>` with no verdict-only rule. Inquisitor 🔎 (PR Reviewer) and Herald 📯 (Release Manager) persist that same shape.
- **Resolution criteria:** `git-pr`, Inquisitor 🔎 (PR Reviewer), and Herald 📯 (Release Manager) require Observed output to be the human-readable verdict only (for pytest: `N passed in Xs`). Progress bars, per-test dots, stack traces, and raw dumps are forbidden unless the user asks for them. Clearing PR UPDATES `user-stories/git-pr-drafting.md`; do not CREATE a new story. That PR deletes this entry.
- **Explicit deferral decision:** User, 2026-09-27 — strip the dots from PR #44 now; standardize the contract later. Non-blocking for #44 merge.

### DEBT-002 — No delegated owner can execute Python pytest

- **ID:** DEBT-002
- **Date:** 2026-09-28
- **Description:** Phase 3 lacked a delegated Python runner, so Cipher 🔓 (Lead Orchestrator) ran the file-scoped test. The whole-suite role, project-level grant, and restarted delegated run are now verified. This entry remains open only until the user-authorized completing PR retires it.
- **Direct evidence:** Phase 3 Forge 🔨 (Implementer) returned `Pytest: not run — Forge Bash permission excludes this command`; Cipher 🔓 (Lead Orchestrator) ran the earlier file-scoped command with `60 passed in 5.12s`. After restart, Crucible 🔥 (Test Architect) ran `uv run --frozen --group dev pytest -q` with exit 0 (`304 passed in 14.10s`), test architecture `[PASS]`. A historical `313 passed` figure recorded under a plan that was later superseded is retained as history only, not as current evidence.
- **Resolution criteria:** Crucible 🔥 (Test Architect) is the delegated test runner. Each project's root `opencode.jsonc` holds `agent.crucible.permission.bash` for that project's reviewed commands; Crucible's shared agent spec has no executable grant. AICore's own grant is its reviewed UV pytest command. After OpenCode restart, Crucible runs the declared command with exit 0 and persistent verdict-only evidence. Clearing PR UPDATES Crucible 🔥 (Test Architect), Warden 🔒 (Dependency Warden), Inquisitor 🔎 (PR Reviewer), `plan-enforce`, `python-pytest`, and the project config contract, then deletes this entry.
- **Explicit deferral decision:** User, 2026-09-28 — record now and continue the destination synchronization plan. Non-blocking for G3-G5.
