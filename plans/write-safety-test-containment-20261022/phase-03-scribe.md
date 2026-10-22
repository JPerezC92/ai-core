# Phase 3 — Write-target documentation

> **Owner:** Scribe ✍️ (Docs & Problems Manager)
> **Pre:** phase 2 accepted (guard behavior and tests green); plan audit `[PASS]`; user execution authorization for this turn.
> **Reads:** `.opencode/skills/core-sync/SKILL.md`; phase 2 return with the delivered behavior and changed paths; approved story `core-sync` AC25.
> **Writes:** `.opencode/skills/core-sync/SKILL.md`

## Assignment and resources

- Workflow / task / instance: `write-safety-test-containment-20261022` / `p3-docs` / `p3-scribe`.
- Accepted predecessors / input identities: accepted phase 2 return; the exact SKILL bytes at that moment; no other writer touches the file.
- Permitted resource access: edit only `core-sync/SKILL.md`; read the delivered code behavior; no shell test execution (Cipher 🔓 (Lead Orchestrator) runs the structural check, Crucible 🔥 (Test Architect) the suite if needed).
- Ownership / output destination: Scribe ✍️ (Docs & Problems Manager) is the only writer of the SKILL file under this plan's explicit assignment; Vault 🔐 (Catalog Steward) reviews it read-only.
- Required gates / continuation / join owner: Vault 🔐 (Catalog Steward) `[PASS]`; Cipher 🔓 (Lead Orchestrator) accepts and releases phase 4.
- Capacity allocation / accounting owner: one writer slot from the coordinator ledger.
- Readiness / serialization evidence: depends on phase 2's accepted behavior; no shared mutable resource with phase 4 (read-only).

## Steps

1. State in the write-target paragraph that **write targets must be regular files**: a symlinked bindings or payload/root/report target is rejected before any read or write, and an existing non-regular target is rejected.
2. Update the troubleshooting row that currently says to correct the "binding/root/symlink mapping" so it tells the operator to **replace a link with a regular file** and re-run `check`.
3. Keep every other section byte-identical; do not re-describe region, raw, or merge behavior.

## Output

- **Artifact:** `.opencode/skills/core-sync/SKILL.md`
- **Schema / shape:** write-target paragraph and one troubleshooting row updated; all other content unchanged.
- **Attribution / identities:** instance `p3-scribe`; consumed SKILL bytes and the phase 2 return; produced identity recorded on return.
- **Parent handoff:** changed path, content identity, Vault 🔐 (Catalog Steward) verdict, and resource-release state.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B -c "from pathlib import Path; t=Path('.opencode/skills/core-sync/SKILL.md').read_text(encoding='utf-8'); assert 'write targets must be regular files' in t and 'replace a link with a regular file' in t"` |

- Vault 🔐 (Catalog Steward) reviews the skill-quality effect and returns `[PASS]` or `[FAIL]`.

## Gate

- ⬜ The SKILL states the regular-file write-target boundary and the correction path.
- ⬜ The structural check exits 0.
- ⬜ Vault 🔐 (Catalog Steward) `[PASS]` with no unresolved finding.
- ⬜ No section outside the write-target paragraph and the one troubleshooting row changed.
- ⬜ Reviewed content stayed stable; identities recorded; parent accepted the return.

## Abort conditions

- Halt if the delivered behavior differs from the documented boundary.
- Halt if the edit requires changing another section or a tool-contract byte.
- Stop before any out-of-assignment write; report `BLOCKED` to the parent.
