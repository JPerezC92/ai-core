<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 1 — Create symptom taxonomy

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** plan.md confirmed; `knowledge/` contains `agents.md` + `debt.md`; `knowledge/symptoms.md` does not exist.
> **Reads:** `knowledge/agents.md` (prior-art section, shared-rules style), `knowledge/debt.md` (scaffold style precedent)
> **Writes:** `knowledge/symptoms.md` (new)

## Steps

1. Create `knowledge/symptoms.md`:
   - H1 `# Symptom Knowledge Base` plus a 1-2 line intro: this catalog is the fixed, durable index of error-signature classes shared by incident and dev teams; each class carries the canonical diagnostic and fix routing.
   - `## Symptom classes` table with columns exactly `ID | Symptom / error signature | Canonical diagnostic | Canonical fix routing` and exactly these 7 rows, fully agnostic wording:
     - S-01 Version-support mismatch — "does not support X on Y", "unsupported platform/OS", "requires version >= Z" | check the current tool version + release notes/platform support | upgrade to a supported version, then re-verify
     - S-02 Missing prerequisite/binary — "Executable doesn't exist", "command not found" | locate the expected binary, check install state | install the prerequisite
     - S-03 Config mismatch — alias/resolution errors, unknown rule, conflicting config | diff config vs the source of truth | align config to the source of truth
     - S-04 Supply-chain / dependency health — dead package, advisory, peer conflict | dependency audit (Warden 🔒 gate in projects that ship the roster) | substitute a maintained package through the dependency gate
     - S-05 Network / download — slow CDN, timeout, 403, proxy | connectivity + artifact size + alternate hosts | one bounded retry; escalate to the user if repeated
     - S-06 Environment / OS — unsupported OS, missing system libs, permission denies | OS version + product support matrix + permission gates | version upgrade first; else environment-appropriate solution; else ask the user
     - S-07 Process / behavioral — operation failed 2x, long-running grind | reassess the approach itself | STOP, present options to the user
   - `## Rules`: (1) classes are durable — never deleted, only added with approval; (2) every record in `knowledge/problems.md` MUST reference >=1 class here; (3) routing is canonical — no workaround before the canonical diagnostic runs (version-first and stop-and-ask per `knowledge/agents.md`).
   - `## Register` — one line: "filed instances live in `knowledge/problems.md`."

## Output

- **Artifact:** `knowledge/symptoms.md`
- **Schema / shape:** H1 + intro; `## Symptom classes` table with exactly 7 rows (S-01..S-07) and 4 columns; `## Rules`; `## Register`. Neutral wording; no file paths, package names, or incidents from any source project.

## Gate

- ⬜ `knowledge/symptoms.md` exists; `grep -c '^| S-0' knowledge/symptoms.md` → 7.
- ⬜ No project-specific content: `grep -iE 'playwright|faker|tismart|belcorp|SDP|ubuntu|personal-portfolio' knowledge/symptoms.md` → no match.
- ⬜ Table header `ID | Symptom / error signature | Canonical diagnostic | Canonical fix routing` present.

## Abort conditions

- Halt if any project-specific tool, version, or incident name would be required to make a class row meaningful — keep classes fully generic or stop.
- Halt if the greps do not pass — do not gate through without them.

## Tool whitelist / blacklist

- Whitelist: read tools; file write on `knowledge/symptoms.md`.
- Blacklist: edits to `knowledge/agents.md`, `knowledge/problems.md`, any skill, or `AGENTS.md` in this phase.
