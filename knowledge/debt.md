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

### DEBT-001 — `git-pr` misses subfolder plans when gathering PR context

- **ID:** DEBT-001
- **Date:** 2026-09-13
- **Description:** `.opencode/skills/git-pr/SKILL.md` step 3 looks only for `plans/*.md`, so subfolder plans at `plans/*/plan.md` are not read; a freshly drafted PR body can omit the plan's Context/motivation.
- **Direct evidence:** `.opencode/skills/git-pr/SKILL.md:43` — "Look for `plans/*.md` with `Status: active` or `Status: completed`". The project's plan layout is subfolder (`plans/<slug>-YYYYMMDD/plan.md`), so the glob matches nothing on a typical plan-bearing branch.
- **Resolution criteria:** line 43 also matches `plans/*/plan.md` (or a glob covering both single-file and subfolder layouts), and a `git-pr` draft run against a subfolder-plan repo includes the plan Context.
- **Explicit deferral decision:** Cipher 🔓 (Lead Orchestrator), 2026-09-13 — minor and non-blocking; ship as a `git-pr` patch (`1.3.0` → `1.3.1`) in the next feature change that touches the skill.

### DEBT-002 — `git-pr` bare `Herald 📯` mentions lack the role parenthetical

- **ID:** DEBT-002
- **Date:** 2026-09-13
- **Description:** `.opencode/skills/git-pr/SKILL.md` uses bare `Herald 📯` at three lines instead of the roster format `Name Emoji (Role)`.
- **Direct evidence:** `.opencode/skills/git-pr/SKILL.md:85,157,185` use bare `Herald 📯`; the compliant `Herald 📯 (Release Manager)` form appears at lines 27, 50, 110, 167, 193.
- **Resolution criteria:** every non-possessive `Herald 📯` mention in the file carries `(Release Manager)`; possessives stay bare.
- **Explicit deferral decision:** Cipher 🔓 (Lead Orchestrator), 2026-09-13 — cosmetic and non-blocking; ship as a `git-pr` patch (`1.3.0` → `1.3.1`) in the next feature change that touches the skill.

### DEBT-003 — `op-model` script has two Python type-annotation violations

- **ID:** DEBT-003
- **Date:** 2026-09-14
- **Description:** `.opencode/skills/op-model/scripts/models.py` violates the shared Python type-hint rules: an untyped function parameter, and structured records carried as untyped `dict` rather than a `TypedDict`.
- **Direct evidence:** `.opencode/skills/op-model/scripts/models.py:79` — `def _num(value) -> float:` has no parameter annotation. Lines 52 and 90 — `def parse_records(stdout: str) -> list[dict]:` and `def matches(query: str, record: dict) -> bool:` use untyped `dict` for structured records (config/id/provider/name/cost_in/cost_out). Found by Bastion 🧱 (Backend & Scripts Architect) during a downstream adopter's atomic adoption, on byte-identical copies (sha256 `7d3c1a9b6cfb22783705efc457ff09d93879bb39bcf29294a5d864f802e8f284`).
- **Resolution criteria:** `_num` has a typed parameter; the record shape is declared as a `TypedDict` and used by `parse_records` and `matches`; Bastion 🧱 (Backend & Scripts Architect) re-audits the file with `[PASS]`.
- **Explicit deferral decision:** Cipher 🔓 (Lead Orchestrator), 2026-09-14 — non-blocking for that adoption: the file is a byte-identical core copy and a local fix would break the adoption mirror and compliance check. Clear and retire in the next AICore release that touches `op-model`; the fix propagates to adopters via `sync-aicore-adoption`.
