<!-- core:begin -->
# User story — concise-skill-authoring

> **Created:** 2026-10-18
> **Title:** Concise skill authoring
> **Status:** active
> **version:** 1.0.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/git-branch-name/`, `.opencode/skills/git-commit/`, `.opencode/skills/git-pr/`, `.opencode/skills/op-skill-creator/`, `.opencode/agents/vault.md`

## Persona

- A maintainer creating or revising reusable skills.

## Goal

- **G:** Skills provide concise, portable instructions without coupling their procedures to a particular project's implementation or environment.
  - Done when: the Git skills and creator follow the acceptance criteria while preserving their existing functional and safety contracts.

## Scenario

- A maintainer invokes a Git skill and receives the expected naming suggestion or draft through minimal, generic instructions.
- A maintainer creates or revises a skill, and the creator applies the same authoring rules.

## Acceptance criteria

- ✅ **AC1 — Standard structure:** Skills use Agent Skills packaging and metadata, clearly distinguishing standard requirements from OpenCode-specific behavior and local conventions.
- ✅ **AC2 — Necessary content:** Instructions contain only necessary steps, decisions, safeguards and outputs. Obvious explanations, duplicated content and unnecessary sections are absent.
- ✅ **AC3 — Generic procedures:** Instructions describe required actions and outcomes rather than fixed command or code recipes. Necessary environment-dependent invocations use project-defined bindings instead of hardcoded runners.
- ✅ **AC4 — Explicit inputs:** Required inputs and missing-input handling are clear, without assuming Claude-specific argument substitution.
- ✅ **AC5 — Preserved Git behavior:** Naming conventions, draft artifacts, approval requirements, mutation restrictions and evidence ownership remain intact.
- ✅ **AC6 — Consistent authoring:** The creator and catalog checks apply these same rules; Examples and Troubleshooting sections are not mandatory when they add no necessary guidance.

## Proof

- AC1 → `.opencode/skills/op-skill-creator/SKILL.md` `## Steps` items 3–5 name, description and string-to-string metadata validation · `## Portable, runtime and local layers` · `.opencode/agents/vault.md` `#### Quality Checklist` authority paragraph
- AC2 → `.opencode/skills/git-branch-name/SKILL.md`, `.opencode/skills/git-commit/SKILL.md`, and `.opencode/skills/git-pr/SKILL.md` `## Steps` compact procedures · `.opencode/skills/op-skill-creator/SKILL.md` `## Generated body requirements`
- AC3 → `.opencode/skills/op-skill-creator/SKILL.md` `## Generated body requirements` project-binding clause and `## Pre-write checks` binding check · `.opencode/skills/git-pr/SKILL.md` `## Steps` item 1 unresolvable-base stop
- AC4 → `.opencode/skills/op-skill-creator/SKILL.md` `## Inputs`, `## Rewrite, rename and migration` independent cleanup/path choices and helper-preservation sequence, and `## Rules` stop-on-missing-input · `.opencode/skills/git-pr/SKILL.md` `## Steps` item 1 base resolution · no `$ARGUMENTS` interpolation in any rewritten skill
- AC5 → `.opencode/skills/git-branch-name/SKILL.md` `### Type`–`### Description`, `## Rules` · `.opencode/skills/git-commit/SKILL.md` `## Message format`, `## Rules` · `.opencode/skills/git-pr/SKILL.md` `## Draft and body contract`, `### Post-PR evidence contract`, `## Rules`
- AC6 → `.opencode/skills/op-skill-creator/SKILL.md` `## Generated body requirements` and `## Pre-write checks` · `.opencode/agents/vault.md` QC-11 and QC-12 conditional applicability · OC-2 compact-body check

## Constraints

- Rewrite only the three Git skills and the creator — because this is the requested scope.
- Permit only necessary supporting governance and Proof-reference updates — because the rules and their references must remain consistent.
- Preserve the existing project-owned command-binding policy — because reusable instructions must not impose a source environment.
- No Git, publication or release authority is added — because rewriting guidance does not authorize those actions.

