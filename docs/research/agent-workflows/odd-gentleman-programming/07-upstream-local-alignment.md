# 07 — Upstream ODD and local alignment: evidence and proposal

## Record metadata

- Primary domain / topic: `agent-workflows` / `odd-gentleman-programming`; supporting study in the existing multi-file publication, using the [research template's](../../_template.md) anatomy.
- Aliases / tags: ODD, feature document, spec-by-reference, work-unit commits, delegation, forecast, local adaptations.
- Researched: 2026-10-28 by Augur 🔮 (Research Analyst), instance `source1`; documentary synthesis and narrow primary-source refetches on 2026-10-28 by Scribe ✍️ (Docs & Problems Manager), instance `research-author1`.
- Reviewed: exact current independent source and semantic review outcomes, with their input identities, are recorded in [the governing feature](../../../../odd/tasks/gentle-ai-odd-blueprint-research.md), T6/`## Log`. L9/L10's prior documentary `[PASS]` applies only to its four recorded hashes, not this chapter or the changed navigation/source files.
- Source versions / revisions: October 22 historical v4.2.0 study (S4); October 27 v4.3.1 target `2dba7784114fff57864519c4c0d067e952a8c98b` (S30–S38); October 28 inspected `main` snapshot `a6e371b502a24a0a0f57e8d75730150416c0d3f3` (S39–S50). Local sources are the inspected working-tree documents, not an asserted committed release (S51).
- Applicability: source-grounded comparison and a nonbinding alignment proposal. No runtime, template, safety, execution, Git, review-mode or memory-policy change is authorized here.
- Freshness / recheck triggers: changed upstream routing/docs/skill copies, changed local authority, or a decision to implement a proposal; no exhaustive current-release or compliance claim.
- Related feature: [`gentle-ai-odd-blueprint-research`](../../../../odd/tasks/gentle-ai-odd-blueprint-research.md), S1–S5/S7 and T2/T4/T6. The [adoption-status page](../../../architecture/odd-adoption-status.md) is a documentary summary, not authority.
- Supersession: the dated October 28 comparison supplements [chapter 06](06-feature-document-blueprint.md), not a rewrite of October 22/27 findings or original feature histories. No superseding ecosystem-wide study is evidenced.

## Question and boundaries

How closely does the actual local ODD contract follow the original Gentleman-Programming repository's feature-document design, and what could be proposed without losing that source or weakening local safeguards?

**Reading rule:** **upstream fact** below means cited source text or history; **local fact** means inspected local authority; **alignment judgment** is this study's interpretation; **proposal** means not approved policy. Research does not execute the proposal. Current local authority remains [the workflow entry](../../../../knowledge/agent-workflow.md), [root runtime](../../../../AGENTS.md), and [ODD skill](../../../../.opencode/skills/odd-workflow/SKILL.md).

## Method and provenance

Augur 🔮 (Research Analyst) identified the inspected `main` SHA on October 28 and reported usage, intended-usage and routing byte-identical to the October 27 snapshot (governing feature L13; S39–S42). That cross-snapshot equality is an **attributed observation**, not a comparison rerun by this author. The commit API gives the inspected SHA's timestamp as `2026-10-28T04:16:59Z`; it identifies a commit, not a permanently current branch tip (S39).

Scribe ✍️ (Docs & Problems Manager) directly refetched the pinned usage/intended-usage/routing passages, review delivery clause, public and embedded work-unit/chained-PR skill passages, October 3 and September 18 commit API records, and the compact task example (S39–S50). Local comparison used direct reads of the actual owners and validator (S51). These are document/source inspections: no upstream installation, runtime execution, test execution, full video playback, autonomous-compliance measurement, or new whole-tree inventory occurred.

Both inspected usage pages still say they track `main` and link to v4.0.0 docs (S40/S41, line 4). Pinned bytes are reproducible evidence; they are not proof of release-specific documentation. The supplied transcript remains version/date unknown (S38). Its “sweet spot” description of task size and RDD-default narration are not used to override pinned prose, choose a present default, or resolve contradictions.

## Sources

Full URLs, revisions, access dates and executors are in [sources.md](sources.md); original S1–S38 identities are preserved.

| IDs | Locator / section | Use and limit |
|---|---|---|
| S39–S42 | Commit API; `docs/usage.md` ODD protocol, One feature document, Task size, Tests, Checking, Delivery; `docs/intended-usage.md` Everyday work / Delegation and skills; `routing.go` `RenderRouting` and separate `piODDSteps` | October 28 pinned design evidence; not a runtime experiment |
| S43–S47 | `docs/review-integration.md` Delivery remains human-owned; embedded/public work-unit-commits and chained-PR skills | Exact conflicting delivery/cadence/name passages; no precedence inferred |
| S48–S50 | October 3 format-transition commit; September 18 older example introduction; current pinned `odd-spec-by-reference.md` | History and examples, not universal schema or hash-length requirements |
| S51 | Local root runtime, workflow, template, ODD skill/checklist, validator and existing test-path inventory; implementation runtime checkpoint clauses | Current written local obligations; static inspection, not a conformance verdict |

## Findings

### 1. Upstream history explains the apparently competing layouts

**Upstream fact:** commit [`6c6649159cfe7b590acffa9b9600db2d10e403b5`](https://github.com/Gentleman-Programming/gentle-ai/commit/6c6649159cfe7b590acffa9b9600db2d10e403b5), timestamp `2026-10-03T17:13:50Z`, replaces the summarized “objective, problem, why, scope, constraints” prescription with short header → `## Specs` → `## Tasks` → `## Log`, preserving exact user fragments and reference-based handoffs (S48, usage/routing diff and commit message). The purpose stated in the commit is avoiding lost exact requirements on the way to subagents.

The older `odd-mandatory-delegation.md` was added September 18 in `f5d5fc2e7fa1954abda64a24b55b0a3b5068907b` and contains Objective/Problem/Scope-style sections (S49). Its continued presence among examples is not evidence of two equally current sanctioned standards. No evidence here establishes that every older task file was migrated. The October 27 inventory remains only its bounded path/heading scan (S37).

**Alignment judgment:** preserve old research and task histories as dated evidence; do not restore those older headings as a universal local blueprint. The current compact local Specs/Tasks/Log direction is materially closer to the October 3 contract (S40, S42, S48, S51).

### 2. Source-to-local comparison

Local references below resolve to S51; line numbers describe the inspected candidate, and named sections remain the recheck anchors.

| Concern | Upstream fact | Local fact | Alignment judgment |
|---|---|---|---|
| Workflow and tracking | Authorize → Explore → Resolve uncertainty → Classify → Track before first write → Implement → Close; small/read-only work has no durable task artifact (S40, lines 14–24). | `knowledge/agent-workflow.md:8–16` and `AGENTS.md:41–47` use that flow and require the feature before the first non-small mutation. | Strong structural alignment; local first-mutation language is broader than upstream's “first source write.” |
| Classification | Small requires understood, contained risk and resumability; source also says large only when resumability fails (S40:21; S42:67,83–87). | `knowledge/agent-workflow.md:13` explicitly makes failure of any of the three conditions non-small. | Shared criteria, but the local exhaustive rule must not be described as an unambiguous upstream equivalence; see contradiction below. |
| Header | Usage says short header; renderer elaborates two or three lines with objective, branch, delivery strategy and test runner (S40:26; S42:158). | `odd/tasks/_template.md:1–5` and checklist Create carry title, Status, Owner, Created; no explicit objective/branch/strategy/runner fields. | Present gap in header guidance, not permission to reconstruct the template from examples or invent a runner. |
| Specs fidelity | Numbered specs quote exact strings, errors, commands and examples verbatim in the user's language; acceptance criteria/checks accompany scope; no unrequested requirements (S40:26; S42:68,158). | Workflow Feature document and skill Create require numbered requirements, exact strings and acceptance checks; L1 is verbatim (`knowledge/agent-workflow.md:37–40`; skill:21–23). | Core shape matches; exact user-fragment preservation is less explicit locally than upstream's no-rewording instruction. |
| Tasks and routes | One line per task: ID, linked spec, route, status and commit/evidence; record inline/delegated route and trigger evidence (S40:26; S42:132,158). | Template:14–17 and workflow:38 allow “route or owner,” plus status and commit. | An owner name alone need not expose routing or its rationale. Upstream renderer also allows RED/GREEN evidence where local done-state anatomy requires a commit. |
| Handoffs and changes | Pass document/task/spec by reference; workers read until `## Log` and report covered specs, while verification reads the whole document; rewrite affected spec and reopen affected task (S40:26–29; S42:68,73). | Workflow:40–42 and skill Change a requirement / Handoff / Close prescribe reference-based handoffs, the worker's read until `## Log`, and independent review; the cited local lines do not separately state the verifier's whole-document read. | Worker handoffs align; the upstream verifier whole-document read is not separately stated in the cited local lines. No wholesale regeneration is called for. |
| Evidence and Log | Observed proof precedes checkoff; append brief corrections, rationale, verification, progress/next step, not an exhaustive decision journal (S40:23,29; S42:158). | Workflow:39,44 and skill Implement and verify require compact provenance-bound evidence and forbid an execution transcript. | Compatible compact evidence intent. The local detailed evidence procedure is a local safeguard, not claimed as an upstream mandate. |
| Commits and abbreviations | Usage and embedded skill use coherent work units, not one commit per task (S40:23; S44:67–72); compact task rows use eight-character references such as `6c664915`, `122e85b7` and `5c460fce` (S50:14–16). | Template:17 requires each done task's work-unit commit; skill:22 and validator:24,121–137 accept 7–64 hex characters and do not enforce distinct commits per task. | Multiple tasks may cite the same coherent commit under the local anatomy. Task evidence can use verified short references; full SHAs remain appropriate for source pinning. No universal upstream abbreviation length is inferred from these passages and no Git resolution is claimed here. Public skill conflicts remain unresolved. |
| Forecast and line heuristics | Forecast authored additions + deletions, exclude generated files, keep running work-unit count; apply a chosen delivery strategy when forecast/count exceeds about 400 (S40:32; S42:174). Task ~400 is separately advisory, not a cap/forced split/RDD trigger (S40:28; S42:157). | Inspected workflow, template and skill/checklist have no explicit forecast/count/strategy procedure. Skill Delivery boundary defines reviewable slices but not this forecast mechanism. | Present procedural gap, not an undocumented delivered capability or a reason for cosmetic shrinking. |
| Tests and verification | Conditional deterministic test-first, meaningful expected outcome, observed RED→GREEN→REFACTOR; otherwise explain exception and check proportionately, never invent a runner (S40:30; S41:16; S42:168). | Workflow:15 and skill:35–41 require applicable checks/evidence and independent semantic completion; root runtime:25 and implementation runtime checkpoints require owner gates after applicable edits. | Current local evidence is not proof that upstream's full test-first policy is already adopted. A narrower sourced proposal is below; local gates remain binding. |

### 3. Explicit local deviations and safeguards

These are **current local facts**, not implementation proposals or claims about upstream origins:

- **No Engram mirror, second tracker or per-request context injection** (`knowledge/agent-workflow.md:43`; skill What I do; checklist Forbidden). Upstream explicitly retains an Engram mirror and two-copy reconciliation (S40:26,34; S42:158). The absence is an explicit local boundary, not forgotten parity work.
- **Delegation floor and code ownership:** `AGENTS.md:21` requires at least one agent per ticket; its code-author/reviewer separation and the implementation runtime's Role / Current task / Workflow checkpoints remain binding. Upstream instead defaults inline and delegates only when named conditions hold; once a trigger truly fires it is mandatory (S41:24; S42:121–132). This is a real local topology difference, not a source-derived universal minimum.
- **Execution-review pause:** `AGENTS.md:74` requires a presentation and stop after writing a feature document, with no same-turn dispatch of Forge 🔨 (Implementer). Upstream describes automatically creating the tracking document and reporting it, not a universal approval pause at that point (S40:22; S42:68). Existing user-only uncertainty stops are distinct from this local mandatory checkpoint.
- **Independent architecture and completion gates:** `AGENTS.md:25` and skill Close require owner review after applicable edits and independent semantic completion, including zero open findings before a clean completion claim. Upstream's proportional routing/native review text must not be used to bypass them (S42:124,170–172).
- **Delivery authority:** local skill Delivery boundary explicitly requires user authorization for commit/push/PR/release/archive. No work-unit language in this research grants Git authority. Upstream itself has conflicting commit-authorization wording, recorded below (S42/S43).
- **Evidence rather than assumptions:** local `knowledge/agents.md`, Evidence discipline, forbids assumptions and requires labeled evidence-grounded hypotheses. The renderer's instruction to mark assumptions (S42:158) does not weaken that local obligation.

### 4. Unresolved upstream contradictions: preserve both sides

All locations are pinned to the October 28 SHA. **No precedence was found in the inspected sources.** These are documentary discrepancies, not a claim that all versions/runtimes behave identically or differently in execution.

| Issue | Opposing exact locations | Consequence for reuse |
|---|---|---|
| Task/commit cadence | Public `skills/work-unit-commits/SKILL.md:67–69` says every substantial task closes with at least one work-unit commit (S45); embedded `internal/assets/skills/work-unit-commits/SKILL.md:67–72` explicitly says not one commit per task, agreeing with usage:23 (S44/S40). | Cite which copy supports a claim. Do not call the copies equivalent or derive a unique commit-per-task requirement. |
| Commit authorization | `routing.go:73` includes feature-branch work-unit commits in authorized large implementation (S42); `docs/review-integration.md:305` says commit/push/PR/release/archive require their own explicit authorization (S43). | Preserve local explicit authorization; do not select an upstream winner or infer authorization from documentation execution. |
| Size classification | `routing.go:83–86` says all three small criteria must hold; :87 and usage:21 say large only when the resume test fails (S42/S40). | Failure of understanding/risk with resumability retained is not resolved by these formulations. Local all-three rule remains authoritative here. |
| Review trigger | Usage Checking:31 names `review_due` true for `high_risk` **or** `slice_budget_reached` (S40); RDD renderer clause `routing.go:170` explicitly names `high_risk` or user-requested review while still retaining pending `under_budget` slice handling (S42). | Do not invent equivalent triggers, remove the pending-slice language, or infer native implementation behavior without investigation. |
| Skill names | Delivery usage:32 / renderer:174 resolve `work-unit-commits` and `chained-pr` by registry name (S40/S42). Embedded chained-PR name is `chained-pr` at :2 (S46); public copy is `gentle-ai-chained-pr` at :2 (S47). Both work-unit copies name `work-unit-commits` (S44/S45). | The naming discrepancy is specifically the chained-PR copy. No installed registry identity or precedence is established by these files alone. |

**Pi boundary:** separate `piODDSteps` and its comments name visible `todo`, phase labels and asset pointers as Gentle Shell additions (`routing.go:17–22,28–29`, S42). Pi-specific projections/stopping guidance and the transcript's demonstration do not become universal local feature fields or phases. The source's own usage page requires observed file/memory/update/resume behavior for Pi parity, not matching prompt text (S40:95–97; historical S34/S35/S38).

## Recommendations and alternatives

### Nonbinding proposal: tighten the compact current anatomy, not revive the old layout

If separately authorized, align the **existing** feature template and its consumers as one coherent change:

1. Retain the short header → Specs → Tasks → Log order. Add concise objective, actual branch, explicitly authorized delivery strategy and actual applicable runner information to the header without restoring Objective/Problem/Why/Scope sections. Preserve useful local Status/Owner/Created metadata; this would be a local adaptation, not a byte-identical upstream header. Use justified N/A or report a missing applicable runner; never manufacture one.
2. Make exact user strings/errors/commands/examples explicitly verbatim within numbered Specs, with acceptance checks alongside them; preserve the user's language and do not add business requirements. Keep original request and dated corrections in Log. Do not retrospectively rewrite feature history into a new standard (S40/S42/S48).
3. Separate task route from owner: make inline/delegated and the relevant reason inspectable while preserving the local ownership/gates. Permit the same authorized coherent commit to evidence multiple tasks; do not require a fresh commit for every checkbox. Keep current 7–64 hexadecimal anatomy unless a separately evidenced need requires change (S44/S50; local skill:22 / validator:24). Proposed task rows may cite verified short references; full SHAs remain appropriate for source pinning, and no Git resolution is claimed.
4. Propose a task-list forecast, count authored additions plus deletions excluding generated files, and maintain observed running work-unit counts. Keep task ~400 advisory separate from delivery slicing. Record any chosen strategy and slice boundaries compactly in the existing document, not a second tracker. Upstream strategy vocabulary is a source reference, **not** automatic local commit/PR authorization or an already installed skill (S40:28,32; S42:157,174).
5. Consider the sourced **conditional deterministic test-first** rule: relevant runnable deterministic test + clear expected outcome → observe RED, implement GREEN, refactor; otherwise record the actual exception and proportionate checks. Carry the actual runner and evidence to workers. This proposal does not copy every upstream test-case/differential-check restriction, fabricate tests for documentation, or transfer whole-suite execution authority (S40:30; S42:168; local skill Implement and verify).
6. Consider more proportional evidence review/dispatch only as an explicit policy decision. Upstream supports inline ordinary work and independent verification on named high-risk changes; it does not justify silently removing this repository's delegation floor, exclusive code author, edit gates, execution-review pause or independent completion review (S41:24; S42:121–132,170–172; local authorities above). Preserve those safeguards pending user decisions.

**Alternative:** retain the current policy and document these deviations. This avoids authority changes but leaves the header, exact-fragment, route and forecast gaps explicit. **Rejected approach:** merge old examples, Pi UI behavior and current prose into a larger mandatory feature template; history and current source do not support it.

### Exact proposed file map — for a later authorized change only

No path below is edited by this study. This map identifies the evidenced owner surfaces, not a new task list or an implementation authorization.

| Proposed concern | Exact candidate owner paths | Boundary |
|---|---|---|
| Header, verbatim fragments, route field and forecast procedure | `knowledge/agent-workflow.md`; `odd/tasks/_template.md`; `.opencode/skills/odd-workflow/SKILL.md`; `.opencode/skills/odd-workflow/references/_checklist.md` | One authoritative procedure, with template/checklist consumers; no additional feature headings or tracker. |
| Mechanical support if anatomy changes | `.opencode/skills/odd-workflow/scripts/validate_feature.py`; `.opencode/skills/odd-workflow/scripts/test_feature_structure.py`; `.opencode/skills/odd-workflow/scripts/test_feature_lifecycle.py`; `.opencode/skills/odd-workflow/scripts/test_feature_cli.py`; `.opencode/skills/odd-workflow/scripts/feature_testkit.py` | Inspect affected tests before selecting exact edits. Validator remains mechanical: it cannot prove verbatim fidelity, actual risk, runner validity, test execution or completion (validator:1–6,18–26,58–156). No hash-length change is presently needed. |
| Conditional test-first and proportional evidence procedure | `knowledge/agent-workflow.md`; `.opencode/skills/odd-workflow/SKILL.md`; `.opencode/skills/odd-workflow/references/_checklist.md` | A proposed procedure extension only; existing execution and test-owner authority remains unchanged. |
| Mandatory stop / delegation floor decisions | `AGENTS.md` Identity & Role / Conventions | Explicit policy decision required before any weakening; do not disguise it as documentation alignment. |
| Implementation checkpoint authority | `.opencode/agents/forge.md` Role / Workflow / Hard Rules | Preservation dependency, not a proposed bypass or grant. Any later change must account for root-runtime owner gates and shared coordination obligations. |

The file map does not create missing work-unit/chained-PR skills, select an RDD engine, change harness configuration, enroll destinations or rewrite released task records. Any later executable/test edit still requires its own authorized scope and applicable owner gates.

## Limitations and open questions

- The exact scope of this study is source/local documentation comparison, not an exhaustive repository, security, current-release, installation, runtime-parity or model-compliance audit. Original renderer tests are evidence of text assertions, not tests run here (S35).
- Commit API metadata and pinned files do not prove `main` remains at that SHA. Release-page latest identity remains the dated October 27 observation (S30); no newer release census is claimed.
- No inspected source settles the five discrepancies above. TODO: requires evidence before asserting precedence, installed registry behavior or native review trigger execution.
- The supplied transcript's release/date and relation to the observed written defaults remain unknown. No retrofit of that narration to October 28 is justified (S38).
- Local line references identify direct static inspection, not a committed whole-repository identity or empirical conformance. The current candidate's independent source and semantic review results must be recorded at their exact input scope in the governing feature; inherited `[PASS]` marks do not cover it.
- Implementation, policy relaxation and delivery remain separate decisions; neither this proposal nor a later documentary review supplies their authorization.

## Reuse and supersession notes

Use this chapter for the October 28 source/local comparison, the historical reason not to restore old headings, and the bounded alignment proposal. Use chapter 06 for its preserved October 27 blueprint evidence and chapters 01–05 for their October 22 ecosystem study. Recheck only changed/disputed inputs before claiming current behavior; preserve source IDs and review/input identities. Execution progress and final acceptance belong only in [the governing feature](../../../../odd/tasks/gentle-ai-odd-blueprint-research.md), not this research page.
