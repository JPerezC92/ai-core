# Phase 1 — Marshal 🎖️ (HR Director): version lifecycle contract

> **Owner:** Marshal 🎖️ (HR Director)
> **Pre:** OpenCode schema checked; no agent version declared; `1.0.0` baseline confirmed.
> **Reads:** `.opencode/agents/marshal.md`; `.opencode/agents/sentinel.md`; `AGENTS.md`; `https://opencode.ai/config.json`
> **Writes:** `.opencode/agents/marshal.md`; `.opencode/agents/sentinel.md`

## Steps

1. Make `version` required repository metadata in every OpenCode agent frontmatter and require Cipher 🔓 (L2 Lead)'s visible root `Spec version` marker.
2. Define SemVer: major for incompatible authority/safety-boundary change; minor for an enforceable capability or rule; patch for compatible runtime correction or clarification; CV-only edits do not bump runtime versions.
3. Give Sentinel 🛡️ (Quality Guardian) the matching field, form, root-marker, and bump-class checks.
4. State that version metadata is not a model, permission, or runtime-behavior control.
5. Re-read both specs for identical policy.

## Output

- **Artifact:** aligned version lifecycle policy
- **Schema / shape:** one OpenCode field rule, one Cipher root rule, and one SemVer policy per authority

## Gate

- ☑ Marshal 🎖️ (HR Director) and Sentinel 🛡️ (Quality Guardian) agree on the same version policy
- ☑ Cipher 🔓 (L2 Lead)'s root structure remains non-frontmatter
- ☑ No role, workflow, permission, or hard-rule change

## Abort conditions

- The schema rejects `version` frontmatter or treats it as runtime behavior → stop and correct the plan.
- A bump rule conflicts with user-authority or release policy → stop and ask.
