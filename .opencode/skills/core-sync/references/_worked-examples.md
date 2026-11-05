# core-sync worked examples

Companion to `.opencode/skills/core-sync/SKILL.md`: the rules live there, and this file only
shows them applied.

## Enrolling a cleared set

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
Already marked region destinations refresh their core and frontmatter; their other outside content is preserved, with line endings normalized to LF as for every text write.

## Per-file region clearance

Per-file `region` clearance is not raw whole-file transport or a directory-root copy.
Source-local project content does not ship. A raw-cleared reference may contain fenced
marker literals: those bytes are ordinary template or example content, not active regions
governing that raw file. Raw mode does not parse or strip those literals.

## Raw and merge mappings

To mirror a raw-cleared whole-file reference, add its mapping with `--bind-raw` and run
`init`; an explicitly declared `--bind-raw` (or persisted raw) target still requires an
existing parent, so a missing parent remains drift. A raw target newly enrolled in bulk by
`--bind-cleared`, however, creates its missing parent directories. A `merge`-cleared source
(such as `opencode.jsonc`) needs no dedicated flag and requires an existing destination.
Modes and revision rules are unchanged.
