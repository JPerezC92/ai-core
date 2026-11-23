# TypeScript import standard documentation

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-23
> **Objective:** Document the accepted TypeScript module-resolution and import standard as the AICore-specific binding and as distributable architecture guidance, without changing source, behaviour, build configuration or dependencies.
> **Branch:** `docs/typescript/import-standard`, created by Herald 📯 (Release Manager) from the fetched base before the first work-unit commit.
> **Delivery:** Strategy `single-pr`. Authored additions and deletions forecast roughly 320–360 lines across two work units — the AICore-specific standard, then the distributed guidance — plus the record and closure edits, below the ~400-line review budget, so no chained delivery is needed. Slice boundaries: WU1 is the AICore-specific standard alone; WU2 is the new scripts guide with the two aligned guides and the navigation row. Rollback boundaries: WU1 reverts by removing the added section from the AICore-specific tooling document; WU2 reverts by deleting the new guide, restoring the two aligned import paragraphs and the mapping cells, and removing the navigation row, without touching WU1. Focused checks: WU1 and WU2 each run per-file `biome format` over their own changed Markdown plus the two ODD validators, and the repository-wide `pnpm lint` and `pnpm typecheck` after the second unit; observed results are recorded in the Log.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`. Per-file formatting is checked with `biome format <path>` rather than the repository-wide gate, because that gate is already red on two unrelated ODD records outside this scope.

## Specs

- S1 — The AICore-specific TypeScript standard is documented. Exact requirement: "U1 — AICore-specific standard - Modify `docs/tooling.md`." Acceptance: read the added section in the AICore tooling document; it states the source-extension rule, the native `#imports` binding with its exact map shapes per production mode, and the enforcement surface.
- S2 — The verified conventions are preserved rather than reinterpreted. Exact requirement: "Preserve the verified `.ts` source-import convention, native `#imports`, cross-package dependencies through public `exports`, and the documented distinctions between direct execution, bundling and compiled packages." Acceptance: compare each documented statement with the accepted compatibility evidence; all four conventions are stated and none contradicts that evidence.
- S3 — A TypeScript scripts guide exists and follows the canonical guide template. Exact requirement: "Create `stacks/typescript/scripts.md` using the canonical guide template." Acceptance: open the new guide; its heading order matches the implementation-guide template and every common obligation and scripts-shape obligation row cites the section that carries it.
- S4 — The backend guide's import conventions are aligned. Exact requirement: "Align the import conventions in `stacks/typescript/nestjs.md`." Acceptance: read its imports section; it states the shared principles with its own alias mechanism, treats a workspace package as a declared dependency rather than an alias, and its dependency obligation row names that section.
- S5 — The frontend guide's import conventions are aligned without replacing its aliases. Exact requirement: "Align the import conventions in `stacks/typescript/react.md`." Acceptance: read its imports section; it retains its project aliases, conditions alias use on the bundler actually resolving them, admits native `#` imports only where the bundler resolves them unaided, and its dependency obligation row names that section.
- S6 — The new guide is discoverable from architecture navigation. Exact requirement: "Update `architecture/README.md` navigation." Acceptance: read the implementation-guide table; it lists the new guide with its application shape and status, and the named path resolves to an existing file.
- S7 — Alias permission is conditioned on a real resolver, and no probe result is over-claimed. Exact requirement: "TypeScript `paths` aliases are permitted only where the chosen build/runtime pipeline actually resolves them. TypeScript type checking alone is not sufficient. Do not imply that NestJS compatibility was verified by the Vite integration probe." Acceptance: read the three changed documents; every alias permission requires an actual resolving pipeline, and no statement claims NestJS, Node or browser runtime verification from the Vite integration evidence.
- S8 — Turborepo caching is not stated as an import-resolution requirement. Exact requirement: "Turborepo caching and `.gitignore` configuration are operational concerns, not mandatory TypeScript import-resolution rules." Acceptance: search the changed documents; no cache or ignore-file configuration is presented as a rule a package must satisfy to resolve a specifier.
- S9 — No collateral change outside documentation. Exact requirement: "Do not change existing source imports, runtime behavior, build configurations, dependencies, or project entry points." Acceptance: inspect the changed-path list at the delivered commit; it contains documentation and record paths only, with no source, configuration, dependency or entry-point file.
- S10 — DEBT-049 is not resolved by this change. Exact requirement: "DEBT-049 remains open until its independent closure criteria are satisfied." Acceptance: read the accepted-debt register entry; it is unchanged, still open, and still carries its resolution criteria.
- S11 — Turborepo is not introduced into the repository. Exact requirement: "Do not introduce Turborepo into AICore." Acceptance: inspect the workspace manifest and task configuration files at the delivered commit; no Turborepo dependency, workspace member or task file is present.
- S12 — No unrelated architecture contract is modified. Exact requirement: "Do not modify unrelated architecture contracts." Acceptance: inspect the changed-path list at the delivered commit; the only architecture documents it names are the new scripts guide, the two aligned TypeScript guides and the architecture navigation file.

## Tasks

