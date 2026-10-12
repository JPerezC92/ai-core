# Plan — source-owned distribution modes and fresh bulk enrollment

> **Status:** active
> **Started:** 2026-10-11 14:32
> **Subject:** Make clearance v2 authoritative for distribution modes, initialize every cleared source with one flag, and detect the destination instruction root
> **Layout:** subfolder pattern

## Context

- Prompted by: the user found that clearance and bindings needed separate per-file maintenance, requested enrollment of every cleared source, rejected destination-controlled raw mode, and requested destination detection for agents/claude/instructions files.
- Goal: a source-owned v2 distribution contract and one-command fresh enrollment, including when the destination bindings file was deliberately removed. Replace incompatible implementation behavior rather than retain it as a backward-compatibility constraint.
- Outcome: an audited source-side CLI/data/test/documentation change. All integration cases use temporary destinations; no real destination project is accessed or modified.
- Classification: programming plan; UPDATE `user-stories/aicore-adoption-sync.md`, which already owns clearance, raw/region synchronization, bindings and enrollment. The index confirms that ownership; no new story is created. Four goals, no goal-count flag.
- Existing work: preserve the user-authorized 36 cleared paths and the prior roster-clearance story edit. Convert their representation, not their eligibility. The two pending source paths are inspected and included in this plan.
- Stash gate: Herald 📯 (Release Manager)'s read-only inventory returned live main `def69f555c2cb516305e6109bb084315d05b0296`, branch `main`, no stash ref and an empty stash list. STASH_FINGERPRINT = absent; no collision with the manifest. Repeat before implementation dispatch.

## Goals

- ⬜ **G1:** Source-owned modes: `distribution-clearance.json` declares raw or region for every cleared source. All three commands reject conflicting mode assertions before reading payloads or writing destination files.
  - Issue: clearance currently records only paths, so a destination can select an unsafe distribution mode.
  - How: require explicit schema-2 records, resolve actual modes from source metadata, validate all persisted/CLI assertions globally, and reject schema-1 clearance rather than infer missing policy.
  - Files: `distribution-clearance.json`; `core_sync.py`; the testkit, clearance metadata/mode/gate tests; the skill and adoption guidance.
  - Done when: both mismatch directions and omitted-destination-mode cases are tested across check/apply/init, an invalid later entry blocks all earlier payload reads/writes, and raw byte-copy behavior is selected only from source metadata.
- ⬜ **G2:** One-command fresh enrollment: `init --bind-cleared` initializes absent bindings metadata, enrolls every cleared source using its declared mode, creates newly enrolled payloads and parents, preserves existing mappings, and repeats without duplicate bindings.
  - Issue: init currently requires an existing bindings file and region targets, preventing the user's planned reset and making roster growth manual.
  - How: build the whole registration/output plan in memory, detect the root, preflight all outputs, and create only genuinely new mappings after validation. Seed required document metadata without copying source-local runtime grants.
  - Files: `core_sync.py`; fresh-init and bulk-init tests; raw-enrollment regression tests; the skill, README and adoption story.
  - Done when: temporary destinations with an existing supported instruction root but no core.yaml receive the complete mixed-mode set and missing nested payloads; repeated enrollment preserves custom/multiple mappings and creates no duplicate entries.
- ⬜ **G3:** Automatic root detection: recognize existing AGENTS.md/agents.md, CLAUDE.md/claude.md, and instructions.md, preserve actual filename spelling, honor explicit root selection, and otherwise prefer agents, then claude, then instructions.
  - Issue: the current resolver omits instructions.md and assumes canonical uppercase names; generic registration does not know the source root's role.
  - How: mark the source root with `role: root`, use one resolver for routing/blockers/preflight, preserve existing mappings, and allow an init root override for fresh metadata when an explicit choice is needed.
  - Files: `core_sync.py`; root-selection, root/raw-alias, bulk-init and fresh-init tests; the skill and adoption guidance.
  - Done when: each supported name and case variant is detected in temporary destinations, configured/CLI roots take precedence, mappings are not silently retargeted, and selected raw-root aliases fail before any write.
