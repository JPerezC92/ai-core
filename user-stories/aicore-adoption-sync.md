# User story — aicore-adoption-sync

> **Created:** 2026-09-11
> **Title:** Core region synchronization
> **Status:** active
> **version:** 1.5.1
> **Epic:** core-governance
> **Affected areas:** `.opencode/agents/`, `.opencode/skills/`, `agents/`, `README.md`, `AGENTS.md`, `knowledge/agents.md`, `opencode.jsonc`, `user-stories/git-pr-drafting.md`, `distribution-clearance.json`

## Persona

- A maintainer on either side of the core/destination boundary: the destination maintainer who must receive every core update without losing project-owned behavior, and the AICore maintainer who ships the core by a deterministic copy-paste only.

## Goal

- **G:** AICore source files define core bytes: markerless files use the post-frontmatter body; marked files use only their `core` region; JSON/JSONC config sources may instead merge by top-level key. A destination region file = `frontmatter` + core region (byte-identical) + a blank line + a destination-owned `project` region. `core-sync` is the only writer of source-derived core bytes, raw whole-file copies, merged top-level keys, and the reconciliation blocker; the destination alone edits its `project` region.
  - Done when: `init` generates a markerless region destination into core + project regions and sets `pending`, while raw destinations copy whole source bytes without regions and merge destinations write the union of source and destination top-level keys with source values winning; `init --bind-raw` can create an absent target for a newly declared raw mapping when its parent exists, but a missing target for an existing raw binding remains drift; `apply` refreshes region cores, raw files, and merge outputs; `check` exits 0 only when every region core matches, every raw file byte-matches, every merge destination carries each source top-level key with the source value, and region `pending` is empty; drift/missing/stale-pending states exit 1 and malformed bindings, malformed JSONC, or invalid region-destination markers exit 2; the tool writes and clears the destination-root blocker for region paths.

## Scenario

- The core maintainer runs `core-sync init` from the AICore checkout against a clean, saved destination. Region bindings generate core/project regions, set `pending`, and write reconciliation reports; raw bindings copy whole source files byte-for-byte without markers or `pending`. A newly declared raw mapping may create an absent target when its parent directory exists; an absent target for an existing raw mapping remains drift. The script writes the destination-root blocker for region paths. The destination project then reconciles its `project` regions, clears `pending`, and the next `check` reports `current`. Routine core updates run `apply` then `check`. The tool never edits the `project` region, and the core never hand-copies synchronized destination files.
- The core maintainer prepares skill payloads for distribution: each skill ships by its root folder — clearance lists each shipped skill root with a default mode and its region-file subset, and the sync tool identifies the files. The sync tool's own skill ships nowhere. Region-bound skill documents deliver only their core; source project declarations stay home and each destination writes its own, and shipped text states project-interpreted commands only through the `<python>` placeholder.

## Acceptance criteria

