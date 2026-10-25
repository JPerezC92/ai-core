<!-- core:begin -->
# Scripts and tooling application shape

## Applicability

Scripts, CLIs, and tooling operations, including independently deployed tooling packages. Read `architecture/clean-architecture.md` first. A smaller executable does not suspend the common contract.

## P1 — Responsibilities

Domain contains data-only constants and pure transformations. Transformations receive typed input data, never perform filesystem/network IO. Application operations take typed parameters and injected domain IO ports and expose `execute()` returning typed domain results/errors. Pure helpers retain the common helper exemption.

## P2 — IO and delivery

Infrastructure loaders/builders/clients implement ports, perform IO, and map external data to domain objects without business rules. The script/server entry point constructs adapters; its delivery handler calls the operation and serializes domain results/errors outside it. File, subprocess, and network effects stay at the entry point or a clearly named infrastructure IO helper.

## P3 — Deployment boundaries

Independent backend tooling packages, standalone ticket scripts, and feature-scoped skill scripts remain separate implementation zones. Their concrete package/import/startup conventions belong in the stack guide; runtime authorization for exact scripts and after-edit gates remains in agent specs.

## Testing selection

Use the current `architecture/testing/architecture.md` and applicable stack guide. Importable CLI code is not automatically a unit boundary; test-design authority stays there.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
