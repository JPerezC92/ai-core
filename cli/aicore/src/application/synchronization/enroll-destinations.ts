/**
 * Use case: enroll markerless destinations and refresh already-marked ones.
 *
 * This coordinator holds the enrollment's own request handling, its declaration
 * gates in their original order, the read preflight, execution of the validated
 * envelope and the result message. The effective document is determined by
 * `PlanSynchronizationDocument`, the payload changes by
 * `PlanEnrollmentChanges`, and the mutations by `PrepareSynchronizationExecution`.
 *
 * Enrollment is the only command that creates a merge target, and only when this
 * run newly binds it and it is absent: every later `init`, and `apply`, report a
 * missing merge destination as drift. A created or recreated region target takes
 * the source's frontmatter, the source core, and an empty project region, so a
 * declaration does not depend on when it was recorded. A newly enrolled or
 * rewritten region destination is recorded in `pending` and in the reconciliation
 * report; raw and merge destinations are non-region and record neither.
 *
 * An already-bound source whose clearance record now declares another
 * destination is the drift `apply` and `check` refuse, refused here before any
 * write: enrollment never moves a destination, and never reports a diverged
 * binding as initialized.
 *
 * A source the destination excludes is never bound and never written here, and
 * dropping a binding it held lists that destination in `pending` without
 * deleting the file.
 *
 * The run reads and writes through two preflights. The read preflight clears
 * every path whose contents the run reads; the mutation preflight clears the
 * complete set of writes the run performs, including the ones it only performs
 * when their content changes.
 */

import { CLEARANCE_FILENAME, MODE_RAW, MODE_REGION } from "#domain/synchronization/constants.ts";
import {
	bindingModeConflict,
	destinationDrift,
	duplicatedDestinations,
	parseInitBindingSpec,
	protectedExclusionFailure,
	withInitDeclarations,
	withOptOuts,
	withRestoredOptOuts,
} from "#domain/synchronization/bindings.ts";
import { drift, failed, invalid, succeeded, type OperationOutcome } from "#domain/synchronization/failures.ts";
import { editorMismatch, effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import { missingRegionSources } from "#domain/synchronization/reconciliation.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type {
	BindingsStore,
	ClearanceStore,
	DestinationFiles,
	FilesystemLayout,
	WriteTargetGuard,
} from "#domain/synchronization/ports.ts";

import { invalidClearance, readClearanceModes } from "./clearance-modes.ts";
import { PlanSynchronizationDocument } from "./plan-synchronization-document.ts";
import { ensureOpenCodeSecrets } from "./open-code-secrets.ts";
import { PlanEnrollmentChanges } from "./plan-enrollment-changes.ts";
import { destinationReadPaths, PrepareSynchronizationExecution } from "./prepare-synchronization-execution.ts";
import type { EnrollmentRequest } from "./requests.ts";

/** Collaborators enrollment needs. */
export type EnrollDestinationsDependencies = {
	readonly bindings: BindingsStore;
	readonly clearance: ClearanceStore;
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
	readonly guard: WriteTargetGuard;
	readonly determineDocument: PlanSynchronizationDocument;
	readonly planChanges: PlanEnrollmentChanges;
	readonly prepareExecution: PrepareSynchronizationExecution;
};

export class EnrollDestinations {
	readonly #dependencies: EnrollDestinationsDependencies;

