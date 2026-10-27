# 04 — Recommendations (proposals)

> Part of the ODD fit publication ([`README.md`](README.md)). Source: `output/research/odd-foundation-fit/brief.md`, Q7. **Every item below is a proposal for the user to accept, modify, or reject.** None is an adopted requirement, none authorizes an edit, and none is delivery evidence for the plan or any story. Each states: mechanism → plan goal/stage served → required surface/owner → falsifier. Citation convention: `S#` = research-set citation IDs; plan passages cited by section name + goal/row identity; `infer:` labels preserved.

1. **Resumability eligibility criterion**
   - Mechanism: adopt ODD's classification sentence ("could be resumed from the request plus `git diff`"; counts of files, commands, tests, fixes, or a requested todo list never decide it, S4) as the definition of Stage D's "consistent lightweight eligibility".
   - Serves: Stage D; R1 proportionality.
   - Surface/owner: `plan-enforce` skill + owning story, revised by Vault 🔐 (Catalog Steward), accepted by Cipher 🔓 (Lead Orchestrator).
   - Falsifier: tasks classified "lightweight" under the resume test repeatedly need re-planning or fail audits in Stage G comparisons.

2. **Snapshot identity on every review**
   - Mechanism: generalize the existing SHA256-bound review practice (plan, Foundation planning review; Current preparation state) into an explicit rule — every review names the exact candidate identity it judged, and any byte change invalidates the verdict (S8, S6).
   - Serves: R2 "binding each review to its snapshot"; Stage E "reuse only unchanged evidence".
   - Surface/owner: `knowledge/agents.md` review rules or `clean-architecture-contract` evidence clauses (Sentinel 🛡️ (Quality Guardian), Cipher 🔓 (Lead Orchestrator)).
   - Falsifier: Stage G finds zero stale-verdict cases caught that naming would not already have caught — overhead without added safety.

3. **Close-report triad in the feedback envelope**
   - Mechanism: make the "Report an outcome" field explicitly require "the verified outcome, every failed or pending check, and the next step" (S4).
   - Serves: G2 ordinary feedback; G3; R4.
   - Surface/owner: `knowledge/agent-workflow.md` (authored per plan, Execution and ownership 2 by Scribe ✍️ (Docs & Problems Manager); reviewed by Sentinel 🛡️ (Quality Guardian)) within the 100-line/900-word budget (plan, Small-document budgets).
   - Falsifier: scenario review (plan, Verification) still shows pending or failed checks dropped from routine reports.

4. **Bounded causal admission for deferrals**
   - Mechanism: adopt "a finding can block only if your change caused it" (S8) **only** for routing unrelated pre-existing defects to their owner with explicit deferral, explicitly subordinated to the plan's safety/authority stop conditions (plan, For encountered defects).
   - Serves: G2 conflict dispositions.
   - Surface/owner: the "Handle a conflict" section of the entry + `agent-workflow-navigation` story criteria (Cipher 🔓 (Lead Orchestrator)).
   - Falsifier: any safety/authority conflict is deferred under the causal rule, or deferrals vanish without a register owner.

5. **Resolvable-command blocker rule**
   - Mechanism: adopt "A message may name a command only if running that command resolves the block" (S7) as a blocker-reporting rule.
   - Serves: G2; Stage E/F "exact invocation evidence" (plan, Execution contracts 6).
   - Surface/owner: `knowledge/agents.md` report discipline.
   - Falsifier: recorded blocker rounds still cite commands that do not resolve their block.

6. **Affected-spec-only story updates**
   - Mechanism: adopt "A requirement change rewrites only the affected spec and reopens only its task" (S4) as the concrete rule behind "do not reset unrelated marks" in Stage C.
   - Serves: Stage C; R3.
   - Surface/owner: `user-story` skill and `plan-lifecycle-governance` corrections (Cipher 🔓 (Lead Orchestrator), independent semantic reviewer per plan, Stage C).
   - Falsifier: partial reopens consistently miss cross-criterion dependencies that collision review does not catch.

7. **Reproducibility contract for pilots**
   - Mechanism: bind Stage G to S7's standard — publish matched inputs/originals/candidates per comparison (following the Isolated foundation-only validation model, plan), and label walkthroughs and unmeasured cells explicitly (plan, Stage G; R4).
   - Serves: Stage G; R4; G3.
   - Surface/owner: project-owned story evidence at actual owners (plan, Stage G "Project-owned evidence at actual story/register owners").
   - Falsifier: a published comparison cannot be re-run from its recorded inputs — the standard it states.

8. **Explicit deferral of tool adoption**
   - Mechanism: record that gentle-ai / engram / gga adoption is out of this program and may return only as a separate dependency decision under Warden 🔒 (Dependency Warden) review and the plan's exclusions (plan, Still excluded; Execution contracts 2).
   - Serves: all stages' scope discipline.
   - Surface/owner: a line in the appropriate ADR or story Constraints (Scribe ✍️ (Docs & Problems Manager) / Vault 🔐 (Catalog Steward)), not a new policy document.
   - Falsifier (i.e., worth revisiting): Stage G evidence shows prose-level disciplines measurably underperform tool-enforced ones **and** the user accepts a dependency/harness change.

## Closing note — tool adoption is a separate decision

Adopting the tools (gentle-ai, engram, gga) is **not** part of proposals 1–7. Per proposal 8, it is a separate dependency decision that may return only under Warden 🔒 (Dependency Warden) review and the plan's exclusions ("runner/model/dependency changes", "adopter mutations"; plan, Still excluded; Execution contracts 2; "No destination sync or destination mutation is authorized", plan, First increment note). Until the user makes that decision explicitly, the tools remain unadopted and unexercised ([`README.md`](README.md) gap 6), and the prose-level disciplines above stand or fall on their own falsifiers.
