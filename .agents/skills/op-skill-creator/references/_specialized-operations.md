# Specialized operations

## Rename and migration

- Before a rename/prefix or copy-based migration, preview every file to create, copy, move, edit or delete. Obtain explicit approval of the target, helper transfers, discovered-reference updates, and whether to preserve output/script paths or retarget them. Resolve target collisions rather than overwriting an unrelated skill.
- Offer source cleanup separately: delete, move to `_deprecated/`, or keep the old source as-is. Delete/archive requires explicit prior confirmation; declined cleanup leaves the source intact and does not prevent an otherwise approved copy. Neither the operation nor target approval implies cleanup approval.
- Copy required helpers and update target references for approved paths. Search project inventories, `odd/tasks/` feature records, knowledge files, agent specs, and existing legacy plan or story surfaces for the old name or path; update approved matches, preserving intentional source references when keeping the source. Record an empty result instead of skipping the search.
- Re-read the target, verify required helpers and all target references, and re-read each edited reference before any approved source cleanup. Helpers may move only as part of explicitly confirmed cleanup after target verification; keep-source leaves the original skill and support tree intact.

## Optional Markdown text integrity

Optional only — not a pre-write check, completion gate, or mandatory every-task scan. Distinct from skill metadata, feature anatomy, and fenced-language validation.

- Read the project's Markdown text-integrity policy when present; absence is not a blocker and not a default path. The caller supplies `--policy PATH`; no source-root policy or destination synchronization is implied.
- Read `scripts/check_markdown_text.ts` explicitly; it is not loaded automatically.
- CLI: `node .agents/skills/op-skill-creator/scripts/check_markdown_text.ts --policy PATH [--check-editor PATH] PATH [PATH ...]`. It runs natively on Node.js `>=24.12.0` from the skill's own TypeScript source, with no build step or runtime dependency; a destination runs it as it stands with nothing installed.
- Required: `--policy PATH` and one or more explicit Markdown file or directory paths. Optional: `--check-editor PATH`. No implicit repository-root scan.
- Read-only: no formatting, Git, network, or runtime dependency installation.
- Exit 0: no errors (warnings may exist; they are not file defects). Exit 1: content errors or editor-projection drift. Exit 2: policy, input, or IO failure.
- No ASCII-only mode. En dashes, emoji, joiners, and ordinary Unicode prose are not errors merely because they are non-ASCII. Editor highlighting is not the checker's complete semantics.
