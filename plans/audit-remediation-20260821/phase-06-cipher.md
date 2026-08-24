# Phase 6 — Cipher 🔓 (L2 Lead): reconcile historical gate records

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** phase 5's Warden 🔒 (Dependency Warden) runtime-policy and authorized CV-deletion gate passes Sentinel 🛡️ (Quality Guardian) audit; user has restarted OpenCode so Warden 🔒 (Dependency Warden) loads the corrected policy. Phase 11 remains responsible for the roster-wide CV heading baseline.
> **Reads:** `.opencode/agents/warden.md`; `plan.md`; `phase-01-marshal.md`; `phase-04-cipher.md`; Sentinel 🛡️ (Quality Guardian) phase-5 audit
> **Writes:** `plan.md`; `phase-01-marshal.md`; `phase-04-cipher.md`

## Steps

1. Replace every old statement that missing PyYAML Trusted Publishing is a release-blocking advisory with the corrected conditional classification: provenance unavailable is INFO only when all stated integrity controls pass; an evidenced anomaly remains ADVISORY or BLOCK.
2. Reconcile G5/G6–G8 done conditions, verification rows, Phase 1 history, and Phase 4 gates so they require a fresh Warden 🔒 (Dependency Warden) PASS with a visible INFO observation rather than user acknowledgment for absent optional metadata.
3. Preserve all factual evidence from the prior implementation, including exact pin, lock, vulnerability/compatibility checks, and the no-PR/no-release constraint. Do not rewrite historical source findings beyond their disproven severity conclusion.
4. Re-read every written plan file, validate the plan directory, and ensure no `Trusted Publishing` text still declares an absent-attestation release hold.

## Output

- **Artifact:** active remediation plan records accurately reflect the corrected Warden 🔒 (Dependency Warden) policy
- **Schema / shape:** no false PyYAML release hold; concrete provenance anomalies remain release-gated; prior implementation evidence remains intact

## Gate

- ☑ Current plan and Phase 1/4 records no longer require acknowledgment for unavailable optional provenance
- ☑ Current plan preserves all exact pin, hash, audit, compatibility, and release-boundary evidence
- ☑ Plan validator passes and content search finds no stale provenance release-hold wording

## Abort conditions

- A historical record would claim Warden 🔒 (Dependency Warden) had passed before the policy correction → stop and report the distinction.
- A reconciliation weakens any documented real dependency integrity control → stop and ask.
