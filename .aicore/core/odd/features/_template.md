# <feature name>

<what this feature is, two or three lines>

**Status:** <achieved | partial | not started>

## Requirements

- [ ] R1 — <what must be true for this feature to count as complete>
- [ ] R2 `<upstream | upstream · local detail | upstream · narrowed | local | local · conflicts>` — <what must be true, and how this repository departs from the standard it adopts>

## Guidance

- Copy this template to `odd/features/<feature-name>.md`; name it for the capability the system provides and never date it. A name that must change whenever the implementation changes describes a change record, not a contract.
- The mark is used only when the feature adopts a standard that already exists, and it records where this repository changed something from that standard: `upstream` unchanged, `upstream · local detail` sharpened here, `upstream · narrowed` relaxed here, `local` added here, `local · conflicts` contradicting the standard. A feature explicit from this repository carries no mark.
- A tick asserts that the requirement currently holds. A change re-verifies only the requirements it affects: the tick stands when verification confirms it, and is removed with the failure or uncertainty and its reason recorded in the change's own record when a regression is established, or when verification could not be completed and the change could have affected the requirement.
- The status is derived from the ticks: every requirement ticked is `achieved`, some ticked is `partial`, none ticked is `not started`.
- Read the affected feature on every change; record affected requirement changes and verification in the task. An unchanged contract and verified status require no feature-file edit.
- Write enduring, verifiable capability requirements, not implementation activities or execution history. An accessible authoritative reference may supplement a self-contained requirement. See skill `### Create or update the feature file` for semantics and examples.
- Before creating a new durable file, read `odd/features/` and decide whether the capability already belongs to an existing file; when it does, update that file instead. A new file is created only for a genuinely distinct, enduring capability with its own observable rules.
- Delete this section when the file is filled.
