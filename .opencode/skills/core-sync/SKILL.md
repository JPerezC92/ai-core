---
name: core-sync
description: "Synchronize cleared source files into bound destinations at a pinned revision. Region mode enrolls or updates shared core while preserving destination-owned content; raw mode copies whole files byte-for-byte; merge mode replaces source-owned top-level JSON/JSONC keys while preserving destination-only content — except the `mcp` key, which merges by server name so a destination-only MCP server survives while a same-named server entry is core-wins. Tracks pending region reconciliation and its root blocker. Use when distributing shared skills, agents, or per-file region sources, mirroring whole-file references, merging config keys, checking drift, or reconciling destination project content."
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.2.3
---

## What I do

Update the bound files of a destination from a source of truth, and keep the destination's root runtime file carrying a reconciliation blocker while region reconciliation is pending. Each binding runs in one of three modes: `region` (the default) mirrors the source `core` region between destination markers; `raw` copies the whole source file byte-for-byte with no markers or project region; `merge` merges only the source's top-level object keys into the destination, source keys winning while destination-only keys, comments, and formatting outside replaced or inserted keys stay — except the `mcp` key, whose `servers` members merge by name (a same-named server entry is core-wins, every destination-only server survives). The source is read-only; raw sources are read as bytes without decoding or newline normalization, and merge sources are read as JSONC text (UTF-8, no newline translation). Before mutation, write targets must be regular files: a symlinked bindings or payload/root/report target is rejected before any read or write, and an existing non-regular target is rejected. All write targets — payloads, bindings, reconciliation report, and root blocker — are resolved and preflighted against the source and destination roots. Existing output-file device/inode identities are checked against regular files under the source tree, so hard links cannot mutate source files; distinct output paths that resolve to the same target are rejected. `init` also rejects a newly created raw target that would become the implicit root runtime file. In region mode, everything outside destination core markers — frontmatter, the destination's own `project` region, and other content — is preserved byte-for-byte. AICore text files are authored LF-only; text IO performs no newline translation, while marker parsing compares exact line content after line splitting. Raw mode preserves source bytes exactly; merge mode preserves every destination byte outside the replaced or inserted top-level keys — and, for `mcp`, outside the replaced or inserted server members — so destination-only keys, comments, and formatting survive.

## Operator boundary (HARD RULE)

The sync operator only **runs this tool and reads its report**. The operator MUST NOT hand-edit any destination file: no `project`-region edits, no marker edits, no writing or removing the blocker, no clearing or editing `pending:`, and no git or other mutation of the destination. The `project` region, the `pending` list, and the reconciliation blocker are **destination-owned**; the destination project reconciles them itself. A `check` that reports drift with a non-empty `pending` is the expected handoff state — not a failure for the operator to fix. Run the tool, report the result, and stop.

## When to use me

- A core-owned file (skill, agent, or individually cleared region source) changed and bound destination copies must be brought current.
- A markerless destination must be enrolled into the core/project region model (`init`).
- A whole file, such as a raw-cleared reference, must be mirrored verbatim rather than by active regions (raw mode).
- A JSON/JSONC object config's top-level keys must be merged into a destination that keeps its own keys and comments, with the `mcp` key merged by server name so destination-only MCP servers survive and a same-named server entry is core-wins (merge mode) — e.g. `opencode.jsonc`.
- A drift check is wanted before shipping: confirm the destination core regions byte-match the pinned source revision.
- A destination must be reminded (via its root runtime file) to reconcile its `project` region and clear `pending`.

## Commands

```bash
# Verify every destination core region against the source revision and sync the blocker.
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check \
  --source <source-dir> --destination <destination-dir> \
  --bindings <bindings-file> --source-revision <40-hex>

# Write: splice each source core region into its destinations and pin the revision.
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py apply \
  --source <source-dir> --destination <destination-dir> \
  --bindings <bindings-file> --source-revision <40-hex>

# Enroll region-mode destinations, raw-copy whole-file bindings, merge
# top-level keys, and refresh existing bindings.
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init \
  --source <source-dir> --destination <destination-dir> \
  --bindings <bindings-file> --source-revision <40-hex>
  [--bind <source>=<destination>]... [--bind-raw <source>=<destination>]...
  [--bind-cleared] [--root <destination-root-path>]
```

