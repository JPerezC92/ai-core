# ADR 0006 — Architecture whole-file distribution and contract boundaries

- **Status:** Proposed
- **Date:** 2026-10-30

## Context

ADR 0003 gave `architecture/` explicit per-file `region` clearance and a protected-core-plus-destination-project-extension model: each of the 13 architecture documents carried a source core region and left a project region to the destination, whose displaced duplicates and local extensions were resolved through a reconciliation report and a `pending` entry (ADR 0003 → Decision; governing feature `odd/tasks/architecture-whole-file-distribution.md` Log L7).

Three evidenced symptoms showed that model was wrong for a rulebook:

- A project region inside a rulebook is a sanctioned place for a destination to record a competing rule. Four testing documents invited exactly that, with destination guidance whose wording pointed at "here": `architecture/testing/architecture.md:120`, `architecture/testing/stacks/_template.md:125`, `architecture/testing/stacks/typescript.md:203`, and `architecture/testing/stacks/python.md:119` (feature S5). Regions remain correct where local content is non-normative — records, evidence, operational bindings, history (feature L10).
- `architecture/testing/architecture.md` listed an agent runtime spec as an owner of the review procedure and referenced `.opencode/agents/crucible.md` at lines 13 and 113. That path leaves `architecture/` and dangles wherever the agent spec is not delivered (feature L4: 11 of 118 path-like references resolved outside `architecture/`, 9 in `README.md`'s project region and these two).
- The two testing guides carried a `Guide owner` field naming an agent, with the testing stack-guide template repeating it (`testing/stacks/typescript.md:6`, `python.md:6`, `_template.md:6`; feature S6). A guideline does not acquire its status from an owner field.

The user fixed the boundary directly: architecture is the only source of implementation guidelines and points at nothing outside its own root, while everything else may point at it. Verbatim (feature L2): "i will not distribute the ADRs but i want to distribute architecture"; and (feature L3): "to be clear all inside Architecxtura can point to any in the same root folder but not outside the root folder".

The governing flow is the one `knowledge/decisions.md` owns: research → ADRs → architecture update → models use the architecture adoptions (Artifact roles; Lifecycle). This source's ADRs and histories are not distributed content (feature L2), so a record that a distributed file must link cannot live inside that file.

## Decision

- **Whole-file transport.** Every architecture document ships whole-file in `raw` mode: 13 explicit per-file clearance rows, no directory root, no ownership markers, and no project region anywhere in the tree. No architecture write produces a reconciliation report or a `pending` entry.
- **No outward references.** No architecture file references a path outside `architecture/`. References between architecture files are unrestricted — any file in the root may point at any other. Permission and authority statements are not references and stay as written: who holds execution authority, who may edit, and which gates apply are stated, not linked.
- **Complete rules.** Architecture states its rules completely and never defers a rule's content to another document. A reader reaches a decision from `architecture/` alone.
- **Distribution identity, not conformance.** Every destination receives identical bytes, and that guarantees distribution only: reference libraries, runners, frameworks, and test commands named in a guide remain reference choices the destination adopts in its own configuration. A destination that needs a different stack writes its own guide, copied from the applicable template; an unbound path survives every sync, so divergence lives there rather than in a distributed file.
- **No owner of a guideline.** No agent or document owns a guideline. A guide's status (`proposed` / `reference`) is carried by the testing contract's status model and its guide index, not by an owner field in the guide.
- **Source-local navigation.** Source-local records, ADR links, and source-local history live in a source-local navigation document (`docs/architecture/README.md` for this project), never inside a distributed architecture file. The shared core never links a source-local record.

This is documentation of a distribution and contract-ownership decision: it authorizes no code edit, refactor, test change, dependency or permission change, or destination mutation, and it claims no application conformance. Status stays `Proposed`; per `knowledge/decisions.md` (Statuses; Acceptance gate) it becomes `Accepted` only on explicit user approval recorded verbatim in the governing feature's `## Log`, after an independent reviewer confirms the owner text below enforces it.

## Alternatives

- **Keep `region` clearance with project regions.** Rejected: the project region is a drift slot with no check behind its promise — a destination could state a competing architecture rule in the most authoritative surface and nothing would detect it.
- **Keep only `architecture/README.md` in `region`.** Rejected (feature L6, superseded by L9): it buys permanent asymmetry in the most-read file and keeps a reconciliation carrier alive for no benefit, while still leaving one outward reference slot in the navigation document.
- **Ship the ADR and history links inside the raw `architecture/README.md`.** Rejected: shared law would then link a source-local record, which the decision forbids for another destination, and the links dangle wherever those records are absent.
- **Add a mechanical conformance test for the reference and marker rules.** Rejected (feature L5): the user's scope decision in `odd/tasks/adr-propagation-and-architecture-conformance.md` L17 and S2 removed tests from this area; enforcement is the architecture-gate obligation citation, not a new suite.
- **Add a new injected decisions-flow file to carry this narrative.** Rejected: `knowledge/decisions.md` Artifact roles and Lifecycle already carry that law, so a new `instructions` entry would duplicate injected law; the flow narrative belongs in this record's `## Context` and in `docs/README.md`.

## Consequences

- Byte equality becomes the guarantee: `core-sync check` fails on any byte difference between a source architecture file and its destination copy.
- A destination edit to a distributed architecture file is overwritten by the next write, with no `pending` entry and no reconciliation report; only a `check` run before that write reports the drift. That is a real cost of the model, accepted in exchange for removing the competing-rule slot.
- Destinations diverge in their own guides, which survive every sync because bindings are per-file. A destination needing local reference choices keeps them out of the shared tree.
- ADR 0003 is amended: its per-file `region` clearance and protected-core-plus-project-extensions model for `architecture/` is retired; its decision body stays unchanged as history.
- `knowledge/decisions.md` §Discoverability is generalized so a source-local documentation navigation route satisfies record discoverability when architecture ships whole-file; "the shared core never links a source-local record" is retained.
- No schema version change, no new injected file, documentation only. No application conformance and no destination migration is claimed.

## Propagation

The operative rules live in these owners, not in this record; acceptance is verified against the owner text rather than against this record.

- `architecture/README.md` → `## Contract boundaries` (no outward reference, complete rules, distribution identity rather than conformance) and the divergence rule under `## Ownership and extension` (never edit a distributed architecture file; add a destination-owned guide from the applicable template).
- `architecture/testing/architecture.md` → `## Purpose` authority list (the contract and the stack guides own the rules; no agent runtime is an owner) and `## Execution and evidence` (the destination owns its runner and commands; divergence is destination-owned configuration).
- `architecture/testing/stacks/typescript.md`, `architecture/testing/stacks/python.md`, and `architecture/testing/stacks/_template.md` → `## Applicability and ownership` (guide status comes from the testing contract, no owner field, destination guidance names no in-file slot).
- `distribution-clearance.json` → the 13 architecture rows, each `{"mode": "raw"}` with no directory root for `architecture/`.
- `distribution-clearance.definition.md` → `## Architecture distribution` (whole-file transport, the byte-equality guarantee, overwrite behaviour with no region, reconciliation, or `pending`, and the destination-owned divergence path), the `Architecture documents` record row under `## Record kinds`, and the `raw`-architecture clause under `## Scope rules`.
- `knowledge/decisions.md` → `### Discoverability` (generalized to a source-local navigation document, retaining that the shared core never links a source-local record).

This record's propagation targets were delivered across the two work units of `odd/tasks/architecture-whole-file-distribution.md` — the `architecture/`, registry, and definition targets in Unit A, and `knowledge/decisions.md` `### Discoverability` in Unit B; Herald 📯 (Release Manager) records the delivering commits in that feature's `## Log`, and this record remains `Proposed` until explicit user approval.
