---
name: dependency-review
description: Reviews a dependency surface change for integrity, approved source, licence, advisories, install-time execution and supply-chain health before any installation is authorized. Use when proposing or changing a package, manifest, lockfile, skill install, or environment declaration.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.0.0
---

## Mandatory core

### What I do

Review one dependency surface change and produce a stated verdict. This is a **review procedure, not an authority**: installing anything remains a user-authorized action, and a review never constitutes that authorization.

### When I apply

Run this review when the authorized task touches a dependency surface:

1. A new package is proposed, or an existing pin changes version.
2. A manifest or lockfile diff is about to be staged.
3. A skill is installed, or a skill's `scripts/` or declared dependencies change.
4. A new `.env.example` variable or a new CI workflow file is proposed.
5. A permission rule or a runtime's declared mandatory command changes.
6. The user explicitly requests a dependency health check over a named surface.

Do not run a dependency audit at the start of a routine task whose scope does not touch a dependency surface. Record the surface as **not inspected for this task** instead — silence is honest, a fabricated clean result is not.

### What I do not do

- I do not install, upgrade, or remove a package.
- I do not edit a manifest, lockfile, source file, or `.gitignore`.
- I do not widen an audit to a remote service, a source-repository research pass, or a per-artifact download without an explicit per-case grant.
- I do not treat an unverified control as a passing control.

### Procedure

**1. Establish the surface.** Discover the root manifest/lock pairs the repository actually declares; never assert a package manager or package set the repository does not have. A manifest without its paired lockfile is a reported gap, not a skipped branch. When both a JavaScript and a Python surface exist, review both independently.

**2. Determine the approved source.** The lockfile records each artifact's integrity digest but not the registry that resolved it. Read the effective registry through the project's authorized command or declared configuration. A declared index, a direct URL, or an unapproved registry is a finding.

**3. Read the exact pins and hash coverage.** Enumerate direct dependencies and dev dependencies, exact pins, and committed integrity digests. A pin that is a range where the project requires exactness, or a lockfile entry without committed hash coverage, is a finding.

**4. Licence.** Record the declared licence of each candidate artifact. Anything absent, non-permissive beyond the project's declared policy, or inconsistent with the manifest is a finding.

**5. Advisories.** Run the project's authorized advisory scan in its configured output mode and read the result. Report findings by severity; do not substitute a memory of an earlier scan for a current one, and do not expand into external research the project has not authorized.

**6. Install-time execution.** Enumerate the lifecycle scripts the candidate and its resolved graph declare — `preinstall`, `install`, `postinstall`, `prepare`. An unknown or unexpected hook on a top-level package is reported immediately. Treat "no declared scripts" as a claim to verify, not an assumption.

**7. Publisher provenance.** Evaluate provenance per artifact and use the strongest tier the artifact supports; a lower tier is not a finding by itself.

- **Tier 1 — attested.** The package ships publisher provenance (for example Trusted Publishing with signed attestations). Verify the attestation identity matches the canonical project; record the evidence source. Status `verified`.
- **Tier 2 — post-hoc source correspondence.** No publisher provenance exists, but the exact pinned bytes provably match the maintainers' canonical source. **Only on an explicit per-case grant naming the packages**, and every step is recorded: fetch the registry's canonical digests; match them against the lockfile hash; download the pinned artifact and close the digest chain; fetch the maintainers' source tag for the same version; content-diff excluding generated metadata and VCS/CI files; verdict `verified` on zero source differences, otherwise a documented source inconsistency.
- **Tier 3 — unverifiable.** Neither is establishable. Status `unavailable` or `indeterminate`.

Missing optional provenance metadata is **not** a finding when the other integrity controls positively pass: approved source, exact pin, committed hash coverage, acceptable licence, clean advisory result, compatible locked environment. A **hash mismatch is never optional** — it is an integrity failure and blocks.

**8. Skill installs.** For a skill, read `SKILL.md` in full, inventory `scripts/` filenames and sizes, and read any vendored bundle's licence header or accompanying licence file. Read a script's full content only when its filename or `SKILL.md` declares a network call, a file write, or shell execution. A vendored bundle with no licence and no version pin is an advisory finding.

**9. Environment declarations and CI.** For a new environment variable, confirm public/private separation follows the framework the repository actually declares, that the variable is referenced in source, and that the corresponding `.env` file is ignored. For a new workflow file, record which actions are pinned by SHA versus tag, whether secrets reach an untrusted context, and whether install steps use a frozen lockfile.

### Evidence reuse

An accepted review whose recorded inputs still match is reused rather than repeated: report the reused evidence, its input identity, and the fact that it was reused. Re-run the affected check when a relevant input changed. A missing optional provenance document is not a repository-wide re-scan trigger.

### Output

Lead with the verdict, then the evidence table.

```
APPROVE | CONDITIONAL | REJECT — one-sentence basis
surface: <manifest/lockfile/skill path>  ·  approved source: <value>  ·  pins: <exact|range>  ·  advisories: <counts>  ·  postinstall: <none|declared|unknown>
```

Then one row per artifact carrying a finding, with the control it fails and the concrete remedy. Record any control you could not discharge as **unverified** with the command that was unavailable — never as passing.

**Severity.** `BLOCK` for a hash mismatch, an unapproved source, a non-permissive licence under the project's policy, a known-exploitable advisory on the candidate, or an unexplained install-time hook. `ADVISORY` for a maintenance signal, a missing optional metadata field with every other control passing, or a vendored bundle without a licence or pin.

### Installation remains user-authorized

A review verdict never installs anything. Installation is an explicit user authorization, and the runtime's own permission prompt is the enforcement point. When a review returns `REJECT` or an unverified blocking control, say plainly that installation should not proceed and why; do not decide for the user, and do not install to "verify" the conclusion.

### Hard limits

- Read-only. No install, no edit, no lockfile write.
- No Git or GitHub command of any kind.
- No widening of the audit beyond the authorized surface.
- A review is not an independent permission boundary: it runs in the same runtime context as the work it reviews. Its value is a stated, evidence-bound verdict.
