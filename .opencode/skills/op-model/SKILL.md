---
name: op-model
description: Set or change the model for any agent in the project's opencode config (opencode.json / opencode.jsonc) deterministically, using `opencode models` as the single source of truth. Filters to subscription-available models and asks via the question tool when the query matches more than one provider. Use when the user wants to set/change an agent's model, mentions a model name (gpt, glm, deepseek, qwen, kimi, minimax, grok, claude, gemini, etc.), asks what models are available, or needs the provider/model name for the config.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.0.1
  domain: opencode
---

# op-model

> **Rule layout:** two-section-v1

## Project extensions

### Model lookup script

This project's model-lookup script is `python3 .opencode/skills/op-model/scripts/models.py` — invoke it with the model query as its argument. It runs `opencode models --verbose` and emits one structured JSON record per match.

### Opencode config files

This project's opencode config file is `opencode.jsonc` (or `opencode.json`); the `OPENCODE_CONFIG` environment variable overrides the path. When neither exists, the minimal config file to create is `opencode.jsonc`.

### Model examples

Concrete provider/model examples used in this project:

- Ambiguous query `deepseek v4 flash`: the lookup script returns `deepseek/deepseek-v4-flash` — DeepSeek V4 Flash, `opencode-go/deepseek-v4-flash` — DeepSeek V4 Flash, and `opencode/deepseek-v4-flash-free` — DeepSeek V4 Flash Free. Because there are ≥2 matches, the skill presents those three options; if the user picks `deepseek/deepseek-v4-flash`, the skill edits `agent.plan.model` in `opencode.jsonc` to `deepseek/deepseek-v4-flash`, preserving `color` and other keys, verifies JSON5 + re-runs the script to confirm the chosen name still appears, and reports "plan → deepseek/deepseek-v4-flash (DeepSeek V4 Flash). Restart the opencode TUI to apply."
- Single match `glm-4.7` returns `zai-coding-plan/glm-4.7`; edit `agent.build.model`, verify, report.
- No match `gpt-4o` — not covered by any authenticated provider (filtered out by subscription).
- Brand/family variant `gpt-5.6` may match `gpt-5.6-terra`, `gpt-5.6-luna`, and `gpt-5.6-sol`.

## Mandatory core

### What I do

Resolve a model name or query against the live `opencode models` output (subscription-filtered), ask via the `question` tool when multiple providers match, and surgically edit `agent.<name>.model` in the project's opencode config. Never invents model names, never picks a provider silently, and only writes models that actually appear in `opencode models`.

### When to use me

- User wants to set or change the model for an agent (plan, build, or any custom agent): "set plan to <model query>", "make build use <model query>", "use <model query> for plan".
- User mentions a model name and it needs to resolve to its `provider/model` config form: gpt, glm, deepseek, qwen, kimi, minimax, grok, claude, gemini, or any other model family.
- User asks which models are available for the config, or wants to know what they can actually use.
- User asks to pick a model before configuring the project's opencode config file.

### Arguments

From the user's request, extract:

- **agent** — the agent whose model to set (e.g. `plan`, `build`, or any custom agent name). Defaults to `plan` if unspecified.
- **model query** — free-text description of the model to look up (e.g. a model family, a provider/model-id, or a variant name).

If either is missing, collect it with the `question` tool.

#### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `agent` | text | non-empty, matches an existing or new agent name | not provided |
| `model_query` | text | non-empty | not provided |

Use one `question` call when both are missing, or per-missing-field otherwise. The first option is the parsed value when one is available; do not add a manual "Other" option.

### Steps

1. **Parse arguments.** Extract `agent` (default `plan`) and `model query`. Collect missing values via the `question` tool (see Argument collection form).

2. **Authoritative lookup (delegated to the script).** Run this skill's model-lookup script against the model query (see Project extensions for the exact command). The script runs `opencode models --verbose`, parses the provider/model blocks, and emits structured JSON records (config, id, provider, name, cost). This is the ONLY source of candidate model names — it already reflects the user's active subscriptions and credentials. NEVER invent, recall from memory, or copy model names from anywhere else (docs, prior sessions, chat examples).

