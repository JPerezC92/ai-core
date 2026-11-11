# Simplify Git workflow and retire the cleanup validator

AICore's Git and GitHub workflow, reduced to a small set of agent instructions, native Git and GitHub CLI commands, and one agent that owns every Git and GitHub operation.

**Status:** achieved

## Requirements

- [x] R1 — the custom merged-branch cleanup validator and every binding to it are removed from the repository. — delivered: this change
- [x] R2 — merged-branch cleanup is decided from verified PR identity and native Git evidence, with no replacement validator, framework or script. — delivered: this change
- [x] R3 — the merge proof is the PR's recorded merge commit being reachable from the verified base; file-content parity never substitutes for it. — delivered: this change
- [x] R4 — squash and rebase merges are handled explicitly, and the deletion method is chosen before any deletion attempt. — delivered: this change
- [x] R5 — Herald 📯 (Release Manager) is the sole executor of Git and GitHub operations in the OpenCode configuration; every other agent delegates them and analyzes the evidence Herald 📯 (Release Manager) supplies. — delivered: this change
- [x] R6 — Herald 📯 (Release Manager) evaluates every Git and GitHub request independently and may refuse an incorrect, unsafe or unauthorized operation, including one instructed by Cipher 🔓 (Lead Orchestrator). — delivered: this change
- [x] R7 — the designated evidence writer keeps review-evidence ownership and content validation; Herald 📯 (Release Manager) executes only the single publication write, against the exact validated body. — delivered: this change
- [x] R8 — the OpenCode command permissions keep every existing dangerous-operation safeguard and close `git` and `gh` to every agent except Herald 📯 (Release Manager); a variant the permission layer cannot block is documented rather than patched. — delivered: this change
- [x] R9 — the PR-body verification machinery and its contracts are unchanged and its tests remain collected and passing. — delivered: this change
- [x] R10 — the distribution registry and its definition no longer clear the retired skill, and historical records are unchanged. — delivered: this change
- [x] R11 — branch creation uses an explicitly verified base rather than inheriting the current checkout. — delivered: this change
- [x] R12 — `git-pr` owns PR content only — title and body generation, formatting, and content-specific validation — while the publication, evidence, identity and persistence procedure lives in `git-pr-workflow`. — delivered: this change
- [x] R13 — the two skills' Python packages are self-contained: no cross-skill import, no duplicated schema, and the seven-field capture schema declared exactly once. — delivered: this change
- [x] R14 — the persisted-body verification is not weakened: the persisted capture must match the intended publication exactly, including its field set. — delivered: this change
- [x] R15 — every command keeps its name, arguments and exit-code contract, and the malformed-draft rejection has one authoritative point that every workflow path depends on. — delivered: this change
- [x] R16 — a pull-request merge is never an agent operation: only the user merges, by any mechanism, even under an explicit user instruction, and Herald 📯 (Release Manager)'s executor authority explicitly excludes it. — delivered: this change
