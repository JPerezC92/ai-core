# Core Sync source lifecycle

Core Sync keeps an enrolled destination's managed distribution aligned with the current
source. A fully Core-owned source that disappears or is withdrawn is retired; a region-managed
or merge-managed one is preserved and blocks reconciliation; added and changed sources need no manual bindings
edit. Ownership comes from the registry's declaration for the path, never from a missing value.

**Status:** achieved

## Requirements

- [x] R1 — A fully Core-owned source that no longer exists retires its managed destination file and its binding.
- [x] R2 — A fully Core-owned source that changed replaces its destination, because the source is authoritative for the whole file.
- [x] R3 — A newly cleared source is enrolled and distributed by the ordinary synchronization run, without a clean initialization.
- [x] R4 — A region-managed source that no longer exists keeps its destination file and its destination-owned region, and is reported as blocked.
- [x] R5 — A blocked source prevents a synchronization or verification from reporting the destination as fully reconciled, while unrelated safe updates still apply.
- [x] R6 — A region-managed source that still exists refreshes only its core region and leaves the destination-owned region unchanged.
- [x] R7 — A source that still exists but is no longer cleared is refused rather than treated as deleted.
- [x] R8 — A file no binding manages is never written or removed by synchronization.
- [x] R9 — A source withdrawn from distribution is retired only when the registry still declares its ownership; one whose ownership cannot be established is preserved and reported.
- [x] R10 — A source whose ownership is not exclusively Core-owned is preserved when it disappears or is withdrawn.
