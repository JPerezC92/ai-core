<!-- core:begin -->
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
- Clear and retire a resolved debt in the same authorized, committed work unit: delete its entry from this register and preserve complete resolution evidence in the governing feature record and its Log, backed by delivery evidence. Identify the debt, evidence that every resolution criterion is met, validation results, independent review results, and the delivering commit; the commit must carry the resolution evidence or its durable governing-record reference. If a PR exists, its body must also carry that evidence or reference; a PR is not required for retirement. Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one authorized, committed resolution work unit.
- **User-directed cancellation.** An explicit user decision may cancel an open debt without satisfying its resolution criteria. Cancellation is not resolution or clearance. Before removing the entry, preserve the user decision, unmet criteria, and supporting evidence in the governing feature record; include the cancellation and its evidence in the authorized delivery. This route does not waive the resolution-evidence requirements for resolved debts.
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.

## Register
<!-- core:end -->

<!-- project:begin -->
## DEBT-042 — Incident-workflow `entities.py` role bucket (unconfirmed, needs more review)

- **Date:** 2026-11-08
- **Review status:** Unconfirmed observation. This entry records a possible architecture conformance gap that needs more review; it asserts no defect, selects no target layout, and authorizes no implementation.
- **Description:** The Python module `.opencode/skills/incident-workflow/scripts/incident_workflow_pkg/domain/entities.py` is named for a role rather than a business concept and mixes several responsibilities: the `Problem` entity, a shared `_NamedCell` base, five closed-value enums, one policy constant, and one enum that the entity does not own. Whether this breaches the applicable rules depends on how the aggregate-ownership allowance is read, so the question is recorded for an architecture ruling rather than resolved here.
- **Direct evidence:** Measured source read on 2026-11-08: `entities.py:1` module docstring reads "Identity-bearing Problem register entity and named domain values"; `_NamedCell` at 22–31 with behaviour (`from_cell`); enums `Team` 33–38, `Lifecycle` 40–48, `AllowExact` 50–54, `Status` 57–62 and `IdentificationVerdict` 64–70 (five, not four); `MATCHABLE_LIFECYCLES` 73–79; `Problem` entity 82–266. `IdentificationVerdict` is consumed only by `domain/rules.py` (lines 82, 311, 702–777) and is not a `Problem` constructor field, while `Team`, `Lifecycle`, `AllowExact` and `Status` are (85–100). Ten files import from this module, measured by bounded literal search across `.opencode/skills` (`incident_workflow_pkg/__init__.py:11`, `entry.py:23`, `application/validate_pre_close.py:6`, `domain/__init__.py:7`, `domain/_test_support.py:5`, `domain/ports.py:8`, `domain/rules.py:13`, `domain/test_problem_activate.py:12`, `domain/test_problem_invariants.py:12`, `domain/test_problem_create.py:10`). Governing text for the strict reading: `architecture/implementation/shapes/scripts.md` P4 line 21 ("One entity per file including children, and one rule-bearing type per module; no generic multi-concept entity/model/value-object buckets") and `architecture/implementation/stacks/python.md` `Concept-role filenames` (`<concept>_<role>.py`, record row line 77) with `architecture/implementation/architecture.md` C8/C10. Governing text against the strict reading: the same P4 sentence keeps "an aggregate's root, children, owned values, events and repository port together", `architecture/implementation/shapes/backend.md:21` places owned value objects "logically beside the root", and `python.md:14` moves value modules into a `value_objects/` subfolder only at a second owned value under a business owner. Only one entity and one rule-bearing type are present, and `Problem` is root-only with no children.
- **Resolution criteria:** Obtain an architecture ruling from Bastion 🧱 (Backend & Scripts Architect), the owner of the scripts shape and Python guide, on whether a role-named module holding an entity, its four owned values, a shared base and one foreign concept breaches P4/C10 given the aggregate-ownership allowance, and which target layout that ruling implies if it does. Then either implement the ruled layout in separately authorized work with the applicable architecture and test verification, or record the no-action ruling here. Retire this entry under this register's canonical retirement rule with direct resolution evidence in a governing record and its Log.
- **Explicit deferral decision:** User instruction on 2026-11-08, verbatim: "add that as a debt but i am not sure if its really a problem  make it a needs more review". This records an unconfirmed observation pending an architecture ruling. It is not a defect admission, a permanent waiver, a repository-wide conformance claim, or authority to change any source file.

## DEBT-043 — Coordinator made unverified capability claims that forced rework

