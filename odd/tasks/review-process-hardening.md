# Review process hardening

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-25

## Specs

- S1 — DEBT-018: inspect the canonical PR drafting/reviewer obligations, then define one reusable, readable PR test-evidence format. It must preserve the exact test-plan item, literal input/action, observed result, executor, immutable head/base/scope, and evidence for every checked item. Align `git-pr`, Herald, and Inquisitor consumers without weakening evidence or checkbox rules. Do not vary the presentation arbitrarily between PRs.
- S2 — DEBT-018 remains open after this feature even when the template and consumers are aligned, because its recorded resolution criteria require demonstration on a later PR. Do not delete the debt entry or claim it retired in this PR. A future PR demonstrates the format and preserves traceability; only then may DEBT-018 be retired in its clearing PR.
- S3 — DEBT-017: add shared all-agent guidance distinguishing proven consumers, explicit governing compatibility contracts, and user mandates from hypothetical external concerns. Hypothetical concerns stay informational; they do not become blockers, scope requirements, retention obligations, or architecture vetoes. Actual compatibility obligations are investigated and reported with evidence and authority; reviewer checks the evidence-to-constraint link.
- S4 — Exercise both DEBT-017 cases in the feature evidence: a no-evidenced-adopter case where the hypothetical concern is informational, and an evidenced-required-consumer case where the verified obligation is surfaced with its authority. Record expected and observed decisions; obtain independent review of the guidance and both cases. Retire DEBT-017 in this PR only if all recorded criteria are met.
- S5 — Refresh `docs/architecture/odd-adoption-status.md` after the review-process changes and PR #89/#90. Include the current six open debts after DEBT-017 retirement (DEBT-018 remains open pending later demonstration), distinguish merged features from proposed/future implementation conformance, and do not claim universal ODD completion.
- S6 — Scope is limited to `knowledge/agents.md`, `AGENTS.md` only if a root-runtime obligation is genuinely required, `.opencode/skills/git-pr/SKILL.md`, the applicable PR-review consumer specs (`herald.md`, `inquisitor.md`), `knowledge/debt.md`, `docs/architecture/odd-adoption-status.md`, a reusable evidence reference/template if needed, and this feature record. No application implementation, dependency, permission, destination, legacy plan/story, or historical record change is authorized.
- S7 — Verification includes zero-open independent Sentinel review, ODD validation, and the whole suite only if a test-file edit applies. Any runtime/skill version advances by its applicable SemVer. No PASS or completion claim precedes the checks. Publication remains separately authorized.

## Tasks

- T1 | S1 | Cipher 🔓 (Lead Orchestrator): inventory current PR drafting/review evidence obligations and choose the single format; no writes beyond this record | open | commit: pending
- T2 | S1 | Scribe ✍️ (Docs & Problems Manager): create the reusable evidence reference/template and align `git-pr`; Vault 🔐 (Catalog Steward) reviews the skill change | open | commit: pending
- T3 | S1 | Marshal 🎖️ (HR Director): align Herald 📯 (Release Manager) and Inquisitor 🔎 (PR Reviewer) bodies with the template and preserve immutable-head/evidence rules | open | commit: pending
- T4 | S3, S4 | Marshal 🎖️ (HR Director): add the shared compatibility-evidence rule; exercise the two cases and record them | open | commit: pending
- T5 | S4 | Sentinel 🛡️ (Quality Guardian): independently review the rule and both cases; zero open findings required | open | commit: pending
- T6 | S2, S5 | Cipher 🔓 (Lead Orchestrator): refresh the adoption summary and record DEBT-018 as intentionally still open pending later demonstration | open | commit: pending
- T7 | S7 | Cipher 🔓 (Lead Orchestrator): validate, record evidence, retire DEBT-017 if criteria are met, and close only after T5 is zero-open | open | commit: pending

## Log

- L1 — "what we can make in a row?"
- L2 — "ok continue"
- L3 — Batch approved: refresh ODD status, harden DEBT-018 PR evidence format, resolve DEBT-017 compatibility reasoning, then run a read-only implementation-conformance audit. Batch B is read-only and separate from this feature.
- L4 — Debt boundary: DEBT-018 cannot be retired here because its resolution criteria require demonstration on a later PR. DEBT-017 can be retired only after both cases and independent review. No debt is silently closed.
- L5 — Classified non-small: shared guidance, PR template, reviewer consumers, and debt retirement evidence. This record exists before the first implementation write. No application code or destination changes are included.
- L6 — T1 inventory/decision: the standard uses two tables in one PR body. `## Findings / blockers` has ID, severity, status, evidence, owner/resolution with statuses OPEN/IN PROGRESS/FIXED/DEFERRED/REJECTED. `## Test evidence` has exact test-plan item, literal action/input, observed result, executor, preceded by immutable PR/head/base/scope. A no-findings PR states `No findings.`; fixed findings remain visible as FIXED; open/deferred findings prevent PASS. The reusable reference is `.opencode/skills/git-pr/references/_pr-evidence-format.md`; `git-pr` drafts the initial body, and Inquisitor 🔎 (PR Reviewer) is the sole post-review evidence writer.
- L7 — T3/T4 implementation: Herald 📯 (Release Manager) 1.7.1→1.7.2 and Inquisitor 🔎 (PR Reviewer) 1.7.2→1.7.3 mandate the canonical PR evidence reference; gate, immutable-head, atomic-join, stash and release authority unchanged. `knowledge/agents.md` adds the compatibility-evidence rule and the PR-body presentation pointer. The skill/reference passed Vault review after two formatting corrections.
- L8 — DEBT-017 case A (no evidenced adopter): a hypothetical downstream consumer of the retired Herald 📯 (Release Manager) default template has no named destination, binding, or contract in this feature. Expected = observed: informational note only; no blocker, scope requirement, retention obligation, or architecture veto.
- L9 — DEBT-017 case B (evidenced required consumer): the canonical reference, `git-pr` SKILL, Herald 📯 (Release Manager), Inquisitor 🔎 (PR Reviewer), and `knowledge/agents.md` are named files bound by this feature. Expected = observed: each obligation surfaced from cited authority and aligned; independent review remains T5.
- L10 — Final Vault skill-quality review passed after two mechanical formatting fixes; final Sentinel audit returned zero open findings. The suite passed: `738 passed in 6.70s`. Versions: git-pr 1.8.0, Herald 1.7.2, Inquisitor 1.7.3; fixture 16/16.
- L11 — DEBT-017 criteria (1)–(5) are met and its entry was removed from `knowledge/debt.md` in this clearing feature; open debts are six and next ID remains DEBT-019. DEBT-018 remains open with criteria 1–3 implemented and later-PR demonstration pending; the status dashboard records the local-only, unpublished state.
