# Incident escalation

<!-- core:begin -->
## Mandatory core

### Purpose and authority

This contract owns routing conditions, evidence references, required ticket selections, and action prerequisites. It does not own diagnosis or grant execution authority. Apply [shared rules](agents.md) → Register-first identification, Evidence discipline, and User-Authority-Only rule; follow the assigned incident workflow for synthesis.

Incident identification remains symptom → incident problem → verdict under those rules. A routing row references that result; it never issues an independent verdict, upgrades a match, or bypasses register-first identification. Generic conditions, such as missing requester information, need no invented problem ID. A receiving team's routing responsibility is not evidence that it caused a defect or owns its remediation.

### Project routing matrix

Maintain this project's actual routing rows and organizational bindings in the project region: teams, ticket fields, allowed values and IDs, tools, execution owners, and approval requirements. Use the sole matrix template below. Do not copy full diagnoses into routing rows; reference the diagnostic owner and current-ticket evidence needed to establish the condition.

Copy the following template for this project's routing rows. Angle-bracket placeholders are illustrative instructions, not live routes, field mappings, or execution evidence.

```markdown
| Problem / condition | Route to | Required evidence | Required ticket fields | Action / approval |
|---|---|---|---|---|
| <diagnostic reference or generic condition; no invented problem ID> | <verified receiving team and responsibility> | <current-ticket evidence references establishing the condition> | <verified field, current allowed value and ID where required; optional field: N/A with reason> | <recommended action; verified tool and execution owner; approval requirement and approval owner> |
```

### Application assignment matrix

When the assignee depends on the affected application rather than on the failure mode, keep that mapping in the project region as a second table. Its use is optional; a project that never assigns by application omits the table and its rows.

```markdown
| Application | Assignee | Precedence / note |
|---|---|---|
| <application name from this project's catalog> | <named person or role resolved through this project's user directory at execution time> | <default, override, or effective-date note> |
```

- A routing row may omit its own assignee; a matching application row still applies under the precedence below.
- Precedence: a user-named assignee overrides the matrix; otherwise a matching application row applies; otherwise the routing row's default applies; otherwise ask. No matching row, no default, an application that matches no row, or more than one matching row means ask, never guess.
- Application values come from this project's current catalog. A remembered value or identifier is not proof of a current valid option.
- Resolve the person through this project's directory at execution time and record the resolved identity in the required ticket fields.
- The matrix selects an assignee only. It does not by itself authorize the assignment, the status change, or any other ticket mutation.

### Synthesis and execution preflight

1. Establish the current-ticket condition from referenced evidence and, when applicable, the diagnostic result. Select a row from the project routing matrix whose condition and scope are evidenced. If the mapping is missing, the route is ambiguous, or required evidence is absent, halt the affected action and report the gap to Cipher 🔓 (Lead Orchestrator); do not guess a target or field mapping.
2. Read the actual ticket and authoritative current ticket-system field/tool definitions before proposing selections. Verify the target, required fields, allowed values and IDs, and tool inputs for this action; a historic row or remembered ID does not prove present validity. Mark an optional field `N/A` with its reason; do not use that marker to bypass a required field. Unavailable verification blocks the affected action.
3. When the assignee comes from the application assignment matrix, resolve and verify that row under the matrix's rules and treat the resolved person as one of the required ticket selections.
4. State the recommendation separately from execution: identify the target, referenced evidence, verified selections, tool, responsible executor, and required approval with its owner and current status. Missing approval prevents execution, not reporting an evidence-supported recommendation. A populated row or dropdown selection is never authorization.
5. Where this project's applicable flow requires them, verify archive synchronization with Ledger 📒 (Record Keeper), the required response note's actual posting status, and ticket-field correctness before routing. These checks neither mandate posting for every route nor authorize posting or field changes. Missing prerequisites halt the affected action under the existing approval and owner workflow.
6. Execute only through the authorized executor and tool after the applicable prerequisites and approval are satisfied. Derive executed-route status from the actual tool return, not from the recommendation, selected row, intended target, or drafted note. Report failures, partial results, or uncertain outcomes as such. Ledger's existing archive-sync procedure owns faithful recording of what actually occurred; this contract creates no competing record-sync procedure.

### Routing knowledge maintenance

Keep proposed routing rows distinguishable from confirmed executed routes: a proposal is not execution evidence. Maintain confirmed routes through Scribe ✍️ (Docs & Problems Manager), using this project's existing documentation approval workflow and deduplication rules. Before proposing an addition, check existing rows for the same condition and route to the receiving team; reuse coverage rather than adding a duplicate. Cite the current case and actual execution result for a confirmed route; preserve the verified tool and evidence references without turning routing history into diagnostic authority.

Application assignment rows follow the same maintenance rule: a confirmed mapping names the application, the resolved assignee and the evidence that established it, and is updated rather than duplicated when the person or policy changes.

Routing-history maintenance does not postpone diagnostic admission. The early confirmed-root-cause admission and pre-collapse obligations remain owned by [shared rules](agents.md) → Register-first identification, independently of whether a route has executed or a routing-history row is ready.

<!-- core:end -->

<!-- project:begin -->
## Project extensions

No organizational routing bindings, application assignment rows, or executed-route records are defined here.
<!-- project:end -->
