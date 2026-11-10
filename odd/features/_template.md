# <feature name>

<what this feature is, two or three lines>

**Status:** <achieved | partial | not started>

## Requirements

- [ ] R1 — <what must be true for this feature to count as complete>
- [ ] R2 `<upstream | upstream · local detail | upstream · narrowed | local | local · conflicts>` — <what must be true, and how this repository departs from the standard it adopts>

## Guidance

- Copy this template to `odd/features/<feature-name>.md`; name it for the feature and never date it.
- The mark is used only when the feature adopts a standard that already exists, and it records where this repository changed something from that standard: `upstream` unchanged, `upstream · local detail` sharpened here, `upstream · narrowed` relaxed here, `local` added here, `local · conflicts` contradicting the standard. A feature explicit from this repository carries no mark.
- Tick a requirement only when a change has delivered it, and only the delivering change may set that tick.
- The status is derived from the ticks: every requirement ticked is `achieved`, some ticked is `partial`, none ticked is `not started`.
- Every change reads this file and records, for each requirement, whether it added one, reworded one, retired one or left it alone.
- The file lists no change records and holds no work-in-progress state; a requirement may name the single change that delivered it, as its evidence.
- If a change finds a ticked requirement no longer satisfied, it flags that requirement and records the failure and its cause in its own record.
- Delete this section when the file is filled.
