# Plan — remediate post-implementation audit blockers

> **Status:** active
> **Started:** 2026-08-21 23:10
> **Subject:** Repair ticket-runbook scaffold validation, root-resolvable validator commands, test coverage, residual governance-contract contradictions, Warden's false provenance gate, and roster-wide CV/runtime conformance found by independent review.
> **Layout:** subfolder pattern

## Context

- Prompted by: independent Vault 🔐 (Catalog Steward) and Sentinel 🛡️ (Quality Guardian) audits after the self-verification and roster-boundary implementations reported four blockers.
- Goal: make a fresh ticket-runbook scaffold validate by design without allowing blanks in completed phases; make every documented validator command runnable from the project root; and make the remaining agent contracts satisfiable.
- Outcome: ticket-runbook has explicit scaffold, phase, and full-validation modes with coverage for the real template; its PyYAML runtime dependency is skill-local, exactly pinned, and UV-locked; documented runbook commands use that locked UV environment while plan-enforce remains stdlib `python3`; Sentinel's AGENTS.md structural contract and Marshal's Vault 🔐 (Catalog Steward) description match the approved governance split.
- Story: skipped — internal tooling and governance only; no product feature or user-visible behavior changes.

## Goals

- ☑ **G1:** A fresh, intentionally partial ticket-runbook scaffold passes structural validation, while an unfilled token in a completed phase still fails.
  - Done when: `--scaffold` validates the copied runbook templates after header initialization; full validation examines only completed phases through `Phase`; `--phase NN` remains strict for the completed phase.
- ☑ **G2:** Every touched validator or test command resolves from the project root and uses its actual runtime environment, with no stale path.
  - Done when: ticket-runbook commands use `uv run --locked --project .opencode/skills/ticket-runbook`; plan-enforce commands use root-resolvable `python3` paths; both validator/test module usage headers and touched historical plan commands match those contracts.
- ☑ **G3:** Tests cover the real ticket-runbook scaffold and its documented phase-aware behavior.
  - Done when: the runbook test suite copies the bundled templates, proves scaffold validation passes, proves future-template blanks are ignored by phase-aware full validation, and proves a blank in a completed phase fails.
- ☑ **G4:** Remaining governance contracts are internally satisfiable and the earlier plan's neutralization check no longer rejects legitimate `Gate` headings.
  - Done when: Sentinel 🛡️ (Quality Guardian) SP-3 defines AGENTS.md's root structure separately from OpenCode agent sections without a blanket exemption; Marshal 🎖️ (HR Director) calls Vault 🔐 (Catalog Steward) skills-catalog governance only; the self-verify plan's source-residue expression excludes generic `gate`.
- ☑ **G5:** PyYAML is portable and auditable as ticket-runbook's skill-local runtime dependency.
  - Done when: `.opencode/skills/ticket-runbook/pyproject.toml` exactly pins `PyYAML==6.0.3`; its committed `uv.lock` is current; the skill-local `.venv` is ignored; and Warden 🔒 (Dependency Warden) returns PASS with publisher provenance recorded separately as INFO when all required integrity controls pass.
- ☑ **G6:** Missing optional publisher provenance metadata is an INFO observation, not a release-blocking finding, when exact artifact-integrity controls pass.
  - Done when: Warden 🔒 (Dependency Warden) records provenance as `verified`, `unavailable`, or `indeterminate`; PyYAML's unavailable attestation with an approved source, exact pin, committed hashes, clean vulnerability scan, compatible environment, and MIT license produces INFO and permits PASS.
- ☑ **G7:** Warden 🔒 (Dependency Warden) escalates provenance only from concrete evidence, not missing optional metadata.
  - Done when: Warden 🔒 (Dependency Warden) ADVISORY requires an evidenced anomaly and BLOCK retains concrete compromise, injection, integrity-failure, or Critical/High vulnerability evidence; the report template separates provenance observations from findings.
