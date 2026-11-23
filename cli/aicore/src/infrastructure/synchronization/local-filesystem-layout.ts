/**
 * Infrastructure: path and layout questions about the two roots.
 *
 * Path composition, the root runtime file's resolution, directory enumeration
 * and the blocker write live here; what the blocker says and how a file is
 * spliced stay in the domain.
 */

import { readdir, stat } from "node:fs/promises";
import { dirname, join, relative, sep } from "node:path";

import { ROOT_CANDIDATES } from "#domain/synchronization/constants.ts";
import { excludedFromDistribution } from "#domain/synchronization/clearance.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import { effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import { syncReconciliationBlocker, type MissingRegionSource } from "#domain/synchronization/reconciliation.ts";
import type { FilesystemLayout, PlannedPayload } from "#domain/synchronization/ports.ts";
import { projectedPayloadText } from "#domain/synchronization/write-targets.ts";

import { ensureDirectory, isMissing, readEntryKind, readTextFile, writeTextFile } from "./local-files.ts";

/** A path's kind, as the preflight and the readers need to know it. */
type PathKind = "absent" | "file" | "other";

export class LocalFilesystemLayout implements FilesystemLayout {
	async exists(path: string): Promise<boolean> {
		return (await readKind(path)) !== "absent";
	}

	async isFile(path: string): Promise<boolean> {
		return (await readKind(path)) === "file";
	}

	async ensureDirectory(path: string): Promise<void> {
		await ensureDirectory(path);
	}

	join(root: string, relativePath: string): string {
		return relativePath === "" ? root : join(root, relativePath);
	}

	parent(path: string): string {
		return dirname(path);
	}

	/**
	 * Every regular file under `root` that a distribution set may contain.
	 *
	 * Each entry is classified by its own `lstat`, so a symbolic link or a
	 * directory junction is never followed and never reported. The walk descends
	 * only into true directories and reports only true regular files, and both
	 * decisions use the domain's `excludedFromDistribution` predicate, so the
	 * exclusion rule has one home.
	 */
	async enumerateFilesUnder(root: string): Promise<readonly string[]> {
		const collected: string[] = [];
		if (!(await this.exists(root))) {
			return collected;
		}
		const walk = async (current: string): Promise<void> => {
			for (const name of await readdir(current)) {
				const absolute = join(current, name);
				const kind = await readEntryKind(absolute);
				if (kind === "directory") {
					if (excludedFromDistribution(name)) {
						continue;
					}
					await walk(absolute);
					continue;
				}
				if (kind !== "file") {
					continue;
				}
				const relativePath = relative(root, absolute).split(sep).join("/");
				if (excludedFromDistribution(relativePath)) {
					continue;
				}
				collected.push(relativePath);
			}
		};
		await walk(root);
		return collected.sort();
	}

	async resolveRootFile(destinationRoot: string, document: BindingsDocument): Promise<string> {
		if (document.root !== null) {
			return join(destinationRoot, document.root);
		}
		const detected = await this.detectRootFile(destinationRoot);
		if (detected !== null) {
			return join(destinationRoot, detected);
		}
		// No instruction root was detected, so the root runtime file's own name is
		// resolved and reported missing by the reader: the blocker write is skipped
		// rather than being written into a file this tool guessed at.
		return join(destinationRoot, ROOT_CANDIDATES[0] ?? "AGENTS.md");
	}

	async detectRootFile(destinationRoot: string): Promise<string | null> {
		for (const candidate of ROOT_CANDIDATES) {
			if ((await readKind(join(destinationRoot, candidate))) === "file") {
				return candidate;
			}
		}
		return null;
	}

	async planBlocker(
		destinationRoot: string,
		document: BindingsDocument,
		pending: readonly string[],
		missing: readonly MissingRegionSource[],
		payload: readonly PlannedPayload[],
	): Promise<{ readonly path: string; readonly content: string } | null> {
		// The caller's read preflight must cover the root and its ancestors before
		// resolution or reading; this method never validates filesystem traversal.
		const rootPath = await this.resolveRootFile(destinationRoot, document);
		// The shared projection rule decides what the pending writes leave behind,
		// so the planned blocker and the executed blocker agree on the content.
		const projected = projectedPayloadText(rootPath, payload);
		const text = projected === undefined ? await readTextFile(rootPath) : projected;
		if (text === null) {
			return null;
		}
		const next = syncReconciliationBlocker(text, pending, effectiveEditor(undefined, document.editor), missing);
		return next === text ? null : { path: rootPath, content: next };
	}

	async syncBlocker(
		destinationRoot: string,
		document: BindingsDocument,
		pending: readonly string[],
		missing: readonly MissingRegionSource[],
	): Promise<void> {
		const rootPath = await this.resolveRootFile(destinationRoot, document);
		const text = await readTextFile(rootPath);
		if (text === null) {
			return;
		}
		const next = syncReconciliationBlocker(text, pending, effectiveEditor(undefined, document.editor), missing);
		if (next !== text) {
			await writeTextFile(rootPath, next);
		}
	}
}

/** Read a path's kind: absent, a regular file, or something else. */
async function readKind(path: string): Promise<PathKind> {
	try {
		const observed = await stat(path);
		return observed.isFile() ? "file" : "other";
	} catch (error) {
		if (isMissing(error)) {
			return "absent";
		}
		throw error;
	}
}
