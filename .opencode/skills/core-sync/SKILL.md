---
name: core-sync
description: "Per-binding core update for destination files. Two modes: `region` (default) enrolls markerless destinations (`init`), splices (`apply`), and verifies (`check`) a source file's core region into each bound destination while leaving everything outside the region byte-identical; `raw` copies the whole source file to the destination byte-for-byte with no markers. Records the pinned source revision in a bindings file and keeps a reconciliation blocker block in the destination's root runtime file while `pending` is non-empty. Use when a core-owned skill or agent file must be pushed to a destination project, when a whole markerless file (e.g. `opencode.jsonc`) must be mirrored verbatim, when a destination's core-region drift needs a check, or when a destination must be reminded to reconcile its `project` region."
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.3.2
---

## What I do

Update the bound files of a destination from a source of truth, and keep the destination's root runtime file carrying a reconciliation blocker while region reconciliation is pending. Each binding runs in one of two modes: `region` (the default) mirrors the source `core` region between destination markers; `raw` copies the whole source file byte-for-byte with no markers or project region. The source is read-only; writes are destination core regions or raw whole files, binding metadata, a reconciliation report for region initialization/refresh, and the root blocker when region paths are pending. In region mode, everything outside destination core markers — frontmatter, the destination's own `project` region, and other content — is preserved byte-for-byte. AICore text files are authored LF-only; text IO performs no newline translation, while marker parsing compares exact line content after line splitting. Raw mode preserves source bytes exactly.

## When to use me

- A core-owned file (skill or agent) changed at the source and the bound destination copies must be brought current.
- A markerless destination must be enrolled into the core/project region model (`init`).
- A whole file must be mirrored verbatim with no region markers (raw mode) — e.g. `opencode.jsonc`.
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

# Enroll region-mode destinations, raw-copy whole-file bindings, and refresh existing bindings.
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init \
  --source <source-dir> --destination <destination-dir> \
  --bindings <bindings-file> --source-revision <40-hex>
  [--bind <source>=<destination>]... [--bind-raw <source>=<destination>]...
