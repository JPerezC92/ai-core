# Portable MCP tooling setup

This guide provides checkout-local setup instructions, not test evidence or authorization to provision before the required review gates. Run commands from the checkout root with UV >=0.13.1 and Python >=3.13,<3.14 available for the tooling projects.

## Provision the locked environments

```text
uv sync --frozen --project .opencode/tooling/basic-memory
uv sync --frozen --project .opencode/tooling/astgrep
uv sync --frozen --project .opencode/tooling/semgrep
```

Each directory owns its manifest, lockfile and ignored `.venv/`. Do not activate an environment, install these dependencies into the root project, regenerate locks during setup, or replace the launchers with global executables or `uvx`. The reviewed direct identities are Basic Memory `0.24.1`, Semgrep `1.182.1`, and ast-grep MCP Git revision `149e20d47bb7125fb0c1451feea2f48a98742034`; the respective lockfiles govern the Python dependency closures.

The astgrep project uses UV's experimental `require-build-hashes` setting, requiring UV >=0.13.1. Its exact build-dependency hashes constrain `setuptools==84.2.1` and `packaging==26.3`. A cached built wheel may be reused without re-verifying those build inputs; this is not full build attestation. Basic Memory and Semgrep remain isolated in their own environments, with root dependencies untouched.

## Register Basic Memory

Replace `<checkout>` with this checkout's absolute path; retain quoting when the path contains spaces. Register the existing `memory/` directory through the locked Basic Memory environment:

```text
uv run --frozen --project .opencode/tooling/basic-memory basic-memory project add ai-core '<checkout>/memory' --local
```

This establishes the machine-local Basic Memory mapping; it does not move, rewrite or migrate existing notes or any legacy store. Keep all note operations scoped to project `ai-core`. Memory remains a cache of repo-derivable facts, not the authoritative home of durable knowledge.

## External Rust prerequisite

Separately install the Rust ast-grep CLI version `0.51.0` using an approved platform-appropriate installation method, and make `ast-grep` available on `PATH`. Verify before starting its MCP server:

```text
ast-grep --version
```

The reported version must be `0.51.0`. The ast-grep MCP Python lock does **not** install or pin this external Rust binary; `sg` is not an accepted substitute.

## Launch and privacy boundaries

Use this checkout's tracked OpenCode configuration, without editing global OpenCode configuration or embedding machine-specific executable paths. The configuration launches the three servers with `uv run --frozen --project` and their respective root-relative tooling directory; launch OpenCode from the checkout root. Root Python scripts still use `uv run --frozen python3 ...`, and root tests retain their reviewed command. Tooling provisioning does not change root dependencies or the root `.venv`.

Keep the existing privacy controls unchanged: Basic Memory uses `BASIC_MEMORY_FORCE_LOCAL=true`, `BASIC_MEMORY_NO_PROMOS=1`, and `BASIC_MEMORY_AUTO_UPDATE=false`; Semgrep uses `SEMGREP_SEND_METRICS=off` and `OTEL_SDK_DISABLED=true`. This setup does not authorize changing other MCP servers, privacy settings, or memory stores. Locking dependencies is not a vulnerability-cleanliness claim.
