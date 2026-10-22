# Plan — Incremental agent-workflow foundation

> **Status:** active
> **Started:** 2026-10-21 02:20
> **Subject:** Establish a discoverable agent workflow, explicit document homes, and an ADR without a broad workflow rewrite.
> **Method:** Standalone plan authored by Cipher 🔓 (Lead Orchestrator), not generated or validated through the current plan-enforce procedure, as explicitly requested by the user.
> **Execution:** A–F instructions are written but not accepted as a combined delivery. The full-content audit found F01–F12; the user authorized their repair with “fix them”. Remediation below is current; comparative pilots and final acceptance remain pending. Not complete, not released.

## Context and authority

The user wants faster preparation, fewer corrective review loops, and trustworthy completion. The first delivery must establish a base pattern for AI agents, define the target file/folder structure now, introduce ADRs now, and let subsequent work correct remaining defects incrementally. The user also explicitly warned that subagents can inherit contradictory rules: their reports are inputs to verify, not authorities that settle a conflict.

The current-task exception concerns use of the existing planning procedure. It is not a permanent bypass, permission change, release authorization, or waiver of clean architecture, truthful evidence, role ownership, independent review, contract approval, or the later execution-authorization turn. Keep the existing plan-enforce binding and its default applicability unchanged. Do not claim its full stash gate or validator has passed for this custom plan.

This is a documentation/runtime-navigation foundation, not application or script implementation. It consumes the approved, active `agent-workflow-navigation` story; approval is not delivery evidence. No durable document may cite this temporal plan as its delivery evidence.

## Goals

- ⬜ **G1: Every new artifact has a defined home, and agents have a discoverable entry point.**
  - Issue: Navigation, enduring policy, historical decisions, and temporary execution material are easy to confuse; the repository already contains a root-level historical workflow decision record.
  - How: Define the target tree below, add an explicitly read workflow entry, record the architecture decision, and move the existing history intact to its final home. Retain the established runtime, skill, persona, story, plan, and code locations.
  - Files: `AGENTS.md`; `knowledge/agent-workflow.md`; `README.md`; `docs/architecture/decisions/0001-agent-workflow-foundation.md`; `planning-workflow-decisions.md` → `docs/architecture/history/planning-workflow-decisions.md`.
  - Done when: Root instructions explicitly require reading the entry; its references resolve; the ADR explains placement and migration; historical bytes are preserved at the new path and the old path is absent.

- ⬜ **G2: Agents assess requests critically and report encountered conflicts clearly without silently widening work.**
  - Issue: A universal story authority would confuse behavior with permissions; indiscriminate obedience, approval requests, and speculative blockers all damage reliability.
  - How: Establish one canonical owner per concern, a short routing sequence, common ordinary-feedback fields, and impact-based conflict dispositions. Clarify the root's existing question-routing tension only as needed for this pattern.
  - Files: `knowledge/agent-workflow.md`; `AGENTS.md`; `user-stories/agent-workflow-navigation.md`; `user-stories/index.md`.
  - Done when: Scenario review establishes critical assessment of both user and subagent input, explicit authority/evidence distinctions, affected-work blocking, safe deferral routing, and preservation of existing role-specific formats and mandatory checks.

- ⬜ **G3: The foundation is verifiable and distributable without claiming the old defects are fixed.**
  - Issue: A root pointer to an undistributed file would break adoption; an ADR or new prose alone cannot prove reliable future execution.
  - How: Clear the new shared file in the existing format, document that clearance, reconcile the approved story delta, and independently review the final combined candidate and a bounded scenario set.
  - Files: `distribution-clearance.json`; `distribution-clearance.definition.md`; `knowledge/agent-workflow.md`; `user-stories/agent-workflow-navigation.md`; `user-stories/index.md`; `README.md`.
  - Done when: Shared references are available and neutral, source-local history remains excluded, evidence is current and durable, and independent findings are resolved. No speed improvement, repository-wide consistency, or debt retirement is claimed from this foundation alone.

## Evidence inspected and limits

| Evidence | Consequence |
|---|---|
| `AGENTS.md`, Identity & Role / Shared agent rules / Conventions | Root is an active runtime, not just an index; existing pushback, ownership, evidence, and approval boundaries remain. Lines 65–71 contain the question-routing tension relevant to G2. |
| `knowledge/agents.md`, ownership, evidence, reports, coordination, clean architecture | These remain canonical cross-cutting policies. The entry routes to them instead of copying their rules. |
| `user-stories/plan-lifecycle-governance.md`, AC12, AC20, AC26, AC28, AC30–37 | Preserve existing planning promises and evidence. Catalogue review corrected the initial ownership proposal: cross-workflow navigation has a distinct trigger/outcome and must not overload this planning-only contract. |
| `user-stories/user-story.md`, AC2–8; story skill and checklist | Behavior approval and collision review remain separate from execution authorization. Full-catalogue review is currently required; this foundation does not silently replace it with filtered search. |
| `user-stories/clean-architecture-contract.md`, AC10–14; adoption-governance contract | Keep necessary touched-file rework, snapshot-bound reviews, actual review owners, and neutral shared payloads. |
| `planning-workflow-decisions.md`, entire file | This is explicitly historical and records prior decisions, not current execution authority. Preserve it instead of drafting a competing historical account. Its old duration/cause claims remain historical, not new measurements. |
| `distribution-clearance.json` and its definition, Knowledge distribution classes | A shared workflow file needs explicit region clearance and a matching class description; no schema or synchronization code change is needed. |
| Root listing, README, `.gitignore` | No `docs/` tree is present in the inspected checkout. Introduce only the decision/history homes required here; keep temporary work out of the root. |
| `knowledge/debt.md`, DEBT-011 and DEBT-012 | Review reliability and release-artifact placement remain open. DEBT-008/009/010 retirement is recorded as provisional. Do not alter or retire these records in this delivery. |

Accepted scope advice: `foundation-vault-1` and `foundation-vault-2`; important recommendations were checked against the actual texts above. The second assignment's proposed separate workflow home is accepted because the user subsequently required placement/routing to be defined now; it is not accepted merely because the report recommends it.

Planning-only safety inventory: `foundation-herald-1` ran permitted `git status --short` and bare `git stash list`, both exit 0. It reported an existing modification to `knowledge/debt.md` and no stash entries. That modification is outside this manifest and must be preserved. No remote proof, full legacy stash-gate verdict, or all-pending-changes disposition is claimed.

