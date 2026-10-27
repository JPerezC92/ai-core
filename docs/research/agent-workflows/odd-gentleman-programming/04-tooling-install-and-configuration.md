# 04 — Tooling: personas, presets, components, delegation, install & licensing

> Part of the [Gentleman Programming / ODD research set](README.md). Research date: 2026-10-22. All claims carry `S#` citations ([sources.md](sources.md)); inferences are labeled `infer:`.

## 1. Persona modes

From usage.md Persona Modes (S4) and pi.dev/gentle-pi (S20):

| Mode | Behavior |
|---|---|
| `gentleman` | Teaching mentor, pushes back on bad practices; per gentle-pi: "Senior architect, teacher, direct technical feedback, Rioplatense Spanish/voseo when the user writes Spanish." |
| `neutral` | "Same teacher, same philosophy, no regional language" |
| `custom` | gentle-ai injects no persona (ownership choice) |

gentle-pi stores the persona at `~/.pi/gentle-ai/persona.json` (S20). Themes Gentleman & Gentleman-Cute are documented at v4.0.0 (S10).

## 2. Presets and components

**Presets** (usage.md CLI flags): `full-gentleman`, `ecosystem-only`, `minimal`, `custom` (S4).

**Components** (install example): `engram,skills,context7,persona,permissions` (S4). The README component table adds (S9):

