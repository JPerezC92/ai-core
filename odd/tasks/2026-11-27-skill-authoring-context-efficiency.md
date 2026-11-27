# Skill authoring context efficiency

> **Status:** closed
> **Closed:** 2026-11-27
> **Disposition:** completed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-27
> **Objective:** Improve skill-authoring context efficiency while preserving valid obligations.
> **Branch:** `refactor/odd/workflow-efficiency`.
> **Delivery:** One scoped documentation unit; forecast under 400 authored changed lines; rollback covers the skill and these records.
> **Runner:** node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks

## Specs

- S1 — Skill authoring uses token and line guidance and applicability-based disclosure. Exact requirement: "Treat 5,000 tokens and 500 lines as upper guidance, not targets." Acceptance: inspect the authoring rules and verify all three approved local-policy retirements.
- S2 — Specialized procedures load only for applicable actions, without weakening safeguards. Exact requirement: "Every conditional reference must state when it is required and before which dependent action it must be consulted." Acceptance: walk creation, modification, rename, migration, declined cleanup and integrity checking against the instructions.
- S3 — Portable, harness and local requirements remain distinct and valid. Exact requirement: "Correcting the portable specification requirements, including the optional compatibility field's length constraint." Acceptance: compare the metadata instructions to the official specification.
- S4 — Existing obligations and activation cases remain accounted for. Exact requirement: "Preserve all valid existing capabilities, safety obligations, authorization boundaries, metadata rules, ownership contracts, and observable behavior." Acceptance: compare original and candidate instructions and record retained, translated and authorized retired obligations.
- S5 — Context costs are compared by operation. Exact requirement: "Evaluate the combined content required for ordinary creation and modification, including mandatory references." Acceptance: measure changed files and report estimated required content for each operation.
- S6 — The checklist's unique applicable criteria are integrated without breaking live consumers. Exact requirement: "Preserve every applicable criterion and its conditional applicability." Acceptance: compare the original checklist against the integrated checks and search for live references before deleting it.

## Tasks

- T1 | S1, S2, S3, S4, S6 | inline (bounded skill documentation rewrite) — Cipher 🔓 (Lead Orchestrator) | done | commit: 96742cd6a0b8c5cd16e8aaa578c5e2b9923103a9
- T2 | S5 | inline (F2 operation-specific comparison) — Cipher 🔓 (Lead Orchestrator) | done | commit: 7cdea1ee215ee5e3ca0488d279d0253385e8ce5c

## Log

- L1 — 2026-11-27 — Original request, verbatim:

````
# AICore — Phase 1.1: Skill Authoring and Context Efficiency

The objective is to improve the existing skill-authoring standard so that future skills consume less context without sacrificing correctness, functionality, safety, or portability.

## Authorized scope

- `.agents/skills/op-skill-creator/SKILL.md`
- `.agents/skills/op-skill-creator/references/_quality-checklist.md`
- Additional references within that skill only if justified and approved.

Do not audit or migrate the entire skill catalog in this phase.

## Confirmed findings to reconcile

1. The current standard uses 5,000 words instead of a token-oriented budget.
2. Line count alone is insufficient to establish context efficiency.
3. Authoring requirements are duplicated between SKILL.md and the quality checklist.
4. Existing reference-reading instructions may encourage unnecessary document loading.
5. Specialized operations such as migration, rename, source cleanup, and optional Markdown integrity checking are loaded even when unrelated to the requested operation.
6. Portable skill requirements must remain distinct from harness-specific behavior and AICore-specific conventions.

## Required design direction

- Follow the official Agent Skills specification:
  https://agentskills.io/specification
- Consider Cursor's official progressive-loading guidance:
  https://cursor.com/docs/skills
- Keep the main SKILL.md focused, preferably below 5,000 tokens and 500 lines.
- Treat those values as upper guidance, not desired document sizes.
- Prefer shorter skills whenever their responsibilities allow it.
- Keep descriptions concise while preserving accurate activation conditions.
- Establish a single authoritative owner for each rule.
- Apply progressive disclosure to specialized procedures, not only static reference material.
- Every conditional reference must state when it is required and before which dependent action it must be consulted.
- Do not move universally applicable safeguards into optional references.
- Do not introduce unconditional reference chains or artificial file fragmentation.
- Reuse information already available in context when its identity and applicability are established.

## Non-negotiable constraints

Preserve all valid existing capabilities, safety obligations, authorization boundaries, metadata rules, ownership contracts, and observable behavior.