	constructor(dependencies: EnrollDestinationsDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(request: EnrollmentRequest): Promise<OperationOutcome> {
		const {
			bindings,
			clearance: clearanceStore,
			destinations,
			layout,
			guard,
			determineDocument,
			planChanges,
			prepareExecution,
		} = this.#dependencies;

		const loaded = await bindings.load(request.bindingsPath);
		if (loaded === null && !request.bindCleared) {
			return failed(invalid(`invalid bindings: ${request.bindingsPath}`));
		}
		const base: BindingsDocument = loaded ?? {
			coreRevision: request.sourceRevision,
			root: null,
			editor: null,
			exclude: [],
			bindings: [],
			pending: [],
		};

		// A destination with no bindings file is not enrolled for any editor yet, so
		// this enrollment chooses one; an enrolled destination keeps the editor it
		// was enrolled for.
		const mismatch = loaded === null ? null : editorMismatch(base.editor, request.editor);
		if (mismatch !== null) {
			return failed(mismatch);
		}
		const editor = effectiveEditor(request.editor, base.editor);

		// Before any clearance read, payload read or write: an opt-out that names the
		// baseline the enrollment delivers is refused, not honored.
		const protectedExclusion = protectedExclusionFailure(base);
		if (protectedExclusion !== null) {
			return failed(protectedExclusion);
		}

		const declared = withInitDeclarations(base, request.regionDeclarations, request.rawDeclarations);
		if (declared.failure !== null) {
			return failed(declared.failure);
		}
		// The destination's own opt-outs win over every path that could bind the
		// source: a fresh enrollment, a re-enrollment, and an explicit declaration.
		const applied = withOptOuts(declared.document);

		const clearance = await readClearanceModes(clearanceStore, layout, request.sourceRoot, editor);

		// A revoked opt-out is delivered again here too, and its outstanding path
		// leaves `pending`, so a re-enrollment and an `apply` agree on the state.
		const restored = withRestoredOptOuts(applied, clearance.modes, clearance.destinations);

		const determination = await determineDocument.execute({
			document: restored,
			clearance,
			editor,
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			intent: {
				kind: "enroll",
				rootOverride: request.rootOverride,
				enrollUnseen: request.bindCleared,
			},
		});
		if (!determination.ok) {
			return failed(determination.failure);
		}
		const determined = determination.value;
		const effective = determined.document;
		const newRawDestinations = new Set<string>([...declared.newRawDestinations, ...determined.newRawDestinations]);

		// Every path this run reads is cleared before it is read: the effective
		// document the run acts on is guarded before any payload read.
		const readRefusal = await guard.refuse({
			command: "init",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document: effective,
			modes: clearance.modes,
			newRawDestinations,
			phase: "read",
			readPaths: await destinationReadPaths(effective, request.destinationRoot, layout),
		});
		if (readRefusal !== null) {
			return failed(readRefusal);
		}

		const clearancePath = layout.join(request.sourceRoot, CLEARANCE_FILENAME);
		if (!clearance.exists) {
			return failed(drift(`missing clearance file: ${clearancePath}`));
		}
		if (clearance.entries === null) {
			return failed(invalidClearance(clearancePath, clearance));
		}

		for (const [spec, declaredMode] of [
			...request.rawDeclarations.map((value) => [value, MODE_RAW] as const),
			...request.regionDeclarations.map((value) => [value, MODE_REGION] as const),
		]) {
			const parsed = parseInitBindingSpec(spec);
			if (parsed === null) {
				continue;
			}
			const actual = clearance.modes.get(parsed.source);
			if (actual !== undefined && actual !== declaredMode) {
				return failed(
					invalid(
						`declared ${declaredMode} for ${parsed.source} conflicts with source clearance mode '${actual}'`,
					),
				);
			}
		}
		for (const entry of effective.bindings) {
			const conflict = bindingModeConflict(entry, clearance.modes);
			if (conflict !== null) {
				return failed(conflict);
			}
		}
		// Two live bindings cannot own one destination, and a distributable binding
		// must not displace one awaiting reconciliation. Nothing is mutated first.
		const duplicated = duplicatedDestinations(effective);
		if (duplicated.length > 0) {
			return failed(invalid(`conflicting destination ownership: ${duplicated.join(", ")}`));
		}
		// Same refusal, at the same position, as `apply` and `check`: an already-bound
		// source whose record now declares another destination is drift, not a state
		// enrollment silently delivers. Nothing is written, because the changed
		// destination is the destination owner's migration.
		const relocated = destinationDrift(effective, clearance.entries, clearance.destinations);
		if (relocated !== null) {
			return failed(relocated);
		}

		const planned = await planChanges.execute({
			document: effective,
			request,
			clearance,
			distributable: determined.distributable,
			retired: determined.retired,
			newMergeDestinations: determined.newMergeDestinations,
		});
		if (!planned.ok) {
			return failed(planned.failure);
		}
		const plan = planned.plan;

		const pinned: BindingsDocument = {
			...effective,
			coreRevision: request.sourceRevision,
			pending: plan.pending,
			editor,
		};

		// The secret setup, the root blocker, the report and the complete mutation
		// set are prepared and validated before the first mutation.
		const preparation = await prepareExecution.execute({
			command: "init",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document: effective,
			pinned,
			pending: plan.pending,
			missingRegions: missingRegionSources(determined.requiresReconciliation),
			modes: clearance.modes,
			newRawDestinations,
			editor,
			plan,
			writesReconciliationReport: plan.reportEntries.length > 0,
		});
		if (!preparation.ok) {
			return failed(preparation.failure);
		}

		const notes = [...plan.notes];
		for (const write of plan.textWrites) {
			await layout.ensureDirectory(layout.parent(write.path));
			await destinations.writeText(write.path, write.content);
		}
		for (const write of plan.byteWrites) {
			await layout.ensureDirectory(layout.parent(write.path));
			await destinations.writeBytes(write.path, write.content);
		}
		for (const deletion of plan.deletions) {
			await destinations.remove(deletion.path);
			notes.push(`retired: ${deletion.destination}`);
		}
		await ensureOpenCodeSecrets(editor, request.destinationRoot, {
			destinations,
			layout,
		});

		if (plan.reportEntries.length > 0) {
			await bindings.writeReport(request.bindingsPath, plan.reportEntries, request.sourceRevision);
		}

		await bindings.save(request.bindingsPath, pinned);
		await layout.syncBlocker(
			request.destinationRoot,
			pinned,
			plan.pending,
			missingRegionSources(determined.requiresReconciliation),
		);

		return succeeded(["initialized", ...notes].join("; "));
	}
}
