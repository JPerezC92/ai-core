# User story — core-sync

> **Created:** 2026-10-14
> **Title:** Core synchronization
> **Status:** active
> **version:** 1.2.2
> **Epic:** core-governance
> **Affected areas:** `.opencode/skills/core-sync/`, `distribution-clearance.json`, `distribution-clearance.definition.md`, `knowledge/`
> **Contract approval:** 2026-10-14 — user approved the active contract and uniform-model correction; 2026-10-15 — user approved retired-declaration/table-ownership corrections and the exact genuinely-markerless-source AC2 clarification after paired semantic review. This source-local contract remains excluded from distribution; revision history is pending under the approved timing rule.

## Persona

- A maintainer on either side of the core/destination boundary: the destination maintainer who must receive every cleared update without losing project-owned content, and the source maintainer who ships by a deterministic, verifiable sync.

## Goal

- **G:** Every cleared source distributes through one deterministic sync — core regions splice, raw files copy byte-for-byte, and JSON/JSONC config merges by top-level key — while destination-owned content (project regions and the records they hold) survives every update.
  - Done when: enrollment, update, and verification enforce the declared modes with the documented exit codes; a core region containing a shared table copies byte-for-byte like any other core region; verification is the same core byte-equality for every region source; the distribution clearance file lists every shippable source with its mode; and a record-bearing register ships its frame only.

## Scenario

- The source maintainer runs enrollment from the source checkout against a clean, saved destination: region bindings generate core/project regions and reconciliation reports, raw bindings copy whole files byte-for-byte, and merge bindings write the union of top-level keys. The destination reconciles its project regions and the next verification reports current. Routine updates refresh the same surfaces and never touch destination-owned content.
- The source maintainer prepares skill payloads and knowledge registers for distribution: each skill ships by its cleared root with its region-file subset, and each knowledge register declares its distribution class — record-bearing registers ship their frame only, shared catalogs ship in full.
- A destination's problem register already holds rows its team filed: they live in the destination's project region, survive every sync, and are never substituted; the shipped core table copies byte-for-byte with the core region and never touches them.

## Acceptance criteria

- ⬜ **AC1 — Marker constancy:** Region markers are project-agnostic and spelled exactly, and a source carrying project markers without a valid core pair fails closed rather than copying source project content.
- ⬜ **AC2 — Core extraction:** A source with a valid core pair delivers only that core byte-identically; a genuinely markerless source delivers its whole post-frontmatter body.
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
- ✅ **AC19 — Core table:** A cleared markdown source's shared core tables ship byte-for-byte with the core region; project-owned records, including tabular records, remain project content and never ship.
- ✅ **AC20 — Knowledge register clearance:** Cleared knowledge registers carry a documented distribution class — a record-bearing register ships its frame only and never carries the source's filed records, while a shared catalog ships in full — and destination-owned records live in the project region and are never substituted by a sync.
- ⬜ **AC21 — Merge bindings:** A merge binding writes a document in which every source top-level key holds the source value and every destination-only top-level key is preserved, with source keys replaced wholesale and no deep merge; the output preserves the destination's comments, key order, and formatting and stays loadable; merge bindings create no markers, reports, or pending entries; a config source whose keys are project-owned is cleared as merge rather than raw.
- ⬜ **AC22 — Merge verification:** Merge verification exits 0 when each source top-level key holds the source value with extra destination keys allowed; a missing or mismatched source key or a missing destination exits 1; malformed JSONC or an unknown mode exits 2.

## Proof

Proof paths below are relative to `.opencode/skills/core-sync/scripts/core_sync_pkg/` (each `.../` abbreviates that base); registry/README paths are repo-relative.