Preserve the distinction between portable, harness-specific, and project-specific requirements.

Preserve Herald's exclusive Git and GitHub authority, the skills-first architecture, and the existing review policy.

Do not introduce new scripts, tokenizers, validators, plugins, MCP servers, agents, or mandatory review gates.

Do not change destination repositories or synchronization behavior.

Do not change existing skill IDs or compatibility metadata without explicit authorization.

Do not apply cosmetic changes merely to reduce line count.

## First deliverable — bounded proposal

Inspect the latest local versions of the two authorized files. Reconcile the confirmed findings against the actual current content.

Provide:

- Actual file sizes, line counts, and approximate token counts if obtainable with existing tools.
- Confirmed defects and any findings that are no longer applicable.
- The proposed structure and rule ownership.
- Specific instructions to retain, consolidate, or relocate.
- Any proposed retirement of an existing obligation, with explicit rationale and required authorization.
- Expected context-efficiency improvements and possible regressions.

Keep the report concise. Do not reproduce entire existing documents or create a second policy document.

Do not implement changes yet. Request approval of the bounded proposal.

Challenge the proposed approach if a simpler or safer solution exists. Do not agree with a requirement merely because the user suggested it.
````
- L2 — 2026-11-27 — Implementation approval and refinements, verbatim:

````
Approved with the following refinements. Proceed with the bounded implementation.

## 1. Scope and policy approval

I explicitly authorize:

- Replacing the hard 5,000-word ceiling with token-oriented guidance.
- Changing the existing 500-line ceiling to recommended guidance.
- Replacing the automatic ~30-line extraction threshold with applicability-based progressive disclosure.
- Adding one focused, skill-local reference for specialized operations.
- Correcting the portable specification requirements, including the optional compatibility field's length constraint.

These are three local-policy retirements, not two. Account for them accurately.

Do not introduce new behavior or permission mechanisms for the experimental allowed-tools field.

## 2. Optimize actual context consumption

The primary objective is to reduce the cumulative context required to perform an operation, not merely the size of SKILL.md.

Evaluate the combined content required for ordinary creation and modification, including mandatory references.

Do not consider moving text between files a successful optimization unless it reduces unnecessary loading or improves rule ownership.

Treat 5,000 tokens and 500 lines as upper guidance, not targets.

## 3. Simplify the quality checklist

Preserve all applicable, unique quality criteria, but do not turn the checklist into a navigation layer that forces repeated document reads.

The author should reuse applicable instructions already available in context.

Critically evaluate whether the checklist remains independently useful after deduplication. If integrating its remaining unique criteria into SKILL.md would produce a simpler and more efficient result, report that alternative before deleting the existing file.

Do not preserve unnecessary structure merely because it already exists.

## 4. Specialized procedures

The additional reference is authorized.

Keep it focused, directly reachable from SKILL.md, and conditionally loaded.

If only a specific section is relevant, avoid requiring unrelated procedures to be read, provided the harness supports bounded reading and the applicable obligations remain complete.

Preserve universal authorization, safety, collision, metadata, and cleanup restrictions in the main file.

No implied cleanup authorization and no expansion of tool authority.

## 5. Verification

Use existing tools and proportionate verification.

Provide a concise before-and-after comparison of:

- File sizes and line counts.
- Approximate token counts, clearly identified as estimates.
- Required documents and approximate cumulative context for ordinary creation, modification, rename, migration, declined cleanup, and optional integrity checking.
- Preserved obligations, consolidated duplicates, and explicitly authorized policy retirements.

Verify that the specialized reference has an unambiguous activation condition and is required before its dependent actions.

Preserve all existing activation cases.

Do not impose an arbitrary percentage reduction or sacrifice correctness to meet a size metric.

## 6. Constraints

- Preserve existing functionality, valid contracts, and security controls.
- Preserve Herald's exclusive Git and GitHub authority.
- Preserve the skills-first architecture and existing review policy.
- Do not introduce scripts, validators, tokenizers, plugins, agents, or new mandatory gates.
- Do not modify other skills, destination repositories, synchronization behavior, or harness configuration.
- Use LF line endings.
- System One is not in use. Its unavailability is not a blocker. Do not investigate or retry it.
- Independent review is not authorized at this stage.

Avoid another broad audit. Implement the approved minimal correction and perform the necessary targeted verification.

If a new decision would change an existing contract beyond this authorization, stop and ask.

Report the final changed paths, verification results, remaining concerns, and explicit completion status.