- ☑ **G8:** All active-plan records and final gates reflect the corrected policy and a fresh independent audit proves it.
  - Done when: this plan's prior PyYAML release hold is reconciled; Sentinel 🛡️ (Quality Guardian) passes Warden's updated spec; and Warden 🔒 (Dependency Warden) returns PASS with an INFO provenance observation for the existing locked PyYAML artifact.
- ☑ **G9:** Every roster CV uses Sentinel's exact canonical structure and canonical roster role.
  - Done when: all 17 CVs use the mandated H1 and ordered `Personality`, `Traits`, `Role within the roster`, `Collaboration Style`, and final `What Name Does NOT Do` headings.
- ☑ **G10:** Every roster CV contains persona only; runtime specs contain all enforceable workflow and routing rules.
  - Done when: each CV's path, command, trigger, gate, output, and routing mechanics are removed only after its runtime counterpart is verified; Cipher's root runtime spec retains any moved lead-specific discipline.
- ☑ **G11:** The identified operating contradictions are resolved at their runtime source before the CVs are normalized.
  - Done when: Quill's correction model has an explicit user decision; all profile-versus-runtime contradictions use the runtime contract; and no CV preserves a competing operational rule.
- ☑ **G12:** Every runtime spec satisfies its applicable canonical structure without losing operational rules.
  - Done when: Quill 🪶 (note drafter), Ledger 📒 (record-keeper), Scribe ✍️ (docs & problem management), and Augur 🔮 (Senior Research Analyst) meet SP-3; Cipher's root spec meets its root mapping; all migrated prohibitions are retained in the appropriate runtime boundary.
- ☑ **G13:** Independent final audit proves roster-wide CV/runtime conformance and the corrected Warden 🔒 (Dependency Warden) policy together.
  - Done when: Sentinel 🛡️ (Quality Guardian) passes all CVs and runtime specs; Warden 🔒 (Dependency Warden) returns the policy-correct PyYAML PASS/INFO result; all plan validators and `git diff --check` pass.

## Current state

