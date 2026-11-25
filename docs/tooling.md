# Portable MCP tooling setup

This guide provides checkout-local setup instructions for **this AICore source**, not test evidence or authorization to provision before the required review gates.

**What the tracked `.opencode/opencode.jsonc` registers:** `system-one`, `chrome-devtools`, `memories`, `qmd`, `context7` (Context7 uses `{file:../.secrets/context7-api-key}`), `astgrep`, and `semgrep`.

**What ships on OpenCode enrollment:** the same list except `system-one`, which is listed in `omit_mcp_servers` on the merge clearance row. Destinations must not receive launch commands under `mcp-servers/` or `.opencode/tooling/`. Cursor enrollment ships no MCP configuration.

**Portable analysis launchers.** `astgrep` is `uvx --from git+https://github.com/ast-grep/ast-grep-mcp@149e20d47bb7125fb0c1451feea2f48a98742034 ast-grep-server`. That MCP is still the official experimental Python server; destinations need `uv` and the Rust `ast-grep` CLI on `PATH` (`sg` is not an accepted substitute). `semgrep` is `uvx --from semgrep==1.182.1 semgrep mcp` with `SEMGREP_SEND_METRICS=off` and `OTEL_SDK_DISABLED=true`. That is the official Semgrep CLI MCP, not a Node rewrite of the engine. First `uvx` run needs network.

**system-one** is this checkout's TypeScript MCP at `mcp-servers/system-one/src/mcp/stdio.ts`. It stays in the source configuration so AICore sessions load it, and merge omits it from destinations. It is launched exactly as registered — `node mcp-servers/system-one/src/mcp/stdio.ts`, run from the checkout root — and it serves one tool, `evaluate_odd_evidence`, over stdio.

**Provisioning.** `mcp-servers/system-one` sits outside `pnpm-workspace.yaml` and owns its install root, `mcp-servers/system-one/package.json`, plus its own lockfile beside it: `pnpm --dir mcp-servers/system-one install --frozen-lockfile --ignore-scripts`. It needs Node.js `>= 24` because `stdio.ts` runs as TypeScript through Node's type stripping rather than a build step.

