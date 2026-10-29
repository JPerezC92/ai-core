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
**Open debts: 2.** The DEBT-008/009/010 deletion made in clearing commit `5eed3317…` is recorded as **provisional**, not a settled retirement; the standing-condition record is preserved in Git history at baseline `db58a74daab8bcddf5731f653dff9c6eed6c1fd4` (former `user-stories/plan-lifecycle-governance.md`), not an active path.

### DEBT-019
- **ID** — `DEBT-019`
- **Date:** 2026-10-28
- **Description:** Remaining active MCP risk: `chrome-devtools-mcp@1.12.0` retains browser-content access. The active `memories` MCP entry was removed during the Basic Memory transition; its CLI installation and database were retained unchanged. The previously disclosed `@memories.sh/cli@0.7.9` transitive high-severity `sharp ~0.34.5` advisories (not reachable through its bundle) and MCP SDK/YAML semver drift risks are historical exposure of that removed integration, not vulnerability-remediated dependencies in the retained CLI. The unpinned-latest and Chrome telemetry/CrUX/update-check issues are resolved.
- **Direct evidence:** Warden 🔒 (Dependency Warden) final gate 2026-10-28 `[ADVISORY]`; `opencode.jsonc` exact pins and privacy flags; `opencode mcp list` all connected; pinned process command lines; memories `get_rules` and Chrome `list_pages` responses; PR #108 and `output/audits/pr-108-20261028.md`.
- **Direct evidence (transition):** `odd/tasks/basic-memory-migration.md` Log L6–L8 records the bounded exposed-source inventory, verified Basic Memory write/search/read, and subsequent removal of only the active `memories` MCP entry while preserving the original database and CLI.
- **Resolution criteria:** Chrome browser-content access is removed or separately narrowed by configuration or server removal, with a fresh Warden 🔒 (Dependency Warden) audit verifying the remaining Chrome risk is resolved. Retire this entry in its clearing PR when those conditions are met.
- **Explicit deferral decision:** User, 2026-10-28, accepted the disclosed residual advisories and authorized continuation (`ok continue`) after the pin and privacy-control proposal.

### DEBT-020
- **ID** — `DEBT-020`
- **Date:** 2026-10-28
- **Description:** Outcome/scope drift in merged-branch cleanup: unnecessary validator implementation and late clarification of conversational confirmation versus OpenCode permission prompts. Deferred work is process research and remediation, including reanalysis of the implementation and plan against the user's actual outcome; recording this debt neither resolves the problem nor permits release of the stopped implementation.
- **Direct evidence:** `odd/tasks/verified-merged-branch-cleanup.md` objective and S1 seek authorized cleanup without duplicate prompts; S4 and S9 retain raw Git permission checks and restrict the helper to read-only verification; L13 records the late read-only re-scope. Current S4/S9 explicitly establish that a standalone `SAFE_TO_CLEAN` validator does not remove raw OpenCode tool asks. L22–L23 record passing implementation tests, not verification that the user's no-duplicate-prompt outcome was delivered. User correction, verbatim: "fuck why it happends? add that as a debt and adda ntoe to verifyu how gentle ai ODD controls this type of errors, then reanalyze the implementation and plan".
- **Research note:** Verify the original Gentleman-Programming/gentle-ai ODD controls using pinned revision `a6e371b502a24a0a0f57e8d75730150416c0d3f3`, specifically `docs/usage.md` and `docs/intended-usage.md`. Reuse saved `docs/research/agent-workflows/odd-gentleman-programming/06-feature-document-blueprint.md` and `docs/research/agent-workflows/odd-gentleman-programming/07-upstream-local-alignment.md` (especially source identities and the source-to-local comparison). The accepted read-only report from Augur 🔮 (Research Analyst) characterizes these as preventive instructions, not a runtime guarantee against scope/outcome drift; do not claim upstream automatically prevents this failure.
- **Resolution criteria:** Inspect the pinned original authorize/explore/resolve-uncertainty flow, spec-update obligations and outcome-verification controls; compare documented prevention with actual guarantees and evidence limits. Reconcile the existing feature objective, acceptance criteria and actual diff with minimum necessary scope. Obtain a user-approved disposition of validator and permission changes; perform independent outcome/semantic review that distinguishes conversational confirmation from OpenCode permission prompts. No broad permission grants or memory-only policy may serve as remediation. Retire only with evidence that these criteria are met, not merely because this entry exists.
- **Explicit deferral decision:** User, 2026-10-28, explicitly requested the debt and research/reanalysis note in the quoted correction above. This authorizes recording deferred process-research/remediation only; all implementation and release remain paused pending reassessment and applicable approval/gates. This debt does not waive that stop or convert the stopped implementation into releasable work.

**ID to use for the next new debt:** `DEBT-021`. This is an allocation counter, not an open debt.
<!-- project:end -->
