# ADR 0003 — Architecture documentation ownership

- **Status:** Accepted
- **Date:** 2026-10-25

## Context

The frontend/backend/script architecture definitions are embedded in reviewer and implementer runtimes. ADR 0001 placed language conventions there; ADR 0002 separated test design and explicitly left its root placement provisional. The governing feature is `odd/tasks/architecture-documentation.md`. Existing decisions must survive extraction; historical rationale for individual React/NestJS/Python choices is unrecorded. No new rationale is asserted for those choices.

## Decision

- Use `architecture/README.md` for selection, `clean-architecture.md` for common semantics, `shapes/` for frontend/backend/scripts responsibility specialization, and `stacks/` for concrete mappings. Copy the non-testing stack template before guides and keep their common headings/obligation tables.
- Read common contract → applicable shape(s) → applicable implementation guide → `architecture/testing/architecture.md` and applicable testing guide. Agent authority, execution, scope, gates, dependency ownership, reports, and uncertainty handling remain in runtimes, not competing document copies.
- Preserve existing concrete decisions. Python implements the same semantic obligations without mechanical Hook/controller equivalents. The user resolved import policy: same-directory TypeScript siblings may use `./`; non-siblings use aliases and no parent traversal. Same-package Python siblings may use `.sibling`; other packages use absolute paths and no parent traversal, without weakening deployment-zone isolation or startup exceptions. The user selected framework-free Python domain classes with internal underscore storage, immutable identity, per-field read-only properties, and `@classmethod create(...)` enforcing existing validity. Python HTTP/repository/serializer/framework bindings remain unselected, not blockers or inferred choices.
- The sole normative testing home is `architecture/testing/`; the four old `testing-architecture/` files retain only compatibility section pointers and their existing clearance rows. Normative text was relocated with owner/path references updated, preserving completed decisions, metadata, parity, and project extensions. Combined documentation transition acceptance is complete.
- Explicit per-file region clearance covers navigation, common/shape contracts, implementation template/guides, and all four canonical testing files. No directory blanket expansion or tool/schema change is needed. New paths require destination-authorized `init --bind-cleared` enrollment, not `apply` alone; old pointers and canonical documents must arrive together. Destination agents reconcile displaced duplicates/local extensions; nonempty `pending` and the reconciliation blocker prevent acceptance until `check` exits `0`. No destination is mutated or claimed migrated here.
- Shared contracts carry protected core plus destination-owned project extensions. This ADR and extraction history remain source-local, not required dependencies of distributed documents.
- This is documentation-first: no application remediation, dependency/permission changes, destination mutation, or assertion of existing code conformance. Guide review establishes only the documentation contract; code adoption needs separate authorization.

## Alternatives

- Keep architecture inside runtimes: avoids new paths but retains mixed responsibilities and competing copies; not the proposed structure.
- One document per language only: conflates language with application shape and hides shared semantics; not the proposed structure.
- Put shared contracts under source-local `docs/architecture/`: incompatible with its existing source-local role.
- Mechanically copy TypeScript UI mechanics into Python: confuses parity with library identity; retain semantic mapping and report gaps instead.
- Immediately delete old testing paths: unsafe for existing core-sync bindings; retain compatibility under the transition gate.

## Consequences

Definition ownership becomes explicit, at the cost of new navigation, per-file clearance, consumer wiring, and complete original-to-candidate accounting. Runtime retargeting, testing transition, clearance, and combined review are separate coordinated tasks. Import and Python entity choices reflect explicit user decisions, not current implementation inference; unknown historical rationale remains unrecorded. The coordinator accepted T6 combined Sentinel 🛡️ (Quality Guardian) PASS on the complete candidate and authorized reference promotion and this ADR's Accepted status. Acceptance concerns documentation only; it proves neither implementation conformance nor destination migration. Existing testing reference status is preserved, not newly awarded by relocation. Templates remain proposed skeletons. This source-local ADR is explanation, not an undistributed dependency of shared contracts.