- ✅ **AC1:** Region markers are project-agnostic and spelled exactly, with no project name embedded; the tool's constants use exactly those spellings.
- ✅ **AC2:** `init` generates a markerless destination deterministically — frontmatter plus the source core body plus a blank line plus the destination's existing body — refreshes marked region files while preserving bytes outside the core region, sets `pending`, and writes a reconciliation report.
- ✅ **AC3:** `apply` refreshes only the core region and proves the outside-marker bytes are unchanged; `check` exits 0 only when every region core byte-matches, every raw destination byte-matches, and region `pending` is empty.
- ✅ **AC4:** Drift, missing targets, and stale `pending` exit 1; malformed bindings, malformed JSONC, and invalid region-destination markers exit 2.
- ✅ **AC5:** The tool writes a self-contained, step-by-step reconciliation blocker into the destination root when region paths are pending and removes it when those paths are reconciled; the blocker tells the destination to adopt the core-region rule, reconcile, clear `pending`, and delete the blocker.
- ✅ **AC6:** Bindings support per-entry `region` (default) and `raw` modes: `init`/`apply` copy raw source bytes exactly, `check` accepts equal bytes, and raw paths create no project regions, reports, or `pending`. Region and raw entries coexist in one bindings file.
- ✅ **AC7:** `apply` and `init` clear stale raw paths from `pending` after a mode change, while `check` rejects stale state and excludes it from the reconciliation blocker.
- ✅ **AC8:** `init` registers region and raw bindings from explicit CLI declarations and writes the binding metadata itself, so enrollment needs no hand edit to the destination bindings file. Identical declarations are idempotent; conflicting source/mode mappings or noncanonical path aliases fail before writes.
- ✅ **AC9:** Destination file-content differences do not block synchronization: region `init` preserves them in the project region and blocker, while an explicit raw binding overwrites the whole target.
- ✅ **AC10:** A newly declared raw mapping creates an absent destination byte-for-byte when its parent directory exists, with no region, report, or `pending` entry. An absent destination on an already stored raw mapping remains an error without writes, even when the identical declaration is repeated; a missing parent fails before any writes.
- ✅ **AC11:** Write-target preflight rejects hard-linked targets sharing an inode with a source file, distinct destination strings resolving to the same path, and a newly created raw target that would become the selected root runtime; each rejection occurs before any write.
- ✅ **AC12:** Persisted binding source, destination, and root paths containing a NUL byte are rejected as malformed before filesystem operations use those values, with no traceback and no writes.
- ✅ **AC13:** Region sources with no exact core or project marker lines use their whole post-frontmatter body; a valid core pair uses only its core region; a source carrying a project pair without a valid core pair fails closed rather than copying source project content.
- ✅ **AC14:** `check`, `apply`, and `init` preflight resolved roots and every write target; overlapping roots, source-contained targets, destination escapes, and blocker/root aliases to raw files fail before mutation.
- ✅ **AC15:** Filesystem write errors produce a concise exit-1 diagnostic without swallowing argument-parse exits or programming errors.
- ✅ **AC16:** AICore's root runtime carries a reusable `core` region and an AICore-owned `project` region, with core first; only the core region is delivered by a region binding, and the delivered core contains no AICore identity or reuse guide.
- ✅ **AC17:** Every governed agent spec keeps its inherited architecture, workflow, template, and reference baseline inside the extracted core; only evidenced local grants, selected bindings, and local history stay in the project region.
- ✅ **AC18:** Every governed agent spec and persona profile carries exactly one ordered core pair immediately after frontmatter, source-only extension text stays in project regions, and no AICore-specific content remains in extracted cores.
- ✅ **AC19:** The distribution clearance file lists the root runtime, the opencode config, the git-pr story, and every agent spec and persona profile. `check`/`apply`/`init` exit 1 naming a bound source absent from it; a missing file exits 1 and a malformed one exits 2.
- ✅ **AC20:** The shared agent rules state the artifact-naming rule and the distribution clearance file uses that business predicate.
- ✅ **AC21:** A registered destination's files are synchronized only by `core-sync`: the destination root's core bytes match the AICore root core with no AICore identity or reuse-guide in the root, changed bound files are refreshed, and the blocker/report cover every region path in `pending`.
- ✅ **AC22:** A raw-bound story payload is created at the destination byte-for-byte and creates no region, report entry, or `pending` item.
- ✅ **AC23:** The retired adoption management tools and their design document are absent from the tree.
- ✅ **AC24:** The sync tool follows the language-agnostic clean-architecture contract: a pure IO-free domain, one use case per operation with a single `execute()`, technology adapters plus CLI composition in infrastructure, and a thin documented entry that re-exports the public API. CLI verbs, exit codes, bindings schema, and markers are unchanged by that refactor.
- ✅ **AC25:** The distribution clearance file is versioned schema: every cleared source — a file or a skill root — declares its binding mode, a skill root declares a default mode plus the file subset that overrides it to region mode, and the source root declares its role; `check`/`apply`/`init` resolve the operational mode from source and reject a binding mode that conflicts with it before any payload read or write.
- ✅ **AC26:** `init --bind-cleared` enrolls every cleared source not already bound — creating new region/raw targets and parents, while a merge source requires an existing destination and is never created — and routes the root to the destination instruction file it detects, or to an explicit root override.
- ✅ **AC27:** Sync tests mirror the architectural layers: domain units, use-case units driven through in-memory port doubles, adapter integration, and CLI end-to-end, with no test importing behavior through the composition facade.
- ✅ **AC28:** `merge` is a selectable source-owned binding mode: `init`/`apply` write a merged JSON/JSONC document in which every source top-level key is present with the source value and every destination-only top-level key is preserved. A source top-level key replaces the destination's same key wholesale, with no deep merge.
- ✅ **AC29:** For merge bindings, `check` exits 0 when each source top-level key is present with the source value and extra destination keys are allowed; it exits 1 on a missing or mismatched source key or a missing destination, and exits 2 on malformed JSONC or an unknown mode.
- ✅ **AC30:** Merge output preserves the destination's comments, key order, and formatting outside replaced or inserted top-level keys and remains valid JSONC that opencode loads.
- ✅ **AC31:** Merge mode creates no region markers, no reconciliation report, and no `pending` entry, and coexists with region and raw bindings in one bindings file.
- ✅ **AC32:** The opencode config source is cleared as `merge` rather than `raw`; a merge binding of it preserves destination-only top-level keys while propagating AICore's source values.
- ✅ **AC33 — Skill payload distribution:** A skill ships as one cleared root: clearance lists each shipped skill root with its default mode and its region-file subset, and the sync tool identifies every file under the root at each sync — subset files are region-bound and deliver only their core region, every other file takes the default mode and copies byte-for-byte, and interpreter caches never ship. The sync tool's own skill is never cleared and reaches no destination; any binding naming it fails the uncleared-source check.
- ✅ **AC34 — Command placeholders:** Shipped skill text invokes project-interpreted commands only through the project-substituted command placeholder `<python>`, with the script path and flags literal — mirroring the base-ref placeholder convention — and embeds no concrete environment invocation; the placeholder's per-project value is declared only in project-owned text.
- ✅ **AC35 — Raw payload neutrality:** A raw-bound payload copies byte-for-byte and its source text carries no concrete environment command, dependency pin, mandated local policy value, or source-project business jargon; the project's response-language record labels (such as its image-attachment names) are language, not jargon. Placeholder commands, absence-tolerant reference lists, and labelled examples remain permitted.
- ✅ **AC36 — Region skill structure:** The region-bound skill document carries exactly one ordered core pair immediately after frontmatter, a project pair only when source-side project text exists, and only its core region is delivered byte-identically.
- ✅ **AC37 — Neutral delivered cores:** A delivered skill core contains no source-project identity or business jargon (response-language record labels excepted, per AC35), concrete environment invocation, dependency pin, or inlined policy value; such declarations live only in project regions or destination-owned frontmatter.

