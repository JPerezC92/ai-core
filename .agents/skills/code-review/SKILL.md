---
name: code-review
description: Reviews a change candidate against correctness, cross-file consistency, scope, dead code and public-API alignment, and returns findings with dispositions. Use for the primary agent's own self-review of a change it authored, including an ordinary request to review, verify, check or confirm the work, and for a review in a separate context only when the user explicitly authorized one.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.1.0
---

## Mandatory core

### What I do

Provide one review rubric for a change candidate, applied in one of two modes. **Mode A — self-review** is the default and normal route: the agent that authored the change applies the rubric directly, fixes what it evidences, and continues. **Mode B — independent review** is a separate reasoning context that applies the same rubric read-only, and it exists only when the user explicitly authorized that review. The rubric is the technical standard in both modes; **the fresh context is what supplies independence**, so only Mode B has it. Mode A is self-review, and it is never described as independent verification.

### Choose the mode

**Mode A — primary-agent self-review. Default, and required whenever applicable work is about to be declared done.** It is also what an ordinary request to review the changes, verify the implementation, check for bugs or make sure everything is correct selects; such a request authorizes Mode A and nothing else.

1. Apply `## Rubric` to the actual candidate.
2. Obtain the candidate and any Git-derived evidence through Herald 📯 (Release Manager). A read-only Git fact is not a separate context and creates no reviewer.
3. Fix every evidenced defect that is in scope, local and reversible under `.aicore/core/knowledge/agents.md` `### Finding disposition`; report the ones it cannot fix.
4. Rerun the checks the correction invalidated.
5. Report the result as self-review, and continue the authorized task.

Loading this skill is observational; it revokes none of the authority the author already held. Mode A needs no reviewer packet, verdict artifact, acceptance report, sign-off or handoff — it uses the task's existing evidence and reporting procedure — and it stays proportionate to the change.

**Mode B — explicitly authorized independent review.** Available only after the user authorized that review. Nothing else authorizes it: not a high-risk item, a large, complex or security-sensitive change, a completed work unit, a failed or corrected check, a remediation, ODD closure, pull-request preparation, an uncertain self-assessment, or a general request to ensure quality. A recommendation is not authorization.

An authorization covers the candidate and review scope it names. When a correction changes that candidate, preserve the earlier verdict with the candidate it actually judged, correct and verify the defect directly, update the delivery evidence truthfully, and dispatch a further review only where the user authorized further review.

An independent review is never a delivery prerequisite. Its absence is not a pending check, a missing acceptance or a blocker.

### What an independent reviewer must receive — Mode B

- The **exact candidate identity**: commit SHA or immutable head, and the literal diff command or the diff content.
- The **changed-file list** reconciled against that diff.
- The **governing requirements** it is judged against, by reference.
- The **evidence already produced**: commands, exit codes, observed results. A reviewer analyzes supplied evidence; it does not re-run another agent's execution.

A reviewer never executes a Git or GitHub command; Git-derived input comes from Herald 📯 (Release Manager). The reviewer is read-only on source, and it acquires no implementation ownership.

### Rubric

Check every applicable item and report only what you can evidence. The rubric is shared: both modes apply every item below, and neither adds a criterion the other lacks.

**Correctness and consistency**

- Does the change do what its requirement says, at the observable boundary the requirement names?
- Do names, shapes and conventions stay consistent **across** the files the change touches — a rename applied everywhere it was needed, an export matching its consumer?
- Does a caller's expectation still match the callee it calls (arguments, return shape, nullability, error path)?
- Public API: does a changed signature have every caller updated, and is an incompatibility declared rather than silently absorbed?

**Scope and cleanliness**

- Does any changed line serve something other than the stated requirement? Unrelated refactors, drive-by renames, formatting-only churn in untouched logic, or a dependency added for convenience.
- Dead code: unreachable branches, an export nobody imports, a flag that is never set, a handler no route reaches, a symbol left behind by a rename.
- Comment and documentation drift: a comment or doc that now contradicts the code.
- Duplicated logic the change introduced where an existing helper already handled it.

**Behaviour and evidence**

- Is the verification evidence real: an exact command, its exit status, and the observed result? A claim with no command is a claim, not evidence.
- For changed command behaviour, is there a previous-versus-current comparison, and does any difference lack authorization?
- Do the tests exercise the rule the requirement names, and would they fail if the rule were broken?
- Are error paths covered, not only the happy path?

**Residual risk**

- What could break that no test covers? Name it, do not speculate about it.

Testing-architecture conformance is owned by `.aicore/core/architecture/testing/architecture.md`; implementation architecture by `.aicore/core/architecture/README.md` and the selected guides. Read the owner text rather than re-deriving a rule. The dependency surface has its own procedure in the `dependency-review` skill; visual and accessibility concerns in `visual-review`.

### Report format — Mode B output

Lead with the verdict, then numbered findings. Each finding carries: the file and location, the governing rule or requirement it violates, the concrete fix, and a severity of `BLOCK` (the delivery is not ready) or `ADVISORY` (worth fixing, does not withhold readiness).

```
[PASS] | [ADVISORY] | [BLOCK] — one-sentence basis
1. <file>:<line> — <finding> — <governing rule> — <fix> — <BLOCK|ADVISORY>
```

`[PASS]` means zero open findings of any severity. An observation that requires no action is an INFO note, not a finding. Never report a finding you cannot point at.

Mode A reports under the task's existing evidence procedure and may use the same severity vocabulary; it produces no separate verdict artifact, because its outcome is the corrected candidate and the checks that were rerun.

### How findings are disposed

Both modes feed one rule, `.aicore/core/knowledge/agents.md` `### Finding disposition`: fix-first when in scope and safe, otherwise a reported decision. In Mode A the author applies it directly and continues. In Mode B the findings return to Cipher 🔓 (Lead Orchestrator), which applies it; the reviewer does not fix source, does not re-review its own remediation, and does not become a gate.

### Hard limits

- Mode B is read-only on all source, tests, records and configuration. Mode A edits only within the authority the task already granted, and only in-scope defects.
- No Git or GitHub command in either mode. Git-derived input comes from Herald 📯 (Release Manager).
- No new acceptance mechanism, sign-off sheet or approval step — a verdict is input, not authority.
- Never present this rubric as an independent reviewer. Applying it in the authoring context is self-review.
- Do not claim that a dispatched review is permission-isolated: a fresh context shares the runtime's permission envelope.