Do not commit, push, or open a PR without further authorization.
````
- L3 — 2026-11-27 — Candidate authored in `op-skill-creator`; author self-review and complete obligation accounting remain in progress. The retired 5,000-word ceiling, mandatory 500-line ceiling and roughly 30-line extraction threshold are replaced with guidance by explicit user authorization. Task stays open pending verification and any later authorized commit.
- L4 — 2026-11-27 — Record scope approval, verbatim (the user repeated this identical message):

````
Approved. You correctly identified the conflict between the authorized file scope and the mandatory ODD workflow.

I authorize the additional ODD record writes required for this implementation, subject to the following constraints:

- Create the proposed task record.
- Check whether an existing durable feature file already governs skill authoring and maintenance.
- Prefer updating the existing feature owner rather than creating a new one.
- Create a new feature file only if no appropriate owner exists and the current ODD contract requires it.
- Keep both records concise and proportionate to the actual scope.
- Reference authoritative requirements instead of duplicating entire policies, proposals, or verification reports.

All previously approved implementation requirements and restrictions remain in force.

This additional authorization does not expand the implementation scope beyond op-skill-creator and its necessary ODD records.

Do not audit unrelated features, modify other skills, change the ODD workflow, or introduce additional infrastructure.

No commit, push, PR, or independent review is authorized. Keep the task record open as required by the existing workflow.

Proceed directly with implementation and targeted verification. Do not repeat the completed exploration or proposal analysis unless new evidence materially invalidates it.

Report the final implementation, before-and-after context estimates, preserved obligations, verification results, changed paths, and explicit completion status.
````
- L5 — 2026-11-27 — Verification continuation, verbatim:

````
Continue with the authorized implementation and complete the pending verification.

The preliminary reduction is promising, but the implementation is not yet accepted.

## 1. Complete the existing work

- Finish the original-to-candidate obligation accounting.
- Verify all required operational scenarios.
- Complete the author self-review.
- Complete the required ODD records and mirror handling according to the existing contract.
- Update durable feature requirements only when their corresponding evidence supports completion.
- Keep the task record open as previously instructed.

Preserve the required verbatim request and correction history, but avoid unnecessary duplication beyond the existing contractual requirements.

## 2. One targeted structural question

The quality checklist is now only 11 lines and 1,247 bytes.

Evaluate whether retaining it as a separate file provides a measurable structural or context-loading benefit.

Specifically, determine:

- Whether it must be loaded for every ordinary authoring operation.
- Whether integrating its remaining unique criteria into SKILL.md would eliminate a mandatory tool call.
- Whether separation provides genuinely useful deferred loading or reuse.
- Whether integration would introduce any semantic, ownership, or compatibility regression.

Provide a concise recommendation with evidence.

Do not delete or merge the checklist without further authorization. This question must not trigger another broad audit.

## 3. Verification boundaries

Reuse existing evidence when it remains valid.

Do not repeat completed exploration, successful validations, or unchanged scenario checks unnecessarily.

Distinguish static instruction-size estimates from actual runtime token savings.

Do not claim that all obligations are preserved until the accounting and scenario verification are complete.

## 4. Execution constraints

All previous restrictions remain in force.

- No System One calls.
- No independent review.
- No Git operations.
- No commit, push, or PR.
- No unrelated changes.
- No additional infrastructure.
- No expansion of the authorized file scope.

Continue without additional intermediate reports unless you encounter a genuine blocker, material regression, or decision requiring my authorization.