Readiness review: `foundation-catalogue-A` and `foundation-catalogue-B` compared the proposal with all 17 existing story bodies; Cipher 🔓 (Lead Orchestrator) read the three locally truncated historical lines separately. Coordinator checks found 17 files/17 matching index rows, no metadata mismatch. Compatible dependencies preserve story approval, architecture, safe coordination, incident ordering, specialized reporting, and source-neutral distribution. The user explicitly approved CREATE of the separate four-criterion story after the paired ownership/collision findings; no existing criterion was silently retired.

Refreshed local safety inventory `foundation-herald-2`: only the existing debt edit and this plan folder were reported before preparation; stash list was empty and `refs/stash` was absent. The first-manifest paths had no stashed overlap. `foundation-scribe-readiness` accepted local repository drafting under the root delegation, expressly excluding incident/wiki publication, problem-record operations, Git and destination mutations. These scoped results resolve the previous readiness advisories; they are not a full legacy remote/ancestry gate.

## Target structure and placement rules — decide now

```text
AGENTS.md                              active orchestrator runtime; mandatory entry pointer
README.md                              human project overview and source-local document map
knowledge/
  agent-workflow.md                    NEW shared agent entry/routing and ordinary feedback
  agents.md                            existing shared policy and architecture owner
  debt.md / problems.md / symptoms.md  existing registers; ownership unchanged
  diagnostic-system-design.md         existing diagnostic design; ownership unchanged
.opencode/
  agents/                              existing role authority and language-specific conventions
  skills/<skill>/SKILL.md              existing reusable procedure owner
  skills/<skill>/references/           supporting non-executable reference material
  skills/<skill>/scripts/              executable tooling, with existing clean-architecture layers
agents/<name>/profile.md               persona only; no workflow duplication
user-stories/                          approved contracts/catalogue; new agent-workflow-navigation.md
docs/architecture/
  decisions/0001-agent-workflow-foundation.md    NEW source-local ADR
  history/planning-workflow-decisions.md       MOVED source-local historical record
plans/<task>/plan.md                   temporary execution contract, not durable requirements
output/                               existing ignored temporal reports, not sole durable proof
```

- These are final homes for their named responsibilities, not staging folders. Do not introduce an extra workflow index, engineering handbook, skill, or competing story catalogue in this slice.
- Current cross-language engineering conventions remain in `knowledge/agents.md`; language/library interpretations remain in their applicable role specifications. The entry names these owners. Do not duplicate conventions into stories or ADRs.
- ADRs capture context, decision, status, alternatives, and consequences. They link to current contracts/policies; they do not grant permissions or override them. New significant decisions use this decision directory; local decision history is not a shared mandatory payload.
- New shared requirements go to the owning story; procedures to their owning skill; common policy to shared rules. New files require a distinct responsibility and owner, not just a convenient empty directory.
- The historical move is the only relocation in this increment. Preserve bytes, update any actual consumers, and remove the old source only after parity is established. Future moves must update consumers and transport bindings atomically; do not leave two active canonical copies.
- Do not create empty reserved folders or migrate application/tooling code just to match a diagram. Existing domain/application/infrastructure boundaries and permitted implementation judgment are unchanged.

### Small-document budgets

The user explicitly rejects new documentation growing into massive files. These are enforceable first-increment delivery limits, not portable policy constants to impose on adopting projects:

| Surface | Maximum lines | Maximum words |
|---|---:|---:|
| New `knowledge/agent-workflow.md`, whole file | 100 | 900 |
| New ADR, whole file | 80 | 600 |
| Root runtime additions, relative to its captured original | 10 | 150 |
| README additions, relative to its captured original | 20 | 250 |
| New foundation story, whole file including local evidence | 80 | 600 |

Measure both limits; long lines cannot hide excessive content. Keep feedback as one reusable envelope, owners as pointers, and scenario evidence concise. Do not copy policy bodies, append running execution transcripts, or mechanically split an oversized document into fragments. If sufficient content will not fit, return a concrete simplification or distinct-responsibility proposal before expanding scope. Subsequent tasks must preserve the entry's bounded responsibility rather than grow it into a handbook; changed local size policy requires explicit review at its owner.

The relocated history is an unchanged pre-existing artifact, not a new authored guide or an exception allowing new large files. Do not append to it or require agents to load it during routine work. Existing large-file cleanup remains separate.

### File boundaries and splitting protocol

| File | Keep here | Do not accumulate here / extraction destination |
|---|---|---|
| `AGENTS.md` | Runtime identity, authority, mandatory entry pointer. | Workflow detail goes to the guide; procedure detail to its owning skill. Do not copy either back into root. |
| `knowledge/agent-workflow.md` | Four short routing sections: find authority, assess a request, report an outcome, handle conflict. Include the shared growth/splitting principle. | Behavioral promises belong in the owning story; full cross-cutting policy in `knowledge/agents.md`; language-specific conventions in their existing role rulebook; execution steps in the owning skill. Link/read those owners instead of expanding the entry. |
| New ADR | One structural decision: context, decision/placement map, alternatives, consequences and status. | A different decision gets the next distinctly named ADR under `docs/architecture/decisions/`; supporting historical narrative belongs in `docs/architecture/history/`. Neither becomes runtime instruction by relocation. |
| New story | Its single behavioral outcome, scenarios, four criteria, Proof pointers, constraints and compact local approval/evidence/history. | Execution sequences stay in plans; recurring procedures in skills; detailed proving material at its real durable owner. Retain concise evidence references, never an endless transcript. |
| Relocated history | Existing bytes, unchanged. | Append nothing; new decisions use ADRs and current requirements use their actual owners. |

**When and how to split:** Before a planned addition exceeds either file budget, or introduces a separately owned responsibility, identify the reader, concern, owner and inputs/outputs. First remove duplication and route content to an existing canonical owner. If extraction is still necessary, select a named, independently meaningful concern—not `part-1`/`part-2`, arbitrary line ranges, or one file per heading. State its purpose, applicability and governing owner; keep the parent as the short entry and explicitly require reading the extracted material when applicable. Extract skill support to `.opencode/skills/<skill>/references/<concern>.md`; executable tooling stays in `scripts/` under its existing architecture. A genuinely new common policy uses `knowledge/<concern>.md`, not another workflow guide. New paths outside this manifest require approved scope and their own budgets before creation.

