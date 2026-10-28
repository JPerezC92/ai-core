# Source-local documentation

This directory holds AICore's explanatory decisions, historical accounting and reusable research. It is not a second workflow router or a required shared dependency. Current runtime authority starts at [AGENTS.md](../AGENTS.md); task-specific reads and ODD classification belong to [knowledge/agent-workflow.md](../knowledge/agent-workflow.md).

| Material | Canonical location | Purpose and boundary |
|---|---|---|
| Saved research | [research/README.md](research/README.md) | Single catalog of reusable evidence; topic/source provenance, applicability and freshness, not execution approval. |
| New research-record format | [research/_template.md](research/_template.md) | Single template for new domain/topic records; existing multi-file publications retain their supporting evidence. |
| Architecture decisions | [architecture/decisions/](architecture/decisions/) | Source-local ADRs explaining decisions; current definitions remain in `architecture/`. |
| ODD adoption assessment | [architecture/odd-adoption-status.md](architecture/odd-adoption-status.md) | Informational upstream/local alignment and dated delivery evidence; not workflow authority, an adoption certificate or a task tracker. |
| Architecture history | [architecture/history/](architecture/history/) | Extraction accounting and prior historical records; preserved source-local history, not current implementation conformance or destination approval. |

## Other canonical owners

- **Operational rules and registers:** [knowledge/agents.md](../knowledge/agents.md), [knowledge/debt.md](../knowledge/debt.md), [knowledge/symptoms.md](../knowledge/symptoms.md), [knowledge/problems.md](../knowledge/problems.md) and [knowledge/diagnostic-system-design.md](../knowledge/diagnostic-system-design.md).
- **Architecture and testing definitions:** [architecture/README.md](../architecture/README.md) selects common/shape/implementation guides and the separate testing contract/guides. Documentation review does not establish code conformance.
- **Current feature scope and decisions:** `odd/tasks/<feature-name>.md`.
- **Research preparation/publication ownership:** [AGENTS.md → Saved-research bindings](../AGENTS.md#saved-research-bindings) selects this repository's storage and owner; `.opencode/agents/augur.md` owns research procedure. Cipher 🔓 (Lead Orchestrator) assigns exact repository-document writes to Scribe ✍️ (Docs & Problems Manager), subject to existing approvals and reviews. A catalog entry is not publication authorization.
- **Temporary artifacts:** `output/research/`, `output/audits/` and `output/design/` are gitignored drafts/reports, not the sole durable home of reusable evidence.

Directory spelling does not change authority: research and historical prose cannot supersede the current governing runtime, workflow, feature or architecture owner.
