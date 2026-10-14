# User story — core-sync

> **Created:** 2026-10-14
> **Title:** Core synchronization
> **Status:** active
> **version:** 1.2.0
> **Epic:** core-governance
> **Affected areas:** `.opencode/skills/core-sync/`, `distribution-clearance.json`, `distribution-clearance.definition.md`, `knowledge/`
> **Contract approval:** 2026-10-14 — user approved CREATE + contract as active after the whole-catalogue review, collision report, and contract preview, and approved the uniform core-table correction (v1.1.0): core tables ship with their core region byte-for-byte and records are project-region content; later the same day the user approved the uniform-model correction (v1.2.0): no table declaration exists, AC19 states the plain core-region fact and AC20's class declaration becomes documentation.

## Persona

- A maintainer on either side of the core/destination boundary: the destination maintainer who must receive every cleared update without losing project-owned content, and the source maintainer who ships by a deterministic, verifiable sync.

## Goal

- **G:** Every cleared source distributes through one deterministic sync — core regions splice, raw files copy byte-for-byte, and JSON/JSONC config merges by top-level key — while destination-owned content (project regions and the records they hold) survives every update.
  - Done when: enrollment, update, and verification enforce the declared modes with the documented exit codes; a core region containing a declared core table copies byte-for-byte like any other core region; verification is the same core byte-equality for every region source; the distribution clearance file lists every shippable source with its mode and core-table declaration; and a record-bearing register ships its frame only.

## Scenario

- The source maintainer runs enrollment from the source checkout against a clean, saved destination: region bindings generate core/project regions and reconciliation reports, raw bindings copy whole files byte-for-byte, and merge bindings write the union of top-level keys. The destination reconciles its project regions and the next verification reports current. Routine updates refresh the same surfaces and never touch destination-owned content.
- The source maintainer prepares skill payloads and knowledge registers for distribution: each skill ships by its cleared root with its region-file subset, and each knowledge register declares its distribution class — record-bearing registers ship their frame only, shared catalogs ship in full.
- A destination's problem register already holds rows its team filed: they live in the destination's project region, survive every sync, and are never substituted; the shipped core table copies byte-for-byte with the core region and never touches them.

## Acceptance criteria