**Configuration.** The server reads `SYSTEM_ONE_ENDPOINT` (default `http://127.0.0.1:1234`), `SYSTEM_ONE_MODEL` (default `d1-2b@q8_0`), `SYSTEM_ONE_TIMEOUT_MS` (default `15000`), `SYSTEM_ONE_PROFILE` (default the package's `profiles/odd-evidence-v4.json`), `SYSTEM_ONE_TRACE_PATH` and `SYSTEM_ONE_IMAGE_DIR`. The tracked configuration sets the first three; a blank or unusable value falls back to the documented default instead of preventing the server from starting. It expects a local LM Studio-compatible endpoint at that address.

**Operational trace.** The server records one JSON line per evaluation to `output/system1/events.jsonl` and writes that exchange's image bytes content-addressed under `output/system1/images/`; both default under the gitignored `output/` and both move with `SYSTEM_ONE_TRACE_PATH` and `SYSTEM_ONE_IMAGE_DIR`. Nothing is written to stdout, which carries protocol frames; diagnostics go to stderr. There is no plugin component: AICore agents reach these directives only by calling the MCP tool, because the MCP protocol does not inject them.

The `npx` servers need Node.js >= 22 and no separate provisioning step. There is no `.opencode/tooling/` Python project.

## External Rust prerequisite

Install the Rust ast-grep CLI version `0.51.0` with an approved platform-appropriate method, and make `ast-grep` available on `PATH`. Verify before starting its MCP server:

```text
ast-grep --version
```

The reported version must be `0.51.0`.

## Launch and privacy boundaries

Use this checkout's tracked OpenCode configuration, without embedding machine-specific executable paths. Launch OpenCode from the checkout root. The repository root carries no Python project.

Keep the existing privacy controls unchanged: the `memories` server sets `MEMORIES_SKIP_POSTINSTALL=1` and the `npx` servers set `npm_config_ignore_scripts=true`; Semgrep uses `SEMGREP_SEND_METRICS=off` and `OTEL_SDK_DISABLED=true`. Locking dependencies is not a vulnerability-cleanliness claim.

## Lint and format

One formatter and one linter cover the whole checkout, installed once at the workspace root. `mcp-servers/system-one` stays outside `pnpm-workspace.yaml` with its own lockfile, but it is reached by both tools because both read files by path and resolve each file's own `tsconfig.json`.

**Two installs are still required.** The root `pnpm install` never installs dependencies for the non-workspace root, so type-aware linting and `typecheck` over it depend on its own `node_modules` existing. Provision both before relying on `verify`.

| Concern                | Tool              | Pinned version |
| ---------------------- | ----------------- | -------------- |
| Formatting             | `@biomejs/biome`  | `2.6.8`        |
| Linting                | `oxlint`          | `1.93.0`       |
| Type-aware lint engine | `oxlint-tsgolint` | `7.0.2007`     |

Every pin is old enough to clear pnpm's default 24-hour release-age gate, so `pnpm-workspace.yaml` carries no `minimumReleaseAgeExclude` exemption. Do not add one to adopt a fresher release; wait for it to age instead.

```text
pnpm format          # rewrite the tree with Biome
pnpm format:check    # read-only: report files that are not formatted
pnpm lint            # oxlint, type-aware, all three source trees
pnpm lint:fix        # oxlint with mechanical fixes
pnpm typecheck       # tsc in the seven workspace packages plus the non-workspace mcp-servers/system-one
pnpm verify          # format:check + lint + typecheck; never writes
pnpm verify:full     # verify, then every package's test suite and the CLI end-to-end suite
```

**`.editorconfig` is the single source of indentation.** `biome.json` sets `formatter.useEditorconfig: true` and deliberately declares no `indentStyle`, `indentWidth` or `lineEnding`, because a value in `biome.json` takes precedence and would silently desynchronize the two files. That absence is the whole guarantee, so it is an invariant: never add those keys to `biome.json`. TypeScript and JavaScript use real tab characters at four columns; JSON, JSONC, YAML and Markdown use two spaces; Markdown keeps trailing whitespace because two trailing spaces are a hard line break. Apart from the scope keys described below, `biome.json` owns only what EditorConfig cannot express: line width, quote style, semicolons, and the Markdown parser and formatter options. The canonical statement of the whitespace contract is the distributed template at `.aicore/core/tooling/editorconfig`; this root file is its operational copy, and the two must stay byte-identical. EditorConfig has no include mechanism, so the template reaches a destination as a file to copy rather than as an inherited configuration.

**Markdown is formatted, with two safeguards.** `markdown.parser.frontmatter` is explicitly `true`; when it is left at its `false` default Biome does not recognize YAML frontmatter and reflows the block as prose, which flattens nested keys and destroys the document's metadata. `markdown.formatter.formatEmbeds` is explicitly `false`, so fenced code and frontmatter are preserved byte-for-byte instead of being re-indented by their own language formatter.

**Scope is declared, not subtracted.** `files.includes` is `["**"]` and carries no negation, so every tracked file is in the formatter's scope and no file is excused by path. `output/` and `.secrets/` are gitignored and stay out of the tree through `vcs.useIgnoreFile`. pnpm's lockfiles need no exclusion: Biome does not process a file named `pnpm-lock.yaml` at any depth (verified over both tracked lockfiles, the root one and `mcp-servers/system-one/pnpm-lock.yaml`), and `pnpm-workspace.yaml`, which Biome does process, is already format-stable.

**ODD change records are outside the Markdown formatter's scope.** One `overrides` entry sets `markdown.formatter.enabled: false` for `odd/tasks/**/*.md`, because a change record's job includes quoting the user's request verbatim and Biome 2.6.8 damages that content. Measured on copies of the affected records with this repository's own `.editorconfig` and `biome.json`: on a record whose verbatim quotation contains a quote-marker-only line directly after a heading inside a blockquote nested in a list item, each `--write` pass adds two more spaces of indentation to that line, so three passes produce three different files and `format` still exits 1; on two other records a single pass converges only by deleting 21 and 26 blank lines from inside the quotation. No configuration option reaches either defect — the Markdown formatter exposes `enabled`, `formatEmbeds`, `indentStyle`, `indentWidth`, `lineEnding`, `lineWidth`, `proseWrap` and `trailingNewline`, none of which governs blockquote idempotency or blank-line retention inside a quotation. Scope is therefore the only lever, and it is applied to the class of document that quotes requests rather than to individual files.

**Markdown stays formatted everywhere else.** `odd/features/`, `docs/`, the skills and every other Markdown surface remain in the formatter's scope and are checked by `format:check`. A durable feature file states requirements in its own words rather than quoting a request, so it carries no verbatim content for the formatter to damage.

**Change records are validated structurally instead.** Because the formatter no longer touches `odd/tasks/`, the ODD validator is the structural gate on those documents: it rejects an unbalanced code fence, and every rule that reads a record — its title and header metadata, its Specs, Tasks and Log entries, its Log-identifier ordering, its Close entry, its user-cancellation authorization, its superseded-record obsolescence explanation, its placeholders and its retirement eligibility — reads only text outside fenced blocks. A record whose fence never closes fails validation rather than rendering its Log as code. See `.agents/skills/odd-workflow/SKILL.md` for the validator's contract.

**These files are distributed.** `.editorconfig`, `biome.json`, `.oxlintrc.json` and the eight project `tsconfig.json` files are this repository's own consumption of the shared tooling standard in `.aicore/core/tooling/`, which is cleared for distribution with its adoption contract. Each of those project files extends a canonical file and keeps only what it owns: the formatter's scope, the linter's non-inheritable settings, and each project's inclusion paths. A destination receives the canonical files and decides for itself, under the adoption contract, whether and when to consume them; receiving them installs nothing and changes no project configuration.

**Scope of the lint rules.** `import/no-relative-parent-imports` is enforced across all three source trees (`cli/**`, `.agents/skills/**`, `mcp-servers/system-one/**`), and it is the only mechanical check of this convention: it enforces the parent-traversal prohibition and nothing else. Outside it, each tree resolves a cross-directory import through the package's own `#`-prefixed Node subpath import map declared in its `package.json` — the mechanism Node ESM, `tsc` and Vitest all honour without extra configuration or dependencies — or through a relative specifier into a child directory of the importing module's own directory. `typescript/unbound-method` is disabled for test files, where `expect(port.method)` is a legitimate reference to an unbound method.

`pnpm lint` reports no errors and no warnings. Nine warnings that the adoption first surfaced — six `no-misused-spread` in the validators that iterate string code points, and three `no-base-to-string` where a value is stringified into a message — were corrected rather than suppressed or written around; the fixes changed validation behavior or message content, so they were delivered as a separate, behavior-bearing change outside the mechanical formatting slice.

## TypeScript module resolution and imports

This section is AICore's own binding for how TypeScript modules name their targets. The architecture obligation it serves lives in `.aicore/core/architecture/` and is distributed; this document is not, so the concrete mechanism recorded here stays project-owned and no destination inherits it. Three source trees are covered: `cli/aicore`, `.agents/skills/*`, and `mcp-servers/system-one`.

### Specifier scope

Three kinds of specifier are never conflated.

1. **Internal references** name a module of the same package: a relative specifier that stays in the importing module's directory or descends into one of that directory's child directories, or a `#` alias declared in that package's own `imports` map. They are private — no other package can name them.
2. **Declared external dependencies** are Node.js built-in modules, third-party packages and other workspace packages. They are named by the dependency identity the manifest declares and resolved through that dependency's own published entry points. They are never routed through the importing package's `#` map, and a filesystem path into another package's tree is not a dependency.
3. **The package's public surface** is exactly what its `exports` field publishes. Adding a public entry point is an `exports` change, never an alias change.

### Source extensions

Every specifier that names a project file carries that file's source extension — `.ts`, `.tsx`, `.mts` or `.cts` — on relative and aliased references alike. Parent-directory traversal (`../`) is not used; a relative specifier may stay in the importing module's directory or descend into a child directory of that directory, and `cli/aicore/src/infrastructure/reconciliation-reader.ts`, `cli/aicore/src/domain/outcomes.ts` and `.agents/skills/incident-workflow/scripts/init_local_registers.ts` use that child-directory form for nine specifiers, which are accepted as compliant rather than pending migration. AICore's current trees are uniform under the remaining rules: 107 relative and 798 aliased specifiers across 302 files, all carrying `.ts`, with no `../` and no extensionless reference.

Each project keeps `module` and `moduleResolution` at `NodeNext`, `noEmit` and `allowImportingTsExtensions` while it executes TypeScript directly. No project declares `paths` or `baseUrl`.

### One alias mechanism per package

A package that declares aliases declares them in its own `package.json#imports`, keyed with `#`; the alias is preferred where it makes a cross-directory or cross-layer reference clearer, and a child-directory relative specifier remains valid where a module uses it instead. AICore uses the extensionless-key form, where the extension arrives in the specifier: `"#domain/*": "./src/domain/*"` resolves `#domain/constants.ts` to `./src/domain/constants.ts`. A second form, where the key carries the `.ts` trailer and the specifier does not, is equally valid internally but mixing both in one package is not.

Directly executed packages point those maps at their sources. A compiled package points them at its build output with the trailer form, `"#domain/*.ts": "./dist/domain/*.js"`, because a compiled target must not receive the source extension.

### Production modes

**Direct execution.** A package runs `node <path>.ts` with no build step and no additional loader. Type stripping requires the extension to be present somewhere the runtime can see it, which the specifier or the map target supplies. `.tsx` is not executable this way: Node rejects the extension outright, so JSX belongs only to bundled code.

**Bundled application.** A bundler erases the imports it consumes, so `.ts` and `.tsx` specifiers are both usable, and a type check runs separately with `noEmit`. Native `#` maps are usable where the selected bundler resolves them, either through its own support for the manifest map or through alias resolution it is explicitly configured with and that has been validated; a project alias declared only in `tsconfig` is resolved by nothing else.

**Compiled package.** Emitted JavaScript keeps `#` specifiers verbatim and rewrites relative `.ts` specifiers to `.js`, which is what `rewriteRelativeImportExtensions` provides; `allowImportingTsExtensions` is not needed there. Source-side type checking still resolves `#` specifiers through the map: with `rootDir` and `outDir` corresponding to the source and output layout, the compiler maps a compiled target back to its source file rather than requiring a build first. Emitted declarations keep both `#` and relative `.ts` specifiers and resolve against their sibling declaration files, so a published package does not need to ship its sources.

### Alias permission

A TypeScript `paths` alias is permitted only where the selected build or runtime pipeline actually resolves it. A passing type check alone does not establish that: Node resolves `imports` and `exports`, not `paths`, and a bundler resolves `paths` only when its own configuration mirrors them. AICore's three trees therefore use no `paths` alias at all, and no cross-package dependency may be expressed as one.

### What is mechanically enforced

`tsc` under `NodeNext` is the real check: it validates each `imports` map, rejects an extensionless or wrongly extended specifier, and refuses a package specifier that the dependency's `exports` does not publish. `import/no-relative-parent-imports` adds the `../` prohibition only; no lint rule can express the preference between an alias and a permitted child-directory relative specifier, so that part of this standard is a convention the reviewer enforces, not a check the toolchain performs.

A monorepo task orchestrator is not a module resolver and adds no requirement here: package boundaries, declared dependencies and `exports` are what make a workspace resolvable. Cache and ignore-file configuration are operational concerns of whichever orchestrator a project selects, not part of this standard.
