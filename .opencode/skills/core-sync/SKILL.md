---
name: core-sync
description: "Synchronize cleared source files into bound destinations at a pinned revision. Region mode enrolls or updates shared core while preserving destination-owned content; raw mode copies whole files byte-for-byte; merge mode replaces source-owned top-level JSON/JSONC keys while preserving destination-only keys, comments, and formatting by content rather than byte-for-byte — except the `mcp` key, which merges by server name so destination-only servers survive while a same-named entry is core-wins. Tracks pending region reconciliation and its root blocker. Use when distributing shared skills, agents, or per-file region sources, mirroring whole-file references, merging config keys, checking drift, or reconciling destination project content."
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.9.1
---

## What I do

Update the bound files of a destination from a source of truth, and keep the destination's root runtime file carrying a reconciliation blocker while region reconciliation is pending. Each binding runs in one of three modes: `region` (the default) mirrors the source `core` region between destination markers; `raw` copies the whole source file byte-for-byte with no markers or project region; `merge` merges only the source's top-level object keys into the destination, source keys winning while destination-only keys, comments, and formatting outside replaced or inserted keys stay — except the `mcp` key, which merges by server name. The source is read-only; raw sources are read as bytes without decoding or newline normalization, and merge sources are read as JSONC text (UTF-8, no newline translation). Before mutation, write targets must be regular files: a symlinked bindings or payload/root/report target is rejected before any read or write, and an existing non-regular target is rejected. All write targets — payloads, bindings, reconciliation report, and root blocker — are resolved and preflighted against the source and destination roots. Existing output-file device/inode identities are checked against regular files under the source tree, so hard links cannot mutate source files; distinct output paths that resolve to the same target are rejected. `init` also rejects a newly created raw target that would become the implicit root runtime file. In region mode, the destination's own `project` region and the rest of the text outside the destination core markers are preserved by content, not byte-for-byte: a destination that used CRLF keeps that outside content while its line endings become LF. The leading YAML frontmatter is the exception — a region write refreshes it from the source, so a key the source defines takes the source value, a source-only key is added, and a destination-only key keeps its exact bytes, which is why `local-version` is never reset; `metadata` merges one level down. Text reads perform no newline translation, while text writes normalize `\r\n` and any lone `\r` to `\n`, so every text file core-sync writes carries LF terminators only. AICore text files are authored LF-only. Marker parsing still compares exact line content after splitting both LF and CRLF separators. Region-mode writes in `apply` are unconditional, so a region destination is rewritten and LF-normalized even when its shared region is unchanged (`init` skips the write only when the rebuilt file would be byte-identical to the current one); merge mode skips the write when the merged text already equals the current text, so an untouched CRLF destination keeps its endings; raw mode remains byte-exact.

## Operator boundary (HARD RULE)

The sync operator only **runs this tool and reads its report**. The operator MUST NOT hand-edit any destination file: no `project`-region edits, no marker edits, no writing or removing the blocker, no clearing or editing `pending:`, and no git or other mutation of the destination. The `project` region, the `pending` list, and the reconciliation blocker are **destination-owned**; the destination project reconciles them itself. A `check` that reports drift with a non-empty `pending` is the expected handoff state — not a failure for the operator to fix. Run the tool, report the result, and stop.

## When to use me