- ⬜ **AC1 — Marker constancy:** Region markers are project-agnostic and spelled exactly, and a source carrying project markers without a valid core pair fails closed rather than copying source project content.
- ⬜ **AC2 — Core extraction:** A marked source delivers only its core region byte-identically; a source without a valid core pair delivers its whole post-frontmatter body.
- ⬜ **AC3 — Enrollment:** Enrollment generates core/project regions from the source core, preserves the destination's previous body in its project region and reconciliation report, records pending state, and writes a self-contained destination-root reconciliation blocker for region paths; raw bindings copy whole source bytes with no regions, reports, or pending entries and create an absent target only for a newly declared mapping whose parent exists.
- ⬜ **AC4 — Update:** Update refreshes region cores, raw files, and merge outputs and proves the bytes outside the core region unchanged; the tool never edits a project region.
- ⬜ **AC5 — Verification:** Verification exits 0 only when every region core matches, every raw file byte-matches, every merge destination carries each source top-level key with the source value, and pending is empty; drift, missing targets, and stale pending exit 1; malformed bindings, malformed JSONC, invalid markers, or an unknown mode exit 2.
- ⬜ **AC6 — Raw mapping lifecycle:** An absent target on a persisted raw mapping is drift and remains an error even when the identical declaration is repeated; a missing parent fails before any write; mode changes clear stale raw pending state and verification rejects leftovers.
- ⬜ **AC7 — Binding declaration:** Bindings register from explicit declarations — idempotent for identical declarations, failing before writes on conflicting source or mode mappings and on noncanonical path aliases — and region, raw, and merge entries coexist in one bindings file.
- ⬜ **AC8 — Write-target preflight:** Overlapping roots, source-contained targets, destination escapes, hard-linked targets sharing an inode with a source, distinct destination strings resolving to one path, blocker or root aliases to raw files, and paths containing a NUL byte all fail before any write and without traceback.
- ⬜ **AC9 — Filesystem errors:** Filesystem write errors produce one concise exit-1 diagnostic without swallowing argument-parse exits or programming errors.
- ✅ **AC10 — Cleared-source authority:** Every bound source is listed in the distribution clearance file; a bound source absent from it, a missing clearance file, and a malformed clearance file each fail with the offending source named.
- ✅ **AC11 — Clearance schema:** Every cleared source — a file or a skill root — declares its binding mode, a skill root declares a default mode plus the file subset overriding it to region mode, and the source root declares its role; a binding mode conflicting with the cleared mode is rejected before any payload read or write.
- ⬜ **AC12 — Cleared enrollment:** Enrolling every cleared source creates new region and raw targets and their parents, requires an existing destination for a merge source, and routes the root to the destination instruction file it detects or to an explicit root override.
- ⬜ **AC13 — Skill payload distribution:** A skill ships as one cleared root: every file under the root is identified at each sync, subset files are region-bound and deliver only their core, every other file copies byte-for-byte, and interpreter caches never ship; the sync tool's own skill is never cleared and any binding naming it fails.
- ⬜ **AC14 — Command placeholders:** Shipped text invokes project-interpreted commands only through the project-substituted command placeholder with the script path and flags literal, and the placeholder's per-project value is declared only in project-owned text.
- ⬜ **AC15 — Payload neutrality:** A raw-bound payload copies byte-for-byte and its source text carries no concrete environment command, dependency pin, mandated local policy value, or source-project business jargon (response-language record labels excepted); a delivered core contains no source identity, reuse guide, or lineage reference.
- ✅ **AC16 — Region document structure:** A region-bound governed document and the root runtime source carry exactly one ordered core pair immediately after frontmatter — a project pair only when source-side project text exists — with core first; inherited baseline content stays in the core, source-only extension text stays in the project region, and only the core region is delivered.
- ⬜ **AC17 — Tool architecture:** The sync tool follows the language-agnostic clean-architecture contract — a pure IO-free domain, one use case per operation with a single entry point, technology adapters plus CLI composition in infrastructure, and a thin documented facade — while CLI verbs, exit codes, bindings schema, and markers stay unchanged by that shape.
- ⬜ **AC18 — Test layering:** Sync tests mirror the architectural layers — domain units, use-case units driven through in-memory port doubles, adapter integration, and CLI end-to-end — and no test imports behavior through the composition facade.
- ✅ **AC19 — Core table:** A cleared markdown source's tables live in its core region and ship with it byte-for-byte like the rest of the core; records the source keeps are project-region content and never ship.
- ✅ **AC20 — Knowledge register clearance:** Cleared knowledge registers carry a documented distribution class — a record-bearing register ships its frame only and never carries the source's filed records, while a shared catalog ships in full — and destination-owned records live in the project region and are never substituted by a sync.
- ⬜ **AC21 — Merge bindings:** A merge binding writes a document in which every source top-level key holds the source value and every destination-only top-level key is preserved, with source keys replaced wholesale and no deep merge; the output preserves the destination's comments, key order, and formatting and stays loadable; merge bindings create no markers, reports, or pending entries; a config source whose keys are project-owned is cleared as merge rather than raw.
- ⬜ **AC22 — Merge verification:** Merge verification exits 0 when each source top-level key holds the source value with extra destination keys allowed; a missing or mismatched source key or a missing destination exits 1; malformed JSONC or an unknown mode exits 2.

## Proof

