# Durable feature file

One living file per feature in `odd/features/`, stating what the feature is and the requirements it must satisfy, so the current definition is readable without reconstructing it from the change records.

**Status:** achieved

## Requirements

- [x] R1 — a durable file exists for this feature at `odd/features/durable-feature-file.md` — delivered: this change
- [x] R2 — the file's shape is fixed: a title for the feature, one paragraph saying what it is, one status line, and the requirement list. — evidence: `odd/features/_template.md` carries it, and both feature files follow it
- [x] R3 — the status is derived from the ticks: every requirement ticked is `achieved`, some ticked is `partial`, none ticked is `not started`. — evidence: `validate_feature_file.py odd/features` reports the derived status
- [x] R4 — a tick asserts the requirement holds, and only a change that delivered it may set that tick. — evidence: `knowledge/agent-workflow.md` → Tick; `SKILL.md:34`
- [x] R5 — every new change reads the file and records, for each requirement, whether it added one, reworded one, retired one or left it alone. — evidence: record `## Log` L26, L32 and L33
- [x] R6 — the file lists no change records and holds no work-in-progress state; a requirement may name the single change that delivered it, as its evidence. — evidence: the clause sits at the five sites listed in record `## Log` L31
- [x] R7 — if a later change finds that a ticked requirement is no longer satisfied, that change flags the requirement and records the failure and its cause in its own record. — evidence: `knowledge/agent-workflow.md` → Regression; `SKILL.md:36`