| Area | Current behavior | Evidence |
|---|---|---|
| Fresh scaffold validation | copied phase templates contain intentional fill markers, but full validation scans every present phase and exits non-zero | `ticket-runbook/SKILL.md:76-87`; `validate_runbook.py:261-277,527-532`; `references/runbook/phase-01-triage.md:25-31` |
| Phase awareness | header phase is parsed then passed to a function that explicitly does not use it | `validate_runbook.py:194-197,518-523` |
| Root commands | both skills prescribe `python scripts/...`; all four validator/test usage headers prescribe `python` or an obsolete path, which do not meet a root-resolvable runtime contract | `ticket-runbook/SKILL.md:87,107`; `plan-enforce/SKILL.md:235`; `validate_runbook.py:5-8`; `test_validate_runbook.py:4`; `validate_plan.py:5-8`; `test_validate_plan.py:4` |
| Test realism | runbook tests construct fully-filled synthetic phase files rather than copying the bundled scaffold | `test_validate_runbook.py:31-84` |
| Sentinel 🛡️ (Quality Guardian) AGENTS contract | AGENTS.md is exempt only from frontmatter/mode, but SP-3 still requires OpenCode-only section names | `sentinel.md:120-122`; `AGENTS.md:5,33` |
| Vault 🔐 (Catalog Steward) wording | Marshal 🎖️ (HR Director) calls Vault 🔐 (Catalog Steward) "skill/agent governance" although Vault 🔐 (Catalog Steward) is catalog-only | `marshal.md:33`; `vault.md:12-14` |
| Neutralization proof | the earlier plan's residue grep searches generic `gate`, which matches required Gate headings | `plans/self-verify-loops-20260820/plan.md:73`; `references/runbook/phase-01-triage.md:33` |
| Python dependency portability | `validate_runbook.py` imports PyYAML, but no Python manifest or lockfile is shipped | `validate_runbook.py:47`; Glob for `pyproject.toml`, `uv.lock`, and requirements files → no files found; Warden 🔒 (Dependency Warden) conditional review |
| Warden Python gate | Warden's bootstrap requires pnpm and has no Python-only branch | `warden.md:61-84`; Warden 🔒 (Dependency Warden) conditional review |
| Plan validator architecture | `validate_plan.py` still mixes file discovery/loading with structural and metadata evaluation | Bastion 🧱 (Backend Architect) Phase-2 audit: `validate_plan.py:137-140,150-153,173-180,184-198,211-220` |
| UV command executor | Warden 🔒 (Dependency Warden) may check but never generate a lock; Forge 🔨 (Implementation Agent) currently forbids every UV command | `warden.md:124-129`; `forge.md:115-124`; Augur 🔮 (Senior Research Analyst) UV grant brief |
| Runbook counter contract | Fresh templates/docs initialize `Query-budget` as `6/6`, while the validator defines the first value as used and treats `6/6` as exhausted | Vault 🔐 (Catalog Steward) final audit: `ticket-runbook/SKILL.md:78`; `references/runbook/runbook.md:6`; `phase-01-triage.md:13`; `phase-04-validate.md:6,12` |
| Scaffold phase validity | `--scaffold` parses but does not validate the `Phase` header | Vault 🔐 (Catalog Steward) final audit: `validate_runbook.py:659-702` |
| Story/index mechanical pass | `plan-enforce` says its loop checks story/index mirroring but omits `--stories user-stories` | Vault 🔐 (Catalog Steward) final audit: `plan-enforce/SKILL.md:232-236`; `validate_plan.py:320-321` |
| Vault format | Vault's runtime spec has roster-name and canonical persona-reference drift | Sentinel 🛡️ (Quality Guardian) final audit: `vault.md:10,20-22,28,30,39,51,104,191-197` |
| Provenance severity | Warden 🔒 (Dependency Warden) classifies missing optional Trusted Publishing metadata as ADVISORY and requires release acknowledgment even when all exact integrity controls pass | `warden.md:79,153-163`; Augur 🔮 (Senior Research Analyst) and Warden 🔒 (Dependency Warden) read-only policy reviews |
| CV structure | 16 of 17 CVs do not meet Sentinel's exact required heading sequence; only Investigator 🔍 (Incident Investigator) has all five canonical body headings | Sentinel 🛡️ (Quality Guardian) roster baseline audit; `sentinel.md:104-105` |
| Persona/runtime boundary | CVs duplicate operational triggers, commands, paths, gates, and routing that belong to runtime specs; five profile rules directly contradict runtime source contracts | Marshal 🎖️ (HR Director) CV migration map; Sentinel 🛡️ (Quality Guardian) roster baseline audit |
| Runtime structure | Quill 🪶 (note drafter), Ledger 📒 (record-keeper), Scribe ✍️ (docs & problem management), Augur 🔮 (Senior Research Analyst), and Cipher's root spec have stated SP-3 or root-mapping deficits | Sentinel 🛡️ (Quality Guardian) roster baseline audit |

## Behavior change

