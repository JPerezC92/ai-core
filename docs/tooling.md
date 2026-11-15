# Portable MCP tooling setup

This guide provides checkout-local setup instructions for **this AICore source**, not test evidence or authorization to provision before the required review gates, and not a list of what an adopting destination receives.

**What the tracked `.opencode/opencode.jsonc` registers (and what ships on OpenCode enrollment):** `chrome-devtools`, `memories`, `qmd`, `context7` (Context7 uses `{file:../.secrets/context7-api-key}`), `astgrep`, and `semgrep`.

**Portable analysis launchers.** `astgrep` is `uvx --from git+https://github.com/ast-grep/ast-grep-mcp@149e20d47bb7125fb0c1451feea2f48a98742034 ast-grep-server`. That MCP is still the official experimental Python server; destinations need `uv` and the Rust `ast-grep` CLI on `PATH` (the MCP shells out; `@ast-grep/napi` is not a substitute MCP). `semgrep` is `uvx --from semgrep==1.182.1 semgrep mcp` with `SEMGREP_SEND_METRICS=off` and `OTEL_SDK_DISABLED=true`. That is the official Semgrep CLI MCP, not a Node rewrite of the engine. First `uvx` run needs network.

**What stays AICore-operator-local and is not distributed:** `system-one` (`mcp-servers/system-one/`). It cannot live in the merged project config without shipping. Destinations must not receive launch commands under `mcp-servers/` or `.opencode/tooling/`. Cursor enrollment ships no MCP configuration.

The `npx` servers need Node.js >= 22 and no separate provisioning step. The two Python tooling directories below remain optional locked environments for this checkout; they are **not** what OpenCode launches.

## Provision the locked environments (this checkout only)

Run commands from the checkout root with UV >=0.13.1 and Python >=3.13,<3.14 available for the tooling projects.

```text
uv sync --frozen --project .opencode/tooling/astgrep
uv sync --frozen --project .opencode/tooling/semgrep
```

Each directory owns its manifest, lockfile and ignored `.venv/`. Do not activate an environment, install these dependencies into the root project, regenerate locks during setup, or replace the launchers with global executables or `uvx`. The reviewed direct identities are Semgrep `1.182.1` and ast-grep MCP Git revision `149e20d47bb7125fb0c1451feea2f48a98742034`; the respective lockfiles govern the Python dependency closures.

The astgrep project uses UV's experimental `require-build-hashes` setting, requiring UV >=0.13.1. Its exact build-dependency hashes constrain `setuptools==84.2.1` and `packaging==26.3`. A cached built wheel may be reused without re-verifying those build inputs; this is not full build attestation. Semgrep remains isolated in its own environment, with root dependencies untouched.

## External Rust prerequisite

Separately install the Rust ast-grep CLI version `0.51.0` using an approved platform-appropriate installation method, and make `ast-grep` available on `PATH`. Verify before starting its MCP server:

```text
ast-grep --version
```

The reported version must be `0.51.0`. The ast-grep MCP Python lock does **not** install or pin this external Rust binary; `sg` is not an accepted substitute.

## Launch and privacy boundaries

Use this checkout's tracked OpenCode configuration, without editing global OpenCode configuration or embedding machine-specific executable paths. Launch OpenCode from the checkout root. Root Python scripts, the root Python test suite and the repository-root Python environment were retired with the TypeScript migration; the MCP tooling projects keep their own locked environments, and the repository root carries no Python environment of its own. Tooling provisioning does not change root dependencies.

Keep the existing privacy controls unchanged: the `memories` server sets `MEMORIES_SKIP_POSTINSTALL=1` and the `npx` servers set `npm_config_ignore_scripts=true` so package lifecycle scripts never run; Semgrep, when launched locally, uses `SEMGREP_SEND_METRICS=off` and `OTEL_SDK_DISABLED=true`. This setup does not authorize changing other MCP servers, privacy settings, or memory stores. Locking dependencies is not a vulnerability-cleanliness claim.