```

- `--source` — directory holding the source files named by the bindings.
- `--destination` — directory holding the destination files named by the bindings.
- `--bindings` — the bindings YAML file (schema below). For a destination root blocker, use the canonical path `<destination>/.aicore/core.yaml`.
- `--source-revision` — the 40-character lowercase hex source revision to compare (`check`) or pin (`apply`/`init`).
- `init --bind SOURCE=DESTINATION` — append a region-mode binding to the loaded bindings file before preflight. Repeatable and idempotent for an identical mapping.
- `init --bind-raw SOURCE=DESTINATION` — append a raw binding. Repeatable and idempotent for an identical mapping; a destination already mapped to a different source/mode fails closed.
- Binding conflict detection is metadata-only: different existing destination bytes never block synchronization. Region `init` preserves old destination content in the `project` region and sets `pending`; raw mode overwrites the target byte-for-byte as explicitly selected.
- These flags let the script update binding metadata and synchronized content together; do not hand-edit destination payload files or copy files manually. The bindings file must already exist. Raw destinations must exist before `init`/`apply`.

For a region binding, `init` rebuilds a markerless destination as frontmatter + a `core` region holding the source core + a `project` region holding the destination's previous body, then records that region path in `pending`. CLI binding flags are merged into the existing bindings file before this enrollment. For a raw binding, `init` copies the source bytes exactly and creates no regions, report, or `pending` entry. `apply` re-splices region cores and copies raw sources as bytes; both `apply` and `init` remove obsolete `pending` paths that are now bound raw. `check` verifies both modes, reports stale raw `pending` paths until a write command normalizes them, and syncs the blocker for region paths (see below).

## Binding modes

Each bindings entry runs in one of two modes, selected by its optional `mode` field.

- **`region`** (the default) — the marker model described under *Marker contract*. `init` enrolls a markerless destination and `apply` splices only the bytes strictly between the destination's `core` markers. The destination carries a `project` region, and `init` records its path in `pending`.
- **`raw`** — whole-file copy with no markers. `init` and `apply` write the source file to the destination byte-for-byte, and `check` verifies byte equality. A raw destination carries **no `project` region**, creates **no reconciliation report**, and never creates a `pending` entry; valid raw entries do not take part in region reconciliation or its blocker. If a path remains in `pending` from a prior region binding after switching it to raw, `check` reports that stale state (exit `1`) without treating it as destination reconciliation; `apply`/`init` clear it. `check` also exits `1` when a raw source/destination is missing or bytes differ, and `2` for an unknown `mode`.

Region mode and raw mode may coexist in one bindings file; each entry is handled independently.

## Marker contract

A marker counts only as an exact line (ignoring surrounding whitespace) outside a fenced code block. The parser recognizes matching backtick and tilde fences and splits both LF and CRLF line separators without newline translation; repository text files and fixtures must use LF.

- `<!-- core:begin -->` / `<!-- core:end -->` — the region-mode destination's core region. The tool owns these bytes: `apply` replaces everything strictly between the two markers with the source region, and keeps the destination markers themselves. A markerless source is valid and its whole post-frontmatter body is the core; raw bindings use no markers.
- `<!-- project:begin -->` / `<!-- project:end -->` — the destination-owned project region. The tool never reads or writes it.

Each region-mode destination must carry exactly one `core` marker pair, BEGIN before END. A missing, duplicated, or reversed destination pair is malformed input. Markerless sources and raw destinations do not require a pair.

A region-mode source is markerless only when it has no exact core marker lines outside fenced code; its whole post-frontmatter body is then the source core. If any exact source core marker line exists, the source must have exactly one ordered pair or the command fails with exit `2` rather than treating malformed markers as a markerless file. Raw bindings do not parse source markers.

## Bindings schema

`schema: 1`. `core_revision` is the pinned 40-hex source revision or `null`. Each `bindings` entry maps one `source` to one or more `destinations`; destination paths must be unique and no path may escape upward with `..`. Each entry may set an optional `mode` of `region` (the default) or `raw`; any other value is malformed input (exit `2`). `pending` lists outstanding paths; `check` requires it to be empty. Region entries are serialized without the default `mode`; a raw entry is serialized with `mode: raw` so the mode survives a later `apply`/`init`.

`root` (optional) is the destination root runtime file, relative to the destination directory (e.g. `CLAUDE.md`). When absent it defaults to `AGENTS.md` when that file exists in the destination, else `CLAUDE.md`. Like every other bindings path it may not escape the destination with `..`. When the resolved root file is missing, the blocker is skipped silently. Destination projects use `.aicore/core.yaml` as the canonical bindings path when a root blocker may be generated; that pairs with `.aicore/reconciliation/init.yaml`.

```yaml
schema: 1
core_revision: "86ef8aab65c9bf7bdaeab65e86edd6e1968207d5"
root: CLAUDE.md
bindings:
  - source: .opencode/agent.md
    destinations:
      - .opencode/agent.md
  - source: opencode.jsonc
    destinations:
      - opencode.jsonc
    mode: raw
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

The block is self-contained; the destination assistant needs no other context. It directs the destination to adopt the two-region rule permanently in its root instructions (`CLAUDE.md` / `AGENTS.md`) if absent. It explains that the upstream-owned `core` region is never edited, moved, or deleted, while the destination-owned `project` region keeps genuine project-specific content and may contain the old core copy that is now superseded.

For each path in `pending:`:
1. Open the file.
2. If `.aicore/reconciliation/init.yaml` exists, read its core revision and source/destination/action metadata; it does not contain displaced file content.
3. Inspect the old project-region text in the destination file, remove only duplicated/contradicted core copies, and keep genuine project-specific content. Never touch the core region or markers.
4. Delete that file's entry from `pending:` in `.aicore/core.yaml`.

When `pending:` is empty, delete the entire blocker block (markers included). The block is appended after one blank line when absent and replaced in place on later runs. Once `pending` is empty, `check` removes it; `check` exits `0` only if revision, source/destination, region, and raw-byte checks also pass. All other root content is preserved.

## Exit contract

Argument-parser/CLI validation errors (including invalid `--source-revision` syntax) exit `2` before a command starts. The table covers successfully parsed commands.