- `--source` — directory holding the source files named by the bindings.
- `--destination` — directory holding the destination files named by the bindings.
- `--bindings` — the bindings YAML file (schema below). For a destination root blocker, use the canonical path `<destination>/.aicore/core.yaml`.
- `--source-revision` — the 40-character lowercase hex source revision to compare (`check`) or pin (`apply`/`init`).
- `init --bind SOURCE=DESTINATION` — append a region-mode binding to the loaded bindings file before preflight. Repeatable and idempotent for an identical mapping.
- `init --bind-raw SOURCE=DESTINATION` — append a raw binding. Repeatable and idempotent for an identical mapping; a destination already mapped to a different source fails closed.
- `init --bind-cleared` — enroll every source `distribution-clearance.json` resolves to that is not already bound, using its resolved `mode`. A skill root resolves to every file under it (its `region_files` members use `region`, the rest use the root's default mode; interpreter caches never join); a file row resolves to itself. Ordinary sources map to the same relative path; the `role: root` source maps to the destination instruction root. Absent bindings are initialized; a region or raw target newly enrolled here may have its missing target and parent directories created after preflight; existing mappings are preserved.
- `init --root PATH` — set the destination path for the root-role source when it is not already mapped and detection must be overridden.
- Binding conflict detection is metadata-only: different existing destination bytes never block synchronization. Region `init` preserves old destination content in the `project` region and sets `pending`; raw mode overwrites the target byte-for-byte as explicitly selected.
- These flags let the script update binding metadata and synchronized content together; do not hand-edit destination payload files or copy files manually. Without `--bind-cleared` the bindings file must already exist; with it, an absent file is initialized from an empty routing document. Raw and merge destinations must exist before `apply` and before `init` for mappings already stored in the bindings file. During `init --bind-raw`, only an absent destination belonging to a newly registered mapping may be created, and only when its parent directory already exists; a missing parent or a missing target on a stored mapping returns exit `1` without writes. Repeating a declaration for a stored mapping does not make it new.

For a region binding, `init` rebuilds a markerless destination as frontmatter + a `core` region holding the source core + a `project` region holding the destination's previous body, then records that region path in `pending`. CLI binding flags are merged into the existing bindings file before this enrollment. For a raw binding, `init` copies the source bytes exactly and creates no regions, report, or `pending` entry; a target newly enrolled in bulk by `--bind-cleared` may have missing parent directories created, while an explicitly declared `--bind-raw` or persisted raw target is created as a byte-exact file only when its parent already exists. For a merge binding, `init` and `apply` write the merged document and likewise create no regions, report, or `pending` entry, and a merge destination must already exist (a merge target is never created). `apply` re-splices region cores, copies raw sources as bytes, and writes merged documents; both `apply` and `init` remove obsolete `pending` paths that are now bound raw or merge. `check` verifies all three modes, reports stale non-region `pending` paths until a write command normalizes them, and syncs the blocker for region paths (see below).

### Operator runbook

Argument origins: `--source .` is the source checkout; `--destination` is the destination directory; `--bindings` is `<destination-dir>/.aicore/core.yaml`; `--source-revision` is the revision being distributed — the 40-character lowercase hex value of `git rev-parse HEAD` in the source checkout. `check` compares against it; `apply`/`init` pin it; `--root` (optional) overrides the detected destination instruction file; the command runs without it.

| Operator state | Command | Expected result |
|---|---|---|
| Unenrolled destination (no `<destination-dir>/.aicore/core.yaml`) | `uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init --source . --destination <destination-dir> --bindings <destination-dir>/.aicore/core.yaml --source-revision <40-hex> --bind-cleared [--root <destination-root-path>]` | `initialized` |
| Enrolled destination receiving an update | `uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py apply --source . --destination <destination-dir> --bindings <destination-dir>/.aicore/core.yaml --source-revision <40-hex>`, then `check` below | `applied`, then `current` (or a drift report) |
| Drift check | `uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check --source . --destination <destination-dir> --bindings <destination-dir>/.aicore/core.yaml --source-revision <40-hex>` | `current`, or the exit-1/exit-2 report under *Exit contract* |

## Binding modes

Each bound source runs in one of three modes, resolved from the source-side `distribution-clearance.json` (its file row, or the skill-root row that expands to it): `region` splices the source core region between destination markers; `raw` copies the whole source byte-for-byte; `merge` merges the source's top-level object keys into the destination, except the `mcp` key, which merges by server name.

- **`region`** (the default) — the marker model described under *Marker contract*. `init` enrolls a markerless destination and `apply` splices only the bytes strictly between the destination's `core` markers. The destination carries a `project` region, and `init` records its path in `pending`.
- **`raw`** — whole-file copy with no markers. `init` and `apply` write the source file to the destination byte-for-byte, and `check` verifies byte equality. A raw destination carries **no `project` region**, creates **no reconciliation report**, and never creates a `pending` entry; valid raw entries do not take part in region reconciliation or its blocker. If a path remains in `pending` from a prior region binding after switching it to raw, `check` reports that stale state (exit `1`) without treating it as destination reconciliation; `apply`/`init` clear it. `check` also exits `1` when a raw source/destination is missing or bytes differ, and `2` for an unknown `mode`.
- **`merge`** — top-level-key merge of a JSON/JSONC object document, with no markers. `init` and `apply` write a document in which every source top-level key carries the source value and every destination-only key, comment, and formatting byte outside replaced or inserted keys is preserved; a source top-level key replaces the destination's same key wholesale (shallow, no deep merge) — **except `mcp`**, whose servers merge by name when both sides hold `mcp.servers` as an object: a same-named server entry is core-wins, every destination-only server survives, a source-only server is inserted, and any non-`servers` child of the destination `mcp` object is preserved. When the destination has no `mcp`, or either side's `mcp` or `mcp.servers` is not an object, the `mcp` value is replaced wholesale like any other key. A merge destination carries **no `project` region**, creates **no reconciliation report**, and never creates a `pending` entry. A merge binding never creates a destination: a missing destination is drift (exit `1`) in `check`, `apply`, and `init`. `check` exits `0` when each source top-level key is present in the destination with the source value (extra destination keys allowed) — for `mcp` with object `mcp.servers` on both sides, extra destination-only servers are also allowed while every source server must still be present with an equal value — and `1` on a missing or mismatched source key; a non-object top level or malformed JSONC in the source or destination exits `2`. If a path remains in `pending` from a prior region binding after switching it to merge, the stale state is reported exactly as for raw: `check` exits `1` without destination reconciliation, and `apply`/`init` clear it.

Region mode, raw mode, and merge mode may coexist in one bindings file; each entry is handled independently.

For raw references, "no markers/project region" means no active region ownership is
introduced or interpreted by synchronization. Fenced template/example marker literals
remain ordinary source bytes and are copied intact, not rejected or extracted.

## Marker contract

A marker counts only as an exact line (ignoring surrounding whitespace) outside a fenced code block. The parser recognizes matching backtick and tilde fences and splits both LF and CRLF line separators without newline translation; repository text files and fixtures must use LF.

- `<!-- core:begin -->` / `<!-- core:end -->` — the region-mode destination's core region. The tool owns these bytes: `apply` replaces everything strictly between the two markers with the source region, and keeps the destination markers themselves. A source with neither core nor project markers outside fenced code is markerless and its whole post-frontmatter body is the core; a source carrying exact `<!-- project:begin -->` / `<!-- project:end -->` marker lines without exactly one ordered core pair is malformed and fails with exit `2`, so its project content is never read as core; raw bindings use no markers.
- `<!-- project:begin -->` / `<!-- project:end -->` — the destination-owned project region. The tool never reads or writes it.

Each region-mode destination must carry exactly one `core` marker pair, BEGIN before END. A missing, duplicated, or reversed destination pair is malformed input. Genuinely markerless sources, raw destinations, and merge destinations do not require a pair.

A region-mode source is markerless only when it has no exact core markers or project markers outside fenced code; its whole post-frontmatter body is then the source core. If any exact source core marker line exists, the source must have exactly one ordered pair or the command fails with exit `2` rather than treating malformed markers as a markerless file. Exact source project-marker lines without a valid ordered core pair also fail with exit `2`. Raw and merge bindings do not parse source markers.

## Bindings schema

`schema: 1`. `core_revision` is the pinned 40-hex source revision or `null`. Each `bindings` entry maps one `source` to one or more `destinations`; source and destination paths must be canonical safe relative POSIX paths and must not contain NUL characters (no absolute paths, empty/`.`/`..` components, backslashes, or Windows drive/root prefixes), and destination paths must be unique. Invalid persisted paths are rejected as malformed bindings (exit `2`) before filesystem operations use them.
A binding carries no `mode`: the distribution mode is owned by source clearance (below). A persisted `mode` key is read as a declaration; a persisted `raw` declaration whose source record is not `raw` fails closed (exit `2`), and the key is dropped on the next save.
`pending` lists outstanding paths; `check` requires it to be empty. A region, raw, or merge binding whose `source` is absent from the source-side `distribution-clearance.json` (`schema: 1`, read from `--source`) is not cleared for distribution and cannot be synchronized.
That file is `{"schema": 1, "cleared": {…}}` — the only accepted version label; any other is rejected (exit `2`), and there is no legacy or migration machinery.
Records are either file rows `{ "mode": "region"|"raw"|"merge", "role"?: "root" }` (the root runtime `AGENTS.md` is the only `role: root`; agent specs and persona profiles are per-file region rows) or skill-root rows — keys ending in `/` with `{ "mode": <default>, "region_files": [<root-relative paths>]? }` as declared by `distribution-clearance.json`.
The sync tool expands skill roots at every sync: `region_files` members deliver only their core region, all other files use the root's default mode, `__pycache__`/`*.pyc` caches never join, and new files join automatically.
The declared mode is authoritative for distribution, so an explicit `--bind`/`--bind-raw` declaration whose mode conflicts with the source record fails closed (exit `2`); the sync tool's own `core-sync` skill is never cleared. Skill files join automatically via their root row after that root's test or review passes; per-file rows are for non-skill sources.

Read `distribution-clearance.definition.md` in full as the format's source of truth.

`root` (optional) is the destination root runtime file, relative to the destination directory (e.g. `CLAUDE.md`). When absent it is detected from the destination instruction files in priority order: `AGENTS.md`/`agents.md`, then `CLAUDE.md`/`claude.md`, then `instructions.md`; the detected spelling is preserved. When present, it must follow the same canonical safe relative POSIX and NUL-free path rules as `source` and `destinations`; malformed values are rejected before filesystem operations. When the resolved root file is missing, the blocker is skipped silently. Destination projects use `.aicore/core.yaml` as the canonical bindings path when a root blocker may be generated; that pairs with `.aicore/reconciliation/init.yaml`.

```yaml
schema: 1
core_revision: "86ef8aab65c9bf7bdaeab65e86edd6e1968207d5"
root: CLAUDE.md
bindings:
  - source: .opencode/agents/lumen.md
    destinations:
      - .opencode/agents/lumen.md
  - source: opencode.jsonc
    destinations:
      - opencode.jsonc
pending: []
```

## Reconciliation blocker

While region-mode paths remain in `pending`, `check`, `apply`, and `init` ensure the destination root runtime file carries a marker-delimited blocker block:

```markdown
<!-- core:reconcile:begin -->
> **⚠️ ACTION REQUIRED — core reconciliation. This project is not current until this is done.**
> …
<!-- core:reconcile:end -->
```

The block is self-contained; the destination assistant needs no other context. It directs the destination to adopt the two-region rule permanently in its root instructions (`CLAUDE.md` / `AGENTS.md`) if absent. It explains that the upstream-owned `core` region is never edited, moved, or deleted, while the destination-owned `project` region keeps genuine project-specific content and may contain the old core copy that is now superseded. It also carries a config-file instruction: if the merge delivered `opencode.jsonc`, migrate the file from the OpenCode V1 layout to the V2 layout when it is still on the old one, and note that the merge preserves this project's own MCP servers alongside the core-registered ones with a same-named server entry core-wins, while every other key is still replaced wholesale.

For each path in `pending:`:
1. Open the file.
2. If `.aicore/reconciliation/init.yaml` exists, read its core revision and source/destination/action metadata; it does not contain displaced file content.
3. Inspect the old project-region text in the destination file, remove only duplicated/contradicted core copies, and keep genuine project-specific content. Never touch the core region or markers.
4. Delete that file's entry from `pending:` in `.aicore/core.yaml`.

When `pending:` is empty, delete the entire blocker block (markers included). The block is appended after one blank line when absent and replaced in place on later runs. Once `pending` is empty, `check` removes it; `check` exits `0` only if revision, source/destination, region, raw-byte, and merge checks also pass. All other root content is preserved.

## Exit contract

Argument-parser/CLI validation errors (including invalid `--source-revision` syntax) exit `2` before a command starts. The table covers successfully parsed commands.

| Exit | `check` | `apply` | `init` |
|---|---|---|---|
| `0` | every core region matches the pinned revision, every raw destination byte-matches its source, every merge destination carries each source top-level key with the source value (extra destination-only keys and, for an object `mcp.servers` on both sides, extra destination-only servers allowed), and `pending` is empty; prints `current` | every region spliced / raw file copied / merge document written and the revision pinned; prints `applied` | every markerless destination enrolled, raw file copied, merge document written, or marked destination refreshed and the revision pinned; prints `initialized` |
| `1` | drift: stale `core_revision`, missing/unreadable source, missing destination, raw/region/merge mismatch, non-empty region `pending`, stale non-region-bound `pending`, a bound source absent from `distribution-clearance.json` or that file itself missing, or write-time filesystem I/O error | drift: missing/unreadable source or missing destination, a bound source absent from `distribution-clearance.json` or that file itself missing, or write-time filesystem I/O error | drift: missing/unreadable source or destination, missing parent for an explicitly declared `--bind-raw` or persisted raw destination, a bound source absent from `distribution-clearance.json` or that file itself missing, or write-time filesystem I/O error |
| `2` | malformed bindings/source markers, a source carrying project markers without a valid core pair, `distribution-clearance.json` present but malformed, malformed JSONC in a merge source/destination, invalid or unreadable region-destination markers, overlapping roots, unsafe root targets (including source-inode aliases), or root/non-region alias | malformed bindings/source markers, a source carrying project markers without a valid core pair, `distribution-clearance.json` present but malformed, malformed JSONC in a merge source/destination, invalid or unreadable region-destination markers, unsafe write targets (including source-inode aliases and duplicate resolved output paths), root/non-region alias, or failed outside-marker preservation (nothing is written) | malformed bindings/source markers, a source carrying project markers without a valid core pair, `distribution-clearance.json` present but malformed, malformed JSONC in a merge source/destination, invalid region-destination markers, unsafe write targets (including source-inode aliases and duplicate resolved output paths), root/non-region alias, or a planned raw target that would become the implicit root |

All commands validate bindings and preflight resolved write targets (including symlinks) before mutation; no write target may resolve inside the source tree or share a regular-file inode with a source-tree file. `apply`/`init` reject distinct output paths resolving to the same target. `init` additionally calculates default-root selection after planned raw creation and rejects a raw target that would become `AGENTS.md`, the implicit root, before writes. `check` validates region sources before blocker sync; after syncing the blocker it can still return exit `1` for revision, missing source/destination, raw-byte drift, region drift, merge drift, or `pending`, and exit `2` for malformed destination markers, malformed JSONC, or unreadable region destinations. `apply`/`init` sync the blocker only after their payload, report, and bindings writes succeed. Earlier binding, path-preflight, marker, or source-validation errors may return without blocker synchronization. A missing or unreadable root file is skipped silently and does not change the result. Write-time filesystem errors return exit `1` with a concise diagnostic; multiple-output operations are not transactional, so an I/O error may follow earlier successful writes and requires a subsequent `check`. Raw and merge destinations never create `pending` entries or contribute to reconciliation. If a path changes from region to a non-region mode (raw or merge) while listed in `pending`, `apply`/`init` remove that stale entry; `check` excludes it from the blocker, returns drift with an instruction to run `apply` or `init`, and leaves bindings unchanged.

The clearance gate runs before any bound-source payload read or destination mutation in `check`, `apply`, and `init`, after the required bindings/clearance metadata reads and write-target preflight; an uncleared source never produces a payload, report, bindings, or blocker write.

## Examples

To enroll a complete applicable cleared set at one revision, use bulk enrollment from the source checkout against a
clean, saved destination. Inspect the selected revision's clearance first; a path is
not deliverable merely because it exists in the source tree. The command below
requires the source's other applicable preconditions too, including existing merge
targets:

```bash
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init \
  --source . --destination ../destination \
  --bindings ../destination/.aicore/core.yaml --source-revision "$(git rev-parse HEAD)" \
  --bind-cleared --root AGENTS.md
```

New region destinations discovered by `--bind-cleared` may be absent: `init` creates
their targets and parents, renders the source core plus an empty project region, and
records pending reconciliation. An explicit region `--bind SOURCE=DESTINATION` alone
does not create an absent target; nor does `apply` enroll a missing or markerless one.
For an already-present markerless region destination, `init` retains its previous body in project.
Already marked region destinations refresh their core while preserving outside bytes.

Per-file `region` clearance is not raw whole-file transport or a directory-root copy.
Source-local project content does not ship. A raw-cleared reference may contain fenced
marker literals: those bytes are ordinary template or example content, not active regions
governing that raw file. Raw mode does not parse or strip those literals.

To mirror a raw-cleared whole-file reference, add its mapping with `--bind-raw` and run
`init`; an explicitly declared `--bind-raw` (or persisted raw) target still requires an
existing parent, so a missing parent remains drift. A raw target newly enrolled in bulk by
`--bind-cleared`, however, creates its missing parent directories. A `merge`-cleared source
(such as `opencode.jsonc`) needs no dedicated flag and requires an existing destination.
Modes and revision rules are unchanged.

## Troubleshooting

- **Raw byte drift (`check` exits 1):** the destination file differs from its source. Run `apply` or `init` with the intended source revision, then run `check` again.
- **Merge drift (`check` exits 1):** a source top-level key is missing from the destination or its value differs — for `mcp` with object `mcp.servers` on both sides, a missing core server or a differing server value is drift, while extra destination-only servers are not. Run `apply` or `init` with the intended source revision, then run `check` again.
- **Merge destination missing (exit 1):** merge never creates a destination. `check`, `apply`, and `init` all require an existing merge target, so a missing one is drift, not enrollment. Create the destination object file first, then re-run.
- **Malformed JSONC (`check`/`apply`/`init` exits 2):** a merge source or destination is not a single JSON/JSONC object — a non-object top level, or malformed syntax such as an unterminated comment or a duplicate key. Merge is object-only; correct the document.
- **Raw destination missing (exit 1):** `apply` and `check` always require the target to exist. `init` also requires an existing target for a raw mapping already stored in YAML. A newly registered `--bind-cleared` mapping creates an absent raw target and any missing parent directories; an explicitly declared `--bind-raw` mapping can create an absent target only when its parent directory already exists, so its missing parent fails before writes. Repeating a declaration for an existing mapping does not enable creation.
- **New region mapping missing:** use supported `init --bind-cleared` enrollment for newly discovered region mappings, not raw copying or an absent explicit `--bind` target. Inspect all applicable-set preconditions before running it; bulk `--bind-cleared` creates missing parent directories for raw targets, while an explicit `--bind-raw` target still requires an existing parent.
- **Legacy raw hint or duplicate shared text:** cause: prior whole-file transport or displaced markerless content. If a binding persists an explicit `mode: raw` hint, it conflicts with region clearance and fails closed with exit `2`. Only if present, remove that obsolete hint through separately authorized destination bindings maintenance, retaining source/destination mappings and pending state, before enrollment; source clearance owns the actual mode. Normal saves omit mode hints; a conflicting hint cannot be removed by a synchronization that already fails preflight. Never bypass the gate or assume every adopter has this hint. Remove displaced duplicate shared text only from project, retaining genuine local evidence and history. Never edit protected core. Fresh region creation does not copy source project sections or seed local records. Clear pending through the existing blocker procedure and require `check` exit `0`; recurring updates use `apply` then `check` at the selected revision, and new or markerless paths require enrollment first. These steps document existing operations, not authority to mutate an adopter or change core locally.
- **Stale non-region-bound pending path (`check` exits 1):** the binding changed from region to raw or merge while the destination was listed in `pending`. Run `apply` or `init` to remove the obsolete reconciliation entry; `check` does not mutate the bindings file.
- **Conflicting binding declaration (`init` exits 2):** the requested destination path is already mapped to a different source. This is a bindings-metadata conflict, not a destination-content conflict; same mappings are idempotent, region content is reconciled through the `project` region/blocker, raw content is replaced by its selected whole-file source, and merge content is re-derived by top-level key (with the `mcp` key merged by server name).
- **Source not cleared for distribution (exit 1):** the bound `source` is absent from `distribution-clearance.json`. Skill files join automatically via their root row once its test or review passes; per-file rows are for non-skill sources, so for those run the file's test or review and add its per-file row. That file is the clearance record, not a content manifest.
- **Source project markers without a core pair (exit 2):** add the ordered `<!-- core:begin -->` … `<!-- core:end -->` pair, or remove the stray project markers from a genuinely markerless source.
- **Malformed source/destination markers (`exit 2`):** genuinely markerless region sources have no exact core or project marker lines outside fences; sources with core markers need one ordered pair, and region destinations must already have one pair. Correct the markers or use a genuinely markerless source.
- **Unsafe or aliased write target (`exit 2`):** source/destination roots overlap; a root or payload target escapes the destination; a write target resolves inside the source or shares an inode with a source-tree file (including a hard link); distinct output paths resolve to one target; the root aliases a non-region (raw or merge) destination; or a new raw target would become the implicit root after `init`. The operator must replace a link with a regular file and re-run `check`; the command fails before writing. Bindings/report paths may be outside the destination if they remain outside the source.

## Roadmap

The destination `project`-region workflow is destination-owned: the core tool never reconciles the `project` region. For region bindings it writes core-region bytes; for raw bindings it writes the whole source file byte-for-byte; for merge bindings it merges the source's top-level object keys into the destination (merging the `mcp` key by server name); it also updates binding revision/pending state, region reconciliation reports, and the root blocker. Planned scale-up work will link each `pending` entry to its reconciliation report (today `pending` is a flat list of paths).
