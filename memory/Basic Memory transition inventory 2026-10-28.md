---
title: Basic Memory transition inventory 2026-10-28
type: note
permalink: ai-core/basic-memory-transition-inventory-2026-10-28
---

# Basic Memory transition inventory — 2026-10-28

Cache of migration evidence; authoritative scope and acceptance record: `odd/tasks/basic-memory-migration.md` (S1–S3, Log L1–L4). This note does not define workflow policy or assert migration completion.

On 2026-10-28, the accepted source-inventory handoff for `basic-memory-migration/docs-1` reported:

- `memories.list_memories(limit=100)` returned `No memories found`.
- `memories.get_context(limit=10)` returned `No context found. Use add_memory to store rules and knowledge.`

No old entries were exposed by those bounded calls, so no source entries were copied. These results do not establish that the underlying database contains no data. The original memories.sh database was left unchanged by this documentation slice.

The transition targets Basic Memory project `ai-core`, configured at repository `memory/`; the active memory binding is documented in `AGENTS.md` under Memory system and summarized in `README.md`. Legacy MCP removal remains a separate, gated operation under S4 of the feature record.
