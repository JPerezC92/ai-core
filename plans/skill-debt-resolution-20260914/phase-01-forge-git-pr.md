# Phase 1 — Correct git-pr

> **Owner:** Forge 🔨 (Implementer)
> **Pre:** User explicitly authorizes Plan 2 execution; stash gate passes for this phase's exact writes; Plan 1 changes remain untouched.
> **Reads:** `.opencode/skills/git-pr/SKILL.md`; `knowledge/debt.md` DEBT-001/002; `user-stories/git-pr-drafting.md`; `.opencode/agents/vault.md`
> **Writes:** `.opencode/skills/git-pr/SKILL.md`; `user-stories/git-pr-drafting.md`

## Steps

1. Bump `git-pr` metadata version from `1.3.0` to `1.3.1`.
2. Change step 3 plan discovery to search both `plans/*.md` and `plans/*/plan.md`; preserve ticket lookup and Context-reading behavior.
3. Correct every non-possessive bare `Herald 📯` occurrence to `Herald 📯 (Release Manager)`; leave possessives bare and preserve all other roster mentions.
4. Preserve git-pr's read-only drafting boundary, branch/diff authority, unchecked test-plan contract, immutable-head evidence contract, output path, and no-PR-mutation rules.
5. Keep the story criteria pending until the real draft run in Phase 6 establishes Context use.
6. Run the declared verify commands and return exact output plus a path-scoped diff summary.

## Output

- **Artifact:** `.opencode/skills/git-pr/SKILL.md`; `user-stories/git-pr-drafting.md`
- **Schema / shape:** Skill `1.3.1`; dual plan-pattern discovery; zero malformed non-possessive Herald mentions; pending criteria remain `⬜`.

## Verify commands

| Executor | Command |
|---|---|
| Forge 🔨 (Implementer) | `grep -n 'plans/\*/plan.md' .opencode/skills/git-pr/SKILL.md` |
| Forge 🔨 (Implementer) | `grep -n 'plans/\*.md' .opencode/skills/git-pr/SKILL.md` |
| Forge 🔨 (Implementer) | `grep -n 'version: 1.3.1' .opencode/skills/git-pr/SKILL.md` |
| Cipher 🔓 (Lead Orchestrator) | `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/skill-debt-resolution-20260914 --stories user-stories` |

## Gate

- ⬜ Both plan layouts are explicit and no existing git-pr authority or evidence rule changes.
- ⬜ Every non-possessive Herald mention conforms; DEBT-001/002 remain open pending later evidence.

## Abort conditions

- Halt if implementation requires executable code, dependency changes, or a new output artifact beyond `pr-draft.md` in Phase 6.
- Halt if any correction changes who may create, edit, or merge a PR.