## Proof

- AC1 → `test_core_sync_markers.py` · `test_core_sync_regions.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC2 → `test_core_sync_init.py` `InitContractTests` · `test_core_sync_init_refresh.py` `InitRefreshTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC3 → `test_core_sync_apply.py` `ApplyContractTests` · `test_core_sync_check.py` `CheckContractTests` · `test_core_sync_check_raw_mode.py` `RawCheckTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC4 → `test_core_sync_check.py` drift/missing/stale-pending → exit 1 cases · `test_core_sync_check_raw_mode.py` · `test_core_sync_init_binding_validation.py` malformed → exit 2 cases
- AC5 → `ReconcileBlockerContentTests`, `ReconcileBlockerLifecycleTests`, `BlockerFenceHandlingTests`, `CheckBlockerWiringTests`, `ApplyBlockerWiringTests`, `InitBlockerWiringTests`, `RootSelectionTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC6 → `BindingModeValidationTests`, `BindingModeSerializationTests`, `BindingModeCoexistenceTests`, `RawCheckTests`, `RawApplyTests`, `RawInitTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC7 → `RawPendingNormalizationTests`, `StaleRawPendingCheckTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC8 → `InitBindingRegistrationTests`, `InitBindingConflictTests`, `InitBindingValidationTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC9 → `test_core_sync_init.py` `InitContractTests` destination-difference cases · `uv run --frozen --group dev pytest -q` → exit 0
- AC10 → `test_core_sync_init_raw_enrollment.py` `RawInitEnrollmentTests` · `test_core_sync_init_missing_inputs.py` `InitMissingInputsTests` · Crucible 🔥 (Test Architect) test-architecture `[PASS]`
- AC11 → `test_core_sync_source_write_protection.py` `SourceWriteProtectionTests` · `test_core_sync_destination_write_boundaries.py` `DestinationWriteBoundariesTests` · `test_core_sync_root_raw_alias.py` `RootRawAliasTests` · Bastion 🧱 (Backend & Scripts Architect) source-write `[PASS]`
- AC12 → `test_core_sync_init_binding_validation.py` `InitBindingValidationTests` NUL-path case · Bastion 🧱 (Backend & Scripts Architect) source-validation `[PASS]`
- AC13 → `SourceCoreTests` · `test_core_sync_source_marker_validation.py` · `test_core_sync_source_project_markers.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC14 → `RootOverlapTests`, `SourceWriteProtectionTests`, `DestinationWriteBoundariesTests`, `RootRawAliasTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC15 → `test_core_sync_io_errors.py` `FilesystemErrorTests` · `core_sync.py` `main`
- AC16 → root/agent core-separation assertion → `core-first/root-separation: PASS` · Sentinel 🛡️ (Quality Guardian) root/agent audit `[PASS]`
- AC17 → `test_core_sync_agent_sources.py` `test_agent_spec_cores_keep_positive_anchors`, `test_agent_sources_keep_local_facts_out_of_core` · Augur 🔮 (Research Analyst) preservation `[PASS]`
- AC18 → `test_core_sync_agent_sources.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC19 → `distribution-clearance.json` · `test_core_sync_clearance.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC20 → `knowledge/agents.md` `### Artifact naming (HARD RULE)`
- AC21 → destination `.aicore/core.yaml` `pending: []` · `.aicore/reconciliation/` records · `core-sync check` → `current`, exit 0 · root-identity grep → no matches
- AC22 → `.aicore/core.yaml` raw binding · source/destination file pair · `init.yaml` region-only contents · `cmp` of source and destination story → exit 0
- AC23 → retired-path absence assertion → `retired adoption paths absent`
- AC24 → `core_sync_pkg/domain/`, `core_sync_pkg/application/`, `core_sync_pkg/infrastructure/` layout · `core_sync.py` documented entry re-export · Bastion 🧱 (Backend & Scripts Architect) code architecture `[PASS]` · Crucible 🔥 (Test Architect) test architecture `[PASS]`
- AC25 → `core_sync_pkg/domain/clearance.py` (file and skill-root entry shapes) · `application/enroll_destinations.py` · `core_sync_pkg/domain/test_clearance_metadata.py` · `core_sync_pkg/domain/test_root_expansion.py` · `core_sync_pkg/domain/test_root_mode_conflict.py` · `core_sync_pkg/application/test_enroll_destinations.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC26 → `core_sync_pkg/tests/test_init_bind_cleared.py`
- AC27 → `core_sync_pkg/domain/test_*.py` · `core_sync_pkg/application/test_*.py` driving `execute()` through in-memory port doubles · `core_sync_pkg/infrastructure/test_*.py` · `core_sync_pkg/tests/test_*.py` CLI end-to-end
- AC28 → `distribution-clearance.json` · `.opencode/skills/core-sync/SKILL.md` `## Binding modes` · `core_sync_pkg/tests/test_merge_check.py`, `test_merge_apply.py`, `test_merge_init.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC29 → `core_sync_pkg/tests/test_merge_check.py` source-key/mismatch/missing-destination exit 1 cases and malformed-JSONC/unknown-mode exit 2 cases
- AC30 → `core_sync_pkg/domain/merge.py` `merge_top_level` · `core_sync_pkg/domain/test_merge_top_level.py` · `.opencode/skills/core-sync/SKILL.md` `## Binding modes`
- AC31 → `core_sync_pkg/tests/test_merge_check.py`, `test_merge_init.py`, `test_binding_coexistence.py`
- AC32 → `distribution-clearance.json` opencode config record
- AC33 → `distribution-clearance.json` skill-root records · expansion enumeration (everything under root minus interpreter caches) · `core-sync check` → exit 1 on a bound uncleared source
- AC34 → shipped skill command examples · `<python>` placeholder form → no concrete invocations present
- AC35 → raw-bound skill file pair · `cmp` source vs destination → exit 0 · jargon/env sweep → no matches (response-language record labels excepted)
- AC36 → delivered region skill file · core-region byte-compare → exit 0
- AC37 → delivered skill core · identity/env/jargon sweep → no matches (response-language record labels excepted)