- **Date:** 2026-11-08
- **Description:** Cipher 🔓 (Lead Orchestrator) asserted integration capabilities without evidence and had to retract them after they shaped implementation: (a) claimed a separate MCP "cannot receive images" and used that to justify the plugin-only design, then found a schema-defined image argument is viable; (b) claimed the OpenCode plugin could call MCP tools directly, then found v2.2.5 exposes MCP management but no documented `callTool`; (c) designed the question profile to demand model citations although `/v1/systemone` returns only choice, probabilities and confidence. Each retraction invalidated prior reasoning and caused discarded or rewritten work.
- **Direct evidence:** Feature `odd/tasks/2026-11-08-odd-adviser.md` Log entries L12 (plugin-vs-MCP comparison), L19 (API returns no citations), L24–L25 (no documented `callTool`; required an official separate client). Profile corrections in L23 and L26 record the citation wording removal. Implementation files created under the superseded assumptions: `src/domain/user-only-decision.ts`, `src/test/helpers/evidence.factory.ts`, and its test are recorded in L16 as superseded.
- **Resolution criteria:** Record each capability claim with the exact inspected source and revision before it drives a design decision, and for integration claims prefer a runnable probe over documentation inference. Clear only after a delivery work unit where dependency-free claims are supported by an executed probe or an explicitly labeled hypothesis, and the feature record cites that probe.
- **Explicit deferral decision:** User instruction on 2026-11-08, verbatim: "u maked many errors add these ass debt u didnt resolved the uncertain asking me u just started codding and didnt told me about your decisions". Deferred, not waived; the underlying feature remains open.

## DEBT-044 — Coordinator took user-owned design decisions without asking

- **Date:** 2026-11-08
- **Description:** Several decisions that materially shaped the delivered design were made unilaterally instead of being raised as focused questions: (a) Node's built-in test runner instead of the project's reference Vitest stack, later reversed by the user; (b) the `tsconfig.json` strictness and option set, including `erasableSyntaxOnly`, `verbatimModuleSyntax` and `noImplicitOverride`; (c) the three ODD evidence questions, their ids and their `present`/`absent`/`unknown` partition; (d) the operational trace location `output/system1/events.jsonl` and its default metadata-only content; (e) the plugin/MCP split and process ownership model; (f) the derived request-side `images` encoding, which was never observed against the live endpoint; (g) the advice-injection shape into the main model's context.
- **Direct evidence:** Feature Log records the decisions at L5 (runner), L22 (trace location proposed), L24–L25 (transport), and the current `tsconfig.json`. The Vitest reversal is recorded in L31. The reviewer noted the unobserved request encoding in `crucible-gateway-tests-1`.
- **Resolution criteria:** Present each open decision to the user with evidence and a recommended default before dependent implementation, and record the user's answer in the feature Log. This debt clears when every listed decision either carries a recorded user answer or is explicitly labeled an implemented hypothesis with the evidence a live probe needs.
- **Explicit deferral decision:** User instruction on 2026-11-08, verbatim: "u maked many errors add these ass debt u didnt resolved the uncertain asking me u just started codding and didnt told me about your decisions". Deferred; the user's Vitest instruction is the first recorded answer to item (a).

## DEBT-045 — Automatic advisory delivery recommended before it was proven

- **Date:** 2026-11-08
- **Description:** Cipher 🔓 (Lead Orchestrator) recommended the OpenCode-plugin design on the strength of documented hook behaviour, without first proving that a plugin-written advisory reaches the model. The plugin loads, captures inline images, calls the local model and composes an advisory; the final delivery hop is unconfirmed. The recommendation therefore rested on an unverified premise, and the inverted cost is concrete: the MCP boundary was proven by a live probe in minutes, while the unproven hop consumed many implementation and review rounds.
- **Direct evidence:** Feature `odd/tasks/2026-11-08-odd-adviser.md` Log L41 proves the MCP boundary with a real 694 KB screenshot (`ok: true`, `visual_evidence: present`, 239 ms). L42 records two real defects found only from runtime diagnostics (`prompt` hook does not fire for ordinary messages; messages carry `content`, not `parts`). L43 records that a valid `SystemPart` was pushed (`context injected parts=5`) while the coordinator did not observe the sentinel in its own context, so delivery is unproven. L44 records the pivot to the registered `system-one` MCP tool, which works and is observable.
- **Resolution criteria:** For any future automatic-injection recommendation, demonstrate the delivery hop end to end before recommending the design: a distinctive sentinel is observed by the consuming model, and the observation method is stated. Clear this debt in a work unit that either (a) shows delivery working with recorded sentinel evidence, or (b) records an explicit user decision to keep the automatic path disabled and retain the tool surface only.
- **Explicit deferral decision:** Recorded by Cipher 🔓 (Lead Orchestrator) on 2026-11-08 after the user challenged the contradiction, verbatim: `U TOLD ME TEH PLUGIN IS BETTER AND NOW U SAID THE PLUGIN DONT WORKS?`. Deferred, not waived; the affected capability stays unclaimed.

**ID to use for the next new debt:** `DEBT-046`. This is an allocation counter, not an open debt.
<!-- project:end -->
