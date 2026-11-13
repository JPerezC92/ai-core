# Core synchronization

Synchronization keeps an adopting project's AICore-owned resources current from a pinned source revision: it initializes a destination that is not yet enrolled, updates one that is, preserves what the destination itself owns, and reports what still requires destination-owner reconciliation.

**Status:** partial

## Requirements

- [x] R1 — A single command synchronizes a destination: it initializes one that is not yet enrolled, updates one that is enrolled, and reports the resulting currency state.
- [x] R2 — The destination and distribution target chosen on a first run are persisted locally and reused by later runs that supply no arguments.
- [x] R3 — An explicitly supplied destination or distribution target overrides the persisted selection, and the persisted selection records the explicit choice.
- [x] R4 — Only a distribution target whose behavior is implemented is accepted; an unimplemented or unknown target is refused with a clear message rather than silently substituted.
- [x] R5 — A distribution target is never inferred for an existing destination whose selection is unknown; the run stops and asks for it explicitly.
- [x] R6 — Source identity is supplied by configuration and never obtained by synchronization executing Git; an absent or malformed identity stops the run rather than falling back implicitly.
- [x] R7 — The destination's synchronization state location and the source checkout location are resolved without per-run arguments.
- [x] R8 — Distribution clearance is enforced: only resources cleared for distribution are delivered to a destination.
- [x] R9 — Synchronization preserves destination-owned content and ownership regions, and reports every conflict that requires destination-owner reconciliation.
- [x] R10 — Synchronization never modifies its source resources and keeps operator-local configuration separate from distributed content and destination-owned synchronization records.
- [ ] R11 — Unsafe filesystem targets are rejected before any write, including symlinked, hard-linked, inode-sharing and overlapping source/destination paths.
- [x] R12 — A refusal is distinguished from an applied change: a refused operation writes nothing, an applied operation reports what it changed and what still requires destination-owner reconciliation, and any outcome that leaves a destination not current exits non-zero rather than reporting success.
- [x] R13 — The shared skills live under `.agents/skills/`, which every supported distribution target discovers natively, and no skill is duplicated into a target-specific directory.
- [x] R14 — The shared documentation is consolidated under `.aicore/core/` in the source and in the destination, while destination-owned synchronization state stays separate from it.
- [ ] R15 — OpenCode and Cursor are both supported distribution targets: each receives the same content, editor-specific agents are delivered to each editor's own agent directory, and what an editor cannot be given is stated rather than implied.
- [ ] R16 — The synchronization engine is TypeScript, and no Python engine or interpreter dependency remains in the synchronization path.
- [ ] R17 — The utilities distributed to destinations are TypeScript, execute standalone without a destination-side installation, and state their runtime prerequisite.
- [ ] R18 — A destination's reconciliation is proposed and inspectable before any destination file changes, and a file whose ownership cannot be established is preserved and reported rather than deleted.
- [ ] R19 — Synchronization distributes ordinary files and directories: it never creates, preserves, follows or manages a symbolic link as a synchronization artifact, and it refuses a managed write path that contains one before the destination is modified.
