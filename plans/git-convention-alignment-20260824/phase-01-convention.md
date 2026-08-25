# Phase 1 — Convention alignment

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** Approved goals G1-G4, empty stash inventory, and no active plan other than this plan.
> **Reads:** `.opencode/skills/git-branch-name/SKILL.md`, `.opencode/skills/git-commit/SKILL.md`, `.opencode/skills/git-pr/SKILL.md`, `.opencode/agents/herald.md`
> **Writes:** `.opencode/skills/git-branch-name/SKILL.md`, `.opencode/skills/git-commit/SKILL.md`, `.opencode/skills/git-pr/SKILL.md`, `.opencode/agents/herald.md`

## Steps

1. Replace git-branch-name's type table with the approved commitlint type set, remove `hotfix`, and define the single-token monorepo scope matrix with split-app and whole-app cases.
2. Update git-commit to use the same types and scope matrix, read the current branch, and derive title type/scope only when its pattern matches and the diff does not contradict it.
3. Update git-pr to use the same types and scope matrix, read the current branch, and report title-versus-branch type/scope mismatches while retaining the diff-derived title.
4. Replace Herald's `feat/<slug>` or `fix/<slug>` fallback with `type/scope/description`.
5. Rewrite Herald's visual-gate hard rule as an imperative without changing when it blocks release work.
6. Read the changed documents and search the four paths for forbidden `hotfix` types, the old Herald two-segment fallback, and non-imperative visual-gate wording.

## Output

- **Artifact:** `.opencode/skills/git-branch-name/SKILL.md`, `.opencode/skills/git-commit/SKILL.md`, `.opencode/skills/git-pr/SKILL.md`, and `.opencode/agents/herald.md`
- **Schema / shape:** Matching commitlint types, shared kebab-case scope grammar, branch-to-commit defaults, branch-to-PR checks, a three-segment Herald fallback, and an imperative visual-gate hard rule.

## Gate

- ☑ G1-G5 are satisfied in the four edited documents.
- ☑ Existing no-mutation boundaries of each git skill remain intact.

## Abort conditions

- Stop if a required convention conflicts with another runtime document not covered by the approved manifest.
- Stop if a branch convention would override diff evidence rather than merely supply a default or warning.
