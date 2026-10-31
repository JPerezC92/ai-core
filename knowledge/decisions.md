# Decisions

<!-- core:begin -->
## Mandatory core

Accepted decisions reach agents through their architecture owners, not through the decision record. This file owns the decision lifecycle: when a record is written, what acceptance requires, and what an agent reads instead of the record.

### Artifact roles

| Artifact | Carries |
|---|---|
| Research record | evidence: what was observed, its bounds, what stays unknown |
| Decision record (ADR) | the immutable rationale of one decision, its alternatives, and its authorization boundary |
| Architecture owner | the normative current rule an agent follows |
| Architecture gate | per-change application of that rule to the edit under review |
| Adoption audit | evidence of how far current code conforms at a point in time — never a conformance certificate |

An agent implementing or reviewing work reads the architecture owner and applies its gate. The record explains why the rule exists and what was rejected; it never overrides the owner and is never the operative text.

### Lifecycle

1. **Research** — evidence is recorded first. A decision without recorded evidence is a preference, not a decision.
2. **Propose** — the record states the decision, its alternatives, and its `## Propagation` target. Status stays `Proposed`.
3. **Propagate** — the operative rule is written into its architecture owner in the same work unit.
4. **Check** — an independent reviewer reads the owner text and confirms it enforces the decision.
5. **Accept** — only then does the status become `Accepted`, and the approval is recorded verbatim in the governing feature `## Log`.
6. **Conform** — conformance is measured by an audit or a mechanical check and reported as adoption evidence, not asserted from the record.

### Statuses

| Status | Meaning |
|---|---|
| `Proposed` | recorded, not in force; no agent obligation arises from it |
| `Accepted` | in force, with its rule present in the named owner |
| `Amended` | accepted and later corrected; the decision text is unchanged and the amendment line carries the change |
| `Superseded` | replaced by a later record; its line cites that record and the delivering commit |

Only explicit user approval moves `Proposed` to `Accepted`; an agent never promotes a record on its own reading, and the decision is recorded verbatim in the governing feature `## Log`. An `Accepted` record is never rewritten: a correction adds an `Amended` line, a replacement adds a `Superseded` line citing the superseding record and its commit. The decision body below those lines stays as originally accepted.

### Acceptance gate

A record may be `Accepted` only when all three hold:

- its normative owner is updated in the same work unit — a follow-up task is not propagation;
- its `## Propagation` section names the exact owner files and sections carrying the rule;
- an independent reviewer verified that the owner text enforces the decision, not that the record claims it does.

A record that changes no rule states `no normative change — reason` in `## Propagation`; that is a valid target, an empty or missing section is not. Acceptance without propagation evidence is a finding against the change, not a pending item.

### Why the records are preserved

An architecture owner states the current rule only, so it cannot also carry why the rule exists, what was rejected, where the evidence stops, what replaced a retired rule, or which code is known not to conform. Preserving the record keeps the rationale and rejected alternatives, so a settled question is not reopened from memory; the evidence bounds, so an inference is not promoted to a rule; the supersession chain, so a retired rule traces to its replacement and commit; the authorization boundary — what the decision did not authorize; and known nonconformance, so a gap is reported rather than silently grandfathered.

### Ownership

- Scribe ✍️ (Docs & Problems Manager) authors decision records.
- Sentinel 🛡️ (Quality Guardian) audits the corpus for lifecycle and propagation compliance.
- The applicable architecture owner gates the affected owner document: Bastion 🧱 (Backend & Scripts Architect) for the common contract, backend and scripts shapes, and implementation guides; Atrium 🏛️ (Frontend Architect) for the frontend shape and React guide; Crucible 🔥 (Test Architect) for the testing contract and testing guides.
- Cipher 🔓 (Lead Orchestrator) routes the work; the user accepts the decision.

### Discoverability

Link a source-local record from the project's own navigation — the `project` region of its architecture navigation or, when that navigation ships whole-file to destinations, a source-local navigation document. The shared core never links a source-local record. Treat a record with no route from navigation as undiscoverable and incomplete.
<!-- core:end -->

<!-- project:begin -->
## Project extensions

### Decision records

This source project's decision records live in `docs/architecture/decisions/`, created from `_template.md`. They are source-local rationale, not distributed shared dependencies, and their links belong in `docs/architecture/README.md`.
<!-- project:end -->
