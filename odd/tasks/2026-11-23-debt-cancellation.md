# Debt register cancellation of twelve open entries

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-23
> **Objective:** Cancel twelve user-selected open accepted-debt entries by explicit user decision, preserving each decision, its unmet resolution criteria and their supporting evidence before the entries leave the register.
> **Branch:** `docs/debt/cancel-open-entries`
> **Delivery:** One local work-unit commit on that branch; forecast roughly 210 authored additions plus deletions, dominated by this record and the twelve-entry deletion block, below the ~400-line strategy trigger, so no slicing is needed. Rollback boundary: this record, `odd/features/accepted-debt-register.md` and `.aicore/core/knowledge/debt.md` revert together with no effect on any other path.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features/accepted-debt-register.md`

## Specs

- S1 — The twelve selected entries are absent from the register while the entries the user did not select remain. Exact requirement: "remove all the next debts, i authorize it / DEBT-043 / DEBT-044 / DEBT-048 / DEBT-049 / DEBT-055 / DEBT-056 / DEBT-057 / DEBT-058 / DEBT-060 / DEBT-062 / DEBT-063 / DEBT-064". Acceptance: read `.aicore/core/knowledge/debt.md`; observe no heading for DEBT-043, DEBT-044, DEBT-048, DEBT-049, DEBT-055, DEBT-056, DEBT-057, DEBT-058, DEBT-060, DEBT-062, DEBT-063 or DEBT-064, and observe DEBT-052 and DEBT-054 still present.
- S2 — Each removal is recorded as a user-authorized cancellation, not as a technical resolution, with the user decision, the entry's unmet resolution criteria and a pointer to its preserved supporting evidence. Exact requirement: "An explicit user decision may cancel an open debt without satisfying its resolution criteria … Before removing the entry, preserve the user decision, unmet criteria, and supporting evidence in the governing feature record". Acceptance: read this record's `## Log`; observe one entry per cancelled debt naming the decision, its unmet criteria and the commit holding its full text, and read no claim that any criterion was satisfied.
- S3 — The register's ID allocation counter still prevents reuse of a retired identifier. Exact requirement: "Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries". Acceptance: read the register's trailing line; observe the next-ID value is unchanged at `DEBT-065`.
- S4 — No shared debt-register obligation is weakened by the cancellation. Exact requirement: "Cancellation is not resolution or clearance." Acceptance: read the register's `### Rules` section; observe the user-directed cancellation rule, the resolution-evidence rule and the ID-allocation rule unchanged.

## Tasks

- T1 | S1 | inline (bounded mechanical edit of one register file) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T2 | S2, S4 | inline (record authorship owned by the coordinator) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T3 | S3 | inline (single-line counter verification) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T4 | S1, S2, S3, S4 | delegated (independent semantic acceptance of a records change; Sentinel 🛡️ is the authority for records and rules) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T5 | S1, S2, S3, S4 | delegated (Git execution ownership) — Herald 📯 (Release Manager) | open | commit: pending

## Log

- L1 — Original request, verbatim: "remove all the next debts, i authorize it
  DEBT-043
  DEBT-044
  DEBT-048
  DEBT-049
  DEBT-055
  DEBT-056
  DEBT-057
  DEBT-058
  DEBT-060
  DEBT-062
  DEBT-063
  DEBT-064"
