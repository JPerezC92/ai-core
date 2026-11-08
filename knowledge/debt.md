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

**ID to use for the next new debt:** `DEBT-043`. This is an allocation counter, not an open debt.
<!-- project:end -->