**Migration acceptance:** Move each obligation to exactly one authoritative home; replace the old body with an appropriate pointer, update all actual consumers/Proof/catalogue/clearance references together, and verify obligations, links and transport availability before deleting the superseded copy. Shared required references must be cleared in the same delivery; source-local evidence cannot become an undeclared shared dependency. If no coherent separate responsibility exists, simplify rather than manufacture more files. Existing giant files are corrected only in their assigned later slice. Teach this principle briefly in the shared guide; keep this delivery's numeric budgets and source-local placement rationale in the ADR, not portable mandatory policy.

## Approved foundation contract and operating pattern

Owner: `user-stories/agent-workflow-navigation.md`, approved through the user's explicit “Approve CREATE (Recommended)” selection following catalogue/collision review. Selected delivery scope is AC1–AC4: discoverable authority, critical assessment, clear ordinary feedback, and encountered-conflict handling. G1 traces to AC1; G2 to AC2–AC4; G3 verifies all four and their distribution boundaries. Existing planning-story AC38–AC40 were only a discarded proposal and are not added. Existing-story repairs remain scheduled in stages C–F.

The guide's public section names are `Find the governing source`, `Assess the request`, `Report an outcome`, and `Handle a conflict`, matching the story's planned Proof pointers. These are proving targets, not claims of implementation. The source-local ADR records layout/rationale rather than granting authority. Runtime changes add the explicit guide read and clarify the broad question clause consistently with existing evidence-first, user-only decision routing; they must not remove a required approval. Update source-local shared-story lists/counts to include the new region-cleared story in the same change.

The shared workflow will be a short entry sequence: critically assess the request and evidence; identify the behavioral and engineering owners; load applicable instructions and relevant dependencies; determine allowed scope/resources; route work to existing procedures and actors; verify applicable evidence; report the result and remaining decisions. Explicitly retain any required full reads, incident register-first ordering, approvals, and owner gates. It is navigation plus common interaction behavior, not a replacement execution engine.

Ordinary recurring messages share result/status → governing source and observed evidence → impact/scope → recommendation/next action → decision needed (`none` when factual). Use explicit conflict/blocker/decision/review/completion labels as appropriate; omit irrelevant fields in routine progress updates. Preserve the existing PR-round format and role-specific audit/incident formats rather than copying a long template into every reply.

For encountered defects: fix only authorized in-scope issues; stop affected work for unmet selected requirements, safety/authority conflicts, or necessary scope changes; route unrelated issues to the existing owner/register with the required explicit deferral. Do not allocate debt entries or mutate that register in this increment. An unresolved finding reported for later consideration is not automatically accepted nonblocking debt.

## First increment: original write/delete manifest

| Action | Path | Purpose |
|---|---|---|
| Modify | `AGENTS.md` | Explicit required workflow read; narrow clarification of question routing; source runtime version bump; source-local shared-story set update. Keep other authority and planning bindings. |
| Add | `knowledge/agent-workflow.md` | Neutral core/project-governed foundation at its final home. |
| Add | `docs/architecture/decisions/0001-agent-workflow-foundation.md` | Source-local ADR for the structure and incremental approach; status truthful to actual approval/delivery. |
| Add | `docs/architecture/history/planning-workflow-decisions.md` | Byte-preserving historical relocation, not a rewrite or newly accepted baseline. |
| Delete | `planning-workflow-decisions.md` | Remove only as the matched relocation, never as cleanup of unfamiliar work. |
| Modify | `README.md` | Explain final homes and ADR discovery; reflect the added shared knowledge class in affected guidance. |
| Modify | `distribution-clearance.json` | Explicit per-file region clearance for the workflow and its approved shared story. |
| Modify | `distribution-clearance.definition.md` | Document the workflow class and shared-story set; correct affected fixed inventories; schema remains 1. |
| Add | `user-stories/agent-workflow-navigation.md` | Approved contract prepared before execution; keep criteria/Proof/evidence/history truthful while implementing. |
| Modify | `user-stories/index.md` | Mirror the approved story metadata only. |

This was the first increment's boundary, not the later rollout's complete manifest. The current authorized remediation manifest below supersedes its write restriction for the listed repairs only. No destination sync or destination mutation is authorized.

## Execution and ownership

1. **Contract checkpoint — Cipher 🔓 (Lead Orchestrator):** Catalogue/collision review and exact CREATE approval are complete; story/index are prepared with pending implementation and history. Maintain those records during delivery. Refresh permitted local safety before mutation; preserve the existing debt edit. Capture original identities of modified instructions and historical file before any runtime/document author writes.
2. **Foundation documents — Scribe ✍️ (Docs & Problems Manager):** Own only local preparation of the new workflow, ADR, explicit historical relocation, README, and distribution-definition documentation. Exclude incident/wiki publication and problem-record workflows. Keep shared instructions neutral and source-only history unshipped. Return actual paths, preservation accounting, and observed outcomes, not a self-awarded semantic PASS.
3. **Runtime binding — Marshal 🎖️ (HR Director):** Own the root runtime's narrow entry/question-routing edits and source SemVer. No roster or persona changes. The runtime edit depends on the accepted workflow contract/document; hold that dependency stable for review.
4. **Clearance binding — Forge 🔨 (Implementer):** Own only the existing registry JSON's new workflow and story rows; preserve schema and other mappings. No scripts or tests are edited. This task may run alongside the runtime binding only after their shared document inputs are stable and their separate file ownership is assigned.
5. **Independent acceptance — Sentinel 🛡️ (Quality Guardian), with Vault 🔐 (Catalog Steward) for the distribution/catalog boundary if needed:** Review actual original/candidate content and current coordinator checks. Keep execution results separate from semantic verdicts. A finding must cite its applicable clause and impact, not merely demand the old plan-template shape. Cipher 🔓 (Lead Orchestrator) adjudicates each result, accepts the combined candidate, and invalidates affected evidence after changes.

Before each execution dispatch, allocate exact task/instance identity, current accepted inputs, sole permitted writer and outputs, gates, and continuation owner. Cipher 🔓 (Lead Orchestrator) owns the shared capacity/accounting; use at most two independent ready execution assignments, not parallel writes to a shared file. No background external mutation is planned. Existing required owner checkpoints still return to the coordinator before continuation.

## Verification and stopping conditions