| Exit | `check` | `apply` | `init` |
|---|---|---|---|
| `0` | every core region matches the pinned revision, every raw destination byte-matches its source, and `pending` is empty; prints `current` | every region spliced / raw file copied and the revision pinned; prints `applied` | every markerless destination enrolled, raw file copied, or marked destination refreshed and the revision pinned; prints `initialized` |
| `1` | drift: stale `core_revision`, missing/unreadable source, missing destination, raw/region mismatch, non-empty region `pending`, stale raw-bound `pending`, or write-time filesystem I/O error | drift: missing/unreadable source or missing destination, or write-time filesystem I/O error | drift: missing/unreadable source or destination, or write-time filesystem I/O error |
| `2` | malformed bindings/source markers, invalid or unreadable region-destination markers, overlapping roots, unsafe resolved write targets, or root/raw alias | malformed bindings/source markers, invalid or unreadable region-destination markers, unsafe write targets, root/raw alias, or failed outside-marker preservation (nothing is written) | malformed bindings/source markers, invalid region-destination markers, unsafe write targets, or root/raw alias |

All commands validate bindings and preflight write targets before mutation. `check` validates region sources before blocker sync; after syncing the blocker it can still return exit `1` for revision, missing source/destination, raw-byte drift, region drift, or `pending`, and exit `2` for malformed destination markers or unreadable region destinations. `apply`/`init` sync the blocker only after their payload, report, and bindings writes succeed. Earlier binding, path-preflight, marker, or source-validation errors may return without blocker synchronization. A missing or unreadable root file is skipped silently and does not change the result. Write-time filesystem errors return exit `1` with a concise diagnostic; multiple-output operations are not transactional, so an I/O error may follow earlier successful writes and requires a subsequent `check`. Raw destinations never create `pending` entries or contribute to reconciliation. If a path changes from region to raw while listed in `pending`, `apply`/`init` remove that stale entry; `check` excludes it from the blocker, returns drift with an instruction to run `apply` or `init`, and leaves bindings unchanged.

## Examples

To enroll the root spec and whole-file config without hand-editing the bindings YAML, run `init` with declarations (the existing bindings file and raw destination file must exist):

```bash
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init \
  --source ./aicore --destination ./destination \
  --bindings ./destination/.aicore/core.yaml --source-revision "$SOURCE_REVISION" \
  --bind AGENTS.md=CLAUDE.md --bind-raw opencode.jsonc=opencode.jsonc
```

The script adds the binding entries, enrolls `CLAUDE.md` into core/project regions, raw-copies `opencode.jsonc` byte-for-byte, and generates a reconciliation blocker for the region path.

To mirror only a markerless whole-file config, add its mapping with `--bind-raw` and run `init`. The destination file becomes byte-identical to the source and receives no region markers, reconciliation report, or `pending` entry.

## Troubleshooting

- **Raw byte drift (`check` exits 1):** the destination file differs from its source. Run `apply` or `init` with the intended source revision, then run `check` again.
- **Raw destination missing (`init`/`apply`/`check` exits 1):** raw mode copies an existing whole-file target; it does not create a missing file. Restore/create the destination target before retrying.
- **Stale raw-bound pending path (`check` exits 1):** the binding changed from region to raw while the destination was listed in `pending`. Run `apply` or `init` to remove the obsolete reconciliation entry; `check` does not mutate the bindings file.
- **Conflicting binding declaration (`init` exits 2):** the requested destination path is already mapped to a different source or mode. This is a bindings-metadata conflict, not a destination-content conflict; same mappings are idempotent, region content is reconciled through the `project` region/blocker, and raw content is replaced by its selected whole-file source.
- **Malformed source/destination markers (`exit 2`):** markerless sources must contain no exact core-marker lines outside fences; region sources need one ordered pair, and region destinations must already have one pair. Correct the markers or use a genuinely markerless source.
- **Unsafe write target (`exit 2`):** source/destination roots overlap; a root or payload target escapes the destination; any write target, including bindings/report, resolves inside the source; or the root path aliases a raw destination. Correct the binding/root/symlink mapping; the command fails before writing. Bindings/report paths may be outside the destination if they remain outside the source.

## Roadmap

The destination `project`-region workflow is destination-owned: the core tool never reconciles the `project` region. For region bindings it writes core-region bytes; for raw bindings it writes the whole source file byte-for-byte; it also updates binding revision/pending state, region reconciliation reports, and the root blocker. Planned scale-up work will link each `pending` entry to its reconciliation report (today `pending` is a flat list of paths).