- **CodeGraph** — read-only symbol graph;
- **security deny-list** — blocks `~/.ssh`, `.env`, credential files;
- **config backups** — snapshotted before every write (backups before every write also back gentle-ai's `state.json`-driven writes, S9).

## 3. Skill library, registry, and project-local precedence

- Curated preset skills (e.g. `go-testing`, `skill-creator`, `branch-pr`, `issue-creation`) plus the community repo **Gentleman-Skills** — "Community-driven AI agent skills for Claude Code, OpenCode, and other AI assistants" (S4, S25).
- `gentle-ai skill-registry refresh` builds an index-first registry (`.atl/skill-registry.md` + cache) (S4).
- **Project-local skills win** over same-name global skills; multiple project roots are recognized incl. `skills/`, `.opencode/skills/`, `.claude/skills/`, `.github/skills/` (S4).

## 4. Delegation — "Delegate for a reason, not for size"

README, via pkg.go.dev gentle-ai/v4 (S9). Named triggers only:

| Trigger | Condition (as documented) |
|---|---|
| **Exploration** | understanding needs > ~3 inline calls / 10k tokens or > ~5 sequential lookups |
| **Parallel writers** | ≥2 independent units with disjoint edit surfaces, ~100+ changed lines |
| **Context backstop** | (named trigger; condition per README) |
| **Independent verifier** | change naming a high-risk item: data, security, shared contracts, concurrency, delivery |

"A trigger holds only when its condition truly holds; none holds by default… File count, task size, or a model price ratio never decide the route on their own." (S9)

**One focused question rule** — ODD step 3: "one focused question for a real product decision" (S4); usage.md "Uncertainty": "Only real unresolved product decisions prompt a focused user question, one at a time with a stop/wait; delegated workers return gaps to the parent rather than assume choices." (S4)

**Risk line** — each work unit carries a "Risk line"; a unit naming a high-risk item gets its own commit for solo native review (S4). In gentle-pi's review layer, findings require `evidence_class`, `causal_disposition`, and concrete changed-hunk / candidate-created-path / differential-test / before/after proof (S20).

**Honest reporting** — ODD Close reports "the verified outcome, **every failed or pending check**, and the next step"; a reported failure is reproduced before anyone claims it works (S4). `infer:` this is the "risk line + honest report on every change" behavior named in the research request; no source was found using the exact phrase "honest report" ([README.md](README.md#open-questions-and-gaps), gap 5).

## 5. Runtimes and per-runtime feature differences

**Supported agents (v4.x README)** (S9): "Pi · OpenCode · Claude Code · Codex · Cursor · VS Code Copilot · Gemini CLI · Kilo Code · Kimi Code · Kiro IDE · Qwen Code · Hermes · Antigravity · Windsurf · OpenClaw · Trae · Conductor" — **17 agents** ("17 agents — Keep the agent you already have").

- Counts differ by version: 15 at v1.36.x, 13 at v1.27.x (S9, S10) ([README.md](README.md#open-questions-and-gaps), gap 6). Hermes is detect-only (install manually first) (S9).
- All runtimes named in the research request are covered; **features differ per runtime** — "available features such as delegation and RDD review can differ" (S9). The atomic RDD lifecycle renders only for Claude Code, OpenCode, Codex, and Pi (S6).

## 6. Install paths

| Target | Method |
|---|---|
| macOS / Linux | curl script `scripts/install.sh \| bash` (with `--channel beta`) (S4) |
| macOS (Homebrew) | tap `Gentleman-Programming/homebrew-tap`; `brew install gentle-ai`; `brew trust --formula …` for Homebrew 6 (S4) |
| **Windows** | **PowerShell source install via `go install github.com/gentleman-programming/gentle-ai/v4/cmd/gentle-ai@<tag>` with Go 1.25.10+** (S9); platforms.md lists Windows as "Supported (binary distribution held)" (S16) |
| engram | `brew install gentleman-programming/tap/engram`; GitHub Releases (S17, S18) |
| engram (self-host) | Docker image `ghcr.io/gentleman-programming/engram:v2.0.0` (S19) |
| gentle-pi | `pi install npm:gentle-pi` (S20) |
| gga | `brew install gentleman-programming/tap/gga` or `./install.sh`; Windows Git Bash + `gga.bat`/`gga.ps1` shim (S22) |

**Windows install conflict/note (both statements, not reconciled):** older v1.x docs push **Scoop** on Windows, while current platforms.md says "Scoop and official Windows binaries are still temporarily unavailable" pending an Authenticode restoration gate (S16). Both stated; see [README.md](README.md#open-questions-and-gaps), gap 4.

**`gentle-ai doctor`** — read-only health check (S4): tool binaries on PATH (5-second version probe, shadow detection), `state.json` validity, installed-asset version match, OpenCode managed-launcher activation, Engram MCP reachability, disk space; pass/warn/fail per check.

## 7. License and trademarks

MIT for gentle-ai, engram, gga, gentle-pi (S9, S17, S18, S20, S22, S23). Trademarks: **Gentle AI™, Engram™, gentle-shell™, gentle-pi™** (README notices) (S9, S20).

## 8. Determinism claim and self-run benchmark numbers

**Determinism claim** (README, S9): "states, routes, hashes, limits and workflow transitions live in the binary, so the model spends its tokens on judgement"; the binary owns RDD review transitions.

**Benchmark claims (self-run, n=1 per cell — treat as directional)** (S9, S21, S28; sources gentle-shell#1723, #1794, #1713):

- Gentle Shell vs the same model in Codex CLI, blind review — **accepted first round in every cell**;
- a **spec passed by reference** beat paraphrased handoffs (73-line spec, 26 hidden checks: paraphrased "13 failing, still 23/26 after two feedback rounds");
- large task **~3× slower** (17.5–17.9 min vs 6.1 min) — flagged by the author as open work.

`infer:` the "3× slower on large tasks" figure is the author's own disclosure against his product, consistent with the reproducibility stance in [`03-rdd-receipt-driven-development.md`](03-rdd-receipt-driven-development.md) ("A number I publish and you cannot reproduce is a claim about my honesty", S7). The benchmarks remain vendor-published with n=1 per cell ([README.md](README.md#open-questions-and-gaps), gap 7).

Next: [`05-comparison-and-assessment.md`](05-comparison-and-assessment.md) — comparative analysis (heavily `infer:`).