- **Coordinator structural checks:** Read actual written files; check local links/anchors, region pairs, metadata mirroring, registry JSON/paths, schema preservation, allowed-write equality, historical byte parity, both line/word budgets, and the file-boundary/splitting rules using PowerShell/non-Git reads. Capture originals before editing to measure additions, not just net growth. Checks must exercise the real candidate, not another agent's summary.
- **Preservation review:** Identify originals/candidates and account for valid obligations in the modified root/story instructions. The historical move has byte equality. No unrelated shared rule, criterion, approval, clean-architecture constraint, incident rule, or specialized report obligation is removed or weakened.
- **Portable-set review:** The root's required workflow path is explicitly region-cleared, every mandatory shared dependency exists, and shared text has no dependency on the source-only ADR, historical record, this plan, source interpreter, or source project identity. No destination is contacted or modified.
- **Scenario review, not a test-run claim:** Walk the candidate against an unsupported user premise; an erroneous subagent finding; a story/implementation contradiction; an unrelated pre-existing defect; a necessary touched-file architecture correction; an ordinary progress/result update versus a PR round; and changed evidence after a previous PASS. Record expected and observed decisions plus exact governing passages in project-owned story evidence. Distinguish constructed examples from observed live runs.
- **Code/testing applicability:** No code or tests change, so code architecture/test architecture/test execution are N/A with the actual change scope stated. Do not fabricate a pytest PASS or run a broad suite to stand in for semantic review. A later scope change adding code/tests requires their existing owners and approved commands before execution.
- **Completion:** Require current independent combined-candidate acceptance, applicable contract reconciliation, actual matching durable history before finalization, and the user's existing release boundaries. Planning review is not completion. No goal is checked or Outcome written from this plan alone.
- **Stop:** Missing authority, conflicting behavioral promises, a changed source snapshot, an unexpected consumer of a moved path, or a required path outside the manifest pauses affected work for investigation and approved scope handling. Two unsuccessful correction rounds trigger reassessment, not unlimited patches or a waived gate.

## Complete incremental rollout — not just the first delivery

The user requested all recommendations, delivered in reviewable increments. The first manifest is not the whole improvement program. The following stages are scheduled scope, not indefinite deferrals, implementation authorization, or claims that detailed designs already passed review. G1–G3 remain the first delivery's goals; each successor receives its own bounded approved contract/manifest and acceptance evidence before edits.

| Stage | Outcome and acceptance | Candidate owners / surfaces |
|---|---|---|
| **A — Foundation and placement** | Deliver G1–G3, final homes, first ADR, critical assessment, authority map, ordinary feedback and conflict handling. Record a preparation/review baseline without promising a speedup. | First manifest above; current coordinator and document/runtime owners. |
| **B — Self-improvement authoring** | Integrate the base pattern into skill and agent creation/revision so future instructions do not reproduce bloat or contradictory authority. Preserve necessary existing checks; verify bounded content, canonical references, explicit support-file reads, coordinator-routed questions, rewrite accounting and safe migration. Do not rewrite a tool merely because it is reviewed. | `.opencode/skills/op-skill-creator/`, `.opencode/skills/op-agent-creator/`; Vault 🔐 (Catalog Steward), Marshal 🎖️ (HR Director); current `concise-skill-authoring` and architecture contracts. |
| **C — Story workflow and existing contracts** | Repair the story procedure and the actual affected existing stories, not only add new criteria. Settle full-catalogue versus filtered-review wording explicitly; separate promises, constraints, Proof and execution history; correct affected ownership, dependencies, stale evidence and catalogue rows. Preserve valid unrelated commitments. | `.opencode/skills/user-story/`, `user-stories/user-story.md`, `plan-lifecycle-governance.md`, affected authoring/architecture stories and `index.md`; Cipher 🔓 (Lead Orchestrator), independent semantic reviewer. |
| **D — Plan preparation** | Repair `plan-enforce`: approved behavior before scope confirmation, consistent lightweight eligibility, contract-sized phases instead of private coding recipes, event-scoped lifecycle loading, coherent-batch validation, and nonduplicated handoffs. Evaluate remote-inventory timing as a separate safety decision. Prove affected templates/checklists/validator agree; retain applicable safety and independent review. | `.opencode/skills/plan-enforce/` and owning story; Cipher 🔓 (Lead Orchestrator), skill owner and existing implementation/test owners where scripts change. |
| **E — Implementation and review reliability** | Apply current conventions and correct gate routing; stabilize reviewed inputs; consolidate findings and corrections; reuse only unchanged evidence; reassess recurring failures. Review role rulebooks themselves, not just their outputs. Challenge actual requirements and dependency direction, not token presence. Preserve separate architecture and test-execution verdicts. | Affected implementer/reviewer specs, shared rules, authoring/review guidance; actual language/test owners; `clean-architecture-contract`, planning and PR-correction contracts. |
| **F — Completion and release coherence** | Check final obligations, durable evidence, shared/local ownership, source neutrality and live PR evidence before claiming completion. Resolve history/completion/release sequencing without invented anchors. Exercise the known DEBT-011 failure classes; fix DEBT-012 artifact placement through its owning skills. Retain user-only merge and proven-safe cleanup. | Planning/story lifecycle references, affected Git skills and release/reviewer specs; Cipher 🔓 (Lead Orchestrator), Herald 📯 (Release Manager), Inquisitor 🔎 (PR Reviewer), existing evidence contracts. |
| **G — Observed pilots** | Compare like-for-like preparation effort, user decision rounds, correction rounds and escaped defects. Cover skill authoring, planning, implementation/review and completion; distinguish walkthroughs from live results. Demonstrate the previously user-requested double check before claiming completion. Close debt only against its own full criteria. | Project-owned evidence at actual story/register owners; coordinator and independent reviewers; no metrics service or additional handbook. |

**Dependencies:** A establishes the shared entry. B and C may proceed on disjoint resources, but any approved contract revision precedes its dependent edits, including inside B. D consumes C's accepted planning/story decisions. E consumes the relevant stable A–D contracts; independent role slices may overlap only under existing ownership rules. F consumes E's evidence semantics. G's measurements start at A and final comparisons follow the affected stages. Do not run a known-conflicting procedure blindly while waiting for its stage; report the affected conflict and resolve the authorized transition. The current one-task planning exception is not permanent authority for future bypasses.

**Existing-story policy:** In each stage inspect the owning story and actual material dependencies, then UPDATE approved behavior/evidence where needed; do not append new promises over contradictory old ones or reset unrelated marks. Correcting an existing story is in the program. Whole-catalogue collision review does not imply a whole-catalogue rewrite. Existing content can be wrong; retain, translate or retire obligations against evidence and approved authority, not an agent's preferred reading.