- L2 — Authorization boundary. The request is an explicit user decision to cancel twelve open debts; under the register's `### Rules` it is a cancellation, not a resolution or clearance, and every entry's resolution criteria stay unmet. DEBT-052 and DEBT-054 were not selected and remain open unchanged. No remediation of any cancelled subject was authorized, requested or performed, and no validator, runtime, permission or architecture change is part of this change.
- L3 — Preservation method. Each cancelled entry's complete text — description, direct evidence, resolution criteria and explicit deferral decision — remains in Git at `8cd5b70`, the commit this change starts from, and the per-debt entries below cite that commit instead of retyping it. The unmet criteria summarised below are the entry's own `Resolution criteria`; where an entry recorded partial delivery, the summary names only what stayed open.
- L4 — DEBT-043 (Coordinator made unverified capability claims that forced rework) — cancelled, unmet: capability claims recorded with the exact inspected source and revision before they drive a design, and a delivery work unit whose dependency-free claims rest on an executed probe or an explicit hypothesis, with the feature record citing it. Full entry and evidence: `8cd5b70` `.aicore/core/knowledge/debt.md`.
- L5 — DEBT-044 (Coordinator took user-owned design decisions without asking) — cancelled, unmet: each of the seven listed design decisions carrying a recorded user answer or an explicit implemented-hypothesis label with the evidence a live probe needs. Full entry and evidence: `8cd5b70`.
- L6 — DEBT-048 (ODD lifecycle never orders record closure against PR merge) — cancelled, unmet: the independent no-contradiction confirmation and the recorded whole-feature acceptance evidence for the ordered closure/delivery/retirement contract. Full entry and its four dated state records: `8cd5b70`.
- L7 — DEBT-049 (Architecture contract may have lost normative rules during agnostic-base extraction) — cancelled, unmet: the bounded architecture-integrity comparison with retained/translated/retired accounting of every changed rule and the resulting backend-architecture ruling. Full entry and evidence: `8cd5b70`.
- L8 — DEBT-055 (cli/aicore and related suites lack required T2 use-case units and host unapproved unit targets) — cancelled, unmet: only user ratification of the criterion wording for the five real-adapter cases and the `system-one` loader placement; the mechanical subjects were recorded resolved in substance. Full entry and five dated state records: `8cd5b70`.
- L9 — DEBT-056 (Tests labeled integration that exercise an assembled entry point or a non-adapter subject) — cancelled, unmet: only user ratification of the criterion wording for the fixture helper's accepted "no test level" classification; the parity corpus, entry-point, clearance and reconciliation subjects were recorded resolved. Full entry and six dated state records: `8cd5b70`.
- L10 — DEBT-057 (Dependency-review stopping and evidence reuse need proportionality assessment) — cancelled, unmet: the canonical-project-mapping classification half of the finite stopping condition, withheld because it changes an established security acceptance policy. Full entry and state record: `8cd5b70`.
- L11 — DEBT-058 (No mechanical check that a declared mandatory command has an authorized executor) — cancelled, unmet: independent review of the manual static comparison, a standing Warden recurrence owner, and resolution of the recorded Ledger `shell *` reachability gap, which needs a permission change. Full entry and its recorded divergences: `8cd5b70`.
- L12 — DEBT-060 (Agent execution reliability in requirements-based test remediation) — cancelled, unmet: demonstrated and independently verified prevention — the pre-publication body-format check, the factual verification of protected sections and the outstanding-decision detection — plus the recorded whole-feature acceptance. Full entry and its nine recurrence records: `8cd5b70`.
- L13 — DEBT-062 (PR review responsibilities are encoded as ODD task rows and as a closure prerequisite) — cancelled, unmet: criterion (c), the demonstrated lifecycle behaviour, and the independent no-contradiction confirmation. Full entry and state record: `8cd5b70`.
- L14 — DEBT-063 (Fragmented independent architecture review interrupts implementation) — cancelled, unmet: the separately authorized clarification of review timing and scope, demonstrated in one incomplete slice and one integrated candidate with independent confirmation. Full entry and evidence: `8cd5b70`.
- L15 — DEBT-064 (Excessive procedural overhead for user-authorized technical debt cancellation) — cancelled, unmet: the proportionality assessment of debt-cancellation procedure itself, which was never performed. Full entry and evidence: `8cd5b70`.
- L16 — Verification. `8cd5b70` entry headings were the pre-removal baseline; after the edit the register carries no cancelled heading, DEBT-052 and DEBT-054 remain, `### Rules` is byte-unchanged and the counter still reads `DEBT-065`. Recorded as the coordinator's mechanical check; independent semantic acceptance is T4.
- L17 — Durable feature file. `odd/features/accepted-debt-register.md` is created by this change as the feature's first durable file; it carries the register's enduring obligations and no history. Requirements R1–R5 were checked against the post-edit register by T1–T3: R1 and R5 confirmed on the two remaining open entries, each of which still carries the five required fields and its originating context; R3 and R4 confirmed by this cancellation; R2 was not exercised by this change and stays unticked, which is why the file's derived status is `partial`.
- L18 — Feature mirror: pending recovery. No backend copy of this record was written, so no synchronization is claimed. The project's mirror adoption is itself recorded as unverified in `AGENTS.md` project extensions, and no exact-key upsert or compare-and-swap is available, so a full-document write and independent readback could not be established here. The repository record remains authoritative; recovery is a bounded follow-up write-and-readback when a verified backend round trip is available.
