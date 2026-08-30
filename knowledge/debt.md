# Accepted Debt Register

Records of deferred technical or process debt that are **non-blocking** for release.

## Entry format

Each entry MUST include:

- **ID** — unique identifier (e.g. `DEBT-001`)
- **Date** — when the deferral decision was made
- **Description** — what is deferred
- **Direct evidence** — the evidence that justifies deferral
- **Resolution criteria** — what must be true for the debt to be cleared
- **Explicit deferral decision** — who decided, and when

## Rules

- An accepted debt is nonblocking only when its record here carries direct evidence, resolution criteria, and an explicit deferral decision (see Herald 📯 (Release Manager) spec).
- Disclose the ID and unresolved criteria in any operation report that touches it.
- Clear and retire a debt in the same PR: the PR that clears a debt deletes its entry from this register, and its body and commit carry the Resolution evidence (criteria met, validation and audit results). Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one PR: its clearing PR.

## Register

### DEBT-001 — PyYAML exact-pin retained; restricted-stdlib-parser option rejected

- **Date:** 2026-08 (read-only dependency comparison)
- **Description:** skill scripts keep exact-pinned PyYAML for YAML parsing; the alternative of a restricted stdlib-only parser was rejected, and no YAML library eliminating the PyPI Trusted-Publishing advisory is adopted.
- **Direct evidence:** Aug 2026 read-only comparison found PyYAML 6.0.3, ruamel.yaml 0.19.1, and StrictYAML 1.7.3 all lack PyPI Trusted Publishing and PEP 740 provenance — switching libraries does not remove the advisory. Re-checked 2026-08-30 (UTC; 2026-08-29 local) — plan `debt-resolution-20260830`, live PyPI per-file metadata: PyYAML 6.0.3 "Uploaded using Trusted Publishing? No" (twine/6.2.0); ruamel.yaml 0.19.1 No (twine/6.2.0, maintainer additionally warns of possible PEP 625 upload block); StrictYAML 1.7.3 No (twine/3.6.0). Retain decision stands.
- **Resolution criteria:** a YAML library ships both PyPI Trusted Publishing and PEP 740 provenance (then re-run the comparison and propose the switch), or the user explicitly reopens the rejected stdlib-parser option.
- **Explicit deferral decision:** Cipher 🔓 (Lead Orchestrator) with user, 2026-08 — retain exact-pinned PyYAML unless either criterion is met.

### DEBT-002 — Per-skill Python environments instead of a single root UV environment ✅ RESOLVED 2026-08-30

- **Date:** 2026-08-29
- **Description:** skill runtime environments are per-skill (only `ticket-runbook` carries `pyproject.toml` + `uv.lock`); the evaluated improvement — one root UV environment with unified pins, migrations generating a destination root env from the dependency union of the selected skills — is deferred.
- **Direct evidence:** full trade-off evaluation 2026-08-29 (user + Cipher 🔓 (Lead Orchestrator)): a root venv is viable and simpler at current scale (one dependency, one pin); dep-union migration is mechanical for the migration skill, which already computes structured per-skill inventories; residual risks manageable (version conflicts detectable at migration time; re-verifying all validators after any dep bump is expected to be fast (sub-second) — hipótesis: runtime estimate, not benchmarked).
- **Resolution criteria:** root `pyproject.toml` + `uv.lock` in place; skills declare dependencies in a migration-readable location (SKILL.md metadata vs root manifest — open decision); `migrate-core-to-project` computes the dependency union with conflict check; validator/test commands run root-level `uv run --locked`; the ticket-runbook per-skill environment is removed; validator tests updated and green.
- **Explicit deferral decision:** user, 2026-08-29 — deferred as too large for the active plan's scope.
- **Resolution:** all six criteria met — plan `debt-resolution-20260830`, 2026-08-30. Root `/pyproject.toml` + `/uv.lock` live (PyYAML==6.0.3, Warden 🔒 (Dependency Warden) PASS ×2); `ticket-runbook/SKILL.md` carries `metadata.dependencies`; `migrate-core-to-project` computes dep-union with conflict check (step 4); all validator commands root-level `uv run --locked`; per-skill env removed; suite 21/21 green.