## Constraints

- `core-sync` is the only writer of source-derived core bytes, raw whole-file copies, merged top-level keys, and the reconciliation blocker — because two writers of the same bytes guarantee drift.
- The destination alone edits its `project` region — because project-owned behavior must survive every core update.
- The core never hand-copies synchronized destination files — because a hand copy is unverifiable and unrepeatable.
- Marker spellings are project-agnostic and constant — because a project name in a marker makes the marker non-reusable across destinations.
- A source project pair without a valid core pair fails closed — because copying source project content would leak source-only identity into a destination.
- A missing target on a persisted raw binding is drift, not an invitation to create — because an absent file on a stored mapping signals a real break.
- Distribution clearance is the authority for which sources may ship — because a bound source absent from clearance is an unreviewed disclosure.
- The opencode config is synchronized by `merge`, not raw — because AICore's source top-level keys are authoritative while destination-only keys and formatting must survive.
- Commands ship as project-substituted `<python>` placeholders — because a concrete invocation in frozen or delivered bytes imposes one project's environment on every adopter.
- The sync tool's own skill ships nowhere — because synchronization runs from the source checkout and a shipped copy would drift unversioned at the destination.
- Skill roots expand dynamically at each sync — because clearance records durable ownership, not file inventories.

## Change log

- before 2026-10-12 — earlier history: see git history for this file.
- 2026-10-12 — core-sync-merge-mode-20261012 (PR #58): added the `merge` binding mode for JSON/JSONC top-level-key merge and reclassified the opencode config from raw to merge.
- 2026-10-12 — story revision (PR #59): split behavioural criteria from `## Proof`, moved synchronization authority policy into `## Constraints`, and dropped test symbols and inline verification commands from criterion text.
- 2026-10-13 — skill-distribution-20261012 (PR #60): delivered the skill-distribution contract — neutral shipped skill payloads (the <python> command-placeholder convention, identity-neutral cores), region markers on workflow skill documents, and the ticket-runbook validator conformance rework.
- 2026-10-13 — skill-root-expansion-20261012 (PR #60): expanded the clearance format in place to the single v1 definition — skill-root rows with region_files and script-side file identification (caches excluded, dynamic at each sync), ten roots replacing per-file skill rows, and distribution-clearance.definition.md as the format source of truth.