| Goal | Before | After | Interface contracts | Do-not-break |
|---|---|---|---|---|
| G1 | Fresh copied templates fail token scanning | `--scaffold` validates all copied files structurally without treating intentional template tokens as completed-phase errors | New `--scaffold` CLI mode; default/phase exit codes remain 0 pass, 1 violation | Header, budgets, Replay-candidate enum, required sections, and strict completed-phase token checks |
| G2 | Relative, obsolete, or host-Python command text fails or omits the skill environment | Locked UV command for ticket-runbook and root-relative `python3` command for stdlib plan-enforce everywhere this remediation touches command documentation | SKILL.md, validator/test usage headers, and historical-plan command text | Existing validator arguments and root working-directory workflow |
| G3 | Synthetic tests miss copied-template failure | Tests exercise copied bundled templates and phase boundary | Standard-library unittest suite | Existing violation and ledger-sync cases |
| G4 | Root-spec and catalog wording contradict contracts; audit proof has false positives | Exact root-spec structural mapping, skills-only Vault 🔐 (Catalog Steward) wording, precise residue pattern | Sentinel 🛡️ (Quality Guardian) SP-3, Marshal 🎖️ (HR Director) roster context, historical plan verification command | AGENTS.md remains Cipher's root spec; all non-structural SP checks remain applicable |
| G5 | PyYAML depends on a host environment and cannot receive a Python-specific Warden 🔒 (Dependency Warden) gate | Skill-local exact pin + `uv.lock`; Warden 🔒 (Dependency Warden) supports Python-only dependency auditing | skill-local `pyproject.toml`, `uv.lock`, `.gitignore`, Warden 🔒 (Dependency Warden) Python bootstrap | `yaml.safe_load()` and no root manifest solely for this skill |
| G6/G7 | Missing optional provenance metadata is treated as release-blocking risk | Evidence state is separate from severity; verified integrity with unavailable provenance is INFO/PASS, while concrete anomalies retain ADVISORY/BLOCK | Warden 🔒 (Dependency Warden) Python branch, gate definitions, and audit-report evidence sections | Exact pins, hashes, approved source, CVE/license checks, and concrete supply-chain stops |
| G8 | Active records repeat the disproven PyYAML release hold | Plan records require an evidence-separated Warden 🔒 (Dependency Warden) PASS/INFO result | Active plan and Phase 1/4 provenance references | Prior exact pin, lock, audit, compatibility, and no-release evidence |
| G9/G10 | CVs use inconsistent headings and duplicate operational content | Every CV uses the canonical structure and contains persona only; operations remain in verified runtime authorities | 17 CVs and their mapped runtime authorities | Persona voice, canonical roster roles, and every operational boundary |
| G11/G12 | Profile/runtime contradictions and five runtime authorities violate applicable structure | Runtime source resolves conflicts before CV edits and every authority meets SP-3 or its root mapping | Quill 🪶 (note drafter) decision record; Quill 🪶 (note drafter)/Ledger 📒 (record-keeper)/Scribe ✍️ (docs & problem management)/Augur 🔮 (Senior Research Analyst) specs; `AGENTS.md` | User authority over Quill 🪶 (note drafter) behavior and all existing operational safeguards |
| G13 | Piecemeal audits cannot prove the full roster satisfies one standard | Sentinel 🛡️ (Quality Guardian) and Warden 🔒 (Dependency Warden) independently verify the full roster and corrected dependency policy | Full CV/runtime audit, locked PyYAML audit, plan validators | No release action and no downgrade of concrete Warden 🔒 (Dependency Warden) findings |

## Design decisions

