# Portable MCP tooling setup

This guide provides checkout-local setup instructions for **this AICore source**, not test evidence or authorization to provision before the required review gates.

**What the tracked `.opencode/opencode.jsonc` registers:** `system-one`, `chrome-devtools`, `memories`, `qmd`, `context7` (Context7 uses `{file:../.secrets/context7-api-key}`), `astgrep`, and `semgrep`.

**What ships on OpenCode enrollment:** the same list except `system-one`, which is listed in `omit_mcp_servers` on the merge clearance row. Destinations must not receive launch commands under `mcp-servers/` or `.opencode/tooling/`. Cursor enrollment ships no MCP configuration.

**Portable analysis launchers.** `astgrep` is `uvx --from git+https://github.com/ast-grep/ast-grep-mcp@149e20d47bb7125fb0c1451feea2f48a98742034 ast-grep-server`. That MCP is still the official experimental Python server; destinations need `uv` and the Rust `ast-grep` CLI on `PATH` (`sg` is not an accepted substitute). `semgrep` is `uvx --from semgrep==1.182.1 semgrep mcp` with `SEMGREP_SEND_METRICS=off` and `OTEL_SDK_DISABLED=true`. That is the official Semgrep CLI MCP, not a Node rewrite of the engine. First `uvx` run needs network.

**system-one** is this checkout's TypeScript MCP at `mcp-servers/system-one/src/mcp/stdio.ts`. It stays in the source configuration so AICore sessions load it, and merge omits it from destinations.

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

One formatter and one linter cover the whole checkout, installed once at the workspace root. `mcp-servers/system-one` and `.opencode/plugins/odd-adviser` stay outside `pnpm-workspace.yaml` with their own lockfiles, but they are reached by both tools because both read files by path and resolve each file's own `tsconfig.json`.

**Three installs are still required.** The root `pnpm install` never installs dependencies for the two non-workspace roots, so type-aware linting and `typecheck` over them depend on their own `node_modules` existing. Provision all three before relying on `verify`.

| Concern                | Tool              | Pinned version |
| ---------------------- | ----------------- | -------------- |
| Formatting             | `@biomejs/biome`  | `2.6.8`        |
| Linting                | `oxlint`          | `1.93.0`       |
| Type-aware lint engine | `oxlint-tsgolint` | `7.0.2007`     |

Every pin is old enough to clear pnpm's default 24-hour release-age gate, so `pnpm-workspace.yaml` carries no `minimumReleaseAgeExclude` exemption. Do not add one to adopt a fresher release; wait for it to age instead.

```text
pnpm format          # rewrite the tree with Biome
pnpm format:check    # read-only: report files that are not formatted
pnpm lint            # oxlint, type-aware, all four source trees
pnpm lint:fix        # oxlint with mechanical fixes
pnpm typecheck       # tsc in all eight workspace projects plus the two non-workspace roots
pnpm verify          # format:check + lint + typecheck; never writes
pnpm verify:full     # verify, then every package's test suite and the CLI end-to-end suite
```

**`.editorconfig` is the single source of indentation.** `biome.json` sets `formatter.useEditorconfig: true` and deliberately declares no `indentStyle`, `indentWidth` or `lineEnding`, because a value in `biome.json` takes precedence and would silently desynchronize the two files. That absence is the whole guarantee, so it is an invariant: never add those keys to `biome.json`. TypeScript and JavaScript use real tab characters at four columns; JSON, JSONC, YAML and Markdown use two spaces; Markdown keeps trailing whitespace because two trailing spaces are a hard line break. Apart from the scope and exclusion keys described below, `biome.json` owns only what EditorConfig cannot express: line width, quote style, semicolons, and the Markdown parser and formatter options.

**Markdown is formatted, with two safeguards.** `markdown.parser.frontmatter` is explicitly `true`; when it is left at its `false` default Biome does not recognize YAML frontmatter and reflows the block as prose, which flattens nested keys and destroys the document's metadata. `markdown.formatter.formatEmbeds` is explicitly `false`, so fenced code and frontmatter are preserved byte-for-byte instead of being re-indented by their own language formatter.

**Exclusions, each justified by what owns the file.** `pnpm-lock.yaml` and `pnpm-workspace.yaml` are written by pnpm itself. `output/` and `.secrets/` are gitignored and excluded through `vcs.useIgnoreFile`. Two historical ODD records — `odd/tasks/2026-11-12-verification-reuse.md` and `odd/tasks/2026-11-14-root-contract-suite-retirement.md` — are excluded because Biome 2.6.8 is not idempotent on them: each pass adds two spaces to the empty `>` lines of the quoted request they contain, so `format:check` can never converge. Their quoted content must stay verbatim regardless.

**When a new file does not converge.** ODD records quote requests inside blockquotes, so the defect above can recur. A slice that adds such a record must run `pnpm format:check` and see it converge; a file that does not converge is excluded by exact path with its reason recorded in that feature's Log. Do not widen an exclusion pattern to cover it.

**These files are not distributed.** `.editorconfig`, `biome.json` and `.oxlintrc.json` sit outside `distribution-clearance.json`, so a destination never receives them. A destination chooses its own tooling; this is intentional, not an omission.

**Scope of the lint rules.** `import/no-relative-parent-imports` is enforced across all four source trees (`cli/**`, `.agents/skills/**`, `mcp-servers/system-one/**`, `.opencode/plugins/odd-adviser/**`). Every one of them resolves non-sibling imports through a `#`-prefixed Node subpath import map declared in its own `package.json`, which is the mechanism Node ESM, `tsc` and Vitest all honour without extra configuration or dependencies. `typescript/unbound-method` is disabled for test files, where `expect(port.method)` is a legitimate reference to an unbound method.

`pnpm lint` reports nine warnings across six files: six `no-misused-spread` in the validators that iterate string code points, and three `no-base-to-string` where a value is stringified into a message. Correcting them would change validation behavior or message content, which is a separate, behavior-bearing change; they are accepted as known and reproduced by running `pnpm lint`, not suppressed and not written around.
