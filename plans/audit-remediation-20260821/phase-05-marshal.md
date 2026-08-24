# Phase 5 — Marshal 🎖️ (HR Director): evidence-based provenance policy

> **Owner:** Marshal 🎖️ (HR Director)
> **Pre:** user-authorized G6–G8; Augur's and Warden's read-only policy reviews are available; current Warden 🔒 (Dependency Warden) spec is read in full.
> **Reads:** `.opencode/agents/warden.md`; `agents/warden/profile.md`; Augur 🔮 (Senior Research Analyst) policy assessment; Warden 🔒 (Dependency Warden) policy self-review; current PyYAML manifest/lock audit evidence
> **Writes:** `.opencode/agents/warden.md`; `agents/warden/profile.md`

## Steps

1. Replace the ticket-runbook Python-branch rule that hard-codes missing Trusted Publishing as ADVISORY. Record a per-artifact provenance observation as `verified`, `unavailable`, or `indeterminate` alongside the approved source, canonical-project mapping, exact version, committed hash coverage, license, vulnerability result, and compatibility result.
2. Classify `unavailable` optional provenance as INFO when the approved index, exact pin, committed hashes, canonical-project mapping, acceptable license, clean vulnerability scan, and compatible locked environment all pass. Classify `indeterminate` as INFO only when those same non-provenance integrity controls are positively verified and provenance retrieval is incomplete without conflicting source evidence; retain it for a future re-check rather than inferring compromise. If any required non-provenance control cannot be verified, report the specific incomplete integrity evidence as ADVISORY and do not PASS. Neither provenance state alone requires user acknowledgment or prevents PASS.
3. Define provenance ADVISORY only for concrete evidence: unapproved/custom index or direct URL, hash mismatch, publisher/package ownership mismatch, verified attestation identity mismatch, previously verified provenance that regresses, revoked or compromised release, or unresolved release-source inconsistency. Keep BLOCK for concrete compromise, injection, integrity failure, or Critical/High vulnerability evidence.
4. Update the gate-signal severity definitions and audit-report template so provenance observations are visible separately from findings. Preserve the rule that a destination project may explicitly adopt a high-assurance provenance requirement; do not make it an AICore-wide release gate.
5. Remove only the obsolete `.gitignore` workflow-routing line from Warden's persona CV. The runtime spec remains the single workflow source of truth. Preserve Warden's non-mutating scope, exact UV/Python audit commands, no-threat-language rule, and existing license/CVE/postinstall/vendored-bundle severity handling. Re-read the full spec and profile.

## Output

- **Artifact:** concrete evidence-based provenance classification, audit-report contract, and Warden 🔒 (Dependency Warden) CV/runtime routing consistency
- **Schema / shape:** missing optional provenance is visible INFO; PASS is possible when all integrity controls pass; only evidenced anomalies produce ADVISORY or BLOCK; no workflow routing remains in the persona CV

## Gate

- ☑ Warden's Python branch records `verified`, `unavailable`, or `indeterminate` provenance without equating absence to compromise
- ☑ PyYAML's exact verified artifact controls map `unavailable` provenance to INFO and permit PASS
- ☑ ADVISORY/BLOCK provenance conditions require concrete evidence and preserve all existing real supply-chain stops
- ☑ Report template has a separate integrity/provenance observation section
- ☑ Warden's CV removes only the obsolete `.gitignore` routing line; runtime remains the single workflow source
- ☑ Sentinel 🛡️ (Quality Guardian) passes the Warden 🔒 (Dependency Warden) runtime policy and authorized CV deletion; roster-wide CV heading conformance is completed in Phase 11

## Abort conditions

- The policy permits an unpinned dependency, unapproved source, hash mismatch, direct URL, integrity failure, or Critical/High vulnerability to PASS because provenance metadata is absent → stop and ask.
- The policy describes absent optional provenance as proof of package safety or publisher trustworthiness → stop and ask.
- The change alters Warden's persona identity beyond removing its obsolete `.gitignore` workflow-routing line, or alters any other agent → stop and ask.