- AC1 → `test_core_sync_markers.py` · `test_core_sync_source_project_markers.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC2 → `SourceCoreTests` · `test_core_sync_source_marker_validation.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC3 → `test_core_sync_init.py` `InitContractTests` · `ReconcileBlockerContentTests` · `InitBindingRegistrationTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC4 → `test_core_sync_apply.py` `ApplyContractTests` · `test_core_sync_init_refresh.py` `InitRefreshTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC5 → `test_core_sync_check.py` `CheckContractTests` · `test_core_sync_check_raw_mode.py` `RawCheckTests` · `test_merge_check.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC6 → `test_core_sync_init_raw_enrollment.py` `RawInitEnrollmentTests` · `RawPendingNormalizationTests` · `StaleRawPendingCheckTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC7 → `InitBindingConflictTests` · `InitBindingValidationTests` · `BindingModeCoexistenceTests` · `uv run --frozen --group dev pytest -q` → exit 0
- AC8 → `RootOverlapTests` · `SourceWriteProtectionTests` · `DestinationWriteBoundariesTests` · `RootRawAliasTests` · `InitBindingValidationTests` NUL-path case · `uv run --frozen --group dev pytest -q` → exit 0
- AC9 → `test_core_sync_io_errors.py` `FilesystemErrorTests` · `core_sync.py` `main`
- AC10 → `test_core_sync_clearance.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC11 → `core_sync_pkg/domain/clearance.py` file and skill-root entry shapes · `test_core_sync_clearance_metadata.py` · `test_root_expansion.py` · `test_root_mode_conflict.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC12 → `test_init_bind_cleared.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC13 → `distribution-clearance.json` skill-root records · expansion enumeration (caches excluded) · `core-sync check` → exit 1 on a bound uncleared source
- AC14 → shipped skill command examples → no concrete invocations present
- AC15 → raw-bound payload pair `cmp` → exit 0 · identity/env/jargon sweep → no matches · root-identity grep → no matches
- AC16 → `test_core_sync_agent_sources.py` · `test_core_sync_regions.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC17 → `core_sync_pkg/domain/`, `application/`, `infrastructure/` layout · `core_sync.py` documented entry re-export · Bastion 🧱 (Backend & Scripts Architect) code architecture `[PASS]` · Crucible 🔥 (Test Architect) test architecture `[PASS]`
- AC18 → `core_sync_pkg/domain/test_*.py` · `core_sync_pkg/application/test_*.py` · `core_sync_pkg/infrastructure/test_*.py` · `core_sync_pkg/tests/test_*.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC19 → `distribution-clearance.json` knowledge rows · shipped register core-region byte-compare → exit 0 · destination project-region preservation check
- AC20 → `distribution-clearance.definition.md` `## Knowledge distribution classes` · `knowledge/debt.md` frame-only core · `README.md` shipping policy
- AC21 → `core_sync_pkg/domain/merge.py` `merge_top_level` · `test_merge_init.py` · `test_binding_coexistence.py` · `uv run --frozen --group dev pytest -q` → exit 0
- AC22 → `test_merge_check.py` source-key, mismatch, and missing-destination exit-1 cases and malformed-JSONC and unknown-mode exit-2 cases

## Constraints

- The sync tool is the only writer of source-derived core bytes, raw whole-file copies, merged top-level keys, and the reconciliation blocker — because two writers of the same bytes guarantee drift.
- The destination alone edits its project region — because project-owned behavior must survive every core update.
- Marker spellings are project-agnostic and constant — because a project name in a marker makes the marker non-reusable across destinations.
- A source project pair without a valid core pair fails closed — because copying source project content would leak source-only identity into a destination.
- A missing target on a persisted raw binding is drift, not an invitation to create — because an absent file on a stored mapping signals a real break.
- Distribution clearance is the authority for which sources may ship — because a bound source absent from clearance is an unreviewed disclosure.
- Commands ship as project-substituted placeholders — because a concrete invocation in frozen bytes imposes one project's environment on every adopter.
- The sync tool's own skill ships nowhere — because synchronization runs from the source checkout and a shipped copy would drift unversioned at the destination.
- Skill roots expand dynamically at each sync — because clearance records durable ownership, not file inventories.

## Change log
