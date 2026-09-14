# Phase 2 — Type op-model records

> **Owner:** Forge 🔨 (Implementer)
> **Pre:** Phase 1 completes; stash gate passes for this phase's exact writes; no test-file edit is authorized.
> **Reads:** `.opencode/skills/op-model/SKILL.md`; `.opencode/skills/op-model/scripts/models.py`; `knowledge/debt.md` DEBT-003; `user-stories/op-model-configuration.md`; `.opencode/agents/bastion.md`
> **Writes:** `.opencode/skills/op-model/SKILL.md`; `.opencode/skills/op-model/scripts/models.py`; `user-stories/op-model-configuration.md`

## Steps

1. Bump `op-model` metadata version from `1.0.0` to `1.0.1`; do not change its triggers, provider-choice policy, config-edit procedure, or user-facing behavior.
2. Import `TypedDict` and declare `ModelRecord` with `config`, `id`, `provider`, and `name` as `str`, and `cost_in`/`cost_out` as `float`.
3. Type `parse_records` as `list[ModelRecord]`, its `records` local accordingly, `matches` with `ModelRecord`, `_num` with an `object` parameter, and `by_provider` as `dict[str, list[ModelRecord]]`.
4. Preserve parsing, malformed-block skipping, no-record failure, normalization, matching, grouping, sorting, JSON-lines output, and exit behavior byte-for-byte except annotation/import/type-declaration lines.
5. Add no test file. Run syntax and deterministic behavior checks against imported functions without invoking live `opencode models`.
6. Keep story criteria pending until Bastion and behavior gates pass.

## Output

- **Artifact:** `.opencode/skills/op-model/SKILL.md`; `.opencode/skills/op-model/scripts/models.py`; `user-stories/op-model-configuration.md`
- **Schema / shape:** Skill `1.0.1`; one `ModelRecord(TypedDict)`; all structured record collections/consumers typed; no runtime behavior change.

## Verify commands

| Executor | Command |
|---|---|
| Forge 🔨 (Implementer) | `python3 -c "from pathlib import Path; p=Path('.opencode/skills/op-model/scripts/models.py'); compile(p.read_text(), str(p), 'exec')"` |
| Forge 🔨 (Implementer) | `python3 -c "import importlib.util; p='.opencode/skills/op-model/scripts/models.py'; s=importlib.util.spec_from_file_location('models', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); data='demo/model-one\n{\"name\":\"Model One\",\"cost\":{\"input\":1,\"output\":2}}\n'; r=m.parse_records(data); assert r==[{\"config\":\"demo/model-one\",\"id\":\"model-one\",\"provider\":\"demo\",\"name\":\"Model One\",\"cost_in\":1.0,\"cost_out\":2.0}]; assert m.matches('model one', r[0]); assert not m.matches('other', r[0])"` |
| Forge 🔨 (Implementer) | `grep -n 'class ModelRecord(TypedDict)' .opencode/skills/op-model/scripts/models.py` |
| Forge 🔨 (Implementer) | `grep -n 'version: 1.0.1' .opencode/skills/op-model/SKILL.md` |

## Gate

- ⬜ Syntax and deterministic behavior checks exit 0 with the documented record schema unchanged.
- ⬜ No test, dependency, manifest, lockfile, subprocess behavior, or config-edit behavior changes.

## Abort conditions

- Halt if the type fix requires `Any`, casts, runtime validation, a dependency, or behavior-changing refactor.
- Halt if execution proposes a test-file edit; add Crucible 🔥 (Test Architect) explicitly before proceeding.
