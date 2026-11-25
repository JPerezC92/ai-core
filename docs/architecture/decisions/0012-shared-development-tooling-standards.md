# ADR 0012 — Shared development tooling standards are canonical and distributed

- **Status:** Proposed — pending review and explicit approval
- **Date:** 2026-11-24

## Context

AICore has used one formatter, one linter and one compiler policy since the code-style adoption, and carried an explicit decision that those configuration files are **not** distributed: `docs/tooling.md` recorded that a destination "chooses its own tooling; this is intentional, not an omission".

That stance produced a measured cost. Eight TypeScript projects in this repository carried byte-identical `compilerOptions` blocks — the same nineteen effective options copied eight times — and nothing in the distributed corpus mentioned a formatter or a linter at all: a destination agent received shared rules, workflows, architecture, skills and agents, and no tooling standard whatsoever. Every destination therefore had to re-derive formatting and linting policy, or invent one.

Two tool facts bound the design, both verified against the tools' own documentation rather than inferred:

- Biome merges an `extends` array left to right, combining list-valued options and applying the extending file last; paths in an extended file resolve from the **extending** config's directory (`https://biomejs.dev/reference/configuration/`).
- Oxlint's `.oxlintrc.json` extends only `rules`, `plugins` and `overrides`; `options`, `env`, `globals` and `ignorePatterns` are never inherited (`https://oxc.rs/docs/guide/usage/linter/nested-config.html`).
- EditorConfig has no include or extends directive: configuration resolves from a file's directory upward and stops at `root = true` (`https://spec.editorconfig.org/`).

## Decision

AICore is the single source of truth for the shared development tooling standards.

1. Six canonical resources live in `.aicore/core/tooling/` and are distributed as a cleared `raw` directory root: `README.md`, `editorconfig`, `biome.base.json`, `oxlint.base.json`, `tsconfig.base.json` and `tsconfig.node-direct.json`. No file there may carry a name a tool auto-loads.
2. AICore consumes what it distributes. The repository's `biome.json`, `.oxlintrc.json` and all eight `tsconfig.json` files extend the canonical files and keep only their project-owned settings: formatter scope, the linter's non-inheritable settings, and each project's inclusion paths.
3. EditorConfig remains the authority for whitespace. Biome keeps `useEditorconfig: true` and declares no indentation setting. Because EditorConfig cannot be inherited, the canonical file is a **template**: a project copies it to its own root `.editorconfig`, and AICore's operational copy is byte-identical to the distributed template.
4. Type-aware linting is a mandatory standard for applicable TypeScript projects, not an optional enhancement. Because Oxlint cannot inherit `options.typeAware`, the adoption contract states the required project-local declaration and its `oxlint-tsgolint` dependency.
5. The tooling root is a protected distribution resource: an opt-out that names it, one of its descendants, or a directory root containing it is refused as malformed bindings before any write. The distributed TypeScript-bearing skills resolve their compiler configuration from it, so its absence is a broken distribution rather than a destination preference.

This decision authorizes distribution and consumption inside AICore. It does not authorize any destination project to adopt the standards, install a dependency, change a project-owned configuration, or reformat existing code; each of those is a separate authorized task under the adoption contract.

## Alternatives

- **Publish the standards as an npm preset package.** Rejected: it needs publishing infrastructure, a registry, an install step and version resolution, and the synchronization tool cannot install or resolve it. Three JSON files delivered through a mechanism that already exists is strictly simpler.
- **Deliver a merged `biome.json` into the destination.** Rejected: merge mode replaces every source top-level key wholesale, so it would overwrite a project's formatting standard and cannot express extension. `extends` is the native, non-destructive primitive.
- **Distribute `.editorconfig` to the destination root.** Rejected: an automatic write to a project-owned configuration file would destroy legitimate project sections, and a whole-directory opt-out would then leave the project with no standard at all.
- **Document a reusable indentation rule inside `biome.base.json` and drop the EditorConfig integration.** Rejected: it duplicates the whitespace contract across three surfaces and abandons the authority that makes the repository's indentation single-sourced.
- **Share only language-level compiler strictness.** Rejected as insufficient: the direct-execution options are the remaining duplication, and — decisively — six distributed skills reference the profile, so distributing a consumer without its profile would create an unresolved dependency inside the distribution set.
- **Leave the tooling root excludable and document the broken combination.** Rejected: it would permit a distribution in which shipped consumers cannot resolve their configuration.
- **Ship per-framework compiler profiles (React, NestJS, bundled, compiled).** Rejected: no established need exists in this repository, and a profile encodes a build-system decision the destination owns.

## Consequences

- A destination receives the canonical standards with the rest of the distribution and no longer has to invent formatting or linting policy.
- Eight duplicated compiler configurations become one baseline plus one profile plus eight inclusion declarations.
- `docs/tooling.md` must stop asserting that these files are not distributed, and `distribution-clearance.definition.md` must describe the new class.
- One observable synchronization behaviour changes: excluding a path that overlaps the protected tooling root is now refused with exit status `2`. No other synchronization semantics change.
- A project that must diverge from a canonical rule gains an authorized-exception route instead of an unrecorded local override.
- Unresolved: nothing. The tested tool versions are recorded in the adoption contract; no minimum-version claim is made beyond them.

## Propagation

The operative rule lives in `.aicore/core/tooling/README.md` — its section set (applicability, consumption, project-owned settings, authorized exceptions, updates, verification, distribution) and the six files whose contents state the rules. Distribution of the directory is carried by the `cleared` entry for `.aicore/core/tooling/` in `distribution-clearance.json` and its record-kind description in `distribution-clearance.definition.md`. The protection rule lives in `PROTECTED_EXCLUSION_SOURCES` and is described in `.opencode/skills/core-sync/SKILL.md` (bindings schema and exit contract). AICore's own consumption is carried by `biome.json`, `.oxlintrc.json` and the eight `tsconfig.json` files. This record changes no architecture rule, so no document under `.aicore/core/architecture/` is its owner.
