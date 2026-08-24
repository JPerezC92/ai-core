# Phase 7 — Cipher 🔓 (L2 Lead): provenance-policy acceptance audit

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** phase 6 complete; OpenCode restarted with the updated Warden 🔒 (Dependency Warden) spec; current skill manifest, lock, and provisioned local environment are available.
> **Reads:** every file written in phases 5 and 6; ticket-runbook `pyproject.toml`, `uv.lock`, and local `.gitignore`; Warden 🔒 (Dependency Warden) runtime output
> **Writes:** none — Sentinel 🛡️ (Quality Guardian) and Warden 🔒 (Dependency Warden) return independent evidence to Cipher 🔓 (L2 Lead)

## Steps

1. Dispatch Sentinel 🛡️ (Quality Guardian) for a read-only audit of the updated Warden 🔒 (Dependency Warden) runtime policy and reconciled plan records. The pre-existing Warden 🔒 (Dependency Warden) CV heading baseline is Phase 11 scope and is not a Phase 7 policy blocker.
2. Dispatch Warden 🔒 (Dependency Warden) for the current PyYAML lock, tree, vulnerability, and compatibility audit under its loaded corrected policy.
3. Require Warden 🔒 (Dependency Warden) to state the exact provenance observation, source, pin, hash, vulnerability, license, and compatibility evidence separately from its gate signal.
4. Run the active remediation plan validator. Delegate Herald 📯 (Release Manager) to run `git diff --check` and return its read-only result; do not stage, commit, push, or create a PR.
5. Return PASS only when Sentinel 🛡️ (Quality Guardian) passes, Warden 🔒 (Dependency Warden) returns PASS with an INFO provenance state for the verified PyYAML artifact, and both commands exit zero.

## Output

- **Artifact:** independent Sentinel 🛡️ (Quality Guardian) and Warden 🔒 (Dependency Warden) PASS evidence with a visible non-blocking provenance observation
- **Schema / shape:** the policy distinguishes absent optional metadata from a concrete anomaly; no release action occurs

## Gate

- ☑ Sentinel 🛡️ (Quality Guardian) returns PASS for Warden 🔒 (Dependency Warden) runtime-policy and plan-record consistency; Phase 11 retains the Warden 🔒 (Dependency Warden) CV heading baseline
- ☑ Warden 🔒 (Dependency Warden) returns PASS, records the exact provenance state as INFO, and reports no dependency integrity/security/license blocker
- ☑ Plan validator and `git diff --check` exit zero

## Abort conditions

- Warden 🔒 (Dependency Warden) returns ADVISORY or BLOCK for a concrete evidence-backed condition → stop and report it without downgrading it.
- Warden 🔒 (Dependency Warden) cannot load the corrected policy after restart → stop and ask for restart confirmation.
