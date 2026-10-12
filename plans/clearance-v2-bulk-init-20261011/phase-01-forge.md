# Phase 1 — implement source-owned modes and fresh bulk enrollment

> **Owner:** Forge 🔨 (Implementer)
> **Configuration author:** Cipher 🔓 (Lead Orchestrator) alone converts `distribution-clearance.json`; Forge 🔨 (Implementer) edits only the Python path in this phase.
> **Goal:** G1, G2, G3, G4
> **Pre:** User execution authorization on a later turn; planning audit `[PASS]`; fresh stash inventory absent/unchanged and no manifest collision.
> **Reads:** `plan.md` in full; `core_sync.py` and the current clearance JSON in full; existing registration/preflight/root/mode/init tests; Bastion's Python script rulebook; all Design decisions.
> **Writes:** `.opencode/skills/core-sync/scripts/core_sync.py`; `distribution-clearance.json`

## Steps

1. Cipher 🔓 (Lead Orchestrator) converts distribution-clearance.json to the specified 36-record schema-2 configuration: AGENTS.md is region/root, the config and git-pr story are raw, and all specs/profiles are region. Forge 🔨 (Implementer) consumes that configuration without editing it and implements the separately versioned reader: path-keyed records, required region/raw mode, optional singleton root role restricted to region. Reject duplicates at every JSON level, unsupported/legacy versions, unsafe paths and unknown/invalid fields. No eligibility expansion.
2. Remove destination-default region as an actual distribution decision. Resolve every entry's operational mode from source before preflight/payload IO; omitted destination modes defer to source, while explicit cached modes and CLI assertions must match. Validate all entries globally. Missing clearance/uncleared paths exit 1; malformed clearance and mode conflicts exit 2 with actionable diagnostics. Check's blocker must remain behind this barrier.
3. Add init-only --bind-cleared and --root. If bulk init's bindings file is absent, build empty routing metadata in memory; malformed existing data still fails. Merge explicit declarations, validate assertions, preserve existing source/custom/multiple routes, then add every remaining record deterministically. Ordinary destinations use same path; the root role uses the selected existing instruction file. Persist root selection; do not silently retarget existing mappings.
4. Implement shared case-aware root resolution: explicit root first, compatible existing root routes next, then agents/claude/instructions precedence with actual spelling preserved. Same-name case collisions require explicit choice; no required root found exits 1 before writes. Existing roots override new defaults only as stated in plan. Use this same decision for blocker writes and prospective raw-root-alias preflight.
5. Stage all source reads and outputs before creating any directory or file. Allow newly registered region/raw targets and parents to be generated; do not reinterpret missing stored targets as new. Region initialization preserves existing destination frontmatter/old body and source-core bytes; new files get only approved identity/document metadata, no source model/permission/tool overrides. Initialize derived-runtime local-version once. Root files must already exist, preserving destination identity.
6. Keep source read-only, safe canonical paths, hard-link/symlink/inode protection, unique resolved outputs, exact raw bytes, marker validation for declared region sources, reconciliation/pending/report handling and partial-IO-error diagnostics. Replace old creation-only/raw and two-name selection assumptions where required; do not add rollback or compatibility scaffolding.
7. Cipher 🔓 (Lead Orchestrator) runs the two checks below; Bastion 🧱 (Backend & Scripts Architect) audits the completed script. Record changed interfaces, error precedence, new-output staging and removed legacy assumptions. Do not run the old-fixture suite until phase 2 migrates fixtures.

## Output

- **Artifact:** v2-capable script and the converted 36-record clearance file.
- **Schema / shape:** source-mode authority; singleton root role; complete registration and write plan; fresh bindings/new payloads; root discovery with shared alias-safe preflight.
- **Evidence:** syntax/inventory checks, scoped code-architecture `[PASS]`, and a legacy sweep accounting for replaced source-set/default-mode/creation/root logic. No implementation result is claimed before execution.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B -c "from pathlib import Path;p=Path('.opencode/skills/core-sync/scripts/core_sync.py');compile(p.read_text(),str(p),'exec');print('core-sync syntax: PASS')"` |
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B -c "import json;from pathlib import Path;d=json.loads(Path('distribution-clearance.json').read_text());assert d['schema']==2 and len(d['cleared'])==36;assert d['cleared']['AGENTS.md']=={'mode':'region','role':'root'};assert {p for p,r in d['cleared'].items() if r['mode']=='raw'}=={'opencode.jsonc','user-stories/git-pr-drafting.md'};assert all(p in d['cleared'] for p in [str(x) for x in Path('.opencode/agents').glob('*.md')]+[str(x) for x in Path('agents').glob('*/profile.md')]);print('v2 clearance inventory: PASS')"` |

## Gate

- ⬜ All 36 source records are retained with authoritative modes and valid root role; legacy metadata does not select policy.
- ⬜ Fresh registration/creation, root detection and validation-before-write staging match the explicit contract; code architecture `[PASS]`.
- ⬜ Legacy/dead-code sweep is recorded; no conflicting default-mode inference, obsolete new-target restriction or validated-but-unused metadata survives.

## Abort conditions

- Stop on missing/contradictory requirements, unreviewed source authority changes, parser ambiguity, source-write risk or any real-destination access requirement.
- Stop if an implementation need requires a path outside Writes; report the exact scope and evidence rather than silently editing.
