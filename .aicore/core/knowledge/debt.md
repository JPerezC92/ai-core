<!-- core:begin -->
# Accepted Debt Register

Records of deferred technical or process debt that are **non-blocking** for release.

## Entry format

Each entry MUST include:

- **ID** — unique identifier (e.g. `DEBT-001`)
- **Date** — when the deferral decision was made
- **Description** — what is deferred
- **Direct evidence** — the evidence that justifies deferral
- **Resolution criteria** — what must be true for the debt to be cleared
- **Explicit deferral decision** — who decided, and when

## Rules

- An accepted debt is nonblocking only when its record here carries direct evidence, resolution criteria, and an explicit deferral decision (see `.opencode/agents/herald.md` for the release-time disclosure duty).
- Disclose the ID and unresolved criteria in any operation report that touches it.
- Clear and retire a resolved debt in the same authorized, committed work unit: delete its entry from this register and preserve complete resolution evidence in the governing feature record and its Log, backed by delivery evidence. Identify the debt, evidence that every resolution criterion is met, validation results, independent review results, and the delivering commit; the commit must carry the resolution evidence or its durable governing-record reference. If a PR exists, its body must also carry that evidence or reference; a PR is not required for retirement. Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one authorized, committed resolution work unit.
- **User-directed cancellation.** An explicit user decision may cancel an open debt without satisfying its resolution criteria. Cancellation is not resolution or clearance. Before removing the entry, preserve the user decision, unmet criteria, and supporting evidence in the governing feature record; include the cancellation and its evidence in the authorized delivery. This route does not waive the resolution-evidence requirements for resolved debts.
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.
- **Every deferred work item is registered here.** A deferral recorded only in a feature `## Log`, a task record, a review summary, or a final report does not satisfy this register: work that is deferred carries an entry with the fields above, linked to the finding, task or feature that produced it, stating why it was deferred, its impact, and the condition for resolution. Group related items under one entry rather than filing duplicates, and search the register before adding one. Creating or holding an entry is never evidence that the underlying issue is fixed, and it never satisfies an unmet requirement whose criterion the deferred work covers.

## Register

<!-- core:end -->

<!-- project:begin -->
## DEBT-054 — Unbalanced Markdown fences in ODD records are not detected by format:check or validate_feature

- **Date:** 2026-11-17
- **Description:** An ODD feature record can contain a Markdown code fence that never closes, so later `## Log` entries are parsed as fenced code rather than as structure. `pnpm format:check` (Biome) and `node .agents/skills/odd-workflow/scripts/validate_feature.ts` both still succeed, because neither balances fences. The malformed document in this adoption was corrected; the **detection gap** remains. **Impact:** a record can pass mechanical validation while its Log history is trapped inside a code block, so later reviewers and agents read a false structure. The same class of defect can recur on any later Log that quotes a fence.
- **Direct evidence:** during the lint-and-format adoption delivered in PR #192 (squash commit `c85fbc7`), an ODD record's Log opened a four-backtick fence whose intended closer carried three backticks plus another character on the same line, which is not a fence closer. Biome inserted a closer at end of file and the entries that followed were swallowed into the code block. `pnpm format:check` and `validate_feature.ts` both exited 0 on that tree: neither balances fences. The malformed record was corrected in the same pull request by repairing the fence pair, and a repository-wide sweep then reported 132 Markdown files, 56 fences, 0 unbalanced. The validator still has no fence-balance rule, so reproducing the pre-fix shape would still pass anatomy validation; this entry is the canonical home of that reproduction.
- **Resolution criteria:** A mechanical check that counts opening and closing fences on an ODD record (or an equivalent structural rule in the existing feature validator) fails closed on a fixture matching the pre-`3dd918c` shape, and `validate_feature.ts` or that named companion exits non-zero. The two existing validators' other contracts stay unchanged. This entry does not require a new Markdown framework, skill, or formatter.
- **Explicit deferral decision:** User instruction on 2026-11-17, verbatim: "Do not build a new Markdown validation framework or expand the tooling implementation merely to resolve this issue now." and "Recording them as debt does not satisfy or close the underlying issue." Deferred, not waived.
- **State as of 2026-11-20:** The documented malformed case reproduced in the existing skill suite (1 failed, 93 passed). A proposed scanner was withdrawn after independent review found it mishandled list and blockquote containers and HTML comments. No dependency-free runtime parser was identified in the bounded skill and lockfile search; this is not a repository-wide absence claim. The defect and the original resolution criteria remain open; no corrected implementation or passing regression is claimed.

## DEBT-065 — Fenced Close entries affect feature-record validation

- **Date:** 2026-11-11
- **Description:** F8 defers the feature validator's use of the raw Log for Close-entry detection while Log-identifier checks use fence-stripped text. A Close entry inside a balanced code fence can satisfy the closed-record Close presence check or trigger the active-record Close diagnostic. Status, task and other evidence checks remain independent. **Impact:** quoted content can be mistaken for a real Close entry; the Close presence check alone does not establish valid closure.
- **Direct evidence:** In `.agents/skills/odd-workflow/scripts/feature_validation/domain/rules.ts`, the Log is extracted from raw lines by `section(lines, "## Log")` at line 420 and the Close-presence check `hasCloseEntry` reads that raw slice at line 470, while the identifier checks read `unfencedLog`, built from fence-stripped text at lines 530–531 and iterated from line 554, with the ASCII-digit finding raised at line 559. A balanced fenced Close can therefore satisfy the closed-record presence check or trigger the active-record diagnostic; status, task and other evidence checks still apply independently. DEBT-054 concerns detection of unbalanced fences and is distinct. Historical provenance supplied by Herald: PR #176, reviewed head `4446a77987a2ded3f94a04d7e10daf5407e659b3`, merge `8bfee9cfc95dee95e2800f1e16b7ca52e12c80de`.
- **Resolution criteria:** Close-entry detection ignores entries inside balanced fenced blocks, while preserving the validator's other existing contracts. Verify ordinary Close entries and Close-shaped text inside balanced fences for both closed and active records, including the corresponding presence and diagnostic outcomes.
- **Explicit deferral decision:** The user deferred F8 on 2026-11-11, originally naming the feature record as the destination. The user subsequently authorized this narrowly scoped debt-register entry; the underlying fix remains deferred, not waived.

**ID to use for the next new debt:** `DEBT-066`. This is an allocation counter, not an open debt.
<!-- project:end -->
