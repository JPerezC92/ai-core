# Source-local architecture records

This document holds this repository's source-local architecture selections, decision records, and history; it is not distributed, because `architecture/` ships whole-file and every file in it refers only to paths inside that root. Read it as explanation and navigation for work in this repository — never as a shared dependency and never as a second architecture authority.

## Current source selections

The previously approved import interpretations are mapped by `architecture/stacks/typescript/react.md` and `architecture/stacks/typescript/nestjs.md` → Imports and language conventions, and `architecture/stacks/python.md` → Imports and language conventions → Deployment zones. Those owners retain the sibling exceptions, non-sibling alias/absolute mappings, traversal prohibitions and deployment/startup boundaries; this navigation adds no competing portable contract.

The approved Python backend-entity representation is mapped by `architecture/stacks/python.md` → Domain and ports and Obligation mapping. Its framework-free entity choice does not select a framework for unrelated DTO/configuration roles or establish application conformance.

No Python HTTP framework, repository library, error registry layout or serializer framework mapping has been selected. These project selections remain open; current implementation patterns do not decide them. Follow `architecture/stacks/python.md` → Open decisions and the applicable runtime's uncertainty route when a missing mapping affects the task. Unselected bindings alone are not blockers for unrelated work.

## Decision rationale

This project's architectural decision records live in [`decisions/`](decisions/) — the source-local ADR directory, not a shared path. `knowledge/decisions.md` owns the decision lifecycle and the requirement that an accepted decision propagates into its architecture owner. The records are [ADR 0001 — Agent workflow foundation](decisions/0001-agent-workflow-foundation.md), [ADR 0002 — Testing architecture layering](decisions/0002-testing-architecture-layering.md), [ADR 0003 — Architecture documentation ownership](decisions/0003-architecture-documentation.md), [ADR 0004 — Domain behavior placement](decisions/0004-domain-behavior-placement.md), [ADR 0005 — Use-case organization and naming](decisions/0005-use-case-organization-and-naming.md), and [ADR 0006 — Architecture whole-file distribution and contract boundaries](decisions/0006-architecture-whole-file-distribution.md) (architecture whole-file distribution and the contract boundaries it settles). ADR 0001 covers the agent-workflow budget; ADR 0002 and ADR 0003 own the testing and architecture-document layout, and ADR 0004 and ADR 0005 own the domain and operation rules above. Shared core never links source-local ADRs: the owners state their own rules, and an ADR is explanation, not an undistributed dependency.

## Optional source-local history

The original extraction inventory, retained-procedure accounting, approval interpretations and documentation-acceptance boundary are preserved in [architecture extraction accounting](history/architecture-extraction-accounting.md). Read it when historical evidence is relevant, not as a shared prerequisite. Reference-guide status and current definitions remain with their architecture owners; the historical review is not implementation conformance, destination migration, external publication or problem-record approval.