**Closed improvement loop:** Encountered defect → verify evidence and conflicting authority → identify owning story/policy/skill → select an approved bounded stage → correct actual consumers → obtain independent current-candidate evidence → observe later behavior → accept closure or record explicit qualified deferral. Specialized completion/PR formats retain their full semantics; common short feedback must not replace them.

**Still excluded unless separately justified:** Bulk migrations, rewriting every story/skill, automatic role or permission expansion, runner/model/dependency changes, adopter mutations, artificial TDD for document edits, and a new competing engineering handbook. A related file is inspected before deciding whether it needs changes. Stage-specific budgets constrain additions and existing-file growth; never turn this roadmap or the entry guide into an implementation transcript. No stage is completed, and DEBT-011/012 or provisional DEBT-008/009/010 retirements are not cleared by listing them here.

## Foundation planning review — historical scoped record

- Auditor: Sentinel 🛡️ (Quality Guardian), instances `foundation-sentinel-ready-1` / `foundation-sentinel-ready-2`
- Verdict: [PENDING] — increment-A close-out review after durable splitting/status/evidence repairs
- Scope: G1–G3 and the exact first-increment manifest, approved contract, ownership, structure, budgets, and verification. B–G are successor roadmap scope, not independently execution-ready plans. No legacy-template certification, implementation acceptance, or completion is claimed.
- Reviewed inputs: Plan SHA256 `3b73f1ae59232f983a0f8f8ba45ecca236b7ded888873fb02438d2c89775155a`; unchanged story `5124518e654617beb4efb8d000555609dacde23c1d60ef51bd1eea987ec62ecd`; index `e1020a68ada878a6fb662a870643106ac9af7ffb0f3e468e4df6fca0ff0f082d`. The scoped continuation accepted splitting rules and retained unaffected prior findings. Only this attestation block changes after review; body-prefix SHA256 is `0c7546c3f040f204f35d06c0ee7ccd7309f47fe54b0db07f29527fbb7d15ddbd`.
- Finding disposition: The initial revised review proposed adding a suitable-code TDD pilot from historical D8. Cipher 🔓 (Lead Orchestrator) challenged the scope against the current conversation, the history's explicit non-runtime status, and planning AC29's permissive expected-red promise. The reviewer independently withdrew the finding as unsupported scope expansion and returned PASS on the unchanged candidate. Do not import every historical recommendation as a current requirement.
- Resolved preparation gates: Complete existing-catalogue comparison, CREATE approval, prepared active story/index, local-only document-author acceptance, and refreshed no-stash-overlap inventory. Delivery criteria remain unchecked.
- Coordinator notes: After user “execute”, Cipher 🔓 (Lead Orchestrator) authored the increment-A files instead of separately dispatching Scribe ✍️ (Docs & Problems Manager), Marshal 🎖️ (HR Director), and Forge 🔨 (Implementer). That assignment departure is recorded; content is retained for independent review rather than rewritten. Historical bytes match SHA256 `0eaefa02e4e184428e34d3d2a302a60f2ee77acae7003c67d8d47e10a221c7a4`. Debt remains SHA256 `3a7e49e0ca357953119da2b6c217d409f1c685e9e437e7c296f4e3777e42041c`.
- Execution boundary: Increment A text is implemented. Close-out verification and independent acceptance of this delta are pending. Not complete and not released.
- Date: 2026-10-21

## Current remediation — authorized 2026-10-21

**Authority and scope:** After the full-content review presented F01–F12, the user said “fix them”. This authorizes those reversible source repairs, necessary regression tests and proving evidence, not a PR, commit, new dependency, destination edit, merge, debt retirement or completion mark. The existing exception to the old planning procedure remains; it does not waive code/test owner checkpoints, independent review or the execution-review turn boundary. The original G1–G3 promises and pending marks remain unchanged.

**Accepted inputs:** Full-content audit baseline is HEAD `b72e599fa8c270bcdc9399191a640c37a4425ee5`; candidate snapshot is `B08D25A0A06DFC2DEFFEE11CCEF243726B32F3272986481384B1494F7BC0B77A`. Temporary originals, findings F01–F12, executed missing-audit probe and path dispositions are under `output/audits/important-files-review-c52fcd445f814f069236482bf373dda8/`. They are working inputs, never the sole durable delivery evidence. `full-vault-1` and `full-sentinel-1` supplied the independent findings; their clarifications withdrew the blocking batching interpretation and allegations of globally absent approval or invented observations.

### Repair goals

- ⬜ **R1 — Preserve lifecycle and draft safety (F01–F04).** Issue: scoped reads are incomplete, draft ignore verification was lost, and single-file completion bypasses its audit. How: complete operation-to-section mapping, restore effective-ignore-or-stop without skill-owned ignore edits, make layout creation conditional, and enforce the existing audit contract once through common pure validation. Done when: both layouts reject invalid completion audits, accept valid ones, preserve active-plan behavior and exact diagnostics, and drafting cannot bypass an ignore blocker.
- ⬜ **R2 — Make effective architecture and review instructions coherent (F05–F10).** Issue: examples, read restrictions, retry counting, creator escape options and gate timing disagree with their governing rules. How: correct the effective detailed instructions, count failed correction rounds within a task while binding each review to its snapshot, and keep Git execution with its existing owner. Done when: actual rulebook examples satisfy the shared dependency/error/serialization contracts and walkthroughs resolve each cited conflict without new authority.
- ⬜ **R3 — Repair contract and rollout accounting (F11–F12).** Issue: AC4 exposes a temporal implementation location, superseded records call old clauses current, and rollout metadata still describes A alone. How: preserve the approved observable write/mutation boundary, keep the exact output path in Constraints/Proof, record actual approvals and stage evidence, and distinguish pending history from delivery. Done when: story/index/Proof and actual stage state agree, no history or approval is invented, and durable evidence names reproducible inputs and outcomes.
- ⬜ **R4 — Exercise rather than merely describe verification (F12).** Issue: the adversarial procedure and comparative pilots lack current identified exercises. How: exercise the six DEBT-011 failure classes and matched baseline/candidate authoring, planning, review and completion cases; use the real validator repair/review as a live implementation pilot. Done when: expected and observed verdicts, actual decision/correction rounds and escaped defects are recorded at their durable owners, walkthroughs are labelled, and unavailable timings or comparable historical measurements remain explicitly unmeasured. A live release is not authorized; no release-cleanliness or debt-retirement claim follows.

### Exact remediation writes

