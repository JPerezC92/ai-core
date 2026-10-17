<!-- core:begin -->
# User story — pr-review-corrections

> **Created:** 2026-10-16
> **Title:** PR review corrections
> **Status:** active
> **version:** 1.0.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/agents/inquisitor.md`, `.opencode/agents/herald.md`, `.opencode/skills/git-pr/SKILL.md`, `knowledge/agents.md`

## Persona

- A maintainer whose authorized PR work contains an evidence-backed factual wording defect.

## Goal

- **G:** Apply an in-scope reversible factual correction through its authorized writer without redundant permission requests.
  - Done when: the minimal supported correction is persisted, live-verified against the same PR/head, and reported while preserving unrelated content, exclusive writer ownership, and the existing scope, authority, and freshness gates.

## Scenario

- A PR Summary count disagrees with the disclosed list: the evidence-backed count correction proceeds through the authorized prose writer and is reported without another permission request.
- An evidence row or checkbox fact needs correction: it goes to the evidence writer rather than a competing prose writer.
- Another writer still owns the PR body: the correction waits for an explicit exclusive handoff after prior access ceases; workers never race edits.
- A proposed correction changes scope, lacks factual support, or requires destructive action: the existing decision/evidence gate applies instead of treating the change as trivial.
- The PR head or body diverges before persistence: the writer stops rather than overwriting stale content; a saved correction is accepted only after live verification.

## Acceptance criteria

- ✅ **AC1:** A confirmed reversible factual correction within existing approved scope proceeds without another permission request and is reported with its factual basis.
- ✅ **AC2:** Evidence/checkbox corrections and general prose corrections route through their respective authorized writers; only one writer owns the body at a time and handoff occurs only after prior access ceases.
- ✅ **AC3:** A correction is a minimal patch preserving unrelated prose, evidence, and verified ticks; prose remains grounded in the authorized draft source rather than newly invented claims.
- ✅ **AC4:** Freshness is checked before mutation and the persisted change is live-reread against the same PR/head; stale or divergent input stops instead of overwriting.
- ✅ **AC5:** Scope expansion, unsupported facts, destructive actions, or missing authority stop for the existing decision/evidence process rather than being classified as trivial.

## Proof

- AC1 → `knowledge/agents.md` `### PR review findings (adjudication)` body-prose row · `.opencode/agents/herald.md` `#### Authorized factual prose correction` step 6 · walkthrough 2026-10-16: authorized Summary-count repair proceeds without a repeated permission request and reports its factual basis
- AC2 → `.opencode/agents/inquisitor.md` `##### PR-body evidence boundary` · `.opencode/agents/herald.md` `#### Authorized factual prose correction` step 1 observed release · walkthrough 2026-10-16: no second writer; Herald writes nothing while the evidence join holds the body
- AC3 → `.opencode/agents/herald.md` `#### Authorized factual prose correction` step 3 minimal delta applied to the fresh live body preserving evidence/ticks/unrelated prose · `.opencode/skills/git-pr/SKILL.md` `### Post-PR evidence contract` — walkthrough 2026-10-16
- AC4 → `.opencode/agents/herald.md` `#### Authorized factual prose correction` steps 4–5 pre-write freshness and live reread · `.opencode/agents/inquisitor.md` `##### PR-body evidence boundary` — walkthrough 2026-10-16: divergence/failed reread blocks instead of overwriting
- AC5 → `knowledge/agents.md` `### PR review findings (adjudication)` scope/destructive rows · `### User-Authority-Only rule` · `.opencode/agents/herald.md` `#### Authorized factual prose correction` stop list · walkthrough 2026-10-16: an unsupported count stops as an unsupported fact instead of being classified as trivial

## Constraints

- Draft generation never mutates live GitHub state — because its output is a review artifact, not permission to publish or alter a PR.
- The evidence reviewer remains evidence-only; general prose corrections require the authorized prose writer — because correction routing must not silently expand the reviewer's mutation authority.
- Only one active writer owns the PR body, and evidence collection retains its own evidence-derived gate — because a prose correction cannot replace verification or permit competing updates.
- No release, merge, destructive-action, or new execution authority is inferred from a correction — because the existing user authorization and role boundaries remain governing.

<!-- core:end -->

<!-- project:begin -->
## Approval record

- 2026-10-16 — The user approved CREATE and the displayed correction contract after catalogue/ownership and collision review, required a designed flow rather than a convention bullet, and subsequently authorized story persistence first. This approval does not authorize a live PR edit or release.

## Local evidence

- AC1–AC5 were exercised on 2026-10-16 by a synthetic, non-live walkthrough (invented PR/head; nothing fetched or written): an authorized Summary-count repair proceeded without a repeated permission request and reported its factual basis; the prose writer stayed out of the body until the evidence writer's release was observed; the delta was applied to the fresh live body with evidence, ticks and unrelated prose preserved; a divergent or failed reread stopped the write; an unsupported count and an unheld evidence claim stopped for the decision/evidence process. This is clause-application evidence, not a live PR-head execution or destination verification.

## Revision tracking

- 2026-10-16 — Approved active contract persisted. Evidence corrections remain owned by the PR evidence-collection contract; this contract adds the distinct factual prose-correction outcome without turning draft generation into a GitHub writer. The authorized prose writer's workflow and exclusive handoff are now specified, and AC1–AC5 are established by clause application on the synthetic 2026-10-16 PR walkthrough. Delivery history is finalized as PR #68. This source-authored story is not automatically cleared for distribution, and no grant, destination mutation, or release action is implied.

## Change log

- 2026-10-16 — pr-review-corrections-20261016 (PR #68): added the authorized serialized factual prose-correction path on the fresh live body, with observed writer release, preserved evidence and a post-write live reread.
<!-- project:end -->