- ⬜ **G4:** Preserve sync guarantees: raw copies remain byte-identical, region updates preserve destination-owned bytes, and invalid metadata/modes, mapping conflicts, or missing required stored targets fail before enrollment writes.
  - Issue: v2 must replace obsolete prerequisites without weakening source/destination boundaries or reconciliation.
  - How: retain core extraction, raw byte IO, source-write/alias guards and region reconciliation; validate the complete output plan before making directories or files; distinguish new-target creation from missing stored targets.
  - Files: `core_sync.py`; the testkit and regression/new test modules; skill exit/troubleshooting guidance and the adoption story.
  - Done when: the reviewed whole-suite command exits 0 with separate code/test architecture verdicts, invalid inputs leave all files and directories unchanged, and the independent completion audit establishes the four goals.

## Current state

| Area | Current behavior | Evidence |
|---|---|---|
| Clearance | schema 1, 36 path strings, no modes | `distribution-clearance.json`; Augur research session `ses_ed3aa710fffeUOGLjE2vmlW8yF` |
| Mode authority | destination mode defaults region | `core_sync.py` → binding normalization, load_clearance, run_check/run_apply/run_init |
| Init | no bulk flag; bindings and region targets must exist | `core_sync.py` → run_init and CLI builder; `test_core_sync_init_missing_inputs.py` |
| Root selection | explicit root, then AGENTS.md/CLAUDE.md; no instructions detection | `core_sync.py` → DEFAULT_ROOT_CANDIDATES and resolve_root_path; `test_core_sync_root_selection.py` |
| New targets | only new raw targets with existing parents can be created | `test_core_sync_init_raw_enrollment.py`; skill Commands and Troubleshooting |
| Fixtures | schema-1 source clearance is auto-seeded | `_core_sync_testkit.py`; `test_core_sync_clearance.py` |
| Required metadata | new runtime specs need identity/version framing and local-version | `AGENTS.md` Reuse guide and active-runtime identity rule; `agents/atrium/profile.md` frontmatter |

## Behavior change

| Goal | Before | After | Interface contracts | Do-not-break |
|---|---|---|---|---|
| G1 | destination selects mode | source records select mode; destination/CLI mode fields are assertions only | clearance schema 2; metadata errors exit 2, uncleared sources exit 1 | raw bytes, no marker inference |
| G2 | long per-file command and prepared files | one bulk flag bootstraps metadata/new payloads | init-only --bind-cleared; source-revision remains required | existing mappings and payload metadata |
| G3 | two-name lookup | three-name case-aware lookup and source root role | optional role=root; explicit root override | actual selected path and alias protections |
| G4 | narrow creation prerequisites | validated creation for new mappings, strict stored-target checks | no validation-time filesystem mutation | source read-only; destination project regions |

## Design decisions

