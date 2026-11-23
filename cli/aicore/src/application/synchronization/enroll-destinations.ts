/**
 * Use case: enroll markerless destinations and refresh already-marked ones.
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

import {
	ACTION_INITIALIZED,
	ACTION_REFRESHED,
	CLEARANCE_FILENAME,
	MODE_MERGE,
	MODE_RAW,
	MODE_REGION,
	RECONCILIATION_DIRECTORY,
	RECONCILIATION_FILENAME,
	ROLE_ROOT,
} from "#domain/synchronization/constants.ts";
import {
	bindingModeConflict,
	destinationDrift,
	type EnrollmentPlan,
	duplicatedDestinations,
	enrollmentCandidates,
	nonRegionDestinations,
	normalizePending,
	parseInitBindingSpec,
	protectedExclusionFailure,
	withEnrolledSources,
	withInitDeclarations,
	withOptOuts,
	withRestoredOptOuts,
	withheldSources,
} from "#domain/synchronization/bindings.ts";
import { drift, failed, invalid, succeeded, type OperationOutcome } from "#domain/synchronization/failures.ts";
import { splitFrontmatter } from "#domain/synchronization/frontmatter.ts";
import { mergeTopLevel } from "#domain/synchronization/merge.ts";
import { hasExactCoreMarkerLines } from "#domain/synchronization/markers.ts";
import type { ReconciliationEntry } from "#domain/synchronization/reconciliation.ts";
import { missingRegionSources } from "#domain/synchronization/reconciliation.ts";
import { protectedBytes, renderInitFile, renderWithRegion, splitRegions } from "#domain/synchronization/regions.ts";
import { editorMismatch, effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import { omitMcpServersOf, type ClearanceEntry } from "#domain/synchronization/clearance.ts";
import type {
	BindingsStore,
	ClearanceStore,
	DestinationFiles,
	FilesystemLayout,
	PlannedMutation,
	PlannedPayload,
	PlannedRead,
	SourceFiles,
	WriteTargetGuard,
} from "#domain/synchronization/ports.ts";

import { invalidClearance, readClearanceModes, sourceFacts } from "./clearance-modes.ts";
import { ensureOpenCodeSecrets, planOpenCodeSecretWrites, prepareOpenCodeSecrets } from "./open-code-secrets.ts";
import { projectName } from "./project-name.ts";
import type { EnrollmentRequest } from "./requests.ts";

/** Collaborators enrollment needs. */
export type EnrollDestinationsDependencies = {
	readonly bindings: BindingsStore;
	readonly clearance: ClearanceStore;
	readonly sources: SourceFiles;
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
	readonly guard: WriteTargetGuard;
};

type TextWrite = { readonly path: string; readonly content: string };
type ByteWrite = { readonly path: string; readonly content: Uint8Array };

export class EnrollDestinations {
	readonly #dependencies: EnrollDestinationsDependencies;

