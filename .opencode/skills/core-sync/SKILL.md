---
name: core-sync
description: Region-based core update for marked destination files. Enrolls markerless destinations (`init`), splices (`apply`), and verifies (`check`) a source file's `<!-- core:begin -->` / `<!-- core:end -->` core region into each bound destination while leaving everything outside the region byte-identical, records the pinned source revision in a bindings file, and keeps a reconciliation blocker block in the destination's root runtime file while `pending` is non-empty. Use when a core-owned skill or agent file must be pushed to a destination project, when a destination's core-region drift needs a check, or when a destination must be reminded to reconcile its `project` region.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.2.0
---

# core-sync

## What I do

Update the core region of destination files from a source of truth, and keep the destination's root runtime file carrying a reconciliation blocker while work is pending. The source is read-only; the writes are each destination's core region, the bindings file, a reconciliation report, and the root runtime file's blocker block. Everything outside the destination core markers — frontmatter, the destination's own `<!-- project:begin -->` / `<!-- project:end -->` region, and any other content — is preserved byte-for-byte.

## When to use me

- A core-owned file (skill or agent) changed at the source and the bound destination copies must be brought current.
- A markerless destination must be enrolled into the core/project region model (`init`).
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

# Enroll markerless destinations (core + project regions) and refresh marked ones.
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init \
  --source <source-dir> --destination <destination-dir> \
  --bindings <bindings-file> --source-revision <40-hex>
```

- `--source` — directory holding the source files named by the bindings.
- `--destination` — directory holding the destination files named by the bindings.
- `--bindings` — the bindings YAML file (schema below).
- `--source-revision` — the 40-character lowercase hex source revision to compare (`check`) or pin (`apply`/`init`).

`init` rebuilds a markerless destination as frontmatter + a `core` region holding the source core + a `project` region holding the destination's previous body, and records each generated/refreshed path in `pending`. `apply` re-splices the core region and pins the revision. `check` and `apply`/`init` also sync the reconciliation blocker (see below).

## Marker contract

A marker counts only as an exact line (ignoring surrounding whitespace) outside a fenced code block.

- `<!-- core:begin -->` / `<!-- core:end -->` — the core region. The tool owns these bytes: `apply` replaces everything strictly between the two markers with the source region, and keeps the destination markers themselves.
- `<!-- project:begin -->` / `<!-- project:end -->` — the destination-owned project region. The tool never reads or writes it.

Each file must carry exactly one `core` marker pair, BEGIN before END. A missing, duplicated, or reversed pair is malformed input.

## Bindings schema

`schema: 1`. `core_revision` is the pinned 40-hex source revision or `null`. Each `bindings` entry maps one `source` to one or more `destinations`; destination paths must be unique and no path may escape upward with `..`. `pending` lists outstanding paths; `check` requires it to be empty.

`root` (optional) is the destination root runtime file, relative to the destination directory (e.g. `CLAUDE.md`). When absent it defaults to `AGENTS.md` when that file exists in the destination, else `CLAUDE.md`. Like every other bindings path it may not escape the destination with `..`. When the resolved root file is missing, the blocker is skipped silently.

```yaml
schema: 1
core_revision: "86ef8aab65c9bf7bdaeab65e86edd6e1968207d5"
root: CLAUDE.md
bindings:
  - source: .opencode/agent.md
    destinations:
      - .opencode/agent.md
pending: []
```

## Reconciliation blocker

While `pending` is non-empty, `check`, `apply`, and `init` ensure the destination root runtime file carries a marker-delimited blocker block:

```markdown
<!-- core:reconcile:begin -->
> **⚠️ ACTION REQUIRED — core reconciliation. This project is not current until this is done.**
> …
<!-- core:reconcile:end -->
```

The block is self-contained — the destination's assistant needs no other context. It first directs the destination to adopt the two-region rule permanently — adding it to the project's root instructions (`CLAUDE.md` / `AGENTS.md`) when absent, since that rule outlives the temporary blocker. It then explains the `<!-- core:begin -->` / `<!-- core:end -->` core region (bytes fixed, never edited, moved, or deleted) and the `<!-- project:begin -->` / `<!-- project:end -->` project region (destination-owned), states that the project region now holds both this project's own rules and an old copy of the core rules the new core region supersedes, and gives step-by-step instructions for every path in `pending:`: open the file, read its report under `.aicore/reconciliation/` when present, edit ONLY inside the project region to drop duplicated/contradicted content while keeping genuine project-specific content, never touch the core region or the markers, then delete that file's entry from `pending:`. To finish, it directs the destination to delete the entire blocker block (markers included) once `pending:` is empty. The block is appended after one blank line when absent; on later runs its body is replaced in place. Once `pending` is empty, `check` removes the block and the command exits `0`. The transform is idempotent and leaves all other root content unchanged.

## Exit contract

| Exit | `check` | `apply` | `init` |
|---|---|---|---|
| `0` | every core region matches the pinned revision and `pending` is empty; prints `current` | every region spliced and the revision pinned; prints `applied` | every markerless destination enrolled / marked destination refreshed and the revision pinned; prints `initialized` |
| `1` | drift: stale `core_revision`, region mismatch, missing destination, or non-empty `pending` | drift: missing source or destination | drift: missing source or destination |
| `2` | malformed bindings, or an invalid source/destination marker pair | malformed bindings, invalid markers, or a failed outside-marker preservation check (nothing is written) | malformed bindings, invalid markers, or a failed outside-marker preservation check |

`check` and `apply`/`init` resolve the root runtime file and sync the reconciliation blocker before returning; a missing root file is skipped silently and never changes the exit code.

## Roadmap

The destination `project`-region workflow is destination-owned: the core tool never reconciles the `project` region — it only writes the core region and the blocker that prompts the destination to reconcile. Planned scale-up work also links each `pending` entry to its reconciliation report (today `pending` is a flat list of paths).