- **Forward-only clearance:** schema 2 has `cleared` as a path-keyed object. Each record has required `mode: region|raw` and optional `role: root`. No enrollment-exceptions object or destination-specific route is stored in source. Reject duplicate JSON keys, unsafe/noncanonical paths, unknown fields/values, missing modes, and multiple root roles. A root role must be region. Legacy schema-1 clearance is rejected with an actionable migration diagnostic.
- **Current eligibility:** retain all 36 paths; `AGENTS.md` is region/root, the 16 specs and 17 profiles are region, and `opencode.jsonc` plus the git-pr story are raw. Do not add other source files or infer policy from extensions/marker presence.
- **Source authority everywhere:** commands resolve actual modes from clearance before target preflight/payload reads. An omitted binding mode defers to source; it never defaults the distribution to region. Explicit binding/CLI mode assertions must match source or fail. Existing route metadata may retain its structurally compatible schema-1 representation and mode annotations; those are not authority and never override source. No legacy mode-selection fallback is preserved.
- **Bulk routes:** preserve every existing source/destination mapping. An unbound ordinary source maps to the same relative path. An unbound root-role source maps to the detected/configured destination root. Explicit declarations merge before defaults; destination collisions fail instead of stealing routes. Existing root-role mappings are preserved; root/blocker selection must remain consistent with the chosen primary root, never silently redirect a received root definition.
- **Fresh metadata:** with --bind-cleared, absent bindings are an empty in-memory routing document. Write metadata only after source validation and full output preflight. An existing malformed bindings file is not treated as absent. The default metadata location remains the supplied --bindings path; no manual YAML preparation is required.
- **Root precedence:** an explicit configured root wins. Init may accept --root for fresh metadata or a matching existing root; conflicting explicit selections fail. If the root source is already mapped, an explicit root must match one of its targets; otherwise select among its existing targets using agents > claude > instructions precedence, or use its sole existing custom target. Multiple unresolved custom targets require --root. Do not discover outside those mappings and silently retarget the definition. For an unmapped root source, detect names case-insensitively across destination-root files in the same priority and preserve actual spelling. Multiple case variants of the same preferred name require an explicit choice. If bulk enrollment includes a root role and no valid existing instruction root can be selected, exit 1 before writes with a named-root diagnostic; this plan creates bindings/payloads, not an invented root identity. Non-root-only operations may skip a nonexistent blocker target.
- **Safe new files:** newly registered region/raw targets and missing parent directories are created by init after preflight. Existing bound targets that disappear still fail. Existing marked region content and frontmatter remain byte-preserved outside core. New non-root region documents receive core/project structure and pending reconciliation; source project regions never copy.
- **New-file metadata:** seed only the source's identity/document metadata (`name`, `description`, `mode`, `version`, `role`, `status`, `license`, `compatibility`, `metadata`) when present; omit model/permission/tools/temperature/color and source-only arbitrary frontmatter fields. Derived runtime specs receive `local-version: 1.0.0`; profiles do not. The root must already exist, so its destination identity and header are preserved. Source frontmatter is not repeatedly synchronized.
- **Validation barrier:** source modes/roles, all mappings, all source payloads, root selection, unsafe aliases and every planned output must pass before any directory/payload/report/bindings/blocker mutation. Unexpected write-time IO errors can still leave partial work; no transactional rollback feature is claimed.
- **Prospective root safety:** simulate root selection after all planned creations using the same rules. A newly created raw file cannot become the implicit root, including instructions.md and case variants. Do not bypass this by prematurely marking an automatically discovered root as an explicit user choice.
- **Simplification:** keep the existing script and testkit, use four concern-focused new test modules, and replace stale tests rather than add compatibility wrappers. No new dependency, catalog, migration utility, destination registry or wrapper script.
- **Documentation/versioning:** core-sync skill becomes 2.0.0 for the breaking source contract. AGENTS.md changes only its project-owned reuse guide and compatible source version marker to 2.7.2; protected core bytes remain unchanged. Updated README avoids unsupported claims about automatic enrollment; the adoption story defines v2 behavior and removes historical destination-run events from feature acceptance.

## Write/delete manifest

| Action | Path |
|---|---|
| Modify | `.opencode/skills/core-sync/scripts/core_sync.py` |
| Modify | `distribution-clearance.json` |
| Modify | `.opencode/skills/core-sync/scripts/_core_sync_testkit.py` |
| Modify | `.opencode/skills/core-sync/scripts/test_core_sync_clearance.py` |
| Modify | `.opencode/skills/core-sync/scripts/test_core_sync_apply.py` |
| Modify | `.opencode/skills/core-sync/scripts/test_core_sync_root_selection.py` |
| Modify | `.opencode/skills/core-sync/scripts/test_core_sync_root_raw_alias.py` |
| Modify | `.opencode/skills/core-sync/scripts/test_core_sync_init_raw_enrollment.py` |
| Modify | `.opencode/skills/core-sync/scripts/test_core_sync_binding_validation.py` |
| Modify | `.opencode/skills/core-sync/scripts/test_core_sync_binding_serialization.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_clearance_metadata.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_clearance_mode_gate.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_bind_cleared.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_fresh.py` |
| Modify | `.opencode/skills/core-sync/SKILL.md` |
| Modify | `AGENTS.md` |
| Modify | `README.md` |
| Modify | `user-stories/aicore-adoption-sync.md` |

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | Implement v2 mode authority, bulk registration and fresh-init planning | Forge 🔨 (Implementer); configuration by Cipher 🔓 (Lead Orchestrator) | `phase-01-forge.md` | Source CLI/data contract and code-architecture report | G1, G2, G3, G4 |
| 2 | Migrate fixtures and verify v2 behaviors | Forge 🔨 (Implementer) | `phase-02-forge.md` | Contract/regression tests, architecture and execution verdicts | G1, G2, G3, G4 |
| 3 | Align guidance, story and final evidence | Cipher 🔓 (Lead Orchestrator) | `phase-03-cipher.md` | Reviewed docs/story, final audit and goal resume | G1, G2, G3, G4 |

## Critical files / tools

