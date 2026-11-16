# Durable feature file

One living file per feature in `odd/features/`, stating what the feature is and the requirements it must satisfy, so the current definition is readable without reconstructing it from the change records.

**Status:** achieved

## Requirements

- [x] R1 — a durable file exists for this feature at `odd/features/durable-feature-file.md`.
- [x] R2 — the file's shape is fixed: a title for the feature, one paragraph saying what it is, one status line, and the requirement list.
- [x] R3 — the status is derived from the ticks: every requirement ticked is `achieved`, some ticked is `partial`, none ticked is `not started`.
- [x] R4 — a tick asserts that the requirement currently holds, a change re-verifies only the requirements it affects, and only the change that delivers or re-verifies a requirement may set its tick.
- [x] R5 — every change reads the affected durable file and records what it changed in it: which requirements it added, reworded or retired, and the verification outcome for each affected requirement; requirements the change did not affect are left alone.
- [x] R6 — the file lists no change records and holds no work-in-progress state; a requirement states only what must remain true and appends no pointer to implementation or history, while a specific path, component or artifact that is itself part of the required behavior is named as the behavior it guarantees.
- [x] R7 — if a later change establishes that a ticked requirement is no longer satisfied, that change removes the tick and records the failure and its cause in its own record.
