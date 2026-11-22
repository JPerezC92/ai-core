# Scripts and tooling application shape

## Applicability

Scripts, CLIs, and tooling operations, including independently deployed tooling packages. Read `.aicore/core/architecture/implementation/architecture.md` first. A smaller executable does not suspend the common contract. The layout and operation obligations below bind at L3 (`C11`); at L1 and L2 a script keeps its own organization, needs no layer folder and no operation class, and may orchestrate external effects directly (`C12`).

## P1 — Responsibilities

Domain contains data-only constants and pure transformations. Transformations receive typed input data, never perform filesystem/network IO. When a script domain has identity and invariants, it may use the stack entity representation; data-only constants, pure transformations, and TypedDict records remain valid, and not every script type must become a class. A script type that claims identity and invariants but leaves its rules to callers is not a record; it is a nonconforming entity. At L3, application operations take typed parameters and injected domain IO ports and expose `execute()` returning typed domain results/errors (C3); at L1 and L2 no operation form is imposed (`C11`, `C3`). Pure helpers retain the common helper exemption.

## P2 — IO and delivery

Infrastructure loaders/builders/clients implement ports, perform IO, and map external data to domain objects without business rules; the outside-data mapping modules live in `infrastructure/adapters/`, a repository adapter, where an aggregate model is used, lives in `infrastructure/repositories/`, and each directory is created only where its responsibility exists. The script/server entry point constructs adapters; its delivery handler calls the operation and serializes domain results/errors outside it. File, subprocess, and network effects stay at the entry point or a clearly named infrastructure IO helper.

The delivery handler is the Interface responsibility (C12): it parses the channel input, maps it in one step, delegates, and binds the result to exit status or output. At L3 it depends on application and domain modules only and imports no concrete adapter or IO helper from `infrastructure/`, even when both live there (`C13`); an independent folder, where C13's evidence authorizes one, is `interfaces/` at the same level as the layer folders. The published contract of the channel the handler serves — a CLI's exit codes and output streams, an HTTP response, or an MCP tool result — follows the external output contract (C14).

## P3 — Deployment boundaries

Independent backend tooling packages, standalone ticket scripts, and feature-scoped skill scripts remain separate implementation zones. Their concrete package/import/startup conventions belong in the stack guide; runtime authorization for exact scripts and after-edit gates remains in agent specs.

## P4 — Business-owned domain organization

Within each deployment zone, group domain modules by business concept. Keep an aggregate's root, children, owned values, events and repository port together when that model is used (C8, C9); a root-only model needs no child scaffolding. One entity per file including children, and one rule-bearing type per module; no generic multi-concept entity/model/value-object buckets.

At the second same-role module within an ownership level, introduce the role folder there, retaining aggregate-owned parts inside their aggregate folder. Pure transformation modules and intentional records keep their own C8/C10 roles, not artificial classes. Constants remain data-only under P1. Infrastructure owns rows/models, delivery owns request/response records; domain read projections remain framework-free. The language guide spells this layout without crossing P3 deployment boundaries.

## Testing selection

Use the current `.aicore/core/architecture/testing/architecture.md` and applicable stack guide. Importable CLI code is not automatically a unit boundary; test-design authority stays there.
