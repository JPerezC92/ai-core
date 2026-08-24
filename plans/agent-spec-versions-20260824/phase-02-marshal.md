# Phase 2 — Marshal 🎖️ (HR Director): baseline metadata

> **Owner:** Marshal 🎖️ (HR Director)
> **Pre:** Phase 1 passes Sentinel 🛡️ (Quality Guardian) review; all runtime authorities are versionless.
> **Reads:** all sixteen `.opencode/agents/*.md` specs; `AGENTS.md`; Phase 1 policy
> **Writes:** all sixteen `.opencode/agents/*.md` specs; `AGENTS.md`

## Steps

1. Add exactly `version: 1.0.0` to Atrium 🏛️ (Frontend Architect), Augur 🔮 (Senior Research Analyst), Bastion 🧱 (Backend Architect), Crucible 🔥 (Test Architect), Forge 🔨 (Implementation Agent), Herald 📯 (Release Manager), Inquisitor 🔎 (PR Reviewer), Investigator 🔍 (Incident Investigator), Ledger 📒 (record-keeper), Lumen ✨ (Visual Director), Marshal 🎖️ (HR Director), Quill 🪶 (note drafter), Scribe ✍️ (docs & problem management), Sentinel 🛡️ (Quality Guardian), Vault 🔐 (Catalog Steward), and Warden 🔒 (Dependency Warden).
2. Add exactly `> **Spec version:** 1.0.0` immediately below Cipher 🔓 (L2 Lead)'s H1, preserving root structure.
3. Re-read all frontmatter and root metadata; verify no other runtime text changed.

## Output

- **Artifact:** seventeen explicit `1.0.0` runtime authority baselines
- **Schema / shape:** sixteen single frontmatter fields and one single Cipher 🔓 (L2 Lead) root marker

## Gate

- ☑ Every OpenCode spec has exactly one `version: 1.0.0` field
- ☑ `AGENTS.md` has exactly one Cipher 🔓 (L2 Lead) `Spec version: 1.0.0` marker
- ☑ Diff contains only Phase 1 policy and Phase 2 metadata

## Abort conditions

- Any agent frontmatter stops parsing or metadata changes runtime behavior → stop and correct it.
- An existing version value is discovered → stop and reconcile rather than overwrite it.
