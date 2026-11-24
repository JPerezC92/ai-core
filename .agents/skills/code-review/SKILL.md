---
name: code-review
description: Reviews a named change candidate against correctness, cross-file consistency, scope, dead code and public-API alignment, and returns findings with dispositions. Use when the user requests an independent review, or when a declared high-risk item makes self-review insufficient.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.0.0
---

## Mandatory core

### What I do

Provide one review rubric for a change candidate, and one procedure for running it in a context that did not author the change. The rubric is knowledge; **the fresh context is what supplies independence**. Applying this skill in the authoring context is self-review and must be described as such.

### When to run a review

Three cases, and only these three:

1. **Self-review (always, cheap).** The author reads their own diff against `### Rubric` before declaring the work done. Report it as self-review.
2. **Requested independent review.** The user asks for one. Dispatch a fresh context — OpenCode's built-in `general` subagent is sufficient and needs no agent document — with a self-contained mission: the exact candidate identity, the diff or changed-file list, this skill's path, and the evidence the reviewer must judge.
3. **Recommended on declared risk.** A work unit whose record declares a high-risk item may be recommended for one. Recommendation, not gate; no review is created without the user's decision.

An independent review is never a delivery prerequisite. Its absence is not a pending check, a missing acceptance or a blocker.

### What a reviewer must receive

- The **exact candidate identity**: commit SHA or immutable head, and the literal diff command or the diff content.
- The **changed-file list** reconciled against that diff.
- The **governing requirements** it is judged against, by reference.
- The **evidence already produced**: commands, exit codes, observed results. A reviewer analyzes supplied evidence; it does not re-run another agent's execution.

A reviewer never runs a Git or GitHub command. Git-derived input comes from Herald 📯 (Release Manager). The reviewer is read-only on source.

### Rubric

Check every applicable item and report only what you can evidence.

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

### Report format

Lead with the verdict, then numbered findings. Each finding carries: the file and location, the governing rule or requirement it violates, the concrete fix, and a severity of `BLOCK` (the delivery is not ready) or `ADVISORY` (worth fixing, does not withhold readiness).

```
[PASS] | [ADVISORY] | [BLOCK] — one-sentence basis
1. <file>:<line> — <finding> — <governing rule> — <fix> — <BLOCK|ADVISORY>
```

`[PASS]` means zero open findings of any severity. An observation that requires no action is an INFO note, not a finding. Never report a finding you cannot point at.

### How findings are disposed

Findings return to the coordinator, which applies `.aicore/core/knowledge/agents.md` `### Finding disposition`: fix-first when in scope and safe, otherwise a reported decision. The reviewer does not fix source, does not re-review its own remediation, and does not become a gate.

### Hard limits

- Read-only on all source, tests, records and configuration.
- No Git or GitHub command of any kind.
- No new acceptance mechanism, sign-off sheet, or approval step — the verdict is input, not authority.
- Never describe this rubric as an independent reviewer. Applying it in the authoring context is self-review.
- Do not claim that a dispatched review is permission-isolated: a fresh context shares the runtime's permission envelope.