3. **Read the records.** The script returns one JSON line per match (or prints all models grouped by provider when no query was given). Work from those records:
   - **No query and no agent target** → show the grouped listing and ask which model to set.
   - **0 matches** → the script already reports "No match" and exits non-zero. Report "no match found in `opencode models`" and list the closest available config names as a suggestion. Do NOT proceed to any edit. If the user names a model that is not in the output, it is not covered by their subscriptions — do NOT write it to the config.
   - **1 match** → use its `config` value (`provider/model`) and proceed to step 5.
   - **≥2 matches** → MUST use the `question` tool before proceeding. One option per matching provider, each labeled with the full config name and human name (e.g. `<provider>/<model> — <Human Name>` for each provider). Proceed only with the provider the user picks. NEVER auto-pick a provider silently — that is a FAIL.

4. **Locate the config file.** Find the project's opencode config file (see Project extensions for this project's file names and override variable). If it does not exist, create the project's opencode config file in the repo root with a minimal valid shape.

5. **Edit surgically.** Open the config and set `agent.<agent>.model` to the chosen `provider/model` value:
   - If the `agent` object exists, change ONLY the `model` line. Preserve every other key in that agent block (`color`, `temperature`, `permission`, etc.).
   - If the `agent` object exists but the named agent is missing, add `"<agent>": { "model": "<provider/model>" }`.
   - If the `agent` object does not exist, add `"agent": { "<agent>": { "model": "<provider/model>" } }`.
   - Preserve all other top-level keys and comments in the file.

6. **Verify.**
   - JSON5-parse the edited file (strip line comments and trailing commas, then strict-parse) — must succeed.
   - Re-run this skill's model-lookup script against the model query and confirm the chosen `provider/model` is still present in the output.
   - Re-read the config file and confirm the `model` value matches exactly.

7. **Report.** State `<agent> → <provider/model> (<human name>). Restart the opencode TUI to apply.` Do NOT commit unless the user explicitly asks.

### Examples

**Ambiguous query → question tool (worked case):** user says "set plan to <model query>".

1. The model-lookup script returns three records (one per matching provider).
2. Because there are ≥2 matches, the skill opens the `question` tool with those three options (full config name + human name).
3. User picks one provider's config name.
4. The skill edits `agent.plan.model` in the project's opencode config to that config name, preserving `color` and other keys.
5. Verifies JSON5 + re-runs the lookup script to confirm the chosen name still appears.
6. Reports: "plan → <provider/model> (<Human Name>). Restart the opencode TUI to apply."

**Single match:** user says "make build use <model query>". The lookup script returns exactly one match — no question needed. Edit `agent.build.model`, verify, report.

**No match:** user says "set plan to <model query>". The script returns "No match" and exits non-zero — it is not covered by any authenticated provider (filtered out by subscription). Report no match + suggest the closest available config names. Do NOT edit.

**Available-models question:** user asks "what models can I use?". Run the lookup script with no query → grouped-by-provider listing, and offer to set one for an agent if the user wants.

### Troubleshooting

- **Model not in the script output:** it is not covered by the user's active subscriptions/credentials. Do NOT write it to the config. Show the closest available names and let the user pick from those instead.
- **Script errors or exits non-zero:** read the error message; if `opencode models --verbose` itself fails, resolve the opencode CLI issue first (PATH, auth). Never proceed on partial/empty data.
- **Query matches multiple providers:** NEVER pick one silently. Use the `question` tool with one labeled option per provider and proceed only on the user's choice.
- **Config file missing:** create the project's opencode config file in the repo root with a minimal valid shape (the `$schema` line plus the `agent` block being added).
- **JSON5 parse fails after edit:** restore the previous file state (the skill made only a surgical change; revert it), verify the original parses, and redo the edit. Never leave the config in an unparseable state.
- **Config uses a strict-JSON file (no comments):** edit accordingly — do not introduce `//` comments or trailing commas into a strict-JSON file.
- **Model name is a brand/family, not an exact ID:** the user may name a family when several variants exist. The script's broad match lists all variants; present them via the `question` tool and let the user pick the exact one.
