# Phase 2 — Forge 🔨 (Implementation Agent): phase-aware validator, architecture remediation, and locked PyYAML

> **Owner:** Forge 🔨 (Implementation Agent)
> **Pre:** phase 1 complete; Warden 🔒 (Dependency Warden) upstream review is CONDITIONAL with its required policy branch landed; the exact one-plan Forge 🔨 (Implementation Agent) UV exception is active; no stash path overlaps the declared writes.
> **Reads:** `.opencode/skills/ticket-runbook/scripts/validate_runbook.py`; `.opencode/skills/ticket-runbook/scripts/test_validate_runbook.py`; `.opencode/skills/ticket-runbook/references/runbook/*.md`; `.opencode/skills/plan-enforce/scripts/validate_plan.py`; `.opencode/skills/plan-enforce/scripts/test_validate_plan.py`; phase-1 Warden 🔒 (Dependency Warden) policy; Warden 🔒 (Dependency Warden) conditional review
> **Writes:** `.opencode/skills/ticket-runbook/scripts/validate_runbook.py`; `.opencode/skills/ticket-runbook/scripts/test_validate_runbook.py`; `.opencode/skills/plan-enforce/scripts/validate_plan.py`; `.opencode/skills/plan-enforce/scripts/test_validate_plan.py`; `.opencode/skills/ticket-runbook/pyproject.toml`; `.opencode/skills/ticket-runbook/uv.lock`; `.opencode/skills/ticket-runbook/.gitignore`

## Steps

1. Preserve the implemented `--scaffold`, phase-aware default, and strict `--phase NN` behavior. Keep `yaml.safe_load()`; do not replace PyYAML with a handwritten parser. Ensure one-line and multiline HTML comments are classified only as `STRAY-COMMENT`, never also as generic angle-token placeholders; real angle placeholders remain `UNFILLED-TOKEN` findings. In scaffold mode, validate `Phase` with the same bounded header rule as default and strict modes.
2. Define a `TypedDict` for the seven runbook header fields. Move file reads, phase-file loading, and ledger-sync filesystem access into clearly named IO helpers; make parsing and structural/token checks consume loaded text or typed values.
3. In `validate_plan.py`, retain the typed plan/story metadata and move plan-file, phase-file, story-file, and index discovery/loading into named IO helpers with typed snapshots. Make section, placeholder, metadata, phase, and index evaluation consume those loaded snapshots. Preserve existing CLI output and exit behavior; the pre-refactor plan test suite passed 12 tests.
4. Remove PyYAML from runbook-test fixture patching. Update fixture frontmatter with constrained standard-library text operations while retaining PyYAML only in the runbook validator's runtime parsing path. Add a future-phase boundary case: a missing required section in a present future phase fails structural validation while its intentional fill tokens remain ignored. Add malformed and out-of-range `Phase` cases that fail both `--scaffold` and strict `--phase NN` validation; fill the selected template phase before strict checks so its intended token enforcement does not obscure the header diagnostic. Use exact findings or stderr assertions for all isolated runbook violation cases.
5. In the plan-validator tests, invoke `validate_plan_dir()` and `validate_single_file()` for valid and invalid isolated fixtures. Assert their exit/output contract and exact diagnostics for missing plan/phase files, `YYYY-MM-DD` unfilled tokens, missing story index, story-status index mismatch, and one-line/multiline HTML comment isolation.
6. Create ticket-runbook's skill-local `pyproject.toml` exactly with `PyYAML==6.0.3`, `requires-python = ">=3.9"`, and `[tool.uv] package = false`; create a local `.gitignore` that ignores only `.venv/`.
7. Generate the colocated `uv.lock` using UV after the manifest exists. Do not use a direct URL, unpinned range, custom index, or a root manifest. Do not alter dependency versions after Warden's conditional approval.
8. Update runbook validator/test usage headers to locked root commands using `uv run --locked --project .opencode/skills/ticket-runbook python`; retain root `python3` usage headers for plan-enforce's stdlib scripts.
9. Run the ticket-runbook suite through its locked UV environment, the plan-enforce suite through `python3`, and both help commands. Request fresh Crucible 🔥 (Test Architect) and Bastion 🧱 (Backend Architect) audits after all Python edits.

## Output

- **Artifact:** phase-aware, architecture-clean runbook and plan validator/test modules; public-entry/diagnostic and real-scaffold coverage; exact skill-local PyYAML manifest and lockfile
- **Schema / shape:** `--scaffold` is structural-only for intentional template bodies; default and `--phase` retain strict completed-phase token enforcement; ticket-runbook usage headers name locked UV commands; plan-enforce usage headers remain root `python3`.

## Verify commands

- ☑ Gate 1: `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py` → 21 tests pass
- ☑ Gate 2: `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py --help` → exit 0
- ☑ Gate 3: `python3 .opencode/skills/plan-enforce/scripts/test_validate_plan.py` → 21 tests pass

## Gate

- ☑ Real copied-template scaffold passes `--scaffold` after valid header initialization
- ☑ Future template tokens do not fail default validation when phases through `Phase` are filled
- ☑ An unfilled token in a completed phase fails default or single-phase validation
- ☑ One-line and multiline HTML comments produce only their exact `STRAY-COMMENT` diagnostic while a real angle placeholder remains an `UNFILLED-TOKEN`
- ☑ A malformed present future phase fails structural validation while its intentional future fill tokens remain allowed
- ☑ Plan-validator tests cover public entry points and all declared structural/status diagnostic branches
- ☑ ticket-runbook usage headers document locked UV commands and plan-enforce headers document root-resolvable `python3` commands
- ☑ `pyproject.toml` exactly pins PyYAML, `uv.lock` is current, and `.venv/` is ignored locally
- ☑ Bastion 🧱 (Backend Architect) reports PASS for the Python change
- ☑ `--scaffold` and strict `--phase NN` reject malformed and out-of-range header `Phase` values
- ☑ Runbook violation tests use exact diagnostics rather than broad containment assertions

## Abort conditions

- The implementation would allow unfilled tokens in a phase identified as completed by the runbook header or `--phase NN` → stop and ask.
- Existing ledger-sync behavior or exit-code meanings would change → stop and ask.
- UV cannot generate a lockfile from the approved exact manifest, or the resulting lock resolves a different PyYAML version → stop and report the exact output.
