# Standalone skill utilities

AICore distributes runtime utilities as part of their skills so operators can invoke them independently. Their original modular TypeScript source is authoritative and runs through native Node.js support with any documented runtime dependencies installed by the operator.

**Status:** achieved

## Requirements

- [x] R1 — Migrated skill runtime utilities use TypeScript as their authoritative implementation source.
- [x] R2 — Tests for migrated skill runtime utilities run under Vitest.
- [x] R3 — Each migrated utility distributes its TypeScript source modules within its own skill, imports no runtime modules from other skills or `cli/aicore/`, and runs natively from an isolated copy without a build or bundle; justified runtime dependencies and the Node.js requirement are documented.
- [x] R4 — Migrated utilities preserve their existing observable behavior, command-line interfaces, diagnostics and exit codes where applicable.
- [x] R5 — A Python implementation is removed only after its replacement has passed the required behavior verification.
