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
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.

## Register
<!-- core:end -->

<!-- project:begin -->
**Open debts: 1.** The DEBT-008/009/010 deletion made in clearing commit `5eed3317…` is recorded as **provisional**, not a settled retirement; the standing-condition record is preserved in Git history at baseline `db58a74daab8bcddf5731f653dff9c6eed6c1fd4` (former `user-stories/plan-lifecycle-governance.md`), not an active path.

### DEBT-019
- **ID** — `DEBT-019`
- **Date:** 2026-10-28
- **Description:** Remaining active MCP risk: `chrome-devtools-mcp@1.12.0` retains browser-content access. The active `memories` MCP entry was removed during the Basic Memory transition; its CLI installation and database were retained unchanged. The previously disclosed `@memories.sh/cli@0.7.9` transitive high-severity `sharp ~0.34.5` advisories (not reachable through its bundle) and MCP SDK/YAML semver drift risks are historical exposure of that removed integration, not vulnerability-remediated dependencies in the retained CLI. The unpinned-latest and Chrome telemetry/CrUX/update-check issues are resolved.
- **Direct evidence:** Warden 🔒 (Dependency Warden) final gate 2026-10-28 `[ADVISORY]`; `opencode.jsonc` exact pins and privacy flags; `opencode mcp list` all connected; pinned process command lines; memories `get_rules` and Chrome `list_pages` responses; PR #108 and `output/audits/pr-108-20261028.md`.
- **Direct evidence (transition):** `odd/tasks/basic-memory-migration.md` Log L6–L8 records the bounded exposed-source inventory, verified Basic Memory write/search/read, and subsequent removal of only the active `memories` MCP entry while preserving the original database and CLI.
- **Direct evidence (2026-10-29 mitigation):** `opencode.jsonc` denies six high-risk Chrome MCP capabilities globally: `evaluate_script`, `upload_file`, `handle_dialog`, `take_heapsnapshot`, `screencast_start`, and `screencast_stop`. The loaded catalog exposes 26 of 32 Chrome tools. This narrows the exposure but does not resolve DEBT-019; browser screenshots, snapshots, console/network reads and the remaining interaction tools still expose browser content.
- **Direct evidence (2026-10-29 Warden audit):** Warden 🔒 (Dependency Warden) returned `[ADVISORY]` on the remaining 26-tool surface: `navigate_page` can carry `initScript` code, `emulate` can inject arbitrary request headers, screenshots/snapshots and console/network reads expose browser content, several tools accept file paths outside the `edit` boundary, and no separate cookie/credential handling rule exists. All 26 tools are available to every agent. The audit states that only server removal literally satisfies the prior resolution criteria; it does not retire DEBT-019.
- **Resolution criteria:** Chrome browser-content access is removed or separately narrowed by configuration or server removal, with a fresh Warden 🔒 (Dependency Warden) audit verifying the remaining Chrome risk. Alternatively, the user may explicitly accept the residual browser-content exposure as a standing, nonblocking risk; that acceptance is recorded here and does not by itself retire this entry. Retire only when the server is removed or narrowed, or when the user explicitly closes the accepted risk in a clearing PR.
- **Explicit deferral decision:** User, 2026-10-28, accepted the disclosed residual advisories and authorized continuation (`ok continue`) after the pin and privacy-control proposal. User, 2026-10-29, accepted the residual 26/32 Chrome surface as a standing risk after the Warden audit, verbatim: "Accept residual risk".

**ID to use for the next new debt:** `DEBT-021`. This is an allocation counter, not an open debt.
<!-- project:end -->