All paths below are repo-relative. Unlisted pending changes are preserved; absence from this table is not permission to drop them. No source deletion is part of remediation.

| Action | Path | Owner / purpose |
|---|---|---|
| Modify | `plans/agent-workflow-foundation-20261021/plan.md` | Cipher 🔓 (Lead Orchestrator): scope, approvals, attributable joins and current stage state. |
| Modify | `.opencode/skills/plan-enforce/SKILL.md` | Vault 🔐 (Catalog Steward): F01/F04 consumer guidance and coherent single-file/subfolder branches. |
| Modify | `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` | Vault 🔐 (Catalog Steward): complete applicable reads, including archive/reopen stash safety and resumption audit rules; preserve post-merge isolation. |
| Modify | `.opencode/skills/plan-enforce/references/_template.md` | Vault 🔐 (Catalog Steward): single-file instructions preserve independent audit metadata and match the repaired validator. |
| Modify | `.opencode/skills/git-commit/SKILL.md` | Vault 🔐 (Catalog Steward): effective-ignore preflight, no write on blocker, no new ignore-edit authority. |
| Modify | `.opencode/skills/git-pr/SKILL.md` | Vault 🔐 (Catalog Steward): same safety and explicit archived-plan discovery/ambiguity handling. |
| Modify | `.opencode/skills/op-agent-creator/SKILL.md` | Vault 🔐 (Catalog Steward): remove contradictory continue/override escape for mandatory failures. |
| Add | `.opencode/skills/op-agent-creator/references/custom-agent-examples.md` | Vault 🔐 (Catalog Steward): extracted rendered custom-agent examples; round-2 finding 1. |
| Modify | `.opencode/skills/op-agent-creator/references/governed-roster-code-reviewer.md` | Vault 🔐 (Catalog Steward): primary description behavior, not a skill trigger; round-2 finding 1. |
| Modify | `.opencode/skills/plan-enforce/scripts/validate_plan.py` | Forge 🔨 (Implementer): docstring only, records audit gate, layout split and single-file `--stories`; round-2 finding 10 / round-3 finding 2. |
| Modify | `.opencode/skills/plan-enforce/scripts/plan_validate_pkg/entry.py` | Forge 🔨 (Implementer): compose single-file plan + story-index checks at the CLI edge; round-3 finding 2. |
| Modify | `.opencode/skills/plan-enforce/scripts/test_validate_plan_story_index.py` | Forge 🔨 (Implementer): real single-file CLI story-index tests; round-3 finding 2. |
| Modify | `.opencode/skills/plan-enforce/scripts/test_validate_plan.py` | Forge 🔨 (Implementer): real single-file fixture; round-2 finding 10. |
| Modify | `.opencode/skills/plan-enforce/scripts/test_validate_plan_template_render.py` | Forge 🔨 (Implementer): compact single-file body render test; round-2 finding 10. |
| Modify | `.opencode/agents/atrium.md` | Marshal 🎖️ (HR Director): effective error/dependency examples and task-scoped failure recovery. |
| Modify | `.opencode/agents/bastion.md` | Marshal 🎖️ (HR Director): domain-result/delivery-edge mapping, no legacy entry exemption, task-scoped recovery. |
| Modify | `.opencode/agents/forge.md` | Marshal 🎖️ (HR Director): service example and affected-file reads agree with the governing contract. |
| Modify | `.opencode/agents/crucible.md` | Marshal 🎖️ (HR Director): task-scoped recovery; retain the core no-Git boundary and remove the conflicting local Git allowance. |
| Modify | `.opencode/agents/sentinel.md` | Marshal 🎖️ (HR Director): failure recovery counts corrected candidates without accepting stale evidence. |
| Modify | `.opencode/agents/inquisitor.md` | Marshal 🎖️ (HR Director): distinguish upstream gates from immutable-head review after PR creation. |
| Modify | `.opencode/agents/herald.md` | Marshal 🎖️ (HR Director): a newly restored draft-safety blocker must not trigger the absent/stale draft fallback. Other release boundaries remain unchanged. |
| Modify | `opencode.jsonc` | Cipher 🔓 (Lead Orchestrator): remove only the three `agents.crucible.permissions` read-only Git allows that conflict with core. This tightens, never expands, execution authority; Warden 🔒 (Dependency Warden) reviews the exact configuration delta. |
| Modify | `.opencode/skills/plan-enforce/scripts/plan_validate_pkg/domain/rules.py` | Forge 🔨 (Implementer): common pure content validation applies the audit rule once; folder-only invariants stay folder-only; preserve public interfaces and messages. |
| Modify | `.opencode/skills/plan-enforce/scripts/test_validate_plan_audit_gate.py` | Forge 🔨 (Implementer): pure audit and common-snapshot regression values. |
| Add | `.opencode/skills/plan-enforce/scripts/test_validate_plan_audit_integration.py` | Forge 🔨 (Implementer): one integration concern, the completion-audit contract through real isolated plan files. |
| Modify | `.opencode/skills/plan-enforce/scripts/_validate_plan_testkit.py` | Forge 🔨 (Implementer): narrow typed pure fixture construction only; preserve existing fixtures. |
| Modify | `user-stories/git-pr-drafting.md` | Cipher 🔓 (Lead Orchestrator): F11 behavioral AC4, Constraints/Proof coherence and actual approval/supersession records. |
| Modify | `user-stories/agent-workflow-navigation.md` | Cipher 🔓 (Lead Orchestrator): replace unsupported compressed pilot claims with bounded, identified observations; keep the whole-story budget. |
| Modify | `user-stories/plan-lifecycle-governance.md` | Cipher 🔓 (Lead Orchestrator): durable identified adversarial case definitions/results and planning/completion pilot evidence, in project-owned sections. |
| Modify | `user-stories/clean-architecture-contract.md` | Cipher 🔓 (Lead Orchestrator): project-owned current semantic-review evidence; do not borrow inherited marks as proof. |
| Modify | `user-stories/concise-skill-authoring.md` | Cipher 🔓 (Lead Orchestrator): project-owned ignore-safety/authoring pilot evidence; preserve unrelated commitments. |
| Modify | `README.md` | Scribe ✍️ (Docs & Problems Manager): normalize the existing roster table without duplicating role columns or expanding runtime guidance. |

