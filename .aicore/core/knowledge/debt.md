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

- An accepted debt is nonblocking only when its record here carries direct evidence, resolution criteria, and an explicit deferral decision (see Herald 📯 (Release Manager) spec).
- Disclose the ID and unresolved criteria in any operation report that touches it.
- Clear and retire a resolved debt in the same authorized, committed work unit: delete its entry from this register and preserve complete resolution evidence in the governing feature record and its Log, backed by delivery evidence. Identify the debt, evidence that every resolution criterion is met, validation results, independent review results, and the delivering commit; the commit must carry the resolution evidence or its durable governing-record reference. If a PR exists, its body must also carry that evidence or reference; a PR is not required for retirement. Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one authorized, committed resolution work unit.
- **User-directed cancellation.** An explicit user decision may cancel an open debt without satisfying its resolution criteria. Cancellation is not resolution or clearance. Before removing the entry, preserve the user decision, unmet criteria, and supporting evidence in the governing feature record; include the cancellation and its evidence in the authorized delivery. This route does not waive the resolution-evidence requirements for resolved debts.
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.
- **Every deferred work item is registered here.** A deferral recorded only in a feature `## Log`, a task record, a review summary, or a final report does not satisfy this register: work that is deferred carries an entry with the fields above, linked to the finding, task or feature that produced it, stating why it was deferred, its impact, and the condition for resolution. Group related items under one entry rather than filing duplicates, and search the register before adding one. Creating or holding an entry is never evidence that the underlying issue is fixed, and it never satisfies an unmet requirement whose criterion the deferred work covers.

## Register

<!-- core:end -->

<!-- project:begin -->
## DEBT-052 — Biome 2.6.8 does not converge on quoted blockquotes, so two ODD records stay excluded

- **Date:** 2026-11-16
- **Description:** Biome's Markdown formatter reaches no fixed point on documents that contain an indented blockquote with empty quote-mark-only lines. Each `--write` pass adds two more spaces of indentation to those lines instead of settling, so the file keeps mutating and `format:check` can never pass. Two historical ODD records that quote a request verbatim are therefore excluded from the formatter by exact path. **Impact:** the exclusion is a safeguard, not a solution. Any future record that quotes a request inside a list item can hit the same defect, which would grow the per-file exclusion list, and the two affected records stay outside formatting indefinitely.
- **Direct evidence:** three consecutive `biome format --write` passes, applied to copies of the affected documents in an isolated directory configured with this repository's own `.editorconfig` and `biome.json`, produced a different SHA-256 after every pass, and `biome format` still exited 1 after the third write; the blank-line indentation inside a verbatim quoted blockquote grew by two spaces per pass instead of stabilizing. The defect was found during the lint-and-format adoption delivered in PR #192 (squash commit `c85fbc7`), which introduced the per-file exclusions as a safeguard. The current `biome.json` `files.includes` exclusions are configuration state, not the home of this evidence: this entry is now the canonical home of the measurement and its provenance, and the detection, restore-to-HEAD and revalidation that produced it were delivered in that same pull request.
- **Resolution criteria:** one of two outcomes clears it — a Biome release formats a verbatim quoted blockquote containing empty quote-mark-only lines to a stable result so that `format:check` converges, or a documented configuration or scope decision keeps verbatim quoted content unformatted without a per-file exclusion list. In either case every surviving exclusion is then removed and `pnpm format:check` passes over the whole tree with no `files.includes` exception. Retirement requires that evidence. No workaround, content rewrite, or forced formatting is attempted to close this entry, because the quoted request text must remain verbatim.
- **Explicit deferral decision:** User instruction on 2026-11-16, verbatim: "Revisa que las excepciones de Biome sean realmente necesarias, especialmente los dos documentos ODD excluidos por el problema de idempotencia." and "No fuerces su formateo si existe riesgo de corrupción." Deferred, not waived: the exclusion protects verbatim quoted content from corruption.

## DEBT-054 — Unbalanced Markdown fences in ODD records are not detected by format:check or validate_feature

- **Date:** 2026-11-17
- **Description:** An ODD feature record can contain a Markdown code fence that never closes, so later `## Log` entries are parsed as fenced code rather than as structure. `pnpm format:check` (Biome) and `node .agents/skills/odd-workflow/scripts/validate_feature.ts` both still succeed, because neither balances fences. The malformed document in this adoption was corrected; the **detection gap** remains. **Impact:** a record can pass mechanical validation while its Log history is trapped inside a code block, so later reviewers and agents read a false structure. The same class of defect can recur on any later Log that quotes a fence.
- **Direct evidence:** during the lint-and-format adoption delivered in PR #192 (squash commit `c85fbc7`), an ODD record's Log opened a four-backtick fence whose intended closer carried three backticks plus another character on the same line, which is not a fence closer. Biome inserted a closer at end of file and the entries that followed were swallowed into the code block. `pnpm format:check` and `validate_feature.ts` both exited 0 on that tree: neither balances fences. The malformed record was corrected in the same pull request by repairing the fence pair, and a repository-wide sweep then reported 132 Markdown files, 56 fences, 0 unbalanced. The validator still has no fence-balance rule, so reproducing the pre-fix shape would still pass anatomy validation; this entry is the canonical home of that reproduction.
- **Resolution criteria:** A mechanical check that counts opening and closing fences on an ODD record (or an equivalent structural rule in the existing feature validator) fails closed on a fixture matching the pre-`3dd918c` shape, and `validate_feature.ts` or that named companion exits non-zero. The two existing validators' other contracts stay unchanged. This entry does not require a new Markdown framework, skill, or formatter.
- **Explicit deferral decision:** User instruction on 2026-11-17, verbatim: "Do not build a new Markdown validation framework or expand the tooling implementation merely to resolve this issue now." and "Recording them as debt does not satisfy or close the underlying issue." Deferred, not waived.
- **State as of 2026-11-20:** The documented malformed case reproduced in the existing skill suite (1 failed, 93 passed). A proposed scanner was withdrawn after independent review found it mishandled list and blockquote containers and HTML comments. No dependency-free runtime parser was identified in the bounded skill and lockfile search; this is not a repository-wide absence claim. The defect and the original resolution criteria remain open; no corrected implementation or passing regression is claimed.

**ID to use for the next new debt:** `DEBT-065`. This is an allocation counter, not an open debt.
<!-- project:end -->