- Use three modes rather than weakening all token checks: `--scaffold` validates the intentional-template state; `--phase NN` strictly validates the phase just completed; default validation checks completed phases through the header. Rejected: globally allow every fill token, because it would hide an incomplete completed phase.
- Keep phase-template structural checks in scaffold mode. Rejected: skip phase validation entirely at scaffold time, because a copied or damaged template could then be accepted.
- Define AGENTS.md's equivalent root structure inside SP-3 instead of forcing it into OpenCode headings or broadly exempting it. Rejected: adding OpenCode frontmatter/sections to the root spec, because the user established AGENTS.md as Cipher's intentionally distinct runtime spec.
- Retain PyYAML rather than hand-parse YAML: user selected UV package management. Keep it skill-local with `PyYAML==6.0.3`, a committed `uv.lock`, and `yaml.safe_load()`. Rejected: untracked host dependency (not portable) and a root Python manifest (would make one skill's dependency global).
- The initial remediation used four phases: Warden's Python policy joined Marshal's existing agent-spec contract phase, and the historical-plan regex correction rode with Vault's skill-contract phase. User-authorized G6–G8 extend it with Phase 5 policy correction, Phase 6 record reconciliation after restart, and Phase 7 independent acceptance.
- Apply Sentinel's exact CV standard; do not weaken it to fit existing profiles. Preserve persona voice as prose within canonical sections, and move enforceable operational content to existing runtime authorities rather than discarding it.
- Use each runtime spec as the authority when a CV conflicts with it. Quill's two conflicting runtime correction instructions have no CV-authority resolution and require the user's explicit decision before its runtime restructuring.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | Python dependency policy and governance repair | Marshal 🎖️ (HR Director) | `phase-01-marshal.md` | Python-only audit branch; one-plan UV grant; corrected root-spec and catalog wording | G4, G5 |
| 2 | Phase-aware validator, architecture remediation, and locked PyYAML | Forge 🔨 (Implementation Agent) | `phase-02-forge.md` | clean Python modules/tests; skill-local UV manifest, lockfile, and ignore rule | G1, G2, G3, G5 |
| 3 | Root command and validation-contract documentation | Vault 🔐 (Catalog Steward) | `phase-03-vault.md` | UV-accurate skill instructions/checklist and precise historical verification expressions | G1, G2, G4 |
| 4 | Independent final acceptance audit | Cipher 🔓 (L2 Lead) | `phase-04-cipher.md` | Independent gate evidence returned to the lead | G1, G2, G3, G4, G5 |
| 5 | Evidence-based provenance policy | Marshal 🎖️ (HR Director) | `phase-05-marshal.md` | INFO/ADVISORY/BLOCK provenance classification, report contract, and CV/runtime routing consistency | G6, G7, G8 |
| 6 | Reconcile historical gate records | Cipher 🔓 (L2 Lead) | `phase-06-cipher.md` | Current plan and its prior policy phases match the corrected Warden 🔒 (Dependency Warden) rule | G8 |
| 7 | Provenance-policy acceptance audit | Cipher 🔓 (L2 Lead) | `phase-07-cipher.md` | Independent evidence that PyYAML passes with visible INFO provenance state | G6, G7, G8 |
| 8 | Resolve runtime decision and map | Cipher 🔓 (L2 Lead) | `phase-08-cipher.md` | Recorded Quill 🪶 (note drafter) correction decision and verified content-migration map | G10, G11 |
| 9 | Runtime canonicalization | Marshal 🎖️ (HR Director) | `phase-09-marshal.md` | SP-3/root-conformant runtime contracts | G10, G11, G12 |
| 10 | Incident CV canonicalization | Marshal 🎖️ (HR Director) | `phase-10-marshal.md` | Four canonical incident CVs with no duplicate operating rules | G9, G10, G11 |
| 11 | Dev CV canonicalization | Marshal 🎖️ (HR Director) | `phase-11-marshal.md` | Nine canonical dev CVs with runtime-authoritative operations | G9, G10, G11 |
| 12 | Cross-cutting CV canonicalization | Marshal 🎖️ (HR Director) | `phase-12-marshal.md` | Four canonical cross-cutting CVs and Cipher 🔓 (L2 Lead) root discipline alignment | G9, G10, G12 |
| 13 | Roster and policy acceptance audit | Cipher 🔓 (L2 Lead) | `phase-13-cipher.md` | Full independent/plan evidence for all thirteen goals | G8, G9, G10, G11, G12, G13 |

## Critical files / tools

- `.opencode/skills/ticket-runbook/SKILL.md`, `references/_consistency-checklist.md`, `scripts/validate_runbook.py`, `scripts/test_validate_runbook.py`, `pyproject.toml`, `uv.lock`, `.gitignore`
- `.opencode/skills/plan-enforce/SKILL.md`, `scripts/validate_plan.py`, `scripts/test_validate_plan.py`
- `plans/self-verify-loops-20260820/plan.md`, `phase-01-vault.md`, `phase-02-vault.md`
- `.opencode/agents/forge.md`, `.opencode/agents/sentinel.md`, `.opencode/agents/marshal.md`, `.opencode/agents/warden.md`, `agents/warden/profile.md`
- `plans/audit-remediation-20260821/phase-05-marshal.md`, `phase-06-cipher.md`, `phase-07-cipher.md`
- `agents/{atrium,bastion,crucible,forge,herald,inquisitor,lumen,sentinel,warden,investigator,quill,ledger,scribe,cipher,augur,marshal,vault}/profile.md`
- `.opencode/agents/{quill,ledger,scribe,augur}.md`; `AGENTS.md`; `plans/audit-remediation-20260821/phase-08-cipher.md`, `phase-09-marshal.md`, `phase-10-marshal.md`, `phase-11-marshal.md`, `phase-12-marshal.md`, `phase-13-cipher.md`

## Verification

- ☑ G1/G3: `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py` → 21 tests pass, including real scaffold and completed-phase token cases
- ☑ G2: `python3 .opencode/skills/plan-enforce/scripts/test_validate_plan.py` → 21 tests pass from project root
- ☑ G2: `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py --help` → exit 0 from project root
- ☑ G4/G5: Vault 🔐 (Catalog Steward) has no skill findings and Sentinel 🛡️ (Quality Guardian) has no governance findings; Warden 🔒 (Dependency Warden) returns PASS with the documented PyYAML INFO provenance observation after all integrity controls pass.
- ☑ G6: Warden's current locked PyYAML audit returns PASS with its exact provenance state recorded as INFO after all integrity controls pass
- ☑ G7: Warden's report template and severity rules expose provenance state separately and escalate only evidenced anomalies
- ☑ G8: Sentinel 🛡️ (Quality Guardian) passes the updated Warden 🔒 (Dependency Warden) spec and active-plan records contain no false PyYAML release hold
- ☑ G9: Incident-CV audit returns no heading, H1 role, or final-boundary deviation across the four incident profiles
- ☑ G9: Dev-CV audit returns no heading, H1 role, or final-boundary deviation across all nine dev profiles
- ☑ G9: Cross-cutting-CV audit returns no heading, H1 role, or final-boundary deviation across the four cross-cutting profiles
- ☑ G10/G11: Every migrated operational statement traces to a verified runtime counterpart; the selected correction behavior is user-decided and has one runtime contract
- ☑ G12: SP-3/root mapping audit passes for all 17 runtime authorities
- ☑ G13: Persisted independent audits return PASS; all three active and two completed plan validators and `git diff --check` exit zero

## Out of scope / Do-not-touch

- Ticket-record schema validators and models
- Skill versions and non-Python dependencies
- Incident ticket data, docs/wiki, problem records, and `output/`
- Rewriting runbook phase content or workflow semantics beyond validation-mode documentation
- Commits, pushes, branches, and PRs

## Resolved decisions

- 2026-08-21 — User confirmed the four remediation goals, programming-plan classification, and no user story after an explanation of each blocker.
- 2026-08-21 — Fresh scaffolds retain intentional template tokens; strict token validation applies when a phase is completed, not to future template files.
- 2026-08-21 — User selected UV package management for PyYAML. G5 adds the approved skill-local manifest/lockfile and Python-only gate; the existing blocked implementation work is resumed only after phase 1's policy update.
- 2026-08-22 — User authorized the smallest one-plan Forge 🔨 (Implementation Agent) UV exception: exact ticket-runbook lock generation plus its locked unittest and help checks; every other UV command remains forbidden.
- 2026-08-22 — All source and test gates passed before the Warden 🔒 (Dependency Warden) policy correction. The former PyYAML publisher-provenance release hold was disproven and is reconciled by phases 5–7; no acknowledgment or release was requested.
- 2026-08-22 — User identified the mandatory provenance advisory as a false positive and authorized three goals: classify absent optional provenance as INFO after verified integrity, retain escalation for concrete anomalies, and reconcile/re-audit the affected records.
- 2026-08-22 — The quality audit found an obsolete `.gitignore` routing rule in the dependency CV that contradicts the runtime spec. User authorized removing that workflow rule from the CV; the runtime spec remains the single workflow source of truth.
- 2026-08-23 — User directed that Sentinel's CV standard be applied, not relaxed. The roster-wide migration preserves persona voice, moves operations to runtime sources, and resolves runtime contradictions before CV normalization.
- 2026-08-23 — User set Quill's correction contract: surgical patch by default; fresh complete draft only on explicit user request. The owner-first migration map records all runtime moves and stale retirements before profile edits.
