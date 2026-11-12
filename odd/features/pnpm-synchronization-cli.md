# pnpm synchronization CLI

A single `pnpm aicore sync` entry point over the existing Python synchronization engine: it remembers the destination and editor chosen on first run, resolves source, bindings and revision without executing Git, and leaves every safety mechanism and advanced command unchanged.

**Status:** partial

## Requirements

- [x] R1 — A pnpm script invokes the synchronization tool from the AICore checkout, with no publishing, installation or global-linking step required.
- [x] R2 — One simple command performs synchronization: it enrolls a destination that is not yet bound, applies the current source to one that is, and reports the resulting currency state.
- [x] R3 — The destination and editor selected on a first run are persisted locally and reused by later runs that supply no arguments.
- [x] R4 — An explicitly supplied destination or editor overrides the persisted selection, and the persisted selection records the explicit choice.
- [x] R5 — Only an editor whose distribution behavior is actually implemented is accepted; a requested but unimplemented editor is refused with a clear message rather than silently applied as a different editor.
- [x] R6 — An editor is never inferred for an existing destination whose selection is unknown; the run stops and asks for it explicitly.
- [x] R7 — The source revision is supplied by configuration rather than obtained by the tool executing Git, and an unavailable revision stops the run with a clear message instead of an unsafe implicit fallback.
- [x] R8 — Operator-local configuration is excluded from version control.
- [x] R9 — The destination's synchronization state location and the source checkout location are resolved automatically, with no per-run arguments required.
- [x] R10 — The existing advanced commands remain available and map to the existing engine's behavior.
- [x] R11 — Every existing synchronization safety guarantee remains in force: clearance gating, write-target preflight, source-tree read-only treatment, ownership markers, reconciliation state and the exit-status contract.
- [x] R12 — Failures are reported with an unmistakable message and a non-zero status, and no failure path silently mutates a destination.
- [ ] R13 — Exactly one authoritative synchronization engine exists, implemented in TypeScript, with no parallel fallback engine retained.
