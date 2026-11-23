/**
 * Application operation: plan what one enrollment writes.
 *
 * The effective document has already been determined. Enrollment is the only
 * command that creates a merge target, and only when this run newly bound it and
 * the path is absent. A markerless region destination is initialized from the
 * source and keeps its prior body in a project region, which records the
 * reconciliation report entry and the outstanding path. A raw destination that
 * already holds the source's bytes is not written again, and an unchanged region
 * destination is not refreshed.
 *
 * Every refusal preserves `init`'s own precedence: a missing source, a missing
 * destination that this run did not bind, malformed markers, and an
 * outside-marker change are reported before anything is written. The ordered
 * payload effects are derived from those writes exactly once.
 */

import { ACTION_INITIALIZED, ACTION_REFRESHED, MODE_MERGE, MODE_RAW } from "#domain/synchronization/constants.ts";
import {
	type AbsentSource,
	type BindingEntry,
	type BindingsDocument,
	nonRegionDestinations,
	normalizePending,
} from "#domain/synchronization/bindings.ts";
import { drift, invalid, type SynchronizationFailure } from "#domain/synchronization/failures.ts";
import { splitFrontmatter } from "#domain/synchronization/frontmatter.ts";
import { omitMcpServersOf } from "#domain/synchronization/clearance.ts";
import { mergeTopLevel } from "#domain/synchronization/merge.ts";
import { hasExactCoreMarkerLines } from "#domain/synchronization/markers.ts";
import { type ReconciliationEntry } from "#domain/synchronization/reconciliation.ts";
import { protectedBytes, renderInitFile, renderWithRegion, splitRegions } from "#domain/synchronization/regions.ts";
import type { DestinationFiles, FilesystemLayout, PlannedPayload, SourceFiles } from "#domain/synchronization/ports.ts";

import type { ClearanceModes } from "./clearance-modes.ts";
import { projectName } from "./project-name.ts";
import type { SynchronizationRequest } from "./requests.ts";

/** One managed deletion: its absolute path, and the destination it was bound to. */
type PlannedDeletion = {
	readonly path: string;
	readonly destination: string;
};

/** What one enrollment writes, and the state it leaves behind. */
export type EnrollmentChangePlan = {
	readonly textWrites: readonly { readonly path: string; readonly content: string }[];
	readonly byteWrites: readonly { readonly path: string; readonly content: Uint8Array }[];
	/** The managed deletions this run performs. */
	readonly deletions: readonly PlannedDeletion[];
	/** The reconciliation report entries this run records. */
	readonly reportEntries: readonly ReconciliationEntry[];
	readonly notes: readonly string[];
	/** The document's outstanding paths after this command's own rule. */
	readonly pending: readonly string[];
	/** The pending effects, in the order the run applies them. */
	readonly payload: readonly PlannedPayload[];
};

/** What the enrollment planner works from. */
export type EnrollmentChangeRequest = {
	readonly document: BindingsDocument;
	readonly request: SynchronizationRequest;
	readonly clearance: ClearanceModes;
	readonly distributable: readonly BindingEntry[];
	readonly retired: readonly AbsentSource[];
	/** Merge destinations this run newly bound; only those may be created. */
	readonly newMergeDestinations: ReadonlySet<string>;
};

/** A command's plan, or the refusal it earns. */
export type EnrollmentChangeOutcome =
	| { readonly ok: true; readonly plan: EnrollmentChangePlan }
	| { readonly ok: false; readonly failure: SynchronizationFailure };

/** Collaborators the enrollment planner needs. */
export type PlanEnrollmentChangesDependencies = {
	readonly sources: SourceFiles;
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
};

export class PlanEnrollmentChanges {
	readonly #dependencies: PlanEnrollmentChangesDependencies;

