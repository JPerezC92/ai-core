# Phase 3 — pilot the two types on tismart-support

> **Owner:** Forge 🔨 (Implementer)
> **Goal:** G3
> **Pre:** Phases 1–2 complete; independent audit `[PASS]`; AICore source is committed at the exact revision supplied to the script; destination `/home/dexm76/projects-personal-tismart/tismart-support` is clean and on `main`; `.aicore/core.yaml` has `pending: []`. If prior `pending` entries exist, stop before binding changes and have the destination resolve them first.
> **Reads:** `plans/core-sync-filetypes-20261006/plan.md`; `.opencode/skills/core-sync/SKILL.md`; the AICore `AGENTS.md` and `opencode.jsonc`; the destination `.aicore/core.yaml`, `opencode.jsonc`, `CLAUDE.md`.
> **Writes:** `/home/dexm76/projects-personal-tismart/tismart-support/.aicore/core.yaml`; `/home/dexm76/projects-personal-tismart/tismart-support/opencode.jsonc`; `/home/dexm76/projects-personal-tismart/tismart-support/CLAUDE.md`; `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/agents/lumen.md`; `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/skills/git-branch-name/SKILL.md`; `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/skills/git-commit/SKILL.md`; `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/skills/git-pr/SKILL.md`; `/home/dexm76/projects-personal-tismart/tismart-support/.aicore/reconciliation/init.yaml`; `user-stories/aicore-adoption-sync.md`

## Steps

1. Read the destination `.aicore/core.yaml` and verify `pending: []` before any binding change; inspect the existing `.opencode/agents/lumen.md` binding, `opencode.jsonc`, and `CLAUDE.md`; read AICore `AGENTS.md` and `opencode.jsonc`.
2. Do not hand-edit Tismart bindings or synchronized files. Keep the existing `.opencode/agents/lumen.md` entry and `root: CLAUDE.md`; pass the new mappings as `--bind AGENTS.md=CLAUDE.md` and `--bind-raw opencode.jsonc=opencode.jsonc` to `init`.
3. Run `core-sync init` from the AICore root using the verified committed source revision and both binding flags. Expect exit 0 (`initialized`): the script adds the new entries to `.aicore/core.yaml`, raw-copies the destination `opencode.jsonc`, refreshes changed existing Lumen and git-skill bindings in their configured modes, initializes the `CLAUDE.md` core/project regions, records region paths in `pending`, and writes the reconciliation blocker to `CLAUDE.md`.
4. The destination project reconciles each region path listed in `pending` (including `CLAUDE.md` and any refreshed existing region file): adopt the permanent core-region rule, prune superseded content, keep genuine Tismart material, and clear `pending`; the script then removes the blocker on the next invocation.
5. Verify: `core-sync check` → `current`, exit 0; the destination `CLAUDE.md` core region is byte-identical to AICore's `AGENTS.md` core region, and the entire destination root file contains no AICore identity/reuse-guide text; the destination `opencode.jsonc` is byte-identical to AICore's.

## Output

- **Artifact:** bound + synchronized destination root and `opencode.jsonc`, plus refreshed existing bindings.
- **Schema / shape:** New `opencode.jsonc` binding = raw byte-copy; existing git-skill bindings remain raw and Lumen remains region mode; `CLAUDE.md` = core region (Mandatory core bytes) + destination project region.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B .opencode/skills/core-sync/scripts/core_sync.py check --source /home/dexm76/projects-personal/AICore --destination /home/dexm76/projects-personal-tismart/tismart-support --bindings /home/dexm76/projects-personal-tismart/tismart-support/.aicore/core.yaml --source-revision "$(git rev-parse HEAD)"` |
| Herald 📯 (Release Manager) | `git -C /home/dexm76/projects-personal-tismart/tismart-support status --porcelain` |

## Gate

- ⬜ `check` exit 0 (`current`).
- ⬜ Destination `CLAUDE.md` core region == AICore `AGENTS.md` core region; the entire destination root file contains no AICore identity/reuse-guide text.
- ⬜ Destination `opencode.jsonc` byte-identical to AICore's.
- ⬜ Full `git status` shows only the bindings file, the new raw `opencode.jsonc` copy, refreshes of the three already raw-bound git skills and region-bound Lumen file, initialized `CLAUDE.md`, and the init-generated reconciliation report — no other destination file touched.

## Abort conditions

- Raw replacement is user-approved; do not edit the destination file manually—only `core-sync` may copy it.
- Halt before binding changes or `init` if the destination's existing `.aicore/core.yaml` has any pending path; do not combine an earlier unresolved reconciliation with this enrollment.
- Halt if the destination core region would receive AICore-personal content (identity/reuse-guide).

## Tool whitelist / blacklist

- Whitelist: the listed bound destination files + running `core-sync init`/`check`.
- Blacklist: other destination files; the tool (phases 1–2); git mutations.
