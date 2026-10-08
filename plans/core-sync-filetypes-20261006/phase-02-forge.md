# Phase 2 — regionize AICore `AGENTS.md`

> **Owner:** Forge 🔨 (Implementer)
> **Goal:** G2
> **Pre:** Phase 1 complete; independent audit `[PASS]`.
> **Reads:** `plans/core-sync-filetypes-20261006/plan.md`; `AGENTS.md` (full); `.opencode/skills/core-sync/SKILL.md`.
> **Writes:** `AGENTS.md`; `user-stories/aicore-adoption-sync.md`

## Steps

1. Read `AGENTS.md` in full.
2. Remove the retired line `> **Rule layout:** two-section-v1`.
3. Insert `<!-- core:begin -->` immediately before the `## Mandatory core` heading, and `<!-- core:end -->` after the last line of that block (the file's hard rules at the end). The core region therefore wraps the reusable lead-orchestration contract (Identity & Role, Roster, Shared agent rules, Conventions, Hard Rules).
4. Place the core region FIRST (around the `## Mandatory core` block), then the project region (around the `## Project extensions` block) — the core region leads the file, matching the generated destination layout. The two section headings stay as plain content labels.
5. Fix the stale Hard Rule that references the retired "recorded collision notice": replace it with the region model equivalent, preserving the obligation — e.g. "Never accept a destination whose core-region bytes differ from the selected upstream revision; `core-sync check` exit 0 is that proof." Keep the adjacent Hard Rules byte-for-byte; do not weaken any `## Mandatory core` obligation.
6. Verify: exactly one `<!-- core:begin -->`, one `<!-- core:end -->`, one `<!-- project:begin -->`, one `<!-- project:end -->`; no `two-section-v1`; `## Mandatory core` obligations intact.

## Output

- **Artifact:** region-native `AGENTS.md`.
- **Schema / shape:** one core pair wrapping the Mandatory-core content + one project pair wrapping the Project-extensions content; source stays marker-bounded so only the core region is ever delivered.

## Verify commands

| Executor | Command |
|---|---|
| Sentinel 🛡️ (Quality Guardian) | `set -e; f=AGENTS.md; test "$(grep -cF -- "<!-- core:begin -->" "$f")" = 1; test "$(grep -cF -- "<!-- core:end -->" "$f")" = 1; test "$(grep -cF -- "<!-- project:begin -->" "$f")" = 1; test "$(grep -cF -- "<!-- project:end -->" "$f")" = 1; ! grep -qF "two-section-v1" "$f"` |

## Gate

- ✅ Marker loop exact command exits 0 (one core pair, one project pair; no `two-section-v1`).
- ✅ Sentinel 🛡️ (Quality Guardian) doc audit `[PASS]` — `## Mandatory core` unweakened; core region = reusable only; AICore identity/reuse-guide inside the project region.
- ✅ The `AGENTS.md` diff contains the region layout, stale Hard Rule correction, and user-requested subagent dispatch contract; no mandatory core obligation is weakened, and AICore-only project content remains outside the core markers.

## Abort conditions

- Halt if regionizing would move or alter a `## Mandatory core` obligation beyond the recorded-collision-notice rule correction.
- Halt if the marker check fails after one correction pass.

## Tool whitelist / blacklist

- Whitelist: edit `AGENTS.md`.
- Blacklist: the tool (phase 1), destination files (phase 3), other agents, git mutations.
