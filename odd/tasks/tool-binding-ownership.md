# Tool-binding ownership for agent specs

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-24
> **Closed:** 2026-10-24

## Specs

- S1 — Core keeps AICore's intrinsic Python toolchain explicit: `python3`, `uv`, pytest for skill scripts/tests, `pyproject.toml`, and `uv.lock` are core-owned implementation/test tooling, not destination application bindings.
- S2 — Core does not present destination application toolchains as universal bindings; `uvicorn` and JavaScript/TypeScript application defaults (`pnpm`, Vitest, Playwright, `package.json`, `pnpm-lock.yaml`) are project-owned or clearly labeled reference defaults.
- S3 — The change is limited to `knowledge/agents.md`, the five PR #80-aligned runtime specs (`.opencode/agents/atrium.md`, `bastion.md`, `crucible.md`, `forge.md`, `inquisitor.md`), the two auditors that carry the same source-neutrality gate (`.opencode/agents/sentinel.md`, `vault.md`), Warden's dependency-tool mapping (`.opencode/agents/warden.md`), and the source-version contract `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_agent_versions.py`; no unrelated agent or project-wide migration is included.
- S4 — AICore's own Python implementation toolchain is explicitly core-owned; destination application toolchains remain project-owned. The shared source-neutrality rule must state that boundary without weakening the ban on destination-specific leakage.
- S5 — Every edited runtime spec retains its original obligations, advances its version by the applicable class, and passes a full original/candidate accounting audit by Sentinel 🛡️ (Quality Guardian).
- S6 — The feature resolves task T5 of `odd/tasks/agent-spec-odd-alignment.md` with current evidence, or records exactly why it remains deferred; no completion or merge claim precedes review.
- S7 — No dependency, permission, plugin, context-injection, or destination change is introduced.

## Tasks

- T1 | S1, S2, S3, S4 | Cipher 🔓 (Lead Orchestrator): inventory and classify every tool/runner reference in the scoped docs and `knowledge/agents.md` | done | commit: f63df3fee0bd4505daa358991441af1d65ed84c5
- T2 | S1, S2, S3, S4, S5 | Marshal 🎖️ (HR Director): update `knowledge/agents.md`, the five specs, the auditor rule copies, and Warden's dependency-tool mapping to make core versus project ownership explicit; preserve all original obligations | done | commit: f63df3fee0bd4505daa358991441af1d65ed84c5
- T3 | S3, S5 | Forge 🔨 (Implementer): align the source-version contract fixture to all eight edited spec versions | done | commit: f63df3fee0bd4505daa358991441af1d65ed84c5
- T4 | S5 | Sentinel 🛡️ (Quality Guardian): audit the complete original/candidate accounting and source-neutrality boundary | done | commit: f63df3fee0bd4505daa358991441af1d65ed84c5
- T5 | S6, S7 | Cipher 🔓 (Lead Orchestrator): record the T5 resolution in `agent-spec-odd-alignment.md`, run feature validation, and report the final outcome | done | commit: f63df3fee0bd4505daa358991441af1d65ed84c5

Allowed status: open, in progress, done. `pending` is valid for open or in-progress work. A task marked done must cite its completed work-unit commit. A feature closes only when every task is done and committed.

## Log

- L1 — agreed
- L2 — Analysis evidence: `.opencode/skills` contains 177 Python files; `pyproject.toml` requires Python >=3.13 with PyYAML and pytest/pytest-xdist; `AGENTS.md:147-148` mandates `python3` and `uv run --frozen`; `crucible.md:247-252` defines pytest conventions; `warden.md:230` treats `pyproject.toml`/`uv.lock` as the Python dependency surface.
- L3 — Conclusion accepted: Python is AICore's own toolchain and stays in core. `uvicorn` is not used by AICore's Python tooling and is a reference application-server choice, not a core binding. `pnpm`/JS application defaults are likewise project-facing reference defaults.
- L4 — The earlier source-neutrality failure conflated core implementation tooling with destination application bindings. This feature corrects that boundary in `knowledge/agents.md` and only the five PR #80-aligned specs; it does not remove Python or perform a broader agent migration.
- L5 — Scope boundary recorded from the earlier user direction: do not overscope the whole project. `agent-spec-odd-alignment.md` T5 remains the tracking point for the deferred audit until this feature supplies the evidence.
- L6 — User confirmed the Python conclusion and said “do it.” The shared source-neutrality rule is included because leaving it unchanged would keep classifying AICore's own Python toolchain as destination leakage.
- L7 — Inventory with the repository search tool found the affected references in `knowledge/agents.md:22` and the five specs: Inquisitor's command matrix/mapping/prohibitions (`:174-197`, `:216-217`), Atrium's frontend dependency surface (`:227-229`), Bastion's skill-test wording (`:291`), Crucible's project tool names (`:280-283`), and Forge's project tool names (`:124-128`). The version contract must move with the five spec version bumps.
- L8 — Sentinel audit found the same stale source-neutrality gate in `.opencode/agents/sentinel.md:59` and `.opencode/agents/vault.md:154,167`, plus the shared rule's final sentence still saying “Source-environment leakage.” Those auditors must carry the corrected destination-specific boundary; their patch versions and the version-contract fixture are added to scope. Sentinel also found Crucible's reference sections are above, not below; fix that and qualify the destination stack as JavaScript/TypeScript.
- L9 — Sentinel's re-audit passed the boundary but flagged `warden.md:243-249` as the same out-of-scope class. Warden's mapping is core and therefore included; its JavaScript tool names become a labeled destination reference example while AICore's `uv`/Python manifest remain core-owned. Crucible's cross-reference wording is corrected at the same time.
- L10 — Work-unit commit `f63df3fee0bd4505daa358991441af1d65ed84c5` delivered the shared boundary, eight runtime-spec clarifications, and the source-version contract. Sentinel's final audit returned [PASS] with full original/candidate accounting; Bastion, Crucible test architecture, and the 738-test whole suite all passed.
- L11 — The initiating user message was `agreed` (acceptance of the Python analysis); the subsequent `do it` authorized execution after this record was drafted.
- L12 — Close: T1–T5 are done and committed; AICore's Python toolchain is explicitly core-owned, destination app toolings are project-owned/reference examples, and `agent-spec-odd-alignment.md` T5 is resolved. No merge occurred; push/PR remains separately authorized.