Your next report should contain the completed implementation assessment, verification evidence, the checklist recommendation, remaining findings if any, and explicit completion status.
````
- L6 — 2026-11-27 — Author self-review compared the original `SKILL.md` and `_quality-checklist.md` read at session start with the candidate files. Obligation accounting: retained ODD preflight and evidence, inputs and missing-input routing, operation classification, portable name and description validation and local uniqueness limits, metadata sourcing/preservation/conflict handling/version advancement, generated-body ownership/markers/inputs/bindings/schemas/error guidance, collision and write boundaries, checks before and after writes, runtime/local/portable distinction, complete rewrite accounting, changed-path reporting, zero-open-findings self-check and opt-in independent review. Retained checklist-specific vendor prefixes, diagrams, nested fences, SQL bounds and image filter columns; examples and troubleshooting remain governed by the main body. Translated reference selection to applicability with context reuse, operational procedures into the directly referenced specialized section, and duplicated checklist checks into the main owner; existing sample frontmatter is illustrative and removed without changing metadata rules. Retired with explicit user authority: 5,000-word ceiling, hard 500-line ceiling, and automatic roughly 30-line extraction. Added portable compatibility length; did not introduce allowed-tools behavior. Self-review corrected the absent-convention preservation wording. No claim is made about runtime enforcement.
- L7 — 2026-11-27 — Manual normal/adverse walkthrough against the candidate: create and modify read main plus checklist, validate metadata, prevent unrelated overwrite and recheck after write; modify also preserves typed metadata and accounts for the original. Rename and migration must read the specialized section before preview or execution and obtain explicit target/helper/reference/path approval; decline of cleanup leaves source and support tree intact, while any delete/archive requires separate approval after target/helper/reference verification. Optional integrity checking reads its own section and script before use with caller-supplied policy, bounded inputs and documented exit semantics; it is never mandatory. Missing required input or unresolved migration choice stops. These are static instruction walkthroughs, not executed skill operations. R1/R2 in `odd/features/skill-authoring.md` are supported by this accounting and walkthrough; no unaffected durable requirements exist.
- L8 — 2026-11-27 — Cipher ran `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks/2026-11-27-skill-authoring-context-efficiency.md` and `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features/skill-authoring.md`; both reported ok and the latter derived achieved. They verify anatomy only, not the walkthrough or runtime behavior. No executable failure applies to this prose-only rewrite. Full mirror remains pending: bounded discovery returned no match but does not prove absence, and no complete payload write and independent readback has been performed; next action is verify exact project/feature identity, preserve any conflicting copy, then store and compare the complete record. No commit, PR or independent review authorized.
- L9 — 2026-11-27 — Checklist integration authorization, verbatim:

````
Approved. Proceed with the final, bounded simplification.

## Checklist integration

I authorize integrating the remaining unique criteria from `_quality-checklist.md` into `SKILL.md` and deleting the separate checklist.

Before deletion:

- Verify actual consumers and references to the checklist.
- Preserve every applicable criterion and its conditional applicability.
- Update references within the authorized scope.
- If an external consumer requires modification, report it before expanding the scope.

Do not perform another general rewrite of the skill.

The intended final structure is SKILL.md plus the conditionally loaded specialized-operations reference.

## Complete verification

- Reuse all previous verification evidence that remains valid.
- Recheck only obligations, scenarios, references, and records affected by the checklist integration.
- Update the final file-size and cumulative context estimates.
- Complete the author self-review and obligation accounting.
- Complete the required ODD mirror handling under the existing contract.

Do not introduce new mechanisms or workarounds to satisfy mirror handling. If the existing mechanism genuinely prevents completion, report the precise blocker rather than entering repeated recovery loops.

Keep the task record open as previously instructed.

## Constraints

All previous restrictions remain in force.

No Git operations, commits, pushes, PRs, independent reviews, System One calls, new infrastructure, or unrelated changes are authorized.

Do not modify the ODD workflow itself.

Avoid repeating successful verification steps or reconstructing evidence already available and still valid.

Provide a concise final report containing changed paths, final context estimates, verification results, remaining blockers, and explicit completion status.
````
- L10 — 2026-11-27 — Checklist integration: before deletion a bounded repository text search for `_quality-checklist.md` found the two live pointers in the skill and only historical request/accounting mentions in this record; after deletion only those historical mentions remain. Author self-review mapped every remaining checklist criterion to the main skill: vendor-prefix rule, conditional Mermaid and fence rules, diagnostic SQL constraints, screenshot filter columns, local OpenCode compatibility, other-harness substitution, and finished-draft self-check without an additional gate. Original duplicate criteria were already in the main skill. An authoring walkthrough confirms these checks are available before and after writing without a checklist read; prior specialized-operation walkthrough is unaffected. No external live reference was identified in the searched repository, which does not establish external consumer absence. Mirror remains pending: the complete payload has not been stored or independently compared; a bounded name search found no match but is not proof of absence. Task remains active; commit and independent review remain unauthorized.
- L11 — 2026-11-27 — User acceptance and mirror instruction, verbatim:

````
The skill implementation is accepted at the author-verification level. No further optimization or structural changes to the skill are requested.

Complete the remaining mandatory ODD mirror operation now.

Your previous reports identify an unfinished operation, not an established blocker.

- Resolve the mirror identity according to the existing contract.
- Store the required complete record.
- Read it back and verify its integrity using the existing mechanism.
- Reuse existing valid evidence.
- Do not perform another general audit or repeat completed validations.

