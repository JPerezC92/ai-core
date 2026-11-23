/**
 * Application operation: plan what one update writes.
 *
 * The effective document has already been determined. For each distributable
 * binding this operation reads the source it needs, renders the destination it
 * owns, and records the write, creation, note or refusal the update command
 * earns. Every refusal preserves `apply`'s own precedence: a missing source,
 * a missing merge destination, malformed markers, and an outside-marker change
 * are reported before anything is written.
 *
 * The ordered payload effects are derived from those writes exactly once, so a
 * later projection reads the content this plan says the run leaves behind. The
 * updated `pending` is this command's own rule, and the pinned document is the
 * coordinator's to assemble from it.
 */

import { MODE_MERGE, MODE_RAW } from "#domain/synchronization/constants.ts";
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
import { protectedBytes, renderInitFile, renderWithRegion, splitRegions } from "#domain/synchronization/regions.ts";
import type { DestinationFiles, FilesystemLayout, PlannedPayload, SourceFiles } from "#domain/synchronization/ports.ts";

import type { ClearanceModes } from "./clearance-modes.ts";
import { projectName } from "./project-name.ts";
import type { SynchronizationRequest } from "./requests.ts";

/** One pending text write. */
export type PlannedTextWrite = {
	readonly path: string;
	readonly content: string;
};

/** One pending byte write. */
export type PlannedByteWrite = {
	readonly path: string;
	readonly content: Uint8Array;
};

/** What one update writes, and the state it leaves behind. */
export type UpdateChangePlan = {
	readonly textWrites: readonly PlannedTextWrite[];
	readonly byteWrites: readonly PlannedByteWrite[];
	/** The absolute paths whose managed files this run removes. */
	readonly deletions: readonly string[];
	/** The destinations this run creates, as relative paths. */
	readonly created: readonly string[];
	readonly notes: readonly string[];
	/** The document's outstanding paths after this command's own rule. */
	readonly pending: readonly string[];
	/** The pending effects, in the order the run applies them. */
	readonly payload: readonly PlannedPayload[];
};

/** What the update planner works from. */
export type UpdateChangeRequest = {
	readonly document: BindingsDocument;
	readonly request: SynchronizationRequest;
	readonly clearance: ClearanceModes;
	readonly distributable: readonly BindingEntry[];
	readonly retired: readonly AbsentSource[];
};

/** A command's plan, or the refusal it earns. */
export type UpdateChangeOutcome =
	| { readonly ok: true; readonly plan: UpdateChangePlan }
	| { readonly ok: false; readonly failure: SynchronizationFailure };

/** Collaborators the update planner needs. */
export type PlanUpdateChangesDependencies = {
	readonly sources: SourceFiles;
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
};

export class PlanUpdateChanges {
	readonly #dependencies: PlanUpdateChangesDependencies;

	constructor(dependencies: PlanUpdateChangesDependencies) {
		this.#dependencies = dependencies;
	}

	async execute(input: UpdateChangeRequest): Promise<UpdateChangeOutcome> {
		const { sources, destinations, layout } = this.#dependencies;
		const { document, request, clearance, distributable, retired } = input;

		const textWrites: PlannedTextWrite[] = [];
		const byteWrites: PlannedByteWrite[] = [];
		const created: string[] = [];
		const notes: string[] = [];

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
					if (!(await layout.isFile(destinationPath))) {
						if (await layout.exists(destinationPath)) {
							return { ok: false, failure: drift(`missing destination: ${destinationPath}`) };
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
					return { ok: false, failure: drift(`missing source: ${sourcePath}`) };
				}
				for (const destination of entry.destinations) {
					const destinationPath = layout.join(request.destinationRoot, destination);
					if (!(await layout.isFile(destinationPath))) {
						return {
							ok: false,
							failure: drift(
								`missing destination: ${destinationPath} ` +
									"(merge mode cannot create it; the destination must exist)",
							),
						};
					}
					const destinationText = await destinations.readText(destinationPath);
					if (destinationText === null) {
						return { ok: false, failure: drift(`missing destination: ${destinationPath}`) };
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
				if (!(await layout.isFile(destinationPath))) {
					if (await layout.exists(destinationPath)) {
						return { ok: false, failure: drift(`missing destination: ${destinationPath}`) };
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
					return { ok: false, failure: invalid(`invalid destination markers: ${destinationPath}`) };
				}
				const rendered = renderWithRegion(split, read.core, sourceFrontmatter);
				if (rendered.skipped !== "") {
					notes.push(`frontmatter not refreshed: ${destinationPath} (${rendered.skipped})`);
				}
				const newSplit = splitRegions(rendered.text);
				if (newSplit === null || protectedBytes(newSplit) !== protectedBytes(split)) {
					return { ok: false, failure: invalid(`outside-marker mismatch: ${destinationPath}`) };
				}
				textWrites.push({ path: destinationPath, content: rendered.text });
			}
		}

		const deletions: string[] = [];
		for (const entry of retired) {
			for (const destination of entry.destinations) {
				deletions.push(layout.join(request.destinationRoot, destination));
			}
		}

		// The pending effects, in the order the run applies them: the content a
		// later projection reads is the content the earlier write leaves behind.
		const payload: PlannedPayload[] = [
			...textWrites.map((write) => ({ kind: "text-write" as const, path: write.path, content: write.content })),
			...byteWrites.map((write) => ({ kind: "byte-write" as const, path: write.path, content: write.content })),
			...deletions.map((path) => ({ kind: "file-delete" as const, path })),
		];

		return {
			ok: true,
			plan: {
				textWrites,
				byteWrites,
				deletions,
				created,
				notes,
				pending: normalizePending(document.pending, nonRegionDestinations(document, clearance.modes)),
				payload,
			},
		};
	}
}
