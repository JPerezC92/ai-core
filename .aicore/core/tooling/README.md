# Shared development tooling standards

This directory is the canonical source of the shared formatting, linting and compiler standards. It holds the rules; a project holds its own configuration that consumes them. Every file here is distributed to a destination unchanged, and a project never edits one in place.

**Receiving these files is not adopting them.** They arrive as part of the shared distribution. They install nothing, change no project configuration, format nothing, and authorize no edit. Adoption is a separate, authorized task in the project that consumes them.

**If a file this document names is missing, report the missing resource and stop the affected adoption.** Never skip an applicable standard, substitute a local guess, or proceed as though the standard did not exist.

## What is here

| File                        | Role                                                                                                                          |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `editorconfig`              | The canonical whitespace and indentation contract. Inert by design: a copy becomes the project's operational `.editorconfig`. |
| `biome.base.json`           | The canonical formatter configuration, consumed through Biome's native `extends`.                                             |
| `oxlint.base.json`          | The canonical lint configuration, consumed through Oxlint's native `extends`.                                                 |
| `tsconfig.base.json`        | The language-level TypeScript compiler standards.                                                                             |
| `tsconfig.node-direct.json` | The direct-execution TypeScript profile, which extends the baseline above.                                                    |

A file's own contents are the normative statement of its rules. This document does not restate them, and a project must not copy them: the values live in exactly one file each.

## Applicability

| Standard                        | Required when                                                                                                                                          | Not applicable when                                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Formatter (`biome.base.json`)   | The project holds any file Biome formats: JS, TS, JSX, TSX, JSON, JSONC, CSS, GraphQL, Markdown                                                        | The project holds none of those file types                                                                                                  |
| EditorConfig (`editorconfig`)   | The project formats code with Biome, because indentation is the EditorConfig contract and Biome reads it                                               | The project uses no EditorConfig-aware tooling and no Biome                                                                                 |
| Linter (`oxlint.base.json`)     | The project holds JavaScript or TypeScript sources                                                                                                     | The project holds no JS/TS source                                                                                                           |
| Type-aware linting              | The project lints TypeScript with Oxlint **and** has a `tsconfig.json` covering its sources. This is a mandatory standard, not an optional enhancement | The project has no TypeScript source. A project with TypeScript but no `tsconfig.json` coverage has a prerequisite to fix, not an exemption |
| TypeScript baseline and profile | The project has a TypeScript compiler configuration                                                                                                    | The project has no TypeScript                                                                                                               |

A language with no standard here (for example Python) is not covered by this document; its structure requirements live in the architecture guides, and its formatting and linting tools are the project's own choice.

## Discovery

This document is reached from the root runtime's mandatory reading and from the workflow's task navigation. Consult it before creating, changing or replacing a `biome.json`, `.oxlintrc.json`, `tsconfig.json`, or `.editorconfig`, before adding a format, lint or typecheck command, and before defining any rule that would duplicate one stated here. Those activities require consulting this document; no other activity does.

## Dependencies

Install these in the project that consumes them, with the project's own authorization:

| Tool              | Tested version | Purpose                                                     |
| ----------------- | -------------- | ----------------------------------------------------------- |
| `@biomejs/biome`  | `2.6.8`        | Formatter                                                   |
| `oxlint`          | `1.93.0`       | Linter                                                      |
| `oxlint-tsgolint` | `7.0.2007`     | Type-aware lint engine, required by the type-aware standard |
| `typescript`      | `6.0.3`        | Type checker                                                |

The tested versions are the versions these files are verified against. This document claims no minimum supported version beyond them: the `extends` forms used below are verified at those versions, and a project adopting an older release is testing an unverified combination. Keep formatter and linter responsibilities separate — Biome formats, Oxlint lints, and neither is asked to do the other's job.

## Consuming the standards

Three native inheritance mechanisms, no loader and no generator.

**Formatter.** The project's `biome.json` extends the canonical base and declares only its own scope:

```json
{
  "$schema": "https://biomejs.dev/schemas/2.6.8/schema.json",
  "extends": ["./<path-to-distributed>/.aicore/core/tooling/biome.base.json"],
  "files": { "includes": ["**"] }
}
```

**Linter.** The project's `.oxlintrc.json` extends the canonical base and declares the settings Oxlint cannot inherit:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "extends": ["./<path-to-distributed>/.aicore/core/tooling/oxlint.base.json"],
  "options": { "typeAware": true },
  "env": { "node": true },
  "plugins": ["node"],
  "ignorePatterns": ["**/node_modules/**", "**/dist/**"]
}
```

`rules`, `plugins` and `overrides` are inherited. `options`, `env`, `globals` and `ignorePatterns` are **not** — Oxlint extends only those three keys — so a project declares its own, and that duplication is a property of the tool, not of this standard. `env`, `plugins` additions and `ignorePatterns` are project-owned: a browser project sets its own environment and drops the `node` plugin.

**Compiler.** The project's `tsconfig.json` extends the profile and keeps only its own inclusion:

```json
{
  "extends": "./<path-to-distributed>/.aicore/core/tooling/tsconfig.node-direct.json",
  "compilerOptions": {
    "target": "ES2024",
    "lib": ["ES2024"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "types": ["node"],
    "noEmit": true,
    "allowImportingTsExtensions": true,
    "erasableSyntaxOnly": true,
    "verbatimModuleSyntax": true
  },
  "include": ["src/**/*.ts", "tests/**/*.ts"]
}
```

The profile's keys are the direct-execution tier: TypeScript runs under Node's type stripping with no build step. A project that bundles or compiles instead selects its own `target`, `module`, `moduleResolution` and `jsx` and extends `tsconfig.base.json` directly; the language-level standards are inherited either way, and the project's own settings are the only ones it states.

**EditorConfig.** EditorConfig has no include or extend directive, so the canonical file is a template rather than an inherited configuration. Create the project's root `.editorconfig` from it, then add the project's own sections after it:

```text
# Copy the canonical `editorconfig` file here, then append project sections,
# for example:
[*.py]
indent_style = space
indent_size = 4
```

Keep `root = true` in the copy. Every section the canonical template states stays as written: indentation and line endings are the contract the formatter reads, and a project overrides them only as an authorized exception. After the copy, the formatter's own configuration must declare no indentation setting, because the formatter reads it from this file.

**Commands and verification.** Expose the standard entry points in the project's package scripts and compose them into one verification command that never writes:

```json
{
  "scripts": {
    "format": "biome format --write .",
    "format:check": "biome format .",
    "lint": "oxlint",
    "lint:fix": "oxlint --fix",
    "typecheck": "tsc --noEmit",
    "verify": "pnpm format:check && pnpm lint && pnpm typecheck"
  }
}
```

**Work layouts.** A single-package project places one configuration of each kind at its root. A workspace places the same files at the workspace root, and a package that needs different rules adds its own configuration that extends the workspace root through the tool's native mechanism: Biome resolves a nested `biome.json` with `"extends": ["//"]`, and Oxlint reads a nested `.oxlintrc.json` that extends `"../../.oxlintrc.json"`. A nested configuration narrows scope or adds rules; it never disables a canonical rule.

## Adopting in a new project

1. Confirm which standards apply from the table above.
2. Add the dependencies for those standards, with the project's own authorization.
3. Add the project-local files shown above, with the canonical files' relative path resolved for the project's layout.
4. Copy the canonical `editorconfig` to the project root and append any language-specific sections the project needs.
5. Add the verification scripts.
6. Run the formatter, the linter and the type checker; all three must exit clean before the adoption is complete.
7. Record the adoption in the project's own documentation.

A project must not define its own formatting or linting rules before consulting this document. Equivalent rules written locally are a duplication defect, not a project decision.

## Adopting in an existing project

This is a procedure for a separate, authorized task. Performing it is not part of receiving these files.

1. **Inspect** the project's existing formatter, linter, compiler and EditorConfig configuration, and every command that runs them.
2. **Classify** each declared setting as _canonical_ (the canonical file already states it), _project-owned_ (the lists below), or _incompatible_ (it would weaken a canonical rule).
3. **Identify behavior changes.** Note every file the formatter would rewrite, every rule the linter would newly report, and every compiler option whose effective value changes. Report them before changing anything.
4. **Obtain authorization.** Adopting the standard does not authorize reformatting the tree, fixing new lint findings, or changing existing code. Those are separate decisions with their own evidence.
5. **Make the minimal edit.** Add the `extends` entry, delete only the settings the canonical file now supplies, and keep every project-owned setting.
6. **Verify effective consumption** as described below, and record what changed.

Duplicated or conflicting rules are resolved by deleting the local copy, not by reconciling two sources: the canonical file is the single home of every rule it states.

## Project-specific settings

These stay project-owned and need no authorization. They are the design, not an exception:

| Tool         | Project-owned settings                                                                                                                                                                                                                            |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Biome        | `files.includes` and any `overrides` for the project's own paths; `vcs` settings beyond the inherited defaults                                                                                                                                    |
| Oxlint       | `env`, `globals`, `options` (including `typeAware`), `ignorePatterns`, and additional `plugins`                                                                                                                                                   |
| TypeScript   | `target`, `lib`, `module`, `moduleResolution`, `jsx`, `types`, `noEmit`, `allowImportingTsExtensions`, `erasableSyntaxOnly`, `verbatimModuleSyntax`, `rootDir`, `outDir`, `paths` where the build pipeline resolves them, and `include`/`exclude` |
| EditorConfig | Sections for languages the canonical template does not cover, and the project's own trailing-whitespace choices outside the inherited sections                                                                                                    |

## Authorized exceptions

An exception is a setting that **weakens** a canonical rule: a different quote style, a canonical rule disabled, a formatter or linter responsibility moved to another tool, or type-aware linting dropped.

- An exception requires explicit authorization from the project's decision-holder.
- It is written down in the project's own documentation, naming the canonical rule it departs from and why.
- It is never made by silently declaring a competing rule in the project's configuration.
- A project may always add a rule; it may not weaken one without authorization.

## Updates and compatibility

Receiving updated canonical files is not authorization to modify project-owned configuration, install a dependency, or change existing code.

- A new canonical file version arrives with the shared distribution.
- Re-read this document when the tested versions change; a dependency update is a separate, authorized action.
- A canonical change that alters formatting or linting results is reported as a potential behavior change before the project runs the formatter or the linter over its tree.
- After an update, re-verify effective consumption (below). A canonical change and a local exception may conflict; the exception is revisited by its owner, never discarded silently.

## Verifying effective consumption

Prefer the tools' own output over a hand-written checker:

| Claim                                                    | How to verify                                                                                                                                                              |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The project's configuration resolves the canonical files | Run the formatter and the linter. An unresolvable `extends` target is a tool error, not a silent fallback                                                                  |
| The project's own config supplies no duplicate rules     | Read the project's configuration files; every rule they state is either project-owned or a recorded exception                                                              |
| Applicable code is covered                               | `biome format --verbose .` lists every processed file; `oxlint --debug=files` lists every file the linter will lint. Compare those lists against the project's source tree |
| The commands reference the intended configuration        | Run the verification script and read its output; a formatter or linter invoked with `--config` pointing elsewhere is a defect                                              |
| Local settings do not weaken the canonical rules         | `oxlint --print-config <file>` prints the effective configuration; compare its rules, plugins and overrides against the canonical file                                     |
| The compiler standards still apply                       | `tsc --showConfig -p .` prints the effective compiler options and the resolved file list; the inherited options must be present                                            |
| Formatting and linting responsibilities stay separate    | The formatter's linter is disabled and the linter performs no formatting; neither tool is configured to take the other's place                                             |

## Distribution

Every file here is distributed unchanged and cannot be excluded from a destination's distribution: the distributed skills resolve their compiler configuration from this directory. A destination receives the whole directory or none of it.
