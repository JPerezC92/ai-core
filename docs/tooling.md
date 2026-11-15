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
