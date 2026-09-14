# Phase 3 — Audit Python architecture

> **Owner:** Bastion 🧱 (Backend & Scripts Architect)
> **Pre:** Phase 2 implementation and deterministic checks pass on the final script content.
> **Reads:** `.opencode/skills/op-model/scripts/models.py`; `.opencode/skills/op-model/SKILL.md`; `knowledge/debt.md` DEBT-003; `plans/skill-debt-resolution-20260914/phase-02-forge-op-model.md`
> **Writes:** none; return a read-only architecture gate response to Cipher 🔓 (Lead Orchestrator)

## Steps

1. Audit the complete script against Bastion's Python script branch, with explicit focus on parameter/return annotations, `TypedDict` use, IO boundaries, subprocess safety, error behavior, and module structure.
2. Re-run the syntax and deterministic behavior commands declared in Phase 2.
3. Verify the change is annotation-only at runtime and satisfies every DEBT-003 resolution criterion.
4. Return `[PASS]` only with exact line and command evidence; otherwise `[FAIL]` with remediation.

## Output

- **Artifact:** Bastion gate response in the phase handoff.
- **Schema / shape:** `[PASS]` or `[FAIL]`, rule-by-rule evidence, exact command outputs, and DEBT-003 criterion disposition.

## Verify commands

| Executor | Command |
|---|---|
| Bastion 🧱 (Backend & Scripts Architect) | `python3 -c "from pathlib import Path; p=Path('.opencode/skills/op-model/scripts/models.py'); compile(p.read_text(), str(p), 'exec')"` |
| Bastion 🧱 (Backend & Scripts Architect) | `python3 -c "import importlib.util; p='.opencode/skills/op-model/scripts/models.py'; s=importlib.util.spec_from_file_location('models', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); data='demo/model-one\n{\"name\":\"Model One\",\"cost\":{\"input\":1,\"output\":2}}\n'; r=m.parse_records(data); assert r[0][\"cost_in\"]==1.0; assert m.matches('model one', r[0])"` |

## Gate

- ⬜ Bastion returns `[PASS]` on the final file and explicitly confirms DEBT-003 criteria are met.

## Abort conditions

- Halt on any untyped parameter, bare structured `dict`, behavior drift, unsafe subprocess change, or unauthorized file edit.