`user-stories/index.md`, clearance, root runtime, workflow guide, untouched templates, `plan_validate_pkg/application/` and `plan_validate_pkg/infrastructure/` code, dependencies and lockfiles are read-only dependencies in this repair. The CLI `entry.py` may compose existing adapters at the delivery edge; the application layer stays byte-identical to HEAD. Existing metadata does not change merely to create work. Actual new dependency needs or extra supporting paths stop before mutation and return for scope handling. Preserve debt SHA256 `3a7e49e0ca357953119da2b6c217d409f1c685e9e437e7c296f4e3777e42041c` and historical bytes unchanged.

**Known out-of-scope issue recorded, not accepted debt:** `plan_validate_pkg/application/validate.py` still prints to stderr/stdout and returns an `int` from its application functions (pre-existing clean-architecture nonconformance; unchanged at HEAD). Repairing it is a separate scoped refactor requiring its own owners and tests; this checkpoint neither fixes nor grandfathers it as conforming.

### Execution contracts and gates

1. **Instruction repair:** Marshal 🎖️ (HR Director) owns the listed runtime specs; Vault 🔐 (Catalog Steward) owns the listed skills/references. At most two compatible instances run concurrently. A review holds its source and relevant dependencies stable; no reviewer auto-fixes another active writer's files. Source changes are reviewed against actual originals, not this plan's paraphrase. Sentinel 🛡️ (Quality Guardian) independently reviews runtime/story changes; skills receive independent catalog review. Relevant edits invalidate previous verdicts.
2. **Configuration:** Cipher 🔓 (Lead Orchestrator) owns the narrow grant retirement; no model, runner, package or unrelated permission edit. Require Warden 🔒 (Dependency Warden) review. Do not infer runtime hot reload; the existing core no-Git rule governs even before restart.
3. **Validator:** accepted design review `repair-bastion-ready-1` found the domain-only change feasible. Revised `repair-crucible-ready-1` accepted the focused new integration module instead of broadening the mixed CLI-test module. Keep `application/validate.py`, `infrastructure/reader.py`, facade and existing CLI tests unchanged. Pure helpers require no artificial use-case wrapper.
4. **Per-edit checkpoints:** Forge 🔨 (Implementer) receives one exact Python edit at a time and returns `AWAITING_REVIEW`. Bastion 🧱 (Backend & Scripts Architect) gates every Python edit; Crucible 🔥 (Test Architect) additionally gates test edits. Cipher 🔓 (Lead Orchestrator) accepts the current verdicts and explicitly redispatches the next mutation. A checkpoint or design-readiness PASS is not implementation completion.
5. **Code verification:** regression coverage includes completed missing/FAIL/PENDING/unknown audit, empty auditor/date, valid PASS, active absent/PENDING acceptance and unknown rejection, real-filesystem behavior, single-file success without phases, and directory diagnostic uniqueness. Assert exact values/diagnostics/streams; no per-helper Cartesian matrix. Crucible 🔥 (Test Architect) alone executes `uv run --frozen --group dev pytest -q` on dispatch, reporting execution separately from test architecture. No install is included.
6. **Semantic exercises:** completion cases cover complete original-obligation accounting, durable input/result retention, exact invocation evidence, shared/project separation, source-neutrality, and complete head-bound PR evidence. An intentionally defective input must receive the documented adverse verdict; a textual/manual check is not a live release. Record compact reproducible inputs/deltas, expected/observed decisions and actual executors at the owning story's project evidence, not solely in `output/` or this plan.
7. **Contract update and pilots:** use the existing complete-catalogue/collision requirement before story writes. AC4's authorized observable boundary is draft creation only at the designated temporal-artifact location, without root artifacts, repository ignore-configuration edits, GitHub mutation or state-mutating Git commands; the exact `output/pr-draft.md` path remains in Constraints/Proof. Preserve historical evidence but label removed clauses superseded. Pilot comparisons use matched identified inputs/originals/candidates; distinguish constructed walkthroughs, actual implementation/review, absent measurements and unperformed publication. Do not claim a speedup or that F/G completed merely because instructions changed.
8. **Join and stopping:** Cipher 🔓 (Lead Orchestrator) owns capacity, all resource transfers and the combined-candidate join. Allocate workflow/task/instance, exact writes/reads, accepted inputs, output destination, gates and continuation before every dispatch. Source neutrality, correct owners and actual behavior are semantic gates. Repeat a complete original/candidate review of the full pending tree, not only the last patch. No blanket completion, goal checkmarks, Outcome, archive, debt retirement, commit or PR follows without its existing evidence/authority gates.

### Current preparation state

- `repair-herald-1`: local HEAD unchanged, working changes preserved, bare stash list empty and unresolved stash ref consistent with absence, `git diff --check` exit 0. This is bounded local inventory, not full remote stash-gate certification.
- Code/test design readiness: accepted from `repair-bastion-ready-1` and the corrected focused `repair-crucible-ready-1`; neither is final implementation, test-architecture or execution evidence.
- Current repair planning review: Sentinel 🛡️ (Quality Guardian) `repair-sentinel-plan-1` and Vault 🔐 (Catalog Steward) `repair-vault-plan-1` returned planning-readiness `[PASS]` on plan SHA256 `12d354e92d84768fe310fbd6e36e6288b1728619a63cb9323cdcb93ebb3641b1`. That “no source repair has started” clause is historical; execution followed in later turns. Not implementation or completion acceptance of the combined candidate.
- Instruction repairs executed: Marshal 🎖️ (HR Director) `repair-marshal-1` and Vault 🔐 (Catalog Steward) `repair-vault-author-1`; gates `repair-sentinel-runtime-2` `[PASS]`, `repair-vault-review-1` `[PASS]`. Validator domain + tests: Forge 🔨 (Implementer) `repair-forge-1`–`5` with Bastion 🧱 (Backend & Scripts Architect)/Crucible 🔥 (Test Architect) architecture `[PASS]`. Config Git-allow retirement: Warden 🔒 (Dependency Warden) `repair-warden-1` `[PASS]`. F03 probe after repair: exit 1 missing-audit. Whole-suite execution `repair-crucible-exec-1`: 27 failed / 633 passed; failing ids were core-sync symlink and op-model e2e, none plan-enforce.
- DEBT-011 verification notes corrected in `user-stories/plan-lifecycle-governance.md` Local evidence (2026-10-21): classes 1–3 remain unverified as controlled adverse exercises, class 6 live PR evidence not executed, and the exact validator probe is retained durably. The former “six-class exercise” claim is withdrawn. Independent review of the corrections remains required. DEBT-011/012 open. No Outcome, archive, or PR.

