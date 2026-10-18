<!-- core:begin -->
# User story — pr-review-corrections

> **Created:** 2026-10-16
> **Title:** PR review corrections
> **Status:** active
> **version:** 1.1.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/agents/inquisitor.md`, `.opencode/agents/herald.md`, `.opencode/skills/git-pr/SKILL.md`, `knowledge/agents.md`

## Persona

- A maintainer at the PR review boundary whose authorized PR work may contain an evidence-backed factual wording defect to correct, and who must be able to tell from every review-round report whether each finding is fixed, open, deferred, or rejected.

## Goal

- **G:** Apply an in-scope reversible factual correction through its authorized writer without redundant permission requests, and report every review round so each finding's resolution state is unambiguous.
  - Done when: the minimal supported correction is persisted, live-verified against the same PR/head, and reported while preserving unrelated content, exclusive writer ownership, and the existing scope, authority, and freshness gates; and every review-round report names each finding's status from a closed vocabulary, leads with an explicit open-count verdict, and carries each finding across rounds until it is resolved or rejected.

## Scenario

- A PR Summary count disagrees with the disclosed list: the evidence-backed count correction proceeds through the authorized prose writer and is reported without another permission request.
- An evidence row or checkbox fact needs correction: it goes to the evidence writer rather than a competing prose writer.
- Another writer still owns the PR body: the correction waits for an explicit exclusive handoff after prior access ceases; workers never race edits.
- A proposed correction changes scope, lacks factual support, or requires destructive action: the existing decision/evidence gate applies instead of treating the change as trivial.
- The PR head or body diverges before persistence: the writer stops rather than overwriting stale content; a saved correction is accepted only after live verification.
- A review round closes with mixed outcomes: the report's first line states how many findings are open and whether anything blocks, and every row's status — fixed, open, deferred, or rejected — is explicit with its basis or destination, so a reader never has to infer closure from prose.

## Acceptance criteria

- ✅ **AC1:** A confirmed reversible factual correction within existing approved scope proceeds without another permission request and is reported with its factual basis.
- ✅ **AC2:** Evidence/checkbox corrections and general prose corrections route through their respective authorized writers; only one writer owns the body at a time and handoff occurs only after prior access ceases.
- ✅ **AC3:** A correction is a minimal patch preserving unrelated prose, evidence, and verified ticks; prose remains grounded in the authorized draft source rather than newly invented claims.
- ✅ **AC4:** Freshness is checked before mutation and the persisted change is live-reread against the same PR/head; stale or divergent input stops instead of overwriting.
- ✅ **AC5:** Scope expansion, unsupported facts, destructive actions, or missing authority stop for the existing decision/evidence process rather than being classified as trivial.
- ✅ **AC6 — Findings status reporting:** Every review-round report names each finding's resolution status from a closed set — fixed, open, deferred, rejected — leads with an explicit open-count verdict stating whether anything is unresolved or blocking, totals the statuses, and carries findings across rounds until they are resolved or rejected rather than dropping them.
- ✅ **AC7 — Status evidence:** A fixed status names the remediation and the party that verified it; a deferred status names its destination and why it is non-blocking; a rejected status carries the literal refutation output — so no resolution status is asserted without its basis.

## Proof

- AC1 → `knowledge/agents.md` `### PR review findings (adjudication)` body-prose row · `.opencode/agents/herald.md` `#### Authorized factual prose correction` step 6 · clause-application walkthrough (recorded in `## Local evidence`)
- AC2 → `.opencode/agents/inquisitor.md` `##### PR-body evidence boundary` · `.opencode/agents/herald.md` `#### Authorized factual prose correction` step 1 observed release · clause-application walkthrough (recorded in `## Local evidence`)
- AC3 → `.opencode/agents/herald.md` `#### Authorized factual prose correction` step 3 minimal delta applied to the fresh live body preserving evidence/ticks/unrelated prose · `.opencode/skills/git-pr/SKILL.md` `### Post-PR evidence contract` · clause-application walkthrough (recorded in `## Local evidence`)
- AC4 → `.opencode/agents/herald.md` `#### Authorized factual prose correction` steps 4–5 pre-write freshness and live reread · `.opencode/agents/inquisitor.md` `##### PR-body evidence boundary` · clause-application walkthrough (recorded in `## Local evidence`)
- AC5 → `knowledge/agents.md` `### PR review findings (adjudication)` scope/destructive rows · `### User-Authority-Only rule` · `.opencode/agents/herald.md` `#### Authorized factual prose correction` stop list · clause-application walkthrough (recorded in `## Local evidence`)
- AC6 → `knowledge/agents.md` `### PR review findings (adjudication)` `First line (open-count verdict)` / `Open count` / `Closed status vocabulary` / `Counts line` / `Carry-over` · `sentinel-review-1 [PASS]`
- AC7 → `knowledge/agents.md` `### PR review findings (adjudication)` `Status basis` · `sentinel-review-1 [PASS]`

