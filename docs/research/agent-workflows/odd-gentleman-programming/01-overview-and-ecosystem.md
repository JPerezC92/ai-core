# 01 — Overview and ecosystem

> Part of the [Gentleman Programming / ODD research set](README.md). Research date: 2026-10-22. All claims carry `S#` citations ([sources.md](sources.md)); inferences are labeled `infer:`.

## 1. Who / what

**Alan Buscaglia** — GitHub `Alan-TheGentleman`, Barcelona, Spain. App Lead at Prowler, Angular Google Developer Expert, Microsoft MVP, creator of Gentleman Programming; 120k+ YouTube, ~15k Twitch, ~50k Instagram, 10k+ Discord (Sponsors page, GitHub profile) (S2, S3).

- GitHub org **`Gentleman-Programming`** hosts the tool repos: gentle-ai, engram, gentle-shell, gentleman-guardian-angel, Gentleman.Dots, homebrew-tap, Gentleman-Skills, agent-teams-lite (archived), gentle-ai-community-docs, and others (S24).
- The site frames the stack as *"the toolset Alan Buscaglia uses every day, refined in public"*, aimed at teams where AI adoption "is not working" (S1).
- Additional context: gentle-ai **supersedes Agent Teams Lite (archived)** (S9).

## 2. Positioning — "verifying beats generating"

The positioning line is used verbatim across the ecosystem docs: *"one rule for AI-assisted work — verifying beats generating"* (pkg.go.dev gentle-ai/v4 README) and *"15 years of enterprise architecture… a community of thousands of developers testing these tools daily"* (same) (S9).

The ecosystem is pitched against unconstrained AI generation: the Sponsors page frames "AI as autocomplete on steroids… a trap" (S3). `infer:` this anti-generation stance is the connective tissue between every component: ODD's read-only default, the verbatim spec quotes, and RDD's byte-frozen receipts all exist to make verification cheap and generation accountable (S4, S6, S8).

## 3. Voice and persona-as-product

The teaching voice is itself a product feature: the persona "actually teaches you"; the Gentleman persona is *"a caring but rigorous mentor who guides you toward your goal"* and *"pushes back on bad practices, explains the why"* (gentle-ai README; usage.md Persona Modes) (S4, S9, S10). gentle-pi describes the persona as *"a senior architect and teacher, not a generic chatbot"* (pi.dev/gentle-pi) (S20).

Persona modes and their language behavior are detailed in [`04-tooling-install-and-configuration.md`](04-tooling-install-and-configuration.md).

## 4. Org inventory

Repositories under the `Gentleman-Programming` GitHub org, per the org page (S24):

| Repository | Role |
|---|---|
| **gentle-ai** | Ecosystem configurator; ODD + RDD host binary |
| **engram** | Persistent memory (MCP) |
| **gentle-shell** | Pi-native workspace shell/UI |
| **gentleman-guardian-angel** (gga) | AI code-review pre-commit hook |
| **Gentleman.Dots** | Personal dev-environment config |
| **homebrew-tap** | Homebrew formulae (gentle-ai, engram, gga) |
| **Gentleman-Skills** | Community-driven skill library |
| **agent-teams-lite** | Archived; superseded by gentle-ai (S9) |
| **gentle-ai-community-docs** | Community documentation |

Gentleman-Skills is described as *"Community-driven AI agent skills for Claude Code, OpenCode, and other AI assistants"* (S25).

## 5. Ecosystem components and versions (as of 2026-10-22)

| Component | What it is | Version evidence |
|---|---|---|
| **gentle-ai** (Go) | "Ecosystem configurator" — writes into each agent's own config: system prompts, skills, ODD routing, persona files, MCP entries; backed by `state.json`, backups before every write | v4.2.0 released (LinkedIn post by Alan, ~2026-10-20, "gentle-ai v4.2.0 y Gentle Shell v4.3.0"; pkg.go.dev `gentle-ai/v4@v4.2.0`). Release history: **v4.0.0 "SDD Retires, ODD Leads, Module Path Moves to /v4"**; v4.1.0 "Proportionate Native Review and a Clean SDD Exit"; v4.1.1 (re-tag of v4.1.0). v3.x line: v3.1.0 (2026-09-17) … v3.7.0 (2026-09-23). Module paths: unsuffixed → `/v2` → `/v3` → `/v4` per major. (S9, S10, S11, S12, S28) |
| **engram** (Go) | Persistent memory: one Go binary → MCP stdio → SQLite + FTS5 (`~/.engram/engram.db`); also HTTP API, CLI, TUI; agent-agnostic; local-first (local SQLite authoritative), optional Engram Cloud replication | **v2.0.0 published 2026-09-18** (pkg.go.dev `engram/v2@v2.0.0`). Note: pkg.go.dev reports "the highest tagged major version is **v3**" on engram pages, and "Homebrew remains on the stable **v1.20.0** line" — version lines coexist (see gaps in [README.md](README.md#open-questions-and-gaps)). (S17, S18, S19) |
| **gentle-pi / gentle-shell** (npm + Go/TUI shell) | Pi development harness: "Turn Pi into el Gentleman" — ODD harness, focused subagents, TDD evidence, native review, skill discovery; gentle-shell adds the workspace UI (live changes, agent views, spend monitoring) | pi.dev `gentle-pi` **v4.3.0, published 2026-10-16**, MIT, author alan_buscaglia, types extension/skill/theme/prompt. Gentle Shell v4.3.0 announced alongside gentle-ai v4.2.0. Trademarks: gentle-shell™, gentle-pi™. (S20, S21, S28) |
| **gga — Gentleman Guardian Angel** (Bash) | Provider-agnostic AI code review as a **git pre-commit hook** on staged files against your `AGENTS.md`; smart cache, PR-review mode; pure Bash core | Badge **v2.10.1**, MIT (GitHub repo). Providers: Claude, Gemini, Codex, OpenCode, Cursor Agent, Kilo, Kiro, Ollama, LM Studio, GitHub Models, MiniMax. (S22) |
| **Gentleman.Dots** | "The same environment on every desk" — personal dev-environment config: Neovim/LazyVim, shells (Fish/Zsh/Nushell), multiplexers (Tmux/Zellij/Herdr), terminals (Ghostty/Kitty/WezTerm/Alacritty), Starship; Go TUI installer; AI layer deliberately split out to gentle-ai | GitHub repo (README: "Install Gentleman.Dots first, then run gentle-ai for the AI layer"). (S23) |

### Version-line caveats

- **gentle-ai**: v4.2.0 is reported as current (S9, S28) while the releases-page crawl showed v4.1.1 at top (S11); the exact latest tag was not re-verified against the tags page ([README.md](README.md#open-questions-and-gaps), gap 3). Any external material describing "gentle-ai SDD workflows" is pre-v4 and stale — SDD was retired in v4.0.0 (S11).
- **engram**: three major lines are visible at once (v1.20.0 Homebrew stable, v2.0.0 published, v3 highest tagged) (S17, S18).
- **Agent counts differ by version** — 17 at v4.x, 15 at v1.36.x, 13 at v1.27.x (S9, S10) ([README.md](README.md#open-questions-and-gaps), gap 6).

Next: [`02-odd-workflow.md`](02-odd-workflow.md) — the ODD workflow in detail.