- Full-source research: Augur's sessions `ses_ed3aa710fffeUOGLjE2vmlW8yF` and `ses_ed3a50227ffeXTbES0s7rFLf6J`; their findings identify current mode, root, fixture and missing-input behavior, not an implementation verdict.
- `core_sync.py` metadata readers, registration merge, root resolver, write-target preflight, init output staging and all three commands; the existing script/testkit are the complete implementation boundary.
- `distribution-clearance.json` and the prior roster-clearance story change are user-authorized existing work; preserve them through representation migration.
- Story: `user-stories/aicore-adoption-sync.md`; index read-only for metadata/ownership checks. No new story.
- `AGENTS.md` and the skill source provide preservation and scope rules; runtime grants/dependencies are not changed.
- Reviews: Bastion 🧱 (Backend & Scripts Architect) for Python code; Crucible 🔥 (Test Architect) for test architecture/execution; independent Vault 🔐 (Catalog Steward) skill review and Sentinel 🛡️ (Quality Guardian) plan/root/story audit.

## Verification

- ⬜ **Phase 1 (G1–G4):** script syntax and schema/mode/role inventory checks pass; all 36 records have declared modes; Bastion 🧱 (Backend & Scripts Architect) code architecture `[PASS]`; legacy implementation sweep has no conflicting mode inference or inert fields.
- ⬜ **Phase 2 (G1–G4):** `uv run --frozen --group dev pytest -q` exits 0 through Crucible 🔥 (Test Architect); separate test-architecture `[PASS]`; complete metadata, mixed-mode, fresh-init, root-discovery and no-write regressions pass in temporary destinations.
- ⬜ **Phase 3 (G1–G4):** documentation and story audits `[PASS]`; `uv run --frozen python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/clearance-v2-bulk-init-20261011 --stories user-stories` exits 0; distinct final layered completion audit `[PASS]` before Outcome or archival.

## Phase verify commands

- Cipher 🔓 (Lead Orchestrator) runs non-Git mechanical checks directly; Crucible 🔥 (Test Architect) owns the approved test command. Prior test results do not certify v2.
- Python edits require scoped Bastion 🧱 (Backend & Scripts Architect) code review; every test-file edit gets a Crucible 🔥 (Test Architect) architecture review before proceeding. No new runner grant or dependency is needed.

## Audit

- Auditor: Sentinel 🛡️ (Quality Guardian)
- Verdict: [PASS]
- Findings: 0 — independent re-audit confirmed the configuration/Python actor split and the complete v2/fresh-init/root-discovery contract.
- Date: 2026-10-11

- Review history: initial `[BLOCK]` had one configuration-ownership finding; corrected actor attribution passed re-audit in session `ses_ed37a57b3ffesLXpSyKoKbJctu`.
- Self-verification passes: 2 — validator exits 0 with three phases; semantic review confirms source authority, fresh metadata/new-target creation, all-cleared scope, root precedence, exact phase/manifest equality and separate completion gates.

This is planning readiness. Final code, test architecture, execution and guidance evidence require a distinct completion audit.

## Out of scope / Do-not-touch

- No access or modifications to Tismart or any real destination. User alone handles removal of its core.yaml and later source refresh/sync. All fixtures and execution scenarios use tmp_path.
- No new eligible files beyond the existing 36; no mode inference from filenames/markers; no source-side adopter registry.
- No source root Mandatory core, agent spec/profile, harness permission/model config, package/dependency/lockfile, debt register, or unrelated skill changes.
- No commit/push/PR/merge operation is authorized by this plan.
- Do not preserve a v1 prerequisite, mode-selection default or fallback merely for compatibility when it conflicts with these goals.

## Pending

- **On hold** — sequenced after `plans/core-sync-clean-arch-20261011` (the core-sync clean-architecture refactor), which edits the same `core_sync.py`. Do not dispatch implementation until that plan completes; resume on top of the layered code.
- Later execution-review authorization turn; independent planning audit is `[PASS]`.

## Resolved decisions

- 2026-10-11 — User selected every cleared source, not an agent-only subset; enrollment must scale with the clearance record.
- 2026-10-11 — Source clearance owns raw/region policy; destination metadata owns paths. Root source role resolves through destination discovery, not source-side filename fallbacks.
- 2026-10-11 — Detect agents/claude/instructions root files automatically, honor explicit selection and preserve actual names.
- 2026-10-11 — User authorized breaking incompatible implementation behavior and requires fresh init after deleting destination core.yaml; G2 includes metadata/new-payload creation and G4 protects required stored targets rather than obsolete new-target prerequisites.
- 2026-10-11 — Tismart is excluded entirely from development/testing; schema-2 clearance replaces schema 1 without guessing legacy modes. Structurally compatible destination routing metadata is not source mode authority.