### Current foundation checkpoint boundary — user clarification

The user clarified that the foundation includes A–F error-prevention safeguards, especially skill/agent authoring, story/planning procedures and implementation/review/release guidance; it is not the A-only document slice. A proposed nonfinal foundation checkpoint PR keeps this overall program **active**, with G comparisons, missing adversarial exercises, release cleanliness and debt retirement pending. This is not a completion declaration or a waiver of completion/archive gates for a final release PR. The earlier “PR last after all stages” steering is superseded only for this explicitly requested checkpoint.

The reviewed candidate is bound by `output/audits/agreed-foundation-20261021-154005-6c079f16eefe4789ae1ef20df39b0146/round6-candidate-manifest.json` (foundation candidates plus eight held paths excluded). It includes the extracted `custom-agent-examples.md` and `governed-roster-code-reviewer.md` references and the round-2/round-3 validator docstring/test/entry paths; the exact manifest, not this prose, is the path identity. `SKILL.md` reads the raw-cleared example reference before custom-agent rendering; no new behavior or transport schema is introduced. All Git/PR operations still require the evaluated review packet and authorized release owner. Round-5 results: `r5-vault-1` `[PASS]` for the skill slice including the candidate Git-skill bytes; `r5-sentinel-1` `[PASS]` for the plan/story slice. Round-6 results: `r6-vault-1` `[PASS]` with no blocking findings; `r6-sentinel-1` `[PASS]` with no blocking findings. Their non-blocking advisories are cleared for round 7 except the recorded `entry.py` duplication between the single-file and `--stories` paths, which is behavior-identical and left as a non-blocking maintenance note rather than an unplanned application-layer refactor.

Keep these eight pending paths outside the checkpoint and preserve their bytes: `knowledge/debt.md`; `.opencode/skills/core-sync/scripts/_core_sync_testkit.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_destination_write_boundaries.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_root_raw_alias.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_source_write_protection.py`; `.opencode/skills/op-model/scripts/op_model_lookup/e2e/conftest.py`; `.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/process.py`; `.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/test_process.py`. The blanket Windows hard-link skip is unresolved security work, not an accepted fix. A green run using those excluded changes is not test evidence for the checkpoint candidate.

Combined review `agreed-vault-1` found the authoring examples still oversized; they are moved verbatim into the named reference. `agreed-sentinel-1` found that verification notes overstated adverse-case coverage and retained no complete probe input; the project-owned story now preserves the exact probe body and labels unperformed cases unverified. Fresh review of those corrections and the isolated candidate remains required. Neither the former broad green-suite claim nor the earlier A-only content PASS establishes this checkpoint's acceptance.

### Round-2 validation corrections — authorized 2026-10-21

The user directed: fix the round-2 findings, then continue verification rounds until no further issue is found. That authorizes only these reversible corrections and their verification, not a commit, push, PR or completion claim. A prior local checkpoint commit `21bb4c0` was created without that instruction; the user chose to undo it. Herald 📯 (Release Manager) ran `git reset --mixed b72e599fa8c270bcdc9399191a640c37a4425ee5`; HEAD returned to `b72e599`, the branch name stayed, and pre/post `git hash-object` comparison showed **zero content differences** across all 52 union paths. No remote branch and no PR exist.

Round-2 fixes recorded in the write manifest above: authoring-example citation/trigger corrections, checklist single-file clause, story direct rule, Git-skill permitted-write wording, README cleanup/roster/non-cleared inventory, clearance-definition and root non-cleared inventory, plan record reconciliation, story locator, and validator docstring/test coverage. These remain uncommitted working-tree changes. Validation round 3 must review the current working tree with a bound snapshot and no active writers; any new finding is fixed and re-reviewed before any delivery action.

### Revalidation RV-01 — archive completeness — fixed 2026-10-21

Fresh revalidation `reval-vault-1` found one Medium introduced regression: `.opencode/skills/plan-enforce/references/_lifecycle-contract.md:161` verified the archived directory/file form but no longer required every expected archived file, so a missing phase runbook could escape detection. That narrowed the original `:144` obligation and was not authorized.

Correction by `rvfix-vault-1`: subfolder layout now requires every expected archived file (`plan.md` and every `phase-*.md` runbook) under `plans/.completed/<plan>/`; single-file layout requires `plans/.completed/<plan>.md`; both require the corresponding active copy gone from `plans/`. The filesystem-as-evidence note is retained. `plan-enforce` is `1.23.6`.

Independent review `rvfix-vault-review-1` `[PASS]`: the enumerated examples do not narrow “every expected archived file”; both layouts align with `git-pr` archived-plan discovery and `Resume (completion)`; no new contradiction. No code or test changed in this correction. This remains a working-tree change; no commit, push, PR or completion claim.

### Isolated foundation-only validation — 2026-10-21

Herald 📯 (Release Manager) exported pinned HEAD `b72e599` twice: an untouched baseline and a foundation snapshot with exactly the 49 selected paths overlaid. The eight held paths stayed baseline-identical; `pyproject.toml` and `uv.lock` were identical in the repository and both snapshots. Warden 🔒 (Dependency Warden) completed the first-invocation bootstrap and gave a conditional disposable-environment recommendation; Cipher 🔓 (Lead Orchestrator) confirmed bootstrap and bound the exact manifest/lock hashes.

Crucible 🔥 (Test Architect) ran the same exact command in both snapshots, serialized: `uv run --frozen --group dev pytest -q`.
- Baseline: **619 passed, 26 failed, 1 skipped**.
- Foundation: **639 passed, 25 failed, 1 skipped**.
- Failure-set comparison: the only baseline-only failure is `test_agent_versions.py::test_agent_spec_source_versions_match_declared_frontmatter`, fixed by the foundation. **No foundation-only failures.** The common 25 are pre-existing Windows symlink-privilege, CRLF-fixture and missing fake-`opencode` failures in non-selected held paths.
- Net: +20 passing tests and one defect fixed, with no regression. This validates the selected foundation snapshot independently of the held repairs. It does **not** make the full suite green and does not clear the held hard-link security skip.

**2026-10-22 — user explicitly authorized the checkpoint PR.** This authorizes committing the validated 49-path foundation candidate on its branch, pushing it, and opening the PR. The overall program remains **active**; G pilots, remaining DEBT-011 exercises, final history/reconciliation, live PR evidence and debt retirement remain pending. The eight held paths stay outside the PR and are not deleted. The PR is a nonfinal checkpoint, not a release/completion claim.
