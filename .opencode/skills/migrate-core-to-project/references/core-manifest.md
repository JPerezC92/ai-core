# Core manifest

| Item | Kind | Source | Destination | Include-rule |
|---|---|---|---|---|
| `git-branch-name` | skill | `.opencode/skills/git-branch-name/` | `<target>/.opencode/skills/git-branch-name/` | always |
| `git-commit` | skill | `.opencode/skills/git-commit/` | `<target>/.opencode/skills/git-commit/` | always |
| `git-pr` | skill | `.opencode/skills/git-pr/` | `<target>/.opencode/skills/git-pr/` | always |
| `op-agent-creator` | skill | `.opencode/skills/op-agent-creator/` | `<target>/.opencode/skills/op-agent-creator/` | always |
| `op-model` | skill | `.opencode/skills/op-model/` | `<target>/.opencode/skills/op-model/` | always |
| `op-skill-creator` | skill | `.opencode/skills/op-skill-creator/` | `<target>/.opencode/skills/op-skill-creator/` | always |
| `plan-enforce` | skill | `.opencode/skills/plan-enforce/` | `<target>/.opencode/skills/plan-enforce/` | always |
| `query-verification` | skill | `.opencode/skills/query-verification/` | `<target>/.opencode/skills/query-verification/` | only if ticket marker |
| `ticket-runbook` | skill | `.opencode/skills/ticket-runbook/` | `<target>/.opencode/skills/ticket-runbook/` | only if ticket marker |
| `atrium` | agent | `.opencode/agents/atrium.md` + `agents/atrium/profile.md` | `<target>/.opencode/agents/atrium.md` + `<target>/agents/atrium/profile.md` | always |
| `augur` | agent | `.opencode/agents/augur.md` + `agents/augur/profile.md` | `<target>/.opencode/agents/augur.md` + `<target>/agents/augur/profile.md` | always |
| `bastion` | agent | `.opencode/agents/bastion.md` + `agents/bastion/profile.md` | `<target>/.opencode/agents/bastion.md` + `<target>/agents/bastion/profile.md` | backend stack OR any selected skill ships Python scripts |
| `crucible` | agent | `.opencode/agents/crucible.md` + `agents/crucible/profile.md` | `<target>/.opencode/agents/crucible.md` + `<target>/agents/crucible/profile.md` | always |
| `forge` | agent | `.opencode/agents/forge.md` + `agents/forge/profile.md` | `<target>/.opencode/agents/forge.md` + `<target>/agents/forge/profile.md` | always |
| `herald` | agent | `.opencode/agents/herald.md` + `agents/herald/profile.md` | `<target>/.opencode/agents/herald.md` + `<target>/agents/herald/profile.md` | always |
| `inquisitor` | agent | `.opencode/agents/inquisitor.md` + `agents/inquisitor/profile.md` | `<target>/.opencode/agents/inquisitor.md` + `<target>/agents/inquisitor/profile.md` | always |
| `investigator` | agent | `.opencode/agents/investigator.md` | `<target>/.opencode/agents/investigator.md` | only if ticket marker |
| `ledger` | agent | `.opencode/agents/ledger.md` + `agents/ledger/profile.md` | `<target>/.opencode/agents/ledger.md` + `<target>/agents/ledger/profile.md` | only if ticket marker |
| `lumen` | agent | `.opencode/agents/lumen.md` + `agents/lumen/profile.md` | `<target>/.opencode/agents/lumen.md` + `<target>/agents/lumen/profile.md` | always |
| `marshal` | agent | `.opencode/agents/marshal.md` + `agents/marshal/profile.md` | `<target>/.opencode/agents/marshal.md` + `<target>/agents/marshal/profile.md` | always |
| `quill` | agent | `.opencode/agents/quill.md` + `agents/quill/profile.md` | `<target>/.opencode/agents/quill.md` + `<target>/agents/quill/profile.md` | only if ticket marker |
| `scribe` | agent | `.opencode/agents/scribe.md` + `agents/scribe/profile.md` | `<target>/.opencode/agents/scribe.md` + `<target>/agents/scribe/profile.md` | only if ticket marker |
| `sentinel` | agent | `.opencode/agents/sentinel.md` + `agents/sentinel/profile.md` | `<target>/.opencode/agents/sentinel.md` + `<target>/agents/sentinel/profile.md` | always |
| `vault` | agent | `.opencode/agents/vault.md` + `agents/vault/profile.md` | `<target>/.opencode/agents/vault.md` + `<target>/agents/vault/profile.md` | always |
| `warden` | agent | `.opencode/agents/warden.md` + `agents/warden/profile.md` | `<target>/.opencode/agents/warden.md` + `<target>/agents/warden/profile.md` | always |
| `cipher` | agent | `agents/cipher/profile.md` | `<target>/agents/cipher/profile.md` | always (CV-only, no runtime spec) |
| `knowledge/agents.md` | infra | `knowledge/agents.md` | `<target>/knowledge/agents.md` | always |
| `knowledge/debt.md` | infra | `knowledge/debt.md` | `<target>/knowledge/debt.md` | always |
| `symptom-problem-register` | infra | `knowledge/symptoms.md` + `knowledge/problems.md` | `<target>/knowledge/symptoms.md` + `<target>/knowledge/problems.md` | always |
| `query-verification-design` | infra | `knowledge/query-verification-design.md` | `<target>/knowledge/query-verification-design.md` | only if ticket marker |
| `plans/` | infra | `plans/.gitkeep` | `<target>/plans/.gitkeep` | always |
| `user-stories/` | infra | `user-stories/.gitkeep` | `<target>/user-stories/.gitkeep` | always |
| `AGENTS.md` | config | (generated) | `<target>/AGENTS.md` | merge, not copy |
| `opencode.jsonc` | config | (permission block) | `<target>/opencode.jsonc` | merge, not copy |
| `.gitignore` | config | (entries) | `<target>/.gitignore` | merge, not copy |