## Constraints

- Draft generation never mutates live GitHub state — because its output is a review artifact, not permission to publish or alter a PR.
- The evidence reviewer remains evidence-only; general prose corrections require the authorized prose writer — because correction routing must not silently expand the reviewer's mutation authority.
- Only one active writer owns the PR body, and evidence collection retains its own evidence-derived gate — because a prose correction cannot replace verification or permit competing updates.
- No release, merge, destructive-action, or new execution authority is inferred from a correction — because the existing user authorization and role boundaries remain governing.

<!-- core:end -->

<!-- project:begin -->
## Approval record

- 2026-10-16 — The user approved CREATE and the displayed correction contract after catalogue/ownership and collision review, required a designed flow rather than a convention bullet, and subsequently authorized story persistence first. This approval does not authorize a live PR edit or release.
- 2026-10-18 — The user approved UPDATE of this contract with the review-findings-status reporting revision (AC6/AC7) after the ownership and collision review, choosing this story as the owner over a CREATE alternative; the draft round-summary format — closed status vocabulary (fixed/open/deferred/rejected), first-line open-count verdict, basis or destination per status, cross-round carry-over — was approved in the same decision. This approval does not authorize code, rules-text, or release actions beyond the planned change.

## Local evidence

- AC1–AC5 were exercised on 2026-10-16 by a synthetic, non-live walkthrough (invented PR/head; nothing fetched or written): an authorized Summary-count repair proceeded without a repeated permission request and reported its factual basis; the prose writer stayed out of the body until the evidence writer's release was observed; the delta was applied to the fresh live body with evidence, ticks and unrelated prose preserved; a divergent or failed reread stopped the write; an unsupported count and an unheld evidence claim stopped for the decision/evidence process. This is clause-application evidence, not a live PR-head execution or destination verification.

## Revision tracking

- 2026-10-18 — Proof-form correction (approved with the cleanup round): the AC1–AC5 Proof lines now carry portable surfaces plus a neutral pointer to `## Local evidence`; the dated walkthrough narratives remain only in project-owned `## Local evidence`. No criterion text, promise, or mark changed.
- 2026-10-16 — Approved active contract persisted. Evidence corrections remain owned by the PR evidence-collection contract; this contract adds the distinct factual prose-correction outcome without turning draft generation into a GitHub writer. The authorized prose writer's workflow and exclusive handoff are now specified, and AC1–AC5 are established by clause application on the synthetic 2026-10-16 PR walkthrough. Delivery history is finalized as PR #68. This source-authored story is not automatically cleared for distribution, and no grant, destination mutation, or release action is implied.
- 2026-10-18 — Approved the review-findings-status reporting revision (UPDATE `pr-review-corrections` AC6/AC7) persisted with pending history: AC6/AC7 stay `⬜`, their Proof targets are explicitly unverified, and no Change log entry is written until a delivery-matching commit/PR/ticket exists. Completion, `## Outcome`, archival, and release handoff remain blocked until the actual reference is established.
- 2026-10-18 — Finalized: AC6/AC7 delivered by commit `b111070` on branch `feat/agents/standardize-review-findings-status`; Proof repointed to the delivered round-summary contract surfaces in `knowledge/agents.md`, the bounded Change log entry added, and the pending history above resolved. Gates on the frozen candidate: independent phase-gate review `[PASS]` (writer `round-summary-forge-1` ≠ reviewer `sentinel-review-1`), plan validator `ok`, byte-identity of the adjudication table and refutation rule verified. Source-local; does not ship.

## Change log

- 2026-10-16 — aicore-debt-fixes-20261016 (PR #68): added the authorized serialized factual prose-correction path on the fresh live body, with observed writer release, preserved evidence and a post-write live reread.
- 2026-10-18 — review-findings-status-reporting-20261018 (b111070): delivered AC6/AC7 — the review-round report now states each finding's resolution status from a closed set (fixed, open, deferred, rejected), leads with an open-count verdict, totals the statuses, and carries findings across rounds.
<!-- project:end -->
