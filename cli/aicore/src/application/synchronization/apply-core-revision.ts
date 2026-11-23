/**
 * Use case: splice each source core into its destinations and pin the revision.
 *
 * A region destination's core region is replaced and its frontmatter identity
 * keys are refreshed from the source; an unrefreshable frontmatter keeps its
 * text and is named in the result message. A declared but absent region or raw
 * target is recreated, because a declaration must not depend on when it was
 * recorded. A merge destination is never created here: only a first enrollment
 * creates one.
 *
 * Writes happen only after every destination has been classified, so a later
 * refusal cannot leave a directory or a half-applied payload behind.
 *
 * The run reads and writes through two preflights. The read preflight clears
 * every path whose contents the run reads; the mutation preflight clears the
 * complete set of writes the run performs, including the ones it only
 * performs when their content changes.
 */

import { CLEARANCE_FILENAME, MODE_MERGE, MODE_RAW, ROLE_ROOT } from "#domain/synchronization/constants.ts";
import {
	bindingModeConflict,
	destinationDrift,
	duplicatedDestinations,
	enrollmentCandidates,
	nonRegionDestinations,
	normalizePending,
	protectedExclusionFailure,
	withEnrolledSources,
	withOptOuts,
	withRestoredOptOuts,
	withheldSources,
} from "#domain/synchronization/bindings.ts";
import { drift, failed, invalid, succeeded, type OperationOutcome } from "#domain/synchronization/failures.ts";
import { splitFrontmatter } from "#domain/synchronization/frontmatter.ts";
import { omitMcpServersOf } from "#domain/synchronization/clearance.ts";
import { mergeTopLevel } from "#domain/synchronization/merge.ts";
import { editorMismatch, effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import { protectedBytes, renderInitFile, renderWithRegion, splitRegions } from "#domain/synchronization/regions.ts";
import { missingRegionSources } from "#domain/synchronization/reconciliation.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
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
import type { SynchronizationRequest } from "./requests.ts";

/** Collaborators the update needs. */
export type ApplyCoreRevisionDependencies = {
	readonly bindings: BindingsStore;
	readonly clearance: ClearanceStore;
	readonly sources: SourceFiles;
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
	readonly guard: WriteTargetGuard;
};

/** One pending text write. */
type TextWrite = {
	readonly path: string;
	readonly content: string;
};

/** One pending byte write. */
type ByteWrite = {
	readonly path: string;
	readonly content: Uint8Array;
};

export class ApplyCoreRevision {
	readonly #dependencies: ApplyCoreRevisionDependencies;

	constructor(dependencies: ApplyCoreRevisionDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(request: SynchronizationRequest): Promise<OperationOutcome> {
		const { bindings, clearance: clearanceStore, sources, destinations, layout, guard } = this.#dependencies;

		const document = await bindings.load(request.bindingsPath);
		if (document === null) {
			return failed(invalid(`invalid bindings: ${request.bindingsPath}`));
		}

		const mismatch = editorMismatch(document.editor, request.editor);
		if (mismatch !== null) {
			return failed(mismatch);
		}
		const editor = effectiveEditor(request.editor, document.editor);

		const protectedExclusion = protectedExclusionFailure(document);
		if (protectedExclusion !== null) {
			return failed(protectedExclusion);
		}

		const clearance = await readClearanceModes(clearanceStore, layout, request.sourceRoot, editor);

		// A source this destination opted out of is unmanaged: no binding, no write
		// and no drift. The refusal below therefore never names it as uncleared, and
		// the write-target preflight never observes its old destination as a target.
		const managed = withOptOuts(document);
		// An opt-out its owner revoked — the entry is gone and the source is cleared
		// for this run — is delivered again, and its outstanding path leaves
		// `pending`.
		const current = withRestoredOptOuts(managed, clearance.modes, clearance.destinations);

		const clearancePath = layout.join(request.sourceRoot, CLEARANCE_FILENAME);
		if (!clearance.exists) {
			return failed(drift(`missing clearance file: ${clearancePath}`));
		}
		if (clearance.entries === null) {
			return failed(invalidClearance(clearancePath, clearance));
		}
		// The domain decides which cleared sources gain bindings and which destinations
		// are new; this operation only probes the facts it needs.
		const rootEntry = [...clearance.entries.entries()].find(
			([, entry]) => entry.kind === "file" && entry.role === ROLE_ROOT,
		);
		const rootSource = rootEntry?.[0] ?? null;
		let rootDestination = current.root;
		if (rootSource !== null) {
			const existingRoot = current.bindings.find((entry) => entry.source === rootSource);
			rootDestination = existingRoot?.destinations[0] ?? (await layout.detectRootFile(request.destinationRoot));
			if (rootDestination === null) {
				return failed(drift("destination instruction root not found; pass --root"));
			}
		}
		const enrollment = enrollmentCandidates(current, {
			modes: clearance.modes,
			destinations: clearance.destinations,
			rootSource,
			rootDestination,
		});
		const existingDestinations = new Set<string>();
		for (const candidate of enrollment.candidates) {
			if (await layout.exists(layout.join(request.destinationRoot, candidate.destination))) {
				existingDestinations.add(candidate.destination);
			}
		}
		const enrolled = withEnrolledSources(current, enrollment, existingDestinations);
		// Presence is probed on the document that is classified, so a source this run
		// enrolled is asked about too: it came from a real enumeration, and the
		// classification must see that it exists.
		const facts = await sourceFacts(enrolled.document, clearance, editor, request.sourceRoot, layout);
		const withheld = withheldSources(enrolled.document, facts, clearance.entries);
		const plan = withheld.document;

		// Every path this run reads is cleared before it is read: the effective
		// document the run acts on is guarded before any payload read.
		const readRefusal = await guard.refuse({
			command: "apply",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document: plan,
			modes: clearance.modes,
			newRawDestinations: enrolled.newRawDestinations,
			phase: "read",
			readPaths: await destinationReadPaths(plan, request.destinationRoot, layout),
		});
		if (readRefusal !== null) {
			return failed(readRefusal);
		}

		for (const entry of plan.bindings) {
			const conflict = bindingModeConflict(entry, clearance.modes);
			if (conflict !== null) {
				return failed(conflict);
			}
		}
		// Two live bindings cannot own one destination, and a distributable binding
		// must not displace one awaiting reconciliation. Nothing is mutated first.
		const duplicated = duplicatedDestinations(plan);
		if (duplicated.length > 0) {
			return failed(invalid(`conflicting destination ownership: ${duplicated.join(", ")}`));
		}
		const relocated = destinationDrift(plan, clearance.entries, clearance.destinations);
		if (relocated !== null) {
			return failed(relocated);
		}

		const textWrites: TextWrite[] = [];
		const byteWrites: ByteWrite[] = [];
		const created: string[] = [];
		const notes: string[] = [];

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
					if (!(await layout.isFile(destinationPath))) {
						if (await layout.exists(destinationPath)) {
							return failed(drift(`missing destination: ${destinationPath}`));
						}
						created.push(destination);
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
					if (!(await layout.isFile(destinationPath))) {
						return failed(
							drift(
								`missing destination: ${destinationPath} ` +
									"(merge mode cannot create it; the destination must exist)",
							),
						);
					}
					const destinationText = await destinations.readText(destinationPath);
					if (destinationText === null) {
						return failed(drift(`missing destination: ${destinationPath}`));
					}
					const mergedText = mergeTopLevel(
						sourceText,
						destinationText,
						projectName(request.destinationRoot),
						omitMcpServersOf(clearance.entries?.get(entry.source)),
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
				if (!(await layout.isFile(destinationPath))) {
					if (await layout.exists(destinationPath)) {
						return failed(drift(`missing destination: ${destinationPath}`));
					}
					textWrites.push({
						path: destinationPath,
						content: renderInitFile("", read.core, sourceFrontmatter).text,
					});
					created.push(destination);
					continue;
				}
				const destinationContent = await destinations.readText(destinationPath);
				const split = destinationContent === null ? null : splitRegions(destinationContent);
				if (split === null) {
					return failed(invalid(`invalid destination markers: ${destinationPath}`));
				}
				const rendered = renderWithRegion(split, read.core, sourceFrontmatter);
				if (rendered.skipped !== "") {
					notes.push(`frontmatter not refreshed: ${destinationPath} (${rendered.skipped})`);
				}
				const newSplit = splitRegions(rendered.text);
				if (newSplit === null || protectedBytes(newSplit) !== protectedBytes(split)) {
					return failed(invalid(`outside-marker mismatch: ${destinationPath}`));
				}
				textWrites.push({ path: destinationPath, content: rendered.text });
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

		const pending = normalizePending(plan.pending, nonRegionDestinations(plan, clearance.modes));
		const pinned = { ...plan, coreRevision: request.sourceRevision, pending };

		// The secret setup reads the ignore file only when it has to plan its
		// rule, so that read is cleared on its own.
		const preparation = await prepareOpenCodeSecrets(editor, request.destinationRoot, payload, layout);
		if (preparation.readsIgnore) {
			const ignoreRefusal = await guard.refuse({
				command: "apply",
				sourceRoot: request.sourceRoot,
				destinationRoot: request.destinationRoot,
				bindingsPath: request.bindingsPath,
				document: plan,
				modes: clearance.modes,
				newRawDestinations: enrolled.newRawDestinations,
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
			...(blocker === null ? [] : [{ path: blocker.path, kind: "file-write" as const, owner: "root" as const }]),
			...secretMutations,
		];
		const mutationRefusal = await guard.refuse({
			command: "apply",
			sourceRoot: request.sourceRoot,
			destinationRoot: request.destinationRoot,
			bindingsPath: request.bindingsPath,
			document: plan,
			modes: clearance.modes,
			newRawDestinations: enrolled.newRawDestinations,
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
		// A retired source owns no destination content, so its managed copy is
		// removed: nothing of the destination's own could be in it.
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

		await bindings.save(request.bindingsPath, pinned);
		await layout.syncBlocker(
			request.destinationRoot,
			pinned,
			pending,
			missingRegionSources(withheld.requiresReconciliation),
		);

		const parts = ["applied", ...notes];
		if (created.length > 0) {
			parts.push(`created: ${created.join(", ")}`);
		}
		return succeeded(parts.join("; "));
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
