# Phase 6 — Marshal 🎖️ (HR Director): acceptance-audit definition remedies

> **Owner:** Marshal 🎖️ (HR Director)
> **Pre:** phase 5 complete; `investigator.md`, `sentinel.md`, and AGENTS.md read in full.
> **Reads:** `.opencode/agents/investigator.md`; `.opencode/agents/sentinel.md`; `AGENTS.md`
> **Writes:** `.opencode/agents/investigator.md` (edit); `.opencode/agents/sentinel.md` (edit)

## Steps

1. In investigator.md, replace the rejected-hypothesis return target that bypasses Cipher 🔓 (L2 Lead) with a return to Cipher 🔓 (L2 Lead). Preserve the existing evidence/rejection workflow; Cipher 🔓 (L2 Lead) remains responsible for deciding any user-facing delivery.
2. In Sentinel's SP-1 and SP-2 checks, distinguish OpenCode runtime specs under `.opencode/agents/*.md` from AGENTS.md. The former require `name`, `description`, and valid `mode`; AGENTS.md is Cipher's root runtime spec by design and is exempt from OpenCode frontmatter/mode fields, but must contain the root H1, `## Identity & Role`, and the explicit runtime-spec declaration.
3. Preserve every other SP requirement for AGENTS.md where applicable (persona reference, role, roster context, naming, hard rules); do not create a blanket AGENTS.md exemption.

## Output

- **Artifact:** corrected `.opencode/agents/investigator.md`; explicit AGENTS.md exception in `.opencode/agents/sentinel.md`
- **Schema / shape:** no Investigator 🔍 (Incident Investigator) workflow path bypasses Cipher 🔓 (L2 Lead); SP-1/2 apply correctly to both runtime-spec forms without weakening the remaining audit contract.

## Gate

- ☑ investigator.md sends every finding and hypothesis result to Cipher 🔓 (L2 Lead)
- ☑ Sentinel 🛡️ (Quality Guardian) SP-1/2 require frontmatter/mode for `.opencode/agents/*.md` and explicitly define AGENTS.md's limited exception
- ☑ AGENTS.md remains subject to all applicable non-frontmatter SP checks

## Abort conditions

- The Investigator 🔍 (Incident Investigator) change would alter evidence standards or let Cipher 🔓 (L2 Lead) rewrite findings instead of deciding delivery → stop and ask.
- An AGENTS.md exception would exempt it from checks beyond frontmatter/mode → stop and ask.
