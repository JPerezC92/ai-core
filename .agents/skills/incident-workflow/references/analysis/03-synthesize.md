# Synthesize — Ticket <ID>

> **Execution model:** by default Cipher 🔓 (Lead Orchestrator) executes this step directly and is not gated on an assignment. When separate work was explicitly authorized, the step runs under that instance's assignment; a recorded assignment procedure never authorizes delegation by itself.

> **Owner:** Cipher 🔓 (Lead Orchestrator), or the explicitly assigned synthesis writer in a delegated run
> **Pre:** `02-investigate.md` exists; ≥1 hypothesis has `Confirmed: yes` or all are `inconclusive`; `Phase` is `investigate`; the investigate step's Gate is satisfied and its header advanced. In a delegated run, additionally: investigation's current outputs, gates and counter snapshot accepted, prior resource-use cessation observed, and this synthesis instance explicitly assigned.
> **Reads:** `01-identify.md`; `02-investigate.md`; `.aicore/core/knowledge/escalation.md` (contract and this project's routing matrix/mappings)
> **Writes:** `03-synthesize.md` (filled); updates `state.md` (`Phase`, `Updated`)

## Execution ownership and accepted join

The default route is direct execution: Cipher 🔓 (Lead Orchestrator) reads the investigation results, states the root cause, selects the derivation, drafts the response surface and writes `03-synthesize.md` and `state.md` itself. Direct execution creates no assignment and no join to accept; Cipher keeps the single budget and records the evidence it obtained.

For a delegated run, record workflow/ticket, task/instance, accepted predecessor/input identities, exact writes/other access, allocated destinations, gates, continuation/join owner and capacity/accounting owner in existing Markdown or the dispatch. This assigned synthesis instance is sole writer of the named working files, and Cipher 🔓 (Lead Orchestrator) remains the acceptance/accounting owner. Read stable accepted investigation and supporting results with separate attribution; do not reset or independently mutate hypothesis/query/rerun counters. New investigation needs return to the coordinator through the existing order and allowances, never parallel queries or hypotheses.

Hold outputs and dependencies stable through review; relevant changes invalidate affected evidence and joins. Return current input/output identities, actual counters, gate evidence and resource-use status for coordinator acceptance before downstream work in a delegated run. Supporting workers have no state-write grant. Inbound `downloads/` and response `screenshots/response-N/` destinations, reports, response drafts, durable records, registers and browser/auth sessions retain their own exclusive resource assignments; a step return does not transfer them implicitly.

## Steps

1. Read the `02-investigate.md` verbatim results. Identify the confirmed hypothesis (or the most-supported inconclusive if no confirmation).
2. State the root cause in ≤3 bullet lines, each labeled `Fact` (direct evidence) or `Hypothesis` (partial evidence + refutation criteria cited).
3. Read `.aicore/core/knowledge/escalation.md` before selecting the derivation path. Use system + root-cause type or an evidenced generic condition (such as missing information) to select a project routing matrix row; cite its row locator and current evidence/gaps. Reference any already-identified problem without issuing or changing diagnostics' verdict; a generic route requires no invented `P-NNN`. Verify required ticket fields and their local values/IDs, target/team and tool mapping against current ticket-system evidence, or justify N/A where not required. Record proposed action, tool, authorized owner and approval status separately from actual execution. Required approval can remain pending while recommending an evidenced route, but the affected action must not execute before its evidence, mappings and approval are verified under the canonical contract.
4. Identify the response surface: what the visible note must convey — symptom confirmed, root cause (labeled), recommended action, derivation target. ≤15 lines total including the derivation call.
5. Write `03-synthesize.md`: root-cause block (Fact/Hypothesis labeled), derivation decision, response surface.
6. Run completed-step validation and satisfy the applicable gates — Cipher's own verification in direct execution, the coordinator's acceptance in a delegated run — and only then update `state.md`: `Phase: synthesize`, `Updated: <now>`, and run full validation. Preserve the accepted incident counter snapshot.

> **Evidence rule:** symptom evidence alone does not establish root-cause equivalence or authorize a fix. Any supported root cause must be labeled `Fact` or `Hypothesis` under Step 2 and meet the applicable evidence bar; a fix requires user approval.

## Output

- **Artifact:** `03-synthesize.md` (filled).
- **Schema:** root-cause block (≤3 bullets, each labeled Fact/Hypothesis), derivation target (named, not TBD), derivation decision with row/source, evidence/gaps, verified required-field mappings or justified N/A, proposed action/tool/authorized owner/approval and separate actual execution status, response surface (≤15 lines). Symptom evidence alone is never represented as root-cause proof or fix authorization.
- **Handoff:** task/instance, consumed input/output identities, accepted supporting results, unchanged counter snapshot, validator/gate evidence and resource-use status. Accept all screenshot producer results and existing local files before response drafting; files for the response being drafted must exist under that response's `screenshots/response-N/` first. Before collapse, require the accepted finished producer/consumer results, prior approved register mutation, durable retention, current pre-close/semantic gates and the exact `Close out now` authorization — plus, in a delegated run, no active working-file user and observed cessation. Synthesis never authorizes deletion or fixes.

## Root cause

- **[Fact/Hypothesis]:** <root cause bullet 1>
- **[Fact/Hypothesis]:** <root cause bullet 2 — if needed>
- **[Fact/Hypothesis]:** <root cause bullet 3 — if needed>

## Derivation decision

- **Target:** <named from the escalation matrix>
- **Target team:** <team>
- **Rationale:** <one line from the escalation matrix>
- **Matrix row / source:** <selected problem or generic condition; project routing row locator and input identity>
- **Current evidence / gaps:** <ticket-specific citations satisfying the row; unresolved requirements explicitly stated>
- **Required ticket fields / verified mapping:** <field names and required values/IDs with current mapping evidence, or justified N/A>
- **Proposed action / tool / authorized owner:** <recommendation and verified ticket-system mappings, or justified N/A for an unneeded tool>
- **Approval status:** <required approval and its evidence, pending/not obtained, or justified N/A under the contract; never infer approval from routing or field selection>
- **Actual execution:** <not executed, or observed tool result and action/status evidence from the authorized executor; never the recommendation alone>

## Response surface (≤15 lines)

<what the visible note must convey — symptom, root cause labeled, action, derivation target>

## Gate

- ⬜ Root-cause bullets present and labeled Fact or Hypothesis
- ⬜ Derivation target named (not "TBD")
- ⬜ Selected row/source and current evidence/gaps recorded under `.aicore/core/knowledge/escalation.md`; diagnostic verdict unchanged and generic conditions require no invented problem ID
- ⬜ Required fields/values/IDs, target/team and tool mappings verified or justified N/A; proposed action/authorized owner/approval distinct from actual execution evidence; unmet requirements block the affected execution
- ⬜ Response surface ≤15 lines
- ⬜ Symptom evidence alone is not represented as root-cause proof or fix authorization; root-cause claims meet the evidence bar and fixes require user approval
- ⬜ Stable relevant investigation/supporting results accounted for; sole writer, conserved accounting and completed-step validation confirmed before the header advances
- ⬜ Files for the response being drafted exist under `screenshots/response-N/` and accepted producer outputs precede drafting; in a delegated run, downstream ownership transfers additionally require observed prior-user cessation and explicit coordinator assignment

## Abort conditions

- All `02-investigate.md` verdicts are `inconclusive` AND no partial evidence is sufficient for a labeled hypothesis → halt; Cipher 🔓 (Lead Orchestrator) escalates without a response surface.
- Halt if symptom evidence alone would be represented as root-cause proof or a user-authorized fix.
- Missing escalation owner/row/target, required evidence or mapping, or ambiguous routing → report the gap and block the affected execution; never guess a target or complete the named-target gate with a placeholder. Missing required approval blocks the affected action, not an otherwise evidenced recommendation. Read-first verification and required approval must precede any affected action; synthesis itself grants no execution authority.
- Stale/incomplete/still-mutating predecessors, conflicting access or, in a delegated run, unobserved prior-user cessation → report `BLOCKED` before transition, transfer or collapse; do not infer acceptance, and do not use the question tool from a delegated run.
