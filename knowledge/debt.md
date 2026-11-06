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
- Clear and retire a debt in the same PR: the PR that clears a debt deletes its entry from this register, and its body and commit carry the Resolution evidence (criteria met, validation and audit results). Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one PR: its clearing PR.
- **User-directed cancellation.** An explicit user decision may cancel an open debt without satisfying its resolution criteria. Cancellation is not resolution or clearance. Before removing the entry, preserve the user decision, unmet criteria, and supporting evidence in the governing feature record; include the cancellation and its evidence in the authorized delivery. This route does not alter the clearing-PR rule for resolved debts.
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.

## Register
<!-- core:end -->

<!-- project:begin -->
## DEBT-037 — Incident-workflow domain record naming

- **Date:** 2026-11-05
- **Description:** Deferred naming/layout migration of `.opencode/skills/incident-workflow/scripts/incident_workflow_pkg/domain/value_objects.py`. Its intentional data records occupy a generic value-object bucket rather than concept-specific record modules under the authored C8/C10/P4 definitions. This is naming/classification drift, not evidence of an anemic entity or broken invariant enforcement.
- **Direct evidence:** Current source read on 2026-11-05: line 1 calls these value-object domain records; line 5 imports `TypedDict`; `AnalysisHeader` (lines 8–17) carries frontmatter fields, `TicketIdentification` (20–25) parsed identification fields, `CloseOutSnapshot` (28–41) filesystem snapshot fields including mutable lists/dictionaries, and `ModeFindings` (44–48) violation/warning lists. These are TypedDict records, not value-equality immutable value objects. Compare `architecture/implementation/architecture.md` C8's Value object/Data-only record rows and C10's record role, `architecture/implementation/shapes/scripts.md` P4's prohibition on generic multi-concept value-object buckets, and `architecture/implementation/stacks/python.md` Concept-role filenames (`<concept>_record.py`). Coverage is this source file only; no repository-wide inventory or runtime defect is asserted.
- **Resolution criteria:** In separately authorized implementation work, classify these record roles, replace the generic bucket with concept-specific modules using the applicable final guide, update all affected consumers, and obtain the applicable architecture and test verification. Retire this entry in that clearing PR with direct resolution evidence; no implementation is changed by the documentation feature.
- **Explicit deferral decision:** User selection recorded in `odd/tasks/2026-11-05-domain-architecture-definitions.md` L5: `Docs only, naming drift recorded as debt (Recommended)`; L10/L11 restrict work to architecture definitions and related documentation. This accepts the verified naming drift for this docs-only delivery, not a permanent waiver, global debt admission, or future on-touch exemption.

## DEBT-038 — Skill frontmatter not synchronized to destinations

- **Date:** 2026-11-05
- **Description:** core-sync region-mode delivery synchronizes only the bytes strictly between a destination's `core` markers. A skill's YAML frontmatter sits above `<!-- core:begin -->`, so it is destination-owned and is never written or refreshed by `apply` or `init`. Two consequences are deferred: (a) a destination skill's catalog `description` and `version` stay frozen at whatever they were when the file was first created, so the model routes on a stale description; (b) a destination `SKILL.md` whose outside-region content carries no frontmatter receives none, which would leave that skill absent from the harness skill catalog.
- **Direct evidence:** Source `.opencode/skills/odd-workflow/SKILL.md:1-9` carries frontmatter (`name: odd-workflow`, `metadata.version: 2.2.0`) with `<!-- core:begin -->` at line 10. Destination `G:\projects-personal-tismart\tismart-support\.opencode\skills\odd-workflow\SKILL.md:1-10` carries frontmatter with `metadata.version: 1.0.0` and a different `description`, also with `<!-- core:begin -->` at line 10 — direct evidence that frontmatter is not synchronized. The reported symptom (skills absent from the session skill catalog) did NOT reproduce in that destination on 2026-11-05: every core-shipped `SKILL.md` there — `git-branch-name`, `git-commit`, `git-pr`, `incident-workflow`, `odd-workflow`, `op-agent-creator`, `op-model`, `op-skill-creator`, `verified-pr-cleanup` — begins with `---` YAML frontmatter. That destination's enrollment report `.aicore/reconciliation/init.yaml` records 10 entries, all `action: refreshed`, zero `created`. Consequence (b) is therefore unverified: `hipótesis:` a newly enrolled markerless `SKILL.md` with no frontmatter above its markers ends up with none; confirming it requires enrolling a skill into a destination whose target file lacks frontmatter and observing the catalog. No repository-wide inventory or runtime defect is asserted.
- **Resolution criteria:** In separately authorized work, choose and implement one distribution treatment for skill frontmatter — either a cleared mechanism that keeps catalog identity current across destinations, or a core-sync check that reports destination `SKILL.md` files missing frontmatter or carrying a stale version against the pinned revision. Then verify in an adopting destination that every core-shipped skill appears in the harness skill catalog with a current description. Retire this entry in that clearing PR with direct resolution evidence.
- **Explicit deferral decision:** User instruction 2026-11-05, verbatim: "there is an issue on the sync can u add it as a debt". Deferral recorded at the user's direction from a destination-project observation; it is not an agent-accepted waiver.

**ID to use for the next new debt:** `DEBT-039`. This is an allocation counter, not an open debt.
<!-- project:end -->
