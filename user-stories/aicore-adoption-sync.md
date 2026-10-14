# User story — aicore-adoption-sync

> **Created:** 2026-09-11
> **Title:** AICore adoption governance
> **Status:** active
> **version:** 2.0.0
> **Epic:** core-governance
> **Affected areas:** `AGENTS.md`, `README.md`, `.opencode/agents/`, `agents/`
> **Contract approval:** 2026-10-14 — user approved the scope narrowing to source-side adoption governance after the whole-catalogue review, collision report, and contract preview.

## Persona

- The AICore maintainer who ships a neutral, reusable core and must keep this project's identity, adoption governance, and registry state from reaching any destination payload.

## Goal

- **G:** AICore ships as a neutral reusable core: no source identity, repository, reuse-guide, or lineage reference reaches any destination payload; source identity lives only in the adopter's bindings record; adoption governance stays source-side.
  - Done when: every delivered core and raw payload is clean of AICore identity and reuse-guide text; the root core is project-agnostic while the reuse guide and project extensions live in source-owned project text; the retired adoption tooling is absent; and the adopter's bindings file is the only home of source identity while AICore keeps no adopter registry.

## Scenario

- The AICore maintainer prepares the core for distribution and reviews what will be delivered: cores carry no identity or reuse-guide text, the reuse guide remains in project-owned text and is never delivered, the retired management tools stay absent, and each adopter's bindings and reconciliation records remain that adopter's own state.

## Acceptance criteria

- ✅ **AC1 — Identity neutrality:** No delivered core or raw payload carries AICore identity, repository, reuse-guide, or lineage references; source identity is recorded only in the adopter's bindings file.
- ✅ **AC2 — Root and reuse separation:** The root runtime's core region is reusable and project-agnostic; the reuse guide and project extensions live in source-owned project text and are never delivered.
- ✅ **AC3 — Retired tooling:** The retired adoption management tools and their design document are absent from the tree.
- ✅ **AC4 — Bindings ownership:** A destination's bindings and reconciliation records are destination-owned state; AICore keeps no adopter registry and no cross-destination verification checker.
- ✅ **AC5 — Artifact naming:** The shared agent rules state the artifact-naming rule and the distribution clearance file uses that business predicate.

## Proof

- AC1 → root/agent core-separation assertion → `core-first/root-separation: PASS` · Sentinel 🛡️ (Quality Guardian) root/agent audit `[PASS]`
- AC2 → `AGENTS.md` `## Project extensions` reuse guide · delivered-root identity grep → no matches
- AC3 → retired-path absence assertion → `retired adoption paths absent`
- AC4 → `AGENTS.md` `## Project extensions` → Destination bindings · adopter `.aicore/core.yaml` ownership
- AC5 → `knowledge/agents.md` `### Artifact naming (HARD RULE)` · `distribution-clearance.json` filename

## Constraints

- Source identity stays home — because a destination payload carrying the source project's identity breaks reuse and leaks lineage.
- AICore keeps no adopter registry — because destination bindings are destination-owned state and cross-destination verification is out of scope.

## Change log

- before 2026-10-12 — earlier history: see git history for this file.
- 2026-10-12 — core-sync-merge-mode-20261012 (PR #58): added the `merge` binding mode for JSON/JSONC top-level-key merge and reclassified the opencode config from raw to merge.
- 2026-10-12 — story revision (PR #59): split behavioural criteria from `## Proof`, moved synchronization authority policy into `## Constraints`, and dropped test symbols and inline verification commands from criterion text.
- 2026-10-13 — skill-distribution-20261012 (PR #60): delivered the skill-distribution contract — neutral shipped skill payloads (the <python> command-placeholder convention, identity-neutral cores), region markers on workflow skill documents, and the ticket-runbook validator conformance rework.
- 2026-10-13 — skill-root-expansion-20261012 (PR #60): expanded the clearance format in place to the single v1 definition — skill-root rows with region_files and script-side file identification (caches excluded, dynamic at each sync), ten roots replacing per-file skill rows, and distribution-clearance.definition.md as the format source of truth.
- 2026-10-14 — knowledge-distribution-20261014 (PR #63): re-scoped the story to source-side adoption governance (v2.0.0) — title, persona, and goal rewritten to identity neutrality and bindings ownership; the sync-mechanism criteria are superseded by the `core-sync` story.