- AC1 → `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/constants.py` `BEGIN`/`END`/`PROJECT_BEGIN`/`PROJECT_END` · `.../domain/test_markers.py` `MarkerValidationTests` · `.../tests/test_source_project_markers.py` `SourceProjectMarkerTests`
- AC2 → `.../domain/test_source_core.py` `SourceCoreTests` · `.../tests/test_source_marker_validation.py` `test_commands_reject_malformed_source_without_writing`
- AC3 → `.../tests/test_init.py` `InitContractTests` · `.../tests/test_init_pending.py` `InitPendingTests` · `.../domain/test_reconcile_blocker.py` `ReconcileBlockerContentTests` · `.../tests/test_init_raw_enrollment.py` `RawInitEnrollmentTests`
- AC4 → `.../tests/test_apply.py` `ApplyContractTests` · `.../tests/test_init_refresh.py` `InitRefreshTests` · `.../tests/test_apply_raw_mode.py` `RawApplyTests` · `.../tests/test_merge_apply.py` `MergeApplyTests`
- AC5 → `.../application/verify_destinations.py` `VerifyDestinations.execute` · `.../tests/test_check.py` `CheckContractTests` · `.../tests/test_check_raw_mode.py` `RawCheckTests` · `.../tests/test_check_pending.py` `CheckPendingTests`
- AC6 → `.../tests/test_init_missing_inputs.py` `InitMissingInputsTests.test_init_missing_stored_raw_target_returns_one_without_writes` · `.../tests/test_init_raw_enrollment.py` missing-parent case · `.../tests/test_pending_normalization.py` `RawPendingNormalizationTests` · `.../tests/test_check_stale_raw_pending.py` `StaleRawPendingCheckTests`
- AC7 → `.../tests/test_init_binding_options.py` `InitBindingRegistrationTests` · `.../tests/test_init_binding_conflicts.py` `InitBindingConflictTests` · `.../tests/test_init_binding_validation.py` `InitBindingValidationTests` · `.../tests/test_binding_coexistence.py` `BindingModeCoexistenceTests.test_region_raw_and_merge_coexist`
- AC8 → `.../infrastructure/filesystem.py` `preflight_write_targets` · `.../tests/test_root_overlap.py` `RootOverlapTests` · `.../tests/test_source_write_protection.py` `SourceWriteProtectionTests` · `.../tests/test_destination_write_boundaries.py` `DestinationWriteBoundariesTests` · `.../tests/test_root_raw_alias.py` `RootRawAliasTests`
- AC9 → `.../tests/test_io_errors.py` `FilesystemErrorTests` · `.../infrastructure/composition.py` `main`
- AC10 → `.../tests/test_clearance.py` `DistributionClearanceTests`
- AC11 → `.../domain/clearance.py` `ClearanceRecord`, `SkillRootEntry`, `parse_clearance` · `.../domain/test_clearance_metadata.py` `ClearanceDocumentTests`, `SkillRootEntryTests`, `RegistryDefinitionConformanceTests` · `.../application/test_enroll_destinations.py` `test_root_derived_mode_conflict_fails_before_payload_io`
- AC12 → `.../tests/test_init_bind_cleared.py` `BindClearedBulkEnrollmentTests` · `.../tests/test_bind_cleared_root.py` `BindClearedRootRoutingTests` · `.../application/enroll_destinations.py` `EnrollDestinations.execute` (bulk raw absent-parent rejection is a known pending gap)
- AC13 → `.../domain/test_root_expansion.py` `RootExpansionTests` · `.../tests/test_bind_cleared_root.py` `BindClearedSkillRootTests` · `.../domain/test_clearance_metadata.py` registry self-exclusion/cache tests
- AC14 → `.opencode/skills/ticket-runbook/references/analysis/02-investigate.md` `## Steps` / `## Optional verifier route` behind `<python>` · `.opencode/skills/plan-enforce/SKILL.md` project-owned `### Python invocation`
- AC15 → `.../tests/test_apply_raw_mode.py` `RawApplyTests` · `.../tests/test_source_project_markers.py` `test_source_with_both_pairs_returns_only_core_bytes` · `.opencode/skills/plan-enforce/references/_template-programming.md` raw payload content
- AC16 → `.../tests/test_agent_sources.py` `test_agent_sources_place_core_markers_after_frontmatter`, `test_agent_sources_keep_local_facts_out_of_core`, `test_agent_sources_keep_optional_project_region_shape` · `.../domain/test_regions.py` `RegionDecompositionTests` · `AGENTS.md` root core/project sections
- AC17 → `.../domain/regions.py` pure transforms · `.../application/enroll_destinations.py` `EnrollDestinations.execute` · `.../application/apply_core_revision.py` `ApplyCoreRevision.execute` · `.../application/verify_destinations.py` `VerifyDestinations.execute` · `.../infrastructure/composition.py` CLI wiring · `.opencode/skills/core-sync/scripts/core_sync.py` documented facade
- AC18 → `.../domain/test_source_core.py` `SourceCoreTests` · `.../application/test_enroll_destinations.py` `EnrollDestinationsTests` · `.../infrastructure/test_root_binding_serialization.py` `RootBindingSerializationTests` · `.../tests/test_init.py` `InitContractTests`
- AC19 → `distribution-clearance.json` knowledge region rows · `knowledge/problems.md` core `## Register` table · `.../domain/regions.py` `extract_source_core` / `render_with_region` · `.../tests/test_apply.py` outside-byte preservation assertions
- AC20 → `distribution-clearance.definition.md` `## Knowledge distribution classes` · `knowledge/debt.md` frame-only core · `README.md` shipping policy
- AC21 → `.../domain/merge.py` `merge_top_level` · `.../domain/test_merge_top_level.py` `MergeTopLevelTests` · `.../tests/test_merge_init.py` `MergeInitTests` · `.../tests/test_binding_coexistence.py` three-mode case · `distribution-clearance.json` `opencode.jsonc: merge`
- AC22 → `.../tests/test_merge_check.py` `MergeCheckTests` · `.../tests/test_check_invalid_bindings.py` `CheckInvalidBindingsTests.test_unknown_binding_mode_returns_two`

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

## Revision tracking

- 2026-10-15 — Approved table-ownership and retired-declaration wording corrections await a delivery-matching history reference. These preserve the existing core-byte/project-preservation contract and do not change transport behavior or auto-check historical pending criteria. History finalization remains required before completion, archival, or release handoff. This source-local story is excluded from distribution.
- 2026-10-15 — User explicitly approved the AC2 existing-behavior clarification under the 48-path corrective scope. Malformed active markers still fail closed; fenced marker literals are not active markers. AC2 retains its identity and pending status, and no engine feature or completed delivery is claimed.

## Change log

- 2026-10-14 — knowledge-distribution-20261014 (PR #63): delivered the five knowledge region rows with documented distribution classes, the knowledge splits, and the living-design rename.
- 2026-10-15 — story-distribution-20261015 (PR #64): clarified AC2 to genuinely-markerless whole-body delivery; removed the retired table-declaration wording; repointed Proof to current modules. (source-local, not distributed)