- A core-owned file (skill, agent, or individually cleared region source) changed and bound destination copies must be brought current.
- A markerless destination must be enrolled into the core/project region model (`init`), including a brand-new empty project, which bulk enrollment seeds.
- A whole file, such as a raw-cleared reference, must be mirrored verbatim rather than by active regions (raw mode).
- A JSON/JSONC object config's top-level keys must be merged into a destination that keeps its own keys and comments, with the `mcp` key merged by server name (merge mode) — e.g. `opencode.jsonc`.
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
- `init --bind-cleared` — enroll every source `distribution-clearance.json` resolves to that is not already bound, using its resolved `mode`. A directory root resolves to every file under it (its `region_files` members use `region`, the rest use the root's default mode; exclusions are in *Bindings schema*); a file row resolves to itself. Ordinary sources map to the same relative path; the `role: root` source maps to the destination instruction root. Absent bindings are initialized; existing mappings are preserved.
- `init --root PATH` — set the destination path for the root-role source when it is not already mapped and detection must be overridden.
- Binding conflict detection is metadata-only: different existing destination bytes never block synchronization. Region `init` preserves old destination content in the `project` region and sets `pending`; raw mode overwrites the target byte-for-byte as explicitly selected.
- These flags let the script update binding metadata and synchronized content together; do not hand-edit destination payload files or copy files manually. Without `--bind-cleared` the bindings file must already exist; with it, an absent file is initialized from an empty routing document. `apply` and `init` create any region or raw target a binding declares, stored or newly declared, creating missing parent directories; `init --bind-cleared` also seeds an absent merge target it newly binds in that run (source keys merged into an empty object), while merge otherwise requires an existing destination.

For a region binding, `init` rebuilds a markerless destination as frontmatter + a `core` region holding the source core + a `project` region holding the destination's previous body, then records that region path in `pending`. CLI binding flags are merged into the existing bindings file before this enrollment. `apply` re-splices region cores, copies raw sources as bytes, and writes merged documents; *Binding modes* below owns each mode's creation and stale-`pending` clearing, and *Reconciliation blocker* owns blocker sync.

### Operator runbook

Argument origins: `--source .` is the source checkout; `--destination` is the destination directory; `--bindings` is `<destination-dir>/.aicore/core.yaml`; `--source-revision` is the revision being distributed — the 40-character lowercase hex value of `git rev-parse HEAD` in the source checkout. `check` compares against it; `apply`/`init` pin it; `--root` (optional) overrides the detected destination instruction file; the command runs without it.

| Operator state | Command | Expected result |
|---|---|---|
| Unenrolled destination (no `<destination-dir>/.aicore/core.yaml`) | `uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init --source . --destination <destination-dir> --bindings <destination-dir>/.aicore/core.yaml --source-revision <40-hex> --bind-cleared [--root <destination-root-path>]` | `initialized` |
| Enrolled destination receiving an update | `uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py apply --source . --destination <destination-dir> --bindings <destination-dir>/.aicore/core.yaml --source-revision <40-hex>`, then `check` below | `applied`, then `current` (or a drift report) |
| Drift check | `uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check --source . --destination <destination-dir> --bindings <destination-dir>/.aicore/core.yaml --source-revision <40-hex>` | `current`, or the exit-1/exit-2 report under *Exit contract* |

## Binding modes

Each bound source runs in one of three modes, resolved from the source-side `distribution-clearance.json` (its file row, or the directory-root row that expands to it): `region`, `raw`, or `merge`, each defined below.

- **`region`** (the default) — the marker model described under *Marker contract*. `init` enrolls a markerless destination and `apply` splices only the content strictly between the destination's `core` markers; either creates an absent target a binding declares. The destination carries a `project` region, and `init` records its path in `pending`.
- **`raw`** — whole-file copy with no markers. `init` and `apply` write the source file to the destination byte-for-byte, and `check` verifies byte equality. A raw destination carries **no `project` region**, creates **no reconciliation report**, and never creates a `pending` entry; valid raw entries do not take part in region reconciliation or its blocker. If a path remains in `pending` from a prior region binding after switching it to raw, `check` reports that stale state (exit `1`) without treating it as destination reconciliation; `apply`/`init` clear it. `check` also exits `1` when a raw source/destination is missing or bytes differ, and `2` for an unknown `mode`.
- **`merge`** — top-level-key merge of a JSON/JSONC object document, with no markers. `init` and `apply` write a document in which every source top-level key carries the source value and every destination-only key, comment, and formatting outside replaced or inserted keys is preserved by content, not byte-for-byte: the merged text is written only when it differs, and a write normalizes the whole file to LF, so destination-only lines keep their content, while an unwritten destination keeps its original line endings; a source top-level key replaces the destination's same key wholesale (shallow, no deep merge) — **except `mcp`**, whose servers merge by name when both sides hold `mcp.servers` as an object: a same-named server entry is core-wins, every destination-only server survives, a source-only server is inserted, and any non-`servers` child of the destination `mcp` object is preserved. Otherwise the `mcp` value is replaced wholesale like any other key. **The `qmd` server's `--index` argument is the destination folder's name** — on every `mcp` write path and in the comparison, so `apply` is never followed by drift and a renamed folder retargets on the next sync; a project wanting a different index declares that server in its own `.opencode/opencode.jsonc`, and retrieval is still verified. A merge destination carries **no `project` region**, creates **no reconciliation report**, and never creates a `pending` entry. A first `init --bind-cleared` creates a merge destination it newly binds when absent, merging the source into an empty object: the created file already carries every source top-level key with the destination folder's `qmd` index, so no later write follows. Otherwise — `check`, `apply`, a stored binding, a later `init` — a missing merge destination is drift (exit `1`). Merge `check` result classes are in *Exit contract*. A path left in `pending` from a prior region binding is handled exactly as for raw.

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
Records are either file rows `{ "mode": "region"|"raw"|"merge", "role"?: "root" }` (the root runtime `AGENTS.md` is the only `role: root`) or directory-root rows — keys ending in `/` with `{ "mode": <default>, "region_files": [<root-relative paths>]? }` as declared by `distribution-clearance.json`. Agent specs are covered by the `.opencode/agents/` directory root, `region`.
The sync tool expands directory roots at every sync: `region_files` members deliver only their core region, all other files use the root's default mode, `__pycache__`/`*.pyc` caches never join, and new files join automatically.
The declared mode is authoritative for distribution, so an explicit `--bind`/`--bind-raw` declaration whose mode conflicts with the source record fails closed (exit `2`). Directory-root coverage of skill and agent directories: see *Source not cleared for distribution*.

Read `distribution-clearance.definition.md` in full as the format's source of truth.

`root` (optional) is the destination root runtime file, relative to the destination directory (e.g. `CLAUDE.md`). When absent it is detected from the destination instruction files in priority order: `AGENTS.md`/`agents.md`, then `CLAUDE.md`/`claude.md`, then `instructions.md`; the detected spelling is preserved. When present, it must follow the same canonical safe relative POSIX and NUL-free path rules as `source` and `destinations`; malformed values are rejected before filesystem operations. When the resolved root file is missing, the blocker is skipped silently.

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

### Retiring a cleared root

Removing a cleared directory root from `distribution-clearance.json` is a compatible registry change, not a schema bump: `schema` stays `1`. A destination still bound to the retired `agents/` root must preserve the persona text it authored in its `project` region before removing its own profile files and the stale binding entries. That reconciliation is destination-owned, and the tool never performs it.

## Reconciliation blocker

While region-mode paths remain in `pending`, `check`, `apply`, and `init` ensure the destination root runtime file carries a marker-delimited blocker block:

```markdown
<!-- core:reconcile:begin -->
> **⚠️ ACTION REQUIRED — core reconciliation. This project is not current until this is done.**
> …
<!-- core:reconcile:end -->
```

The block is self-contained; the destination assistant needs no other context. It directs the destination to adopt the two-region rule permanently in its root instructions (`CLAUDE.md` / `AGENTS.md`) if absent. It explains that the upstream-owned `core` region is never edited, moved, or deleted, while the destination-owned `project` region keeps genuine project-specific content and may contain the old core copy that is now superseded. It also carries destination-facing config guidance covering the OpenCode V1-to-V2 migration, core-wins for same-named MCP server entries, and the QMD index, which the merge already sets from the destination's folder name so no manual edit is needed, with any different index declared in the project's own `.opencode/opencode.jsonc` before retrieval is verified. An empty result under this project's own index name may mean this project has never built that index, so populate it with the project's own retrieval tooling before treating the empty result as a synchronization defect. Conditional legacy incident-knowledge guidance preserves diagnostic evidence, skill references and genuine organization mappings, requiring live-consumer updates and replacement verification before separately authorized retirement without expanding the operator boundary. The shipped block, not this description, is the operative text.

For each path in `pending:`:
1. Open the file.
2. If `.aicore/reconciliation/init.yaml` exists, read its core revision and source/destination/action metadata; it does not contain displaced file content.
3. Inspect the old project-region text in the destination file, remove only duplicated/contradicted core copies, and keep genuine project-specific content. Never touch the core region or markers.
4. Delete that file's entry from `pending:` in `.aicore/core.yaml`.

When `pending:` is empty, delete the entire blocker block (markers included). The block is appended after one blank line when absent and replaced in place on later runs. Once `pending` is empty, `check` removes it. All other root content is preserved.

## Exit contract

Argument-parser/CLI validation errors (including invalid `--source-revision` syntax) exit `2` before a command starts. The table covers successfully parsed commands.

| Exit | `check` | `apply` | `init` |
|---|---|---|---|
| `0` | every core region matches the pinned revision, every raw destination byte-matches its source, every merge destination carries each source top-level key with the source value (extra destination-only keys and, for an object `mcp.servers` on both sides, extra destination-only servers allowed), the `qmd` server's `--index` is the destination folder's name, and `pending` is empty; prints `current` | every region spliced or created / raw file copied / merge document written and the revision pinned; prints `applied`, or `applied; created: <path>[, <path>]` when it recreated absent targets | every markerless destination enrolled, absent region, raw, or newly bound merge target created, raw file copied, merge document written, or marked destination refreshed and the revision pinned; prints `initialized` |
| `1` | drift: stale `core_revision`, missing/unreadable source, missing destination, raw/region/merge mismatch (including a `qmd` `--index` other than the destination folder's name), `frontmatter drift` (a region destination frontmatter a write would change), non-empty region `pending`, stale non-region-bound `pending`, a bound source absent from `distribution-clearance.json` or that file itself missing, or write-time filesystem I/O error | drift: missing/unreadable source, a merge destination that does not exist, a bound source absent from `distribution-clearance.json` or that file itself missing, or write-time filesystem I/O error | drift: missing/unreadable source, a merge destination that does not exist and this enrollment did not newly bind, a bound source absent from `distribution-clearance.json` or that file itself missing, or write-time filesystem I/O error |
| `2` | malformed bindings/source markers, a source carrying project markers without a valid core pair, `distribution-clearance.json` present but malformed, malformed JSONC in a merge source/destination, invalid or unreadable region-destination markers, overlapping roots, unsafe root targets (including source-inode aliases), or root/non-region alias | malformed bindings/source markers, a source carrying project markers without a valid core pair, `distribution-clearance.json` present but malformed, malformed JSONC in a merge source/destination, invalid or unreadable region-destination markers, unsafe write targets (including source-inode aliases and duplicate resolved output paths), root/non-region alias, or failed outside-marker preservation (nothing is written) | malformed bindings/source markers, a source carrying project markers without a valid core pair, `distribution-clearance.json` present but malformed, malformed JSONC in a merge source/destination, invalid region-destination markers, unsafe write targets (including source-inode aliases and duplicate resolved output paths), root/non-region alias, or a planned raw target that would become the implicit root |

`check` reports an absent bound destination as drift and creates nothing; `apply` and `init` repair a declared region or raw target by creating it, while merge is created only by the first enrollment that newly binds it, and drift otherwise.

`apply` and `init` append `frontmatter not refreshed: <path> (<reason>)` to their success message when a region destination's frontmatter could not be refreshed, and still exit `0`: that frontmatter keeps its current text, so the rest of the write stands. The reason distinguishes a whole-document skip, where nothing refreshed, from an unmappable `metadata` block, which keeps its bytes while every other source-defined key still refreshes. `check` reports neither as drift — only a frontmatter a refresh would change.

All commands validate bindings and preflight resolved write targets (including symlinks) before mutation; *Troubleshooting* owns the rejected shapes. `init` additionally calculates default-root selection after planned raw creation and rejects a raw target that would become `AGENTS.md`, the implicit root, before writes. `check` validates region sources before blocker sync and can still fail afterwards; the exit table above owns the classes. `apply`/`init` sync the blocker only after their payload, report, and bindings writes succeed. Earlier binding, path-preflight, marker, or source-validation errors may return without blocker synchronization. A missing or unreadable root file is skipped silently and does not change the result. Write-time filesystem errors return exit `1` with a concise diagnostic; multiple-output operations are not transactional, so an I/O error may follow earlier successful writes and requires a subsequent `check`. If a path changes from region to a non-region mode (raw or merge) while listed in `pending`, `apply`/`init` remove that stale entry; `check` excludes it from the blocker, returns drift with an instruction to run `apply` or `init`, and leaves bindings unchanged.

The clearance gate runs before any bound-source payload read or destination mutation in `check`, `apply`, and `init`, after the required bindings/clearance metadata reads and write-target preflight; an uncleared source never produces a payload, report, bindings, or blocker write.

## Examples

To enroll a complete applicable cleared set at one revision, use bulk enrollment from the source checkout against a
clean, saved destination. Inspect the selected revision's clearance first; a path is
not deliverable merely because it exists in the source tree. The command below
requires the source's other applicable preconditions too, and an empty destination becomes
the seeded project:

```bash
uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init \
  --source . --destination ../destination \
  --bindings ../destination/.aicore/core.yaml --source-revision "$(git rev-parse HEAD)" \
  --bind-cleared --root AGENTS.md
```

A declared region target may be absent: `apply` and `init` recreate it as a fresh
creation (source frontmatter, source core, empty project region), and `init` also records
pending reconciliation for a newly enrolled one. A markerless destination that already
exists still needs `init`, which retains its previous body in the project region.
Already marked region destinations refresh their core and their source-defined frontmatter while preserving the rest of their outside content.

Per-file `region` clearance is not raw whole-file transport or a directory-root copy.
Source-local project content does not ship.

## Troubleshooting

- **Raw byte drift (`check` exits 1):** the destination file differs from its source. Run `apply` or `init` with the intended source revision, then run `check` again.
- **Merge drift (`check` exits 1):** a source top-level key is missing from the destination or its value differs — for `mcp` with object `mcp.servers` on both sides, a missing core server or a differing server value is drift, while extra destination-only servers are not, and the `qmd` `--index` is expected to be the destination folder's name, so a stale index or renamed folder is drift until the next write. Run `apply` or `init` with the intended source revision, then run `check` again.
- **Merge destination missing (exit 1):** only a first `init --bind-cleared` creates a merge target, and only when the target it newly binds is absent; `check`, `apply`, and every later `init` report a missing one as drift. Re-run that enrollment, or create the destination object file yourself, then re-run.
- **Malformed JSONC (`check`/`apply`/`init` exits 2):** a merge source or destination is not a single JSON/JSONC object — a non-object top level, or malformed syntax such as an unterminated comment or a duplicate key. Merge is object-only; correct the document.
- **Raw destination missing (exit 1):** `check` reports it and never repairs it. `apply` and `init` write a declared raw target byte-exact, creating the target and any missing parent directories whether the mapping was stored or newly declared; an absent path no binding declares is not created. Run `check` again after the repair.
- **New region mapping missing:** `apply` and `init` recreate a declared region target (see *Examples*). A markerless destination still needs `init`. Inspect all applicable-set preconditions before running it.
- **Frontmatter drift (`check` exits 1) or `frontmatter not refreshed` (an `apply`/`init` message):** a region destination's leading YAML frontmatter does not say what a write would emit. Run `apply` or `init`, then `check` again; destination-only keys, `local-version` included, keep their exact bytes, so nothing local resets. When a reason is reported, that frontmatter kept its text: correct the destination YAML or key layout the reason names, then re-run.
- **Legacy raw hint or duplicate shared text:** cause: prior whole-file transport or displaced markerless content. If a binding persists an explicit `mode: raw` hint, it conflicts with region clearance and fails closed with exit `2`. Only if present, remove that obsolete hint through separately authorized destination bindings maintenance, retaining source/destination mappings and pending state, before enrollment; source clearance owns the actual mode. Normal saves omit mode hints; a conflicting hint cannot be removed by a synchronization that already fails preflight. Never bypass the gate or assume every adopter has this hint. Remove displaced duplicate shared text only from project, retaining genuine local evidence and history. Never edit protected core. Fresh region creation does not copy source project sections or seed local records. Clear pending through the existing blocker procedure and require `check` exit `0`. These steps document existing operations, not authority to mutate an adopter or change core locally.
- **Stale non-region-bound pending path (`check` exits 1):** the binding changed from region to raw or merge while the destination was listed in `pending`. Run `apply` or `init` to remove the obsolete reconciliation entry; `check` does not mutate the bindings file.
- **Conflicting binding declaration (`init` exits 2):** the requested destination path is already mapped to a different source. This is a bindings-metadata conflict, not a destination-content conflict; same mappings are idempotent, region content is reconciled through the `project` region/blocker, raw content is replaced by its selected whole-file source, and merge content is re-derived by top-level key (with the `mcp` key merged by server name).
- **Source not cleared for distribution (exit 1):** the bound `source` is not covered by `distribution-clearance.json`. Check the selected revision's clearance: a directory-root row covers files recursively, subject to its mode, overrides, and cache exclusions; a raw root such as `architecture/` delivers covered files byte-for-byte. Clear a root only when every current and future file under it is intended for distribution, after its applicable test or review passes; otherwise run the individual file's test or review and add a per-file row. The registry is the clearance record, not a content manifest. If the missing coverage is a retired directory root, follow *Retiring a cleared root*. After clearance, enroll new paths with `init --bind-cleared`; `apply` alone does not enroll them. Review applicable destination preconditions first and require `check` exit `0` after enrollment and reconciliation.
- **Source project markers without a core pair (exit 2):** add the ordered `<!-- core:begin -->` … `<!-- core:end -->` pair, or remove the stray project markers from a genuinely markerless source.
- **Malformed source/destination markers (`exit 2`):** genuinely markerless region sources have no exact core or project marker lines outside fences; *Marker contract* above owns the pair requirements. Correct the markers or use a genuinely markerless source.
- **Unsafe or aliased write target (`exit 2`):** source/destination roots overlap; a root or payload target escapes the destination; a write target resolves inside the source or shares an inode with a source-tree file (including a hard link); distinct output paths resolve to one target; the root aliases a non-region (raw or merge) destination; or a new raw target would become the implicit root after `init`. The operator must replace a link with a regular file and re-run `check`; the command fails before writing. Bindings/report paths may be outside the destination if they remain outside the source.

## Roadmap

The destination `project`-region workflow is destination-owned: the core tool never reconciles the `project` region. For region bindings it writes core-region bytes; for raw bindings it writes the whole source file byte-for-byte; for merge bindings it merges the source's top-level object keys into the destination; it also updates binding revision/pending state, region reconciliation reports, and the root blocker. Planned scale-up work will link each `pending` entry to its reconciliation report (today `pending` is a flat list of paths).