The required mirror readback is not an independent agent review. The former is authorized; the latter remains unauthorized.

If the mirror operation actually fails, report the specific operation, error, and resulting blocker. Do not enter repetitive recovery loops or introduce workarounds.

Do not expand the investigation into hypothetical external checklist consumers unless concrete evidence establishes a dependency.

All previous restrictions remain in force. Keep the task record open. No Git operations, commits, pushes, PRs, System One calls, or unrelated changes.

Report only the remaining operation's outcome and the final completion status.
````
- L12 — 2026-11-27 — Mirror identity remains unresolved: searches for the feature title and locator returned no matches but the exposed full-text search has neither exact identity nor explicit project-scope filters; those results alone do not prove absence of an existing mirror. No full payload was written or read back and no backend error occurred. The project is `github.com-personal/JPerezC92/ai-core`, the feature is `skill-authoring-context-efficiency`, and the intended locator is this record. Preserve this pending state rather than claim synchronization or create an unverified duplicate.
- L13 — 2026-11-27 — The user authorized combined delivery with the ODD workflow efficiency candidate and explicitly authorized applying its revised policy to both tasks. That candidate retires the mandatory mirror prerequisite; L8, L10 and L12 remain historical facts, no synchronization is claimed and adoption on main is not claimed. User authorized commit-bound verification, closure and one PR, plus focused independent review; merge, tags, branch deletion, System One and destination synchronization remain unauthorized. The feature stays active until its implementation commit, verification and closure evidence exist.
- L14 — 2026-11-27 — Herald committed skill-authoring implementation as `96742cd6a0b8c5cd16e8aaa578c5e2b9923103a9` on `refactor/odd/workflow-efficiency`; the ODD implementation is `85441acb04b1d7a482686ac40180d3c3a696ba20`. Closure is blocked on the retirement-policy conflict described in `odd/tasks/2026-11-27-odd-workflow-efficiency.md` L9; user prohibited unrelated historical cleanup, and the existing policy prescribes deletion of eligible old records during closure. No mirror synchronization, closure, independent review or publication is claimed.
- L15 — 2026-11-27 — Prior closure at `b13e7a4482c494d1fa5f8e52250bbec059b922a7` assessed S1–S6 against `96742cd6a0b8c5cd16e8aaa578c5e2b9923103a9`; the independent review found S5's operation-specific comparison missing and the record is reopened at L16. No mirror synchronization or adoption on main was claimed.
- L16 — 2026-11-27 — Independent review F2 against `b13e7a4482c494d1fa5f8e52250bbec059b922a7` found the required S5 size comparison absent. Herald measured base Git blobs: original `SKILL.md` 15,915 bytes and 103 lines (current 92 lines plus 22 deletions minus 11 additions), original `_quality-checklist.md` 7,790 bytes and 54 lines; the current `SKILL.md` is 14,285 bytes/92 lines and `_specialized-operations.md` is 2,754 bytes/20 lines. Before, ordinary creation, modification, rename, migration, declined cleanup and optional integrity checking required the 23,705-byte main-plus-checklist baseline. After, ordinary creation and modification require the 14,285-byte main file; rename, migration, declined cleanup and optional integrity checking require the applicable specialized reference too, at most 17,039 bytes total when loaded in full. A crude bytes/4 estimate is roughly 5,926 tokens before, 3,571 after for ordinary operations, and 4,260 after for specialized operations; these are not tokenizer or runtime measurements, and bounded section reads may load less. Prior source is base blob `61987b1bb864f313cc165fa23f07020202ae1fea`, checklist blob `9f63e9b75e39d5ff8c6555d31db0e067adc9f65e`; current blobs are `2dc58f188bac02657bb00c9ce9f038fe5d42e75e` and `d3408b315e6c73628bcecfc9ab803df7922dd0cc`. This comparison corrects the unsupported S5 closure claim; it does not assert measured runtime savings.
- L17 — Close: S1–S4 and S6 are verified against `96742cd6a0b8c5cd16e8aaa578c5e2b9923103a9` using the accounting and walkthroughs at L6–L10; S5 is supported by the measured comparison committed at `7cdea1ee215ee5e3ca0488d279d0253385e8ce5c` and reported at L16. No applicable executable failure applies to the prose-only skill rewrite. The user-authorized ODD candidate removes the mandatory mirror prerequisite; no mirror synchronization or adoption on main is claimed. Final-head independent review remains pending.
