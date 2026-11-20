# Simplify Git workflow and retire the cleanup validator

AICore's Git and GitHub workflow, reduced to a small set of agent instructions, native Git and GitHub CLI commands, and one agent that owns every Git and GitHub operation.

**Status:** achieved

## Requirements

- [x] R1 — the custom merged-branch cleanup validator and every binding to it are removed from the repository.
- [x] R2 — merged-branch cleanup is decided from verified PR identity and native Git evidence, with no replacement validator, framework or script.
- [x] R3 — the merge proof is the PR's recorded merge commit being reachable from the verified base; file-content parity never substitutes for it.
- [x] R4 — squash and rebase merges are handled explicitly, and the deletion method is chosen before any deletion attempt.
- [x] R5 — Herald 📯 (Release Manager) is the sole executor of Git and GitHub operations in the OpenCode configuration; every other agent delegates them and analyzes the evidence Herald 📯 (Release Manager) supplies.
- [x] R6 — Herald 📯 (Release Manager) evaluates every Git and GitHub request independently and may refuse an incorrect, unsafe or unauthorized operation, including one instructed by Cipher 🔓 (Lead Orchestrator).
- [x] R7 — the designated evidence writer keeps review-evidence ownership and content validation; Herald 📯 (Release Manager) executes only the single publication write, against the exact validated body.
- [x] R8 — the OpenCode command permissions keep every existing dangerous-operation safeguard and close `git` and `gh` to every agent except Herald 📯 (Release Manager); a variant the permission layer cannot block is documented rather than patched.
- [x] R9 — PR-body verification keeps the attribution checks and the exact persisted-body check when the publication input changes.
- [x] R10 — the distribution registry and its definition no longer clear the retired skill, and historical records are unchanged.
- [x] R11 — branch creation uses an explicitly verified base rather than inheriting the current checkout.
- [x] R12 — `git-pr` owns PR content only — title and body generation, formatting, and content-specific validation — while the publication, evidence, identity and persistence procedure lives in `git-pr-workflow`.
- [x] R13 — the two skills' utilities are independently distributable, with no cross-skill runtime import and no duplicated schema.
- [x] R14 — the persisted-body verification is not weakened: the persisted capture must match the intended publication exactly, including its field set.
- [x] R15 — the publication input has one authoritative validation point before each creation or review update, and invalid input cannot reach publication.
- [x] R16 — a pull-request merge is never an agent operation: only the user merges, by any mechanism, even under an explicit user instruction, and Herald 📯 (Release Manager)'s executor authority explicitly excludes it.
