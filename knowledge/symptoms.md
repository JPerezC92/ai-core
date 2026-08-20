# Symptom Knowledge Base

This catalog is the fixed, durable index of error-signature classes shared by incident and dev teams; each class carries the canonical diagnostic and fix routing.

## Symptom classes

| ID | Symptom / error signature | Canonical diagnostic | Canonical fix routing |
|---|---|---|---|
| S-01 | Version-support mismatch — "does not support X on Y", "unsupported platform/OS", "requires version >= Z" | check the current tool version + release notes/platform support | upgrade to a supported version, then re-verify |
| S-02 | Missing prerequisite/binary — "Executable doesn't exist", "command not found" | locate the expected binary, check install state | install the prerequisite |
| S-03 | Config mismatch — alias/resolution errors, unknown rule, conflicting config | diff config vs the source of truth | align config to the source of truth |
| S-04 | Supply-chain / dependency health — dead package, advisory, peer conflict | dependency audit (Warden 🔒 gate in projects that ship the roster) | substitute a maintained package through the dependency gate |
| S-05 | Network / download — slow CDN, timeout, 403, proxy | connectivity + artifact size + alternate hosts | one bounded retry; escalate to the user if repeated |
| S-06 | Environment / OS — unsupported OS, missing system libs, permission denies | OS version + product support matrix + permission gates | version upgrade first; else environment-appropriate solution; else ask the user |
| S-07 | Process / behavioral — operation failed 2x, long-running grind | reassess the approach itself | STOP, present options to the user |

## Rules

- Classes are durable — never deleted, only added with approval.
- Every record in `knowledge/problems.md` MUST reference >=1 class here.
- Routing is canonical — no workaround before the canonical diagnostic runs (version-first and stop-and-ask per `knowledge/agents.md`).

## Register

Filed instances live in `knowledge/problems.md`.