- T1 | S1, S2 | inline (settled specialist text transcribed into its project-owned home) — Cipher 🔓 (Lead Orchestrator) | done | commit: 7a2d4f5
- T2 | S3 | inline (new guide from the canonical template, mirroring the established scripts-zone counterpart) — Cipher 🔓 (Lead Orchestrator) | done | commit: 179a04b
- T3 | S4, S6 | inline (alignment paragraph plus navigation row) — Cipher 🔓 (Lead Orchestrator) | done | commit: 179a04b
- T4 | S5, S6 | inline (alignment paragraph plus its dependency mapping cell) — Cipher 🔓 (Lead Orchestrator) | done | commit: 179a04b
- T5 | S7, S8, S9, S10, S11, S12 | inline (verification evidence for the constraint set) — Cipher 🔓 (Lead Orchestrator) | done | commit: 179a04b

## Log

- L1 — Original request, verbatim:

  "# AICore — TypeScript Standardization Implementation

  The isolated full-stack integration probe is accepted as sufficient compatibility evidence for the tested environment.

  No additional application prototypes or broad compatibility investigations are required.

  Implement only the approved TypeScript standardization documentation workstreams, preserving the exact inventory previously reviewed:

  **U1 — AICore-specific standard**
  - Modify `docs/tooling.md`.

  **U2 — Distributed architecture guidance**
  - Create `stacks/typescript/scripts.md` using the canonical guide template.
  - Align the import conventions in `stacks/typescript/nestjs.md`.
  - Align the import conventions in `stacks/typescript/react.md`.
  - Update `architecture/README.md` navigation.
  - Create the required ODD records.

  Apply the existing Bastion and Atrium specialist wording, with two clarifications:
  1. TypeScript `paths` aliases are permitted only where the chosen build/runtime pipeline actually resolves them. TypeScript type checking alone is not sufficient. Do not imply that NestJS compatibility was verified by the Vite integration probe.
  2. Turborepo caching and `.gitignore` configuration are operational concerns, not mandatory TypeScript import-resolution rules.

  Preserve the verified `.ts` source-import convention, native `#imports`, cross-package dependencies through public `exports`, and the documented distinctions between direct execution, bundling and compiled packages.

  Do not change existing source imports, runtime behavior, build configurations, dependencies, or project entry points.

  Do not introduce Turborepo into AICore.

  Do not modify unrelated architecture contracts.

  DEBT-049 remains open until its independent closure criteria are satisfied.

  Use the established ODD process, architecture ownership, independent review, and Herald-only Git workflow. Do not merge without explicit user authorization.

  Report the final changed-file inventory, validation evidence, review findings and PR status."

- L2 — Bootstrap: this record and the durable feature file `odd/features/typescript-module-resolution.md` were created as the sole authorized bootstrap writes, before any documentation edit. Classification is non-small: the change establishes a normative standard, creates a distributed guide and touches architecture navigation, so it is not resumable from the request plus a diff alone. The ownership and neutrality rules in `.aicore/core/architecture/README.md` were re-read and no rule in that document is changed; its only later edit is the navigation row this change adds.
- L3 — Authoring basis: the import wording in the three guides is the specialists' own approved text — the backend guide text returned by Bastion 🧱 (Backend & Scripts Architect) and the frontend guide text returned by Atrium 🏛️ (Frontend Architect) in this feature's review round — with the user's two clarifications applied. Cipher 🔓 (Lead Orchestrator) transcribes that approved text rather than drafting a competing standard; independent review remains required.
- L4 — Authorization boundary: the user's instruction authorizes this bounded documentation work. The 2026-11-13 deferral in DEBT-049 is not treated as lifted in general, and DEBT-049 is not resolved, retired or edited here; its own closure criteria remain unsatisfied and record the outstanding architecture-integrity accounting.
- L5 — Full feature mirror: pending recovery, not synchronized. No verified full-copy write and independent read-back of this record was performed against the configured memory backend in this change, so the repository record remains the sole authority and no mirror claim is made.
- L6 — WU1 delivered in `7a2d4f5`: the AICore-specific standard in the tooling document, with this record and the durable feature file. Focused check: per-file `biome format` converged on the changed Markdown, and both ODD validators exit 0.
- L7 — WU2 delivered in `179a04b`: the new scripts guide, the aligned backend and frontend import paragraphs with their mapping cells, and the navigation row. Repository-wide `pnpm lint` and `pnpm typecheck` are clean, and no Turborepo dependency, workspace member or task file exists anywhere in the repository.
- L8 — Round 1 independent acceptance at `179a04b` returned findings from three acceptors. Bastion 🧱 found a mapping cell naming a section that does not exist and an unsupported coverage claim on the script-organization row; Atrium 🏛️ found a frontend citation asserting an applicability the cited guide disclaims, and an identifier attached to a fact that identifier does not state; Sentinel 🛡️ found two over-broad specifications, a missing specification for the unrelated-contract prohibition, and absent per-unit focused checks. All were adjudicated real, in scope and mechanically fixable, and are corrected in the remediation commit that carries this entry.
- L9 — Blocked: the open closure prerequisite is independent semantic acceptance of the remediation round, which must return at the remediation commit before the closure edit is written and committed.
