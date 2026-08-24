# Phase 1 — Vault 🔐 (Catalog Steward): plan-enforce self-verify tooling

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** active plan; stash gate clean (no planned-path overlap); `plan-enforce/SKILL.md` + `references/` templates read in full.
> **Reads:** `.opencode/skills/plan-enforce/SKILL.md`; `.opencode/skills/plan-enforce/references/_template.md`, `_template-programming.md`, `_phase-template.md`, `_template-user-story.md`; `.opencode/agents/sentinel.md` (rules 7/8)
> **Writes:** `.opencode/skills/plan-enforce/references/_consistency-checklist.md`; `.opencode/skills/plan-enforce/scripts/validate_plan.py`; `.opencode/skills/plan-enforce/scripts/test_validate_plan.py`; `.opencode/skills/plan-enforce/SKILL.md` (edit)

## Steps

1. Write `references/_consistency-checklist.md` — the canonical plan/phase/story contract, grouped by artifact: plan.md (Status ∈ {active, completed} + `Completed:` line when completed; required sections; no `<...>`/`YYYY-MM-DD`/stray `<!-- -->` placeholders; `## Goals` checkboxes match confirmed goals; every dispatch-table phase traces to ≥1 goal and references an existing phase file; verification checkbox count == phase-output count; `## Critical files / tools` cites each touched story); phase file (Owner/Pre/Reads/Writes populated; no `TBD` in Steps/Output/Gate/Abort; `## Writes` == derived manifest); story/index (`index.md` lists every feature; title/status mirror; no placeholders; dated `## Change log` entry per touching plan).
2. Write `scripts/validate_plan.py` — mechanical subset only: Status enum, `Completed:` line presence, required sections, unfilled `<...>`/`TBD`/`YYYY-MM-DD` detection, phase section + blockquote labels, index mirroring. Subfolder plan dir is the default; `--single-file` mode covers the exception layout. Mirror the CLI style of `validate_runbook.py` (exit 0 pass / 1 fail; warnings vs violations).
3. Write `scripts/test_validate_plan.py` covering: valid subfolder plan passes; valid single-file plan passes; each violation class (bad Status, missing section, unfilled token, missing phase section, index mismatch) is caught.
4. Run `python3 .opencode/skills/plan-enforce/scripts/test_validate_plan.py` from the project root — must exit 0.
5. Edit `plan-enforce/SKILL.md`: add the post-write self-verification loop (re-read written files → run `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py <plan-dir>` or `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py <plan.md> --single-file` → analysis against `_consistency-checklist.md` → fix mechanical, stop-and-ask on judgment → repeat until clean, S-07 cap); reference the checklist + script paths; bump frontmatter `version` to `1.5.0`.

## Output

- **Artifact:** `references/_consistency-checklist.md`, `scripts/validate_plan.py`, `scripts/test_validate_plan.py`, edited `SKILL.md`
- **Schema / shape:** checklist lists the full contract grouped by artifact (plan/phase/story+index); `validate_plan.py` mirrors the `validate_runbook.py` CLI; `SKILL.md` has the loop section + `version: 1.5.0`.

## Verify commands

- ⬜ `python3 .opencode/skills/plan-enforce/scripts/test_validate_plan.py` → exit 0
- ⬜ `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/self-verify-loops-20260820/` → exit 0 on a well-formed plan

## Gate

- ⬜ `test_validate_plan.py` exits 0
- ⬜ `_consistency-checklist.md` covers all three artifact groups (plan/phase/story+index) with no `TBD`
- ⬜ `SKILL.md` loop section present; `version: 1.5.0` set

## Abort conditions

- `test_validate_plan.py` non-zero → fix the validator before proceeding; never ship a failing validator.
- A checklist item needs a value not evidenced anywhere → stop and ask; never invent.
