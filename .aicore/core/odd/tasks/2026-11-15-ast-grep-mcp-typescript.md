# ast-grep MCP TypeScript spawn server

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-15
> **Objective:** Replace the Python uvx ast-grep MCP with a first-party TypeScript stdio server that spawns the Rust CLI, works in AICore and clean OpenCode destinations, and leaves Semgrep, System One, and core-sync placement unchanged.
> **Branch:** feat/mcp/ast-grep-typescript-spawn
> **Delivery:** one focused PR; forecast ~400–800 authored lines including tests, clearance, and docs; slice: packaging+server+tests, then config/docs/cleanup
> **Runner:** `pnpm --dir mcp-servers/astgrep test` (package tests including live CLI); `pnpm --dir cli/aicore test` for clearance/enrollment regressions

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — The four tools keep the pinned Python MCP contracts. Exact requirement: Preserve the four existing tools: dump_syntax_tree, find_code, find_code_by_rule, test_match_code_rule. Maintain behavioral compatibility, including CLI arguments and execution behavior, supported languages and custom language configuration, YAML rules, JSON/JSONL processing, text formatting and debug output, exit-code handling and no-match behavior, standard input and error handling, Windows, WSL, and Linux compatibility. Do not silently simplify or remove capabilities. Acceptance: run the four tools on representative valid, invalid, match, and no-match inputs against the real Rust CLI and compare with the pinned Python behavior; schemas, outputs, and errors match.
- S2 — ast-grep MCP uses Node.js/TypeScript and spawn, not Python, uvx, or napi. Exact requirement: Use the official TypeScript MCP SDK. Node.js child_process.spawn. The existing Rust ast-grep CLI as the analysis engine. Do not use @ast-grep/napi to reimplement the scanning engine. No Python or uvx dependency for this MCP. Acceptance: inspect the launch command and process tree; Node starts the server; ast-grep is the child; no uvx or Python interpreter is required for this MCP.
- S3 — Clean OpenCode destinations run the server without this workspace. Exact requirement: A downstream project must not depend on AICore's local pnpm workspace, absolute filesystem paths, or manually copied dependencies. Prefer a versioned, reproducible Node.js executable installable through npm/pnpm without requiring the entire AICore repository. If a private or unpublished package would prevent clean destinations from running the MCP, that is not an acceptable final solution. Acceptance: enroll a clean OpenCode destination, start the shipped command, list tools, and execute one real tool; the command contains no mcp-servers/ path, no uvx, and no AICore-absolute path.
- S4 — Semgrep and System One are unchanged in role. Exact requirement: Keep the official Semgrep CLI and its current Python-based runtime. Preserve System One in AICore's project configuration. Continue excluding it from downstream projects. Acceptance: read the merged destination MCP map; semgrep remains uvx from semgrep==1.182.1; system-one is absent; source configuration still registers system-one.
- S5 — core-sync stays OpenCode-local. Exact requirement: Keep .opencode/skills/core-sync/ exactly where it is. Do not move, duplicate, or redesign this skill. Acceptance: the skill path is unchanged and is not a cleared key.
- S6 — Obsolete Python ast-grep launchers are removed after verification. Exact requirement: Remove the obsolete Python ast-grep MCP launch configuration. Ensure no active reference points to the retired implementation. Do not delete ignored local environments. Acceptance: tracked config and docs launch Node for astgrep; uvx remains only for Semgrep; ignored venvs are not deleted.

## Tasks

- T1 | S3 | inline (packaging decision required before server code) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T2 | S1, S2 | delegated (new MCP package and tests; material backend/tooling) — Forge 🔨 (Implementer) | open | commit: pending
- T3 | S3, S4, S6 | delegated (OpenCode command, clearance of shipped runtime, docs, enrollment tests) — Forge 🔨 (Implementer) | open | commit: pending
- T4 | S5 | inline (no move; verify path) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending

## Log

- L1 — Original request, verbatim: # AICore — Post-PR #188 Architecture Correction and MCP Modernization (full session request covering Python MCP migration, core-sync location, PR #188 contracts, leftovers, complexity gate, testing, Git/PR).
- L2 — 2026-11-15 — User correction, dated and verbatim: keep official Semgrep Python engine; evaluate spawn-over-CLI vs napi; do not treat retaining uvx as completing the TypeScript migration.
- L3 — 2026-11-15 — User correction, dated and verbatim: Keep .opencode/skills/core-sync/; .agents/skills/ is shared/distributed; .opencode/skills/ is AICore-specific; Cursor non-discovery is accepted.
- L4 — 2026-11-15 — User authorization, dated and verbatim: first-party TypeScript ast-grep MCP using child_process.spawn and the Rust CLI; packaging must work for clean destinations without a new registry unless separately approved; Semgrep and System One unchanged; core-sync unmoved; new branch from main; one PR; no merge.
- L5 — Packaging decision (T1): do not publish an npm package (no registry/pipeline authorized). Do not launch destinations at mcp-servers/ (enrollment forbids that path in destination MCP commands). Author the server as a source-local package mcp-servers/astgrep (tests, SDK dependency) like system-one. Ship a committed ESM bundle to an OpenCode-only raw-cleared path under .opencode/mcp/ast-grep/ (not .opencode/tooling/). Source and destination launch: node .opencode/mcp/ast-grep/stdio.mjs. Bundle is required so destinations need no pnpm workspace and no unpublished package; the MCP SDK cannot run from bare TypeScript without node_modules. Runtime deps: Node.js, bundled SDK, PATH ast-grep. Eliminated for this MCP: Python, uvx. Retained globally: uvx/Python for Semgrep only.