	constructor(dependencies: PlanEnrollmentChangesDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(input: EnrollmentChangeRequest): Promise<EnrollmentChangeOutcome> {
		const { sources, destinations, layout } = this.#dependencies;
		const { document, request, clearance, distributable, retired, newMergeDestinations } = input;

		const textWrites: { path: string; content: string }[] = [];
		const byteWrites: { path: string; content: Uint8Array }[] = [];
		const reportEntries: ReconciliationEntry[] = [];
		const notes: string[] = [];
		let pending = normalizePending(document.pending, nonRegionDestinations(document, clearance.modes));

		for (const entry of distributable) {
			const mode = clearance.modes.get(entry.source);
			const sourcePath = layout.join(request.sourceRoot, entry.source);

			if (mode === MODE_RAW) {
				const sourceBytes = await sources.readBytes(sourcePath);
				if (sourceBytes === null) {
					return { ok: false, failure: drift(`missing source: ${sourcePath}`) };
				}
				for (const destination of entry.destinations) {
					const destinationPath = layout.join(request.destinationRoot, destination);
					const destinationBytes = await destinations.readBytes(destinationPath);
					if (destinationBytes === null) {
						if (await layout.exists(destinationPath)) {
							return { ok: false, failure: drift(`missing destination: ${destinationPath}`) };
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
					return { ok: false, failure: drift(`missing source: ${sourcePath}`) };
				}
				for (const destination of entry.destinations) {
					const destinationPath = layout.join(request.destinationRoot, destination);
					const destinationText = await destinations.readText(destinationPath);
					if (destinationText === null) {
						if (!newMergeDestinations.has(destination) || (await layout.exists(destinationPath))) {
							return {
								ok: false,
								failure: drift(
									`missing destination: ${destinationPath} ` +
										"(merge mode cannot create it; the destination must exist)",
								),
							};
						}
						const created = mergeTopLevel(
							sourceText,
							"{}",
							projectName(request.destinationRoot),
							omitMcpServersOf(clearance.entries?.get(entry.source)),
						);
						if (created === null) {
							return { ok: false, failure: invalid(`invalid JSONC: ${sourcePath}`) };
						}
						textWrites.push({ path: destinationPath, content: created });
						continue;
					}
					const mergedText = mergeTopLevel(
						sourceText,
						destinationText,
						projectName(request.destinationRoot),
						omitMcpServersOf(clearance.entries?.get(entry.source)),
					);
					if (mergedText === null) {
						return { ok: false, failure: invalid(`invalid JSONC: ${destinationPath}`) };
					}
					if (mergedText !== destinationText) {
						textWrites.push({ path: destinationPath, content: mergedText });
					}
				}
				continue;
			}

			const read = await sources.readCore(sourcePath);
			if (read === null) {
				return { ok: false, failure: drift(`missing source: ${sourcePath}`) };
			}
			if (read.kind === "malformed") {
				return { ok: false, failure: invalid(`invalid source markers: ${sourcePath}`) };
			}
			const sourceText = await sources.readText(sourcePath);
			const sourceFrontmatter = sourceText === null ? "" : splitFrontmatter(sourceText).frontmatter;

			for (const destination of entry.destinations) {
				const destinationPath = layout.join(request.destinationRoot, destination);
				const destinationContent = await destinations.readText(destinationPath);
				if (destinationContent === null) {
					if (await layout.exists(destinationPath)) {
						return { ok: false, failure: drift(`missing destination: ${destinationPath}`) };
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
						return { ok: false, failure: invalid(`invalid destination markers: ${destinationPath}`) };
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
					return { ok: false, failure: invalid(`outside-marker mismatch: ${destinationPath}`) };
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

		const deletions: PlannedDeletion[] = [];
		for (const entry of retired) {
			for (const destination of entry.destinations) {
				deletions.push({ path: layout.join(request.destinationRoot, destination), destination });
			}
		}

		// The pending effects, in the order the run applies them: the content a
		// later projection reads is the content the earlier write leaves behind.
		const payload: PlannedPayload[] = [
			...textWrites.map((write) => ({ kind: "text-write" as const, path: write.path, content: write.content })),
			...byteWrites.map((write) => ({ kind: "byte-write" as const, path: write.path, content: write.content })),
			...deletions.map((deletion) => ({ kind: "file-delete" as const, path: deletion.path })),
		];

		return {
			ok: true,
			plan: { textWrites, byteWrites, deletions, reportEntries, notes, pending, payload },
		};
	}
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