<!-- core:end -->

<!-- project:begin -->
## Approval record

- 2026-10-18 — The user selected CREATE after catalogue and ownership review, reviewed the six-criterion contract and metadata proposal, clarified that necessary Python invocations use the existing project-defined runner binding, and authorized continuation with "nice, u can continue". The proposed exact-command exception was withdrawn before this approval. This approves the behavioral contract and staged story persistence, not skill implementation or release.

## Local evidence

- 2026-10-18 — Runtime governance: `.opencode/agents/vault.md` `1.5.0`, SHA256 `c59695579745410554eaf072a6510e9dd05a48fb38610ba7ec89b20d4eb7a38e`; Sentinel 🛡️ (Quality Guardian) `sentinel-runtime-2` `[PASS]`, zero findings, SP-1–SP-12.
- 2026-10-18 — Skills: `git-branch-name` `1.1.1` `4310e7bc…90975`; `git-commit` `1.2.2` `8d7d6825…a9a9c`; `git-pr` `1.6.1` `b623840b…003fd`; `op-skill-creator` `1.3.0` `4aa43978…3500c`. Independent review `csa-skills-reviewer-2` `[PASS]` after remediating three findings (portable-versus-local name uniqueness, degraded-mode trigger convention, unresolvable-base stop); one advisory accepted: the creator's trigger example is permissive against the literal catalog form, with audit ownership retained by the catalog owner.
- 2026-10-18 — Structural checks: plan/story validator exit 0; frontmatter metadata assertions pass for all four skills; `git-branch-name` and `git-commit` byte-unchanged during remediation.
- 2026-10-18 — The preceding skill/final PASS acceptance was invalidated by fresh review `vault-recheck-2` after original-to-candidate comparison `herald-recheck-1` against `af36e6cddd37079abdf043c8835df6d154f260d5`: creator `4aa439786cc1e30537f03477a322c04c21c6e87cdcfd8e744deba66f5200350c` lost cleanup choices, helper transfer and metadata type checks and added source-specific UV wording. AC1/AC3/AC4/AC6 were not established at that failed snapshot; unchanged AC2/AC5 evidence was preserved. User authorized corrective work. The false-PASS process failure is separately recorded as DEBT-010, not cleared by implementation repair.
- 2026-10-18 — Corrected creator SHA256 `4c1d2925305af9d1899879b636c8607519621745b55551144ebb50f526238237`, version `1.3.0`: independent review `vault-correction-review-1` `[PASS]` restored all four failed obligations. Clause-application walkthroughs covered migration plus keep, rename/prefix plus helpers and archive, declined cleanup, invalid list/numeric metadata, non-UV project binding, target collision and intentional retained-source references; these were textual reviews, not live migration or script execution. Coordinator verified metadata types and unchanged three Git-skill identities. This evidence restores the affected marks; final story/plan reconciliation remains separately gated.

## Revision tracking

- 2026-10-18 — Delivered by PR #71 on branch `feat/skills/concise-skill-authoring` (feature commit `ce3e0b2b0fc2dff3ae33957805477ba2f07c91f9`, debt commit `83d0e5ccc6879a1394e73867ef750c272f6829de`). Pending delivery tracking resolved: the reviewed Proof surfaces and corrective evidence above are the accepted basis for AC1–AC6. The false-PASS process debt remains open separately as DEBT-010 and is not cleared by this delivery. No distribution clearance or destination mutation is authorized.

## Change log

- 2026-10-18 — concise-skill-authoring (PR #71): created the feature definition; condensed the three Git skills into generic portable procedures and aligned the creator and catalog checks with conditional authoring guidance (`vault` `1.5.0`, `op-skill-creator` `1.3.0`, Git skills patch-level).

<!-- project:end -->
