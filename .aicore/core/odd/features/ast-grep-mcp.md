# ast-grep MCP

OpenCode sessions run a local MCP that exposes ast-grep structural search as four tools, using the official TypeScript MCP SDK and the installed Rust ast-grep CLI. Python and uvx are not used for this server. Semgrep remains the official Python CLI MCP.

**Status:** not started

## Requirements

- [ ] R1 — The four tools dump_syntax_tree, find_code, find_code_by_rule, and test_match_code_rule keep the previous schemas, defaults, outputs, and error behavior.
- [ ] R2 — The server is TypeScript, launched with Node.js, and does not use Python or uvx.
- [ ] R3 — The analysis engine is the installed Rust ast-grep CLI invoked without a shell except where Windows requires it for the ast-grep batch wrapper.
- [ ] R4 — A clean OpenCode destination synchronized from this core can start the same server without this repository's pnpm workspace, absolute source paths, or unpublished packages.
- [ ] R5 — Semgrep stays the official Python CLI MCP; System One stays in this source configuration and is omitted from destinations.
- [ ] R6 — The core-sync skill stays an undistributed OpenCode-local skill.
