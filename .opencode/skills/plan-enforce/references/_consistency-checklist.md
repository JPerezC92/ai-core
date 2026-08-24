# Plan / Phase / Story — consistency checklist

> Canonical contract for artifacts written by the `plan-enforce` skill. Applied at write-time by the skill's post-write self-verification loop (analysis) and mechanically by `scripts/validate_plan.py` (repetitive subset). Sentinel 🛡️ (Quality Guardian) audits `plans/` and `user-stories/` against this same checklist — keep the two in lockstep.

## plan.md

- `Status:` value is `active` or `completed` (no other values).
- When `Status: completed`, a `Completed: YYYY-MM-DD HH:MM` line is present in the metadata header.
- Metadata header has `Started` and `Subject` (and `Layout` for subfolder plans).
- Required sections present: `## Context`, `## Goals`, `## Critical files / tools`, `## Verification`, `## Out of scope` (or `## Out of scope / Do-not-touch`), plus `## Body` (base template) or `## Current state` + `## Behavior change` (programming template).
- `## Goals` checkboxes present and match the confirmed goal list; programming goals each carry a `Done when:` criterion.
- No unfilled placeholders: `<task subject>`, a literal `YYYY-MM-DD HH:MM`, or stray `<!-- -->` comment lines (the `## Pending` section may retain its example comments).
- Every dispatch-table phase references an existing `phase-NN-<owner>.md` file.
- Every phase traces to ≥1 goal ID (programming plans: the `Goals` column is populated for every phase).
- Verification checkbox count equals the phase-output count; each verification checkbox traces to a phase output.

## phase-NN-<owner>.md

- `Owner`, `Pre`, `Reads`, `Writes` blockquote labels populated.
- No `TBD` in `Steps`, `Output`, `Gate`, or `Abort conditions`.
- `## Writes` paths match the derived write/delete manifest.
- No unfilled `<...>` placeholder tokens.

## user-stories

- `user-stories/index.md` exists and lists every feature file.
- Each story's `Title` and `Status` mirror the corresponding `index.md` columns.
- No unfilled `<...>`, `TODO`, or `TBD` placeholders.
- A dated `## Change log` entry is present for every plan that touched the story.

## Loop rule

Analysis items (everything above) are the skill's responsibility — a value must match evidence, never be invented to satisfy a check. `scripts/validate_plan.py` enforces only the mechanical/repetitive subset (enum values, section presence, placeholder/TBD detection, index mirroring); it is a helper, not the authority.