	constructor(dependencies: EnrollDestinationsDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(request: EnrollmentRequest): Promise<OperationOutcome> {
		const { bindings, clearance: clearanceStore, sources, destinations, layout, guard } = this.#dependencies;

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

		// The domain decides which cleared sources gain bindings and which destinations
		// are new; this operation only probes the facts it needs.
		const entries = clearance.entries ?? new Map<string, ClearanceEntry>();
		const rootEntry = [...entries.entries()].find(([, entry]) => entry.kind === "file" && entry.role === ROLE_ROOT);
		const rootSource = rootEntry?.[0] ?? null;
		let rootDestination = restored.root;
		if (rootSource !== null) {
			const existingRoot = restored.bindings.find((entry) => entry.source === rootSource);
			rootDestination =
				existingRoot?.destinations[0] ??
				request.rootOverride ??
				(await layout.detectRootFile(request.destinationRoot));
			if (rootDestination === null) {
				return failed(drift("destination instruction root not found; pass --root"));
			}
		}
		const enrollment: EnrollmentPlan = request.bindCleared
			? enrollmentCandidates(restored, {
					modes: clearance.modes,
					destinations: clearance.destinations,
					rootSource,
					rootDestination,
				})
			: { root: restored.root, candidates: [] };
		const existingDestinations = new Set<string>();
		for (const candidate of enrollment.candidates) {
			if (await layout.exists(layout.join(request.destinationRoot, candidate.destination))) {
				existingDestinations.add(candidate.destination);
			}
		}
		const enrolled = withEnrolledSources(restored, enrollment, existingDestinations);
		// Presence is probed on the document that is classified, so a source this run
		// enrolled is asked about too: it came from a real enumeration, and the
		// classification must see that it exists.
		const facts = await sourceFacts(enrolled.document, clearance, editor, request.sourceRoot, layout);
		const withheld = withheldSources(enrolled.document, facts, entries);
		const document = withheld.document;
		const newRawDestinations = new Set<string>([...declared.newRawDestinations, ...enrolled.newRawDestinations]);
		const newMergeDestinations = enrolled.newMergeDestinations;

		// Every path this run reads is cleared before it is read: the effective
		// document the run acts on is guarded before any payload read.
		const readRefusal = await guard.refuse({
			command: "init",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document,
			modes: clearance.modes,
			newRawDestinations,
			phase: "read",
			readPaths: await destinationReadPaths(document, request.destinationRoot, layout),
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
		for (const entry of document.bindings) {
			const conflict = bindingModeConflict(entry, clearance.modes);
			if (conflict !== null) {
				return failed(conflict);
			}
		}
		// Two live bindings cannot own one destination, and a distributable binding
		// must not displace one awaiting reconciliation. Nothing is mutated first.
		const duplicated = duplicatedDestinations(document);
		if (duplicated.length > 0) {
			return failed(invalid(`conflicting destination ownership: ${duplicated.join(", ")}`));
		}
		// Same refusal, at the same position, as `apply` and `check`: an already-bound
		// source whose record now declares another destination is drift, not a state
		// enrollment silently delivers. Nothing is written, because the changed
		// destination is the destination owner's migration.
		const relocated = destinationDrift(document, clearance.entries, clearance.destinations);
		if (relocated !== null) {
			return failed(relocated);
		}

		const textWrites: TextWrite[] = [];
		const byteWrites: ByteWrite[] = [];
		const reportEntries: ReconciliationEntry[] = [];
		const notes: string[] = [];
		let pending: readonly string[] = normalizePending(
			document.pending,
			nonRegionDestinations(document, clearance.modes),
		);
		for (const entry of withheld.distributable) {
			const mode = clearance.modes.get(entry.source);
			const sourcePath = layout.join(request.sourceRoot, entry.source);

			if (mode === MODE_RAW) {
				const sourceBytes = await sources.readBytes(sourcePath);
				if (sourceBytes === null) {
					return failed(drift(`missing source: ${sourcePath}`));
				}
				for (const destination of entry.destinations) {
					const destinationPath = layout.join(request.destinationRoot, destination);
					const destinationBytes = await destinations.readBytes(destinationPath);
					if (destinationBytes === null) {
						if (await layout.exists(destinationPath)) {
							return failed(drift(`missing destination: ${destinationPath}`));
						}
						byteWrites.push({ path: destinationPath, content: sourceBytes });
						continue;
					}
					if (equalBytes(destinationBytes, sourceBytes)) {
						continue;
					}
					byteWrites.push({ path: destinationPath, content: sourceBytes });
				}
				continue;
			}

			if (mode === MODE_MERGE) {
				const sourceText = await sources.readText(sourcePath);
				if (sourceText === null) {
					return failed(drift(`missing source: ${sourcePath}`));
				}
				for (const destination of entry.destinations) {
					const destinationPath = layout.join(request.destinationRoot, destination);
					const destinationText = await destinations.readText(destinationPath);
					if (destinationText === null) {
						if (!newMergeDestinations.has(destination) || (await layout.exists(destinationPath))) {
							return failed(
								drift(
									`missing destination: ${destinationPath} ` +
										"(merge mode cannot create it; the destination must exist)",
								),
							);
						}
						const created = mergeTopLevel(
							sourceText,
							"{}",
							projectName(request.destinationRoot),
							omitMcpServersOf(clearance.entries.get(entry.source)),
						);
						if (created === null) {
							return failed(invalid(`invalid JSONC: ${sourcePath}`));
						}
						textWrites.push({ path: destinationPath, content: created });
						continue;
					}
					const mergedText = mergeTopLevel(
						sourceText,
						destinationText,
						projectName(request.destinationRoot),
						omitMcpServersOf(clearance.entries.get(entry.source)),
					);
					if (mergedText === null) {
						return failed(invalid(`invalid JSONC: ${destinationPath}`));
					}
					if (mergedText !== destinationText) {
						textWrites.push({ path: destinationPath, content: mergedText });
					}
				}
				continue;
			}

			const read = await sources.readCore(sourcePath);
			if (read === null) {
				return failed(drift(`missing source: ${sourcePath}`));
			}
			if (read.kind === "malformed") {
				return failed(invalid(`invalid source markers: ${sourcePath}`));
			}
			const sourceText = await sources.readText(sourcePath);
			const sourceFrontmatter = sourceText === null ? "" : splitFrontmatter(sourceText).frontmatter;

			for (const destination of entry.destinations) {
				const destinationPath = layout.join(request.destinationRoot, destination);
				const destinationContent = await destinations.readText(destinationPath);
				if (destinationContent === null) {
					if (await layout.exists(destinationPath)) {
						return failed(drift(`missing destination: ${destinationPath}`));
					}
					textWrites.push({
						path: destinationPath,
						content: renderInitFile("", read.core, sourceFrontmatter).text,
					});
					reportEntries.push({ destination, source: entry.source, action: ACTION_INITIALIZED });
					pending = appendOnce(pending, destination);
					continue;
				}
				const split = splitRegions(destinationContent);
				if (split === null) {
					if (hasExactCoreMarkerLines(destinationContent)) {
						return failed(invalid(`invalid destination markers: ${destinationPath}`));
					}
					const rendered = renderInitFile(destinationContent, read.core, sourceFrontmatter);
					if (rendered.skipped !== "") {
						notes.push(`frontmatter not refreshed: ${destinationPath} (${rendered.skipped})`);
					}
					textWrites.push({ path: destinationPath, content: rendered.text });
					reportEntries.push({ destination, source: entry.source, action: ACTION_INITIALIZED });
					pending = appendOnce(pending, destination);
					continue;
				}
				const rendered = renderWithRegion(split, read.core, sourceFrontmatter);
				if (rendered.skipped !== "") {
					notes.push(`frontmatter not refreshed: ${destinationPath} (${rendered.skipped})`);
				}
				const newSplit = splitRegions(rendered.text);
				if (newSplit === null || protectedBytes(newSplit) !== protectedBytes(split)) {
					return failed(invalid(`outside-marker mismatch: ${destinationPath}`));
				}
				if (rendered.text === destinationContent) {
					continue;
				}
				textWrites.push({ path: destinationPath, content: rendered.text });
				if (newSplit.region === split.region) {
					continue;
				}
				reportEntries.push({ destination, source: entry.source, action: ACTION_REFRESHED });
				pending = appendOnce(pending, destination);
			}
		}

		// The pending effects, in the order the run applies them: the content a
		// later projection reads is the content the earlier write leaves behind.
		const payload: PlannedPayload[] = [
			...textWrites.map((write) => ({ kind: "text-write" as const, path: write.path, content: write.content })),
			...byteWrites.map((write) => ({ kind: "byte-write" as const, path: write.path, content: write.content })),
		];
		const retiredPaths: string[] = [];
		for (const retired of withheld.retired) {
			for (const destination of retired.destinations) {
				retiredPaths.push(layout.join(request.destinationRoot, destination));
			}
		}
		payload.push(...retiredPaths.map((path) => ({ kind: "file-delete" as const, path })));

		const pinned: BindingsDocument = {
			...document,
			coreRevision: request.sourceRevision,
			pending,
			editor,
		};

		// The secret setup reads the ignore file only when it has to plan its
		// rule, so that read is cleared on its own.
		const preparation = await prepareOpenCodeSecrets(editor, request.destinationRoot, payload, layout);
		if (preparation.readsIgnore) {
			const ignoreRefusal = await guard.refuse({
				command: "init",
				sourceRoot: request.sourceRoot,
				destinationRoot: request.destinationRoot,
				bindingsPath: request.bindingsPath,
				document,
				modes: clearance.modes,
				newRawDestinations,
				phase: "read",
				readPaths: [{ path: preparation.paths.gitignore, owner: "secret" }],
			});
			if (ignoreRefusal !== null) {
				return failed(ignoreRefusal);
			}
		}
		const secretMutations = await planOpenCodeSecretWrites(editor, preparation, payload, {
			destinations,
			layout,
		});

		// The root runtime file's blocker is a write of its own, and the
		// projection says whether this run performs one.
		const blocker =
			(await layout.planBlocker(
				request.destinationRoot,
				pinned,
				pending,
				missingRegionSources(withheld.requiresReconciliation),
				payload,
			)) ?? null;

		const mutations: PlannedMutation[] = [
			...textWrites.map((write) => ({
				path: write.path,
				kind: "file-write" as const,
				owner: "payload" as const,
			})),
			...byteWrites.map((write) => ({
				path: write.path,
				kind: "file-write" as const,
				owner: "payload" as const,
			})),
			...retiredPaths.map((path) => ({ path, kind: "file-delete" as const, owner: "payload" as const })),
			{ path: request.bindingsPath, kind: "file-write", owner: "bindings" },
			...(reportEntries.length > 0
				? [
						{
							path: layout.join(
								layout.parent(request.bindingsPath),
								`${RECONCILIATION_DIRECTORY}/${RECONCILIATION_FILENAME}`,
							),
							kind: "file-write" as const,
							owner: "report" as const,
						},
					]
				: []),
			...(blocker === null ? [] : [{ path: blocker.path, kind: "file-write" as const, owner: "root" as const }]),
			...secretMutations,
		];
		const mutationRefusal = await guard.refuse({
			command: "init",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document,
			modes: clearance.modes,
			newRawDestinations,
			phase: "mutations",
			mutations,
		});
		if (mutationRefusal !== null) {
			return failed(mutationRefusal);
		}

		for (const write of textWrites) {
			await layout.ensureDirectory(layout.parent(write.path));
			await destinations.writeText(write.path, write.content);
		}
		for (const write of byteWrites) {
			await layout.ensureDirectory(layout.parent(write.path));
			await destinations.writeBytes(write.path, write.content);
		}
		for (const retired of withheld.retired) {
			for (const destination of retired.destinations) {
				await destinations.remove(layout.join(request.destinationRoot, destination));
				notes.push(`retired: ${destination}`);
			}
		}
		await ensureOpenCodeSecrets(editor, request.destinationRoot, {
			destinations,
			layout,
		});

		if (reportEntries.length > 0) {
			await bindings.writeReport(request.bindingsPath, reportEntries, request.sourceRevision);
		}

		await bindings.save(request.bindingsPath, pinned);
		await layout.syncBlocker(
			request.destinationRoot,
			pinned,
			pending,
			missingRegionSources(withheld.requiresReconciliation),
		);

		return succeeded(["initialized", ...notes].join("; "));
	}
}

/**
 * The destination paths whose contents this run reads before it writes.
 *
 * Every bound destination is cleared, whatever its mode and whatever it is on
 * disk: a destination that is a directory is an unsafe write target, not a
 * missing file, and the read preflight is where that class is refused. Each
 * read carries the owner of the path it reads.
 */
async function destinationReadPaths(
	document: BindingsDocument,
	destinationRoot: string,
	layout: FilesystemLayout,
): Promise<readonly PlannedRead[]> {
	const paths: PlannedRead[] = [];
	for (const entry of document.bindings) {
		for (const destination of entry.destinations) {
			paths.push({ path: layout.join(destinationRoot, destination), owner: "payload" });
		}
	}
	return paths;
}

function appendOnce(pending: readonly string[], path: string): readonly string[] {
	return pending.includes(path) ? pending : [...pending, path];
}

function equalBytes(left: Uint8Array, right: Uint8Array): boolean {
	if (left.length !== right.length) {
		return false;
	}
	return left.every((byte, index) => byte === right[index]);
}
