# Phase 3 — Cipher 🔓 (L2 Lead): restart and acceptance audit

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** Phases 1 and 2 pass Sentinel 🛡️ (Quality Guardian) review; user restarted OpenCode after agent-file edits.
> **Reads:** all runtime authorities; Marshal 🎖️ (HR Director) and Sentinel 🛡️ (Quality Guardian) version rules; Phase 1 and 2 gates
> **Writes:** none — Sentinel 🛡️ (Quality Guardian) returns independent evidence to Cipher 🔓 (L2 Lead)

## Steps

1. Confirm user restart after Phase 2.
2. Dispatch Sentinel 🛡️ (Quality Guardian) for full version, root-marker, SemVer, canonical-structure, and persona/runtime-boundary acceptance.
3. Delegate Herald 📯 (Release Manager) to run `git diff --check`; no release command is allowed.
4. Return PASS only when Sentinel 🛡️ (Quality Guardian) passes and whitespace is clean.

## Output

- **Artifact:** independent acceptance evidence without behavioral regression
- **Schema / shape:** one Sentinel 🛡️ (Quality Guardian) PASS plus one clean whitespace result

## Gate

- ☑ OpenCode restart confirmed
- ☑ Sentinel 🛡️ (Quality Guardian) returns PASS for all seventeen runtime authorities
- ☑ `git diff --check` exits 0

## Abort conditions

- Sentinel 🛡️ (Quality Guardian) finds malformed, duplicate, missing, or behavior-changing metadata → reopen the responsible phase.
- Restart exposes an OpenCode parsing error → stop and correct exact metadata.
