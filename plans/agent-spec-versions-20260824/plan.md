# Plan — establish agent-spec version metadata

> **Status:** active
> **Started:** 2026-08-24
> **Subject:** Add durable version metadata and lifecycle rules to all OpenCode agent runtime specs and Cipher's root runtime specification.
> **Layout:** subfolder pattern

## Context

- Prompted by: agent versions were raised during the roster-boundary work but were not converted into an implementation goal.
- Goal: give every runtime authority a comparable, reviewable version baseline without treating CV/persona edits as runtime releases.
- Outcome: every OpenCode agent spec has `version: 1.0.0`; Cipher's root runtime specification has an equivalent `Spec version: 1.0.0` marker; Marshal 🎖️ (HR Director) and Sentinel 🛡️ (Quality Guardian) enforce one versioning policy.
- Story: skipped — non-programming AICore governance metadata.

## Goals

- ☑ **G1:** All seventeen runtime authorities carry an explicit baseline version.
  - Done when: all sixteen `.opencode/agents/*.md` files have `version: 1.0.0` frontmatter and `AGENTS.md` has `> **Spec version:** 1.0.0` beside its root runtime metadata.
- ☑ **G2:** Runtime-spec versions have one documented, enforceable lifecycle.
  - Done when: Marshal 🎖️ (HR Director) documents SemVer bump rules; Sentinel 🛡️ (Quality Guardian) validates field presence, SemVer form, Cipher's root marker, and whether a reviewed runtime change uses the stated bump class; CV-only edits do not bump a runtime version.
- ☑ **G3:** The new metadata is safe for OpenCode and independently accepted.
  - Done when: OpenCode is restarted after the agent-file change; Sentinel 🛡️ (Quality Guardian) passes every authority; no runtime rule is altered except the versioning contract; and `git diff --check` passes.

## Body

| Area | Current behavior | Evidence |
|---|---|---|
| OpenCode agent frontmatter | all sixteen shipped specs have no version metadata | repository scan for `^version:` returns no matches |
| Cipher root runtime spec | intentionally has no YAML frontmatter and no equivalent version marker | `AGENTS.md:1-8` |
| Schema behavior | OpenCode accepts unknown file-frontmatter keys as agent options rather than rejecting startup | `https://opencode.ai/config.json` AgentConfig plus `customize-opencode` guidance |
| Lifecycle policy | Marshal 🎖️ (HR Director) and Sentinel 🛡️ (Quality Guardian) describe runtime-spec structure but not version baselines or bump classes | `.opencode/agents/marshal.md:51-59`; `.opencode/agents/sentinel.md` SP rules |
| Archive retention | user explicitly deleted every completed-plan archive; no plan archive is retained | user instruction, 2026-08-24 |

### Intended contract

| Goal | Before | After | Interface contract | Do-not-break |
|---|---|---|---|---|
| G1 | no comparable runtime version exists | every authority declares baseline `1.0.0` | standard frontmatter key for OpenCode files; root metadata marker for Cipher 🔓 (L2 Lead) | existing names, descriptions, modes, permissions, and workflow text |
| G2 | reviewers infer release significance from prose | Marshal 🎖️ (HR Director) and Sentinel 🛡️ (Quality Guardian) apply one SemVer policy | major for authority/safety boundary break; minor for new enforceable capability; patch for compatible runtime correction | CV-only persona edits never change runtime versions |
| G3 | version metadata has no independent acceptance evidence | restart and Sentinel 🛡️ (Quality Guardian) audit confirm the version contract | restart is required for agent-file configuration changes | no agent behavior or model configuration changes |

### Design decisions

- Use `1.0.0` as the first comparable baseline. No historical semantic version is inferred from prior unversioned edits.
- Version is repository metadata, not an OpenCode behavior setting. The schema accepts it as an agent option; Sentinel 🛡️ (Quality Guardian) treats the file value as the authoritative review marker.
- Cipher 🔓 (L2 Lead) keeps its intentional root runtime shape and uses a visible `Spec version` marker instead of incompatible YAML frontmatter.
- Apply SemVer to runtime authority changes only. CV-only persona changes do not bump a runtime version.
- Do not add a validator script for one repeated field. Sentinel 🛡️ (Quality Guardian)'s existing agent-document audit is the independent mechanical and semantic gate.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output |
|---|---|---|---|---|
| 1 | Version lifecycle contract | Marshal 🎖️ (HR Director) | `phase-01-marshal.md` | Marshal 🎖️ (HR Director)/Sentinel 🛡️ (Quality Guardian) version policy, G2 |
| 2 | Baseline metadata | Marshal 🎖️ (HR Director) | `phase-02-marshal.md` | sixteen frontmatter baselines plus Cipher 🔓 (L2 Lead) root marker, G1 |
| 3 | Restart and acceptance audit | Cipher 🔓 (L2 Lead) | `phase-03-cipher.md` | independent Sentinel 🛡️ (Quality Guardian) acceptance evidence, G3 |

## Critical files / tools

- `.opencode/agents/{atrium,augur,bastion,crucible,forge,herald,inquisitor,investigator,ledger,lumen,marshal,quill,scribe,sentinel,vault,warden}.md`
- `AGENTS.md`
- `.opencode/agents/marshal.md`, `.opencode/agents/sentinel.md`
- `https://opencode.ai/config.json`

## Verification

- ☑ Phase 1: Marshal 🎖️ (HR Director) and Sentinel 🛡️ (Quality Guardian) define the same SemVer and CV-only policy without conflicting rules, G2
- ☑ Phase 2: all sixteen agent files expose exactly `version: 1.0.0`; `AGENTS.md` exposes exactly `Spec version: 1.0.0`, G1
- ☑ Phase 3: restarted OpenCode loads the metadata; Sentinel 🛡️ (Quality Guardian) returns PASS; `git diff --check` exits 0, G3

## Out of scope / Do-not-touch

- CV/profile content and personality versions
- Skill versions, dependency versions, and lockfiles
- Agent runtime behavior, models, permissions, roles, and roster ownership
- Commit, push, branch, and PR actions

## Resolved decisions

- 2026-08-24 — User directed deletion of every completed-plan archive rather than archive-record repair.
- 2026-08-24 — User confirmed a non-programming, no-story plan with three goals: `1.0.0` baselines, lifecycle enforcement, and restart acceptance.
