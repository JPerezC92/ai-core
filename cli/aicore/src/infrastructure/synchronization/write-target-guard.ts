/**
 * Infrastructure: observing every write target before a command mutates anything.
 *
 * Synchronization distributes ordinary files and directories; a symbolic link is
 * never an artifact. A managed write path that contains a link is refused
 * before the destination is modified: the link itself, or a path that resolves
 * through one into the source tree or out of the destination root.
 *
 * This adapter collects the facts — whether a path is a symlink, whether it is a
 * regular file, its resolved location, and its device/inode identity — and hands
 * them to the domain's preflight rule. It decides nothing itself: a fabricated
 * or omitted observation would let an unsafe target through.
 */

import type { BigIntStats } from "node:fs";
import { lstat, readdir, realpath, stat } from "node:fs/promises";
import { basename, dirname, join, relative, resolve, sep } from "node:path";

import {
	type BindingMode,
	MODE_MERGE,
	MODE_RAW,
	RECONCILIATION_DIRECTORY,
	RECONCILIATION_FILENAME,
	ROOT_CANDIDATES,
} from "#domain/synchronization/constants.ts";
import { type SynchronizationFailure, invalid } from "#domain/synchronization/failures.ts";
import type {
	FilesystemLayout,
	PlannedRead,
	WriteTargetGuard,
	WriteTargetRequest,
} from "#domain/synchronization/ports.ts";
import {
	type FileIdentity,
	isWithin,
	pathIdentity,
	refuseWriteTargets,
	type MutationOwner,
	type NonRegionDestinationObservation,
	type PlannedRawCreation,
	type WriteTargetFacts,
	type WriteTargetKind,
	type WriteTargetObservation,
	writeTargetKind,
} from "#domain/synchronization/write-targets.ts";

import { isFileSystemError, isMissing } from "./local-files.ts";

export class LocalWriteTargetGuard implements WriteTargetGuard {
	readonly #layout: FilesystemLayout;

	constructor(layout: FilesystemLayout) {
		this.#layout = layout;
	}

	/**
	 * Observe the targets and return the preflight refusal, if any.
	 *
	 * A target the filesystem refuses to resolve is unsafe, so the engine
	 * reports it as malformed input (exit 2). Any other exception is a
	 * programming fault and propagates unchanged.
	 */
	async refuse(request: WriteTargetRequest): Promise<SynchronizationFailure | null> {
		try {
			return await this.#refuse(request);
		} catch (error) {
			if (!isFileSystemError(error)) {
				throw error;
			}
			const detail = error instanceof Error ? error.message : String(error);
			return invalid(`invalid write target: could not resolve write target: ${detail}`);
		}
	}

	async #refuse(request: WriteTargetRequest): Promise<SynchronizationFailure | null> {
		const sourceRoot = await realPathOf(request.sourceRoot);
		const destinationRoot = await realPathOf(request.destinationRoot);
		if (request.phase === "read") {
			return await this.#refuseReads(request, sourceRoot, destinationRoot);
		}
		if (request.phase === "mutations") {
			return await this.#refuseMutations(request, sourceRoot, destinationRoot);
		}

		const rootPath = await this.#layout.resolveRootFile(request.destinationRoot, request.document);
		const targets: WriteTargetObservation[] = [await observe("root", rootPath)];
		if (request.command === "apply" || request.command === "init") {
			for (const entry of request.document.bindings) {
				for (const destination of entry.destinations) {
					targets.push(await observe("destination payload", join(request.destinationRoot, destination)));
				}
			}
			targets.push(await observe("bindings", request.bindingsPath));
		}
		if (request.command === "init") {
			targets.push(
				await observe(
					"report",
					join(dirname(request.bindingsPath), RECONCILIATION_DIRECTORY, RECONCILIATION_FILENAME),
				),
			);
		}

		const facts: WriteTargetFacts = {
			command: request.command,
			sourceRoot,
			destinationRoot,
			sourceFileIdentities: await sourceFileIdentities(request.sourceRoot),
			targets,
			nonRegionDestinations: await this.#nonRegionDestinations(request),
			implicitRoot:
				request.command === "init" && request.document.root === null
					? await observeImplicitRoot(request.destinationRoot)
					: null,
			plannedRawCreations: await plannedRawCreations(request.destinationRoot, request.newRawDestinations),
		};
		return refuseWriteTargets(facts);
	}

	/**
	 * Validate every path whose contents are about to be read.
	 *
	 * A read follows links, so the path is checked before it is read: no
	 * component may be a link, the resolved path must stay inside the
	 * destination root, and an existing path must be a regular file. The
	 * write-only refusals — a target sharing a source file's inode, a target
	 * aliasing a destination — are not applied here: a destination that is
	 * only read stays readable.
	 *
	 * Each read carries the owner of the path it reads. One owner is
	 * tolerated over a directory: the secret setup's ignore file, whose read
	 * classifies a directory as absent and whose write is the operation that
	 * reports the filesystem's refusal. Every other owner still refuses a
	 * directory before the read happens.
	 */
	async #refuseReads(
		request: WriteTargetRequest,
		sourceRoot: string,
		destinationRoot: string,
	): Promise<SynchronizationFailure | null> {
		if (isWithin(sourceRoot, destinationRoot) || isWithin(destinationRoot, sourceRoot)) {
			return invalid("invalid write target: source and destination roots overlap");
		}
		const rootPath = await this.#layout.resolveRootFile(request.destinationRoot, request.document);
		const reads: readonly PlannedRead[] = [{ path: rootPath, owner: "root" }, ...(request.readPaths ?? [])];
		for (const read of reads) {
			const observed = await observe(writeTargetKind(read.owner), read.path);
			if (await hasLinkInPath(read.path, request.destinationRoot)) {
				return invalid(`invalid write target: read path contains a symbolic link: ${read.path}`);
			}
			if (!isWithin(observed.resolvedPath, destinationRoot)) {
				return invalid(`invalid write target: read path escapes destination root: ${read.path}`);
			}
			if (observed.exists && !observed.regularFile && !toleratesDirectory(read.owner, observed)) {
				return invalid(`invalid write target: read path is not a regular file: ${read.path}`);
			}
		}
		return null;
	}

	/**
	 * Validate the complete set of mutations before the first one happens.
	 *
	 * Each mutation carries the owner of the path it changes, so the rule knows
	 * which paths are the same target and which are two owners colliding. The
	 * destination's root runtime file is observed first, as the phase-less
	 * branch observes it: a binding that owns the instruction root aliases it,
	 * and that alias is refused before anything is written.
	 */
	async #refuseMutations(
		request: WriteTargetRequest,
		sourceRoot: string,
		destinationRoot: string,
	): Promise<SynchronizationFailure | null> {
		const rootPath = await this.#layout.resolveRootFile(request.destinationRoot, request.document);
		const targets: WriteTargetObservation[] = [await observe("root", rootPath)];
		for (const mutation of request.mutations ?? []) {
			const kind = writeTargetKind(mutation.owner);
			const observed = await observe(kind, mutation.path);
			targets.push({
				...observed,
				symbolicLink: await hasLinkInPath(mutation.path, request.destinationRoot),
				directoryTarget: mutation.kind === "directory-create",
			});
		}
		return refuseWriteTargets({
			command: request.command,
			sourceRoot,
			destinationRoot,
			sourceFileIdentities: await sourceFileIdentities(request.sourceRoot),
			targets,
			nonRegionDestinations: await this.#nonRegionDestinations(request),
			implicitRoot:
				request.command === "init" && request.document.root === null
					? await observeImplicitRoot(request.destinationRoot)
					: null,
			plannedRawCreations: await plannedRawCreations(request.destinationRoot, request.newRawDestinations),
		});
	}

	async #nonRegionDestinations(request: WriteTargetRequest): Promise<readonly NonRegionDestinationObservation[]> {
		const observations: NonRegionDestinationObservation[] = [];
		for (const entry of request.document.bindings) {
			const mode: BindingMode | undefined = request.modes.get(entry.source);
			if (mode !== MODE_RAW && mode !== MODE_MERGE) {
				continue;
			}
			for (const destination of entry.destinations) {
				const path = join(request.destinationRoot, destination);
				const observed = await observe("destination payload", path);
				observations.push({
					path,
					resolvedPath: observed.resolvedPath,
					exists: observed.exists,
					regularFile: observed.regularFile,
					identity: observed.identity,
				});
			}
		}
		return observations;
	}
}

/**
 * Return whether a read of a path that exists as a directory is tolerated.
 *
 * Only the secret setup's own read is: the ignore file's read classifies a
 * directory as absent, and the write that follows raises the filesystem's
 * refusal. Every other owner refuses a directory before the read happens.
 */
function toleratesDirectory(owner: MutationOwner, observed: WriteTargetObservation): boolean {
	return owner === "secret" && observed.directory;
}

/** Inspect each lexical component without reading file contents. */
async function hasLinkInPath(path: string, destinationRoot: string): Promise<boolean> {
	const absolute = resolve(path);
	const root = resolve(destinationRoot);
	const within = isWithin(absolute, root);
	const start = within ? root : resolve(absolute, "..");
	const components = within ? relative(root, absolute).split(sep).filter(Boolean) : [basename(absolute)];
	let current = start;
	if ((await lstatOrNull(current))?.isSymbolicLink()) {
		return true;
	}
	for (const component of components) {
		current = join(current, component);
		if ((await lstatOrNull(current))?.isSymbolicLink()) {
			return true;
		}
	}
	return false;
}

/**
 * Observe one write target.
 *
 * `symlink` is read with `lstat` so a link to a file is still a link, and the
 * rest with `stat`, which follows it: the preflight refuses both shapes.
 */
async function observe(kind: WriteTargetKind, path: string): Promise<WriteTargetObservation> {
	const link = await lstatOrNull(path);
	const observed = await statOrNull(path);
	return {
		kind,
		path,
		resolvedPath: await realPathOf(path),
		lexicalPath: pathIdentity(path),
		symbolicLink: link?.isSymbolicLink() ?? false,
		exists: observed !== null,
		regularFile: observed?.isFile() ?? false,
		directory: observed?.isDirectory() ?? false,
		identity: identityOf(observed),
	};
}

async function observeImplicitRoot(
	destinationRoot: string,
): Promise<{ readonly path: string; readonly resolvedPath: string; readonly regularFile: boolean }> {
	const path = join(destinationRoot, ROOT_CANDIDATES[0] ?? "AGENTS.md");
	const observed = await statOrNull(path);
	return {
		path,
		resolvedPath: await realPathOf(path),
		regularFile: observed?.isFile() ?? false,
	};
}

async function plannedRawCreations(
	destinationRoot: string,
	destinations: ReadonlySet<string>,
): Promise<readonly PlannedRawCreation[]> {
	const creations: PlannedRawCreation[] = [];
	for (const destination of destinations) {
		const path = join(destinationRoot, destination);
		const observed = await statOrNull(path);
		const parent = await statOrNull(dirname(path));
		creations.push({
			path,
			resolvedPath: await realPathOf(path),
			exists: observed !== null,
			parentIsDirectory: parent?.isDirectory() ?? false,
		});
	}
	return creations;
}

/**
 * Collect every regular file's identity reachable under the source root.
 *
 * Symlinked directories are followed, with a cycle guard, because a hard link or
 * a symlinked tree must not let a destination payload mutate a source file.
 * An identity is reported only when the filesystem reports a non-zero inode.
 */
async function sourceFileIdentities(root: string): Promise<readonly FileIdentity[]> {
	const rootStat = await statOrNull(root);
	if (rootStat === null) {
		return [];
	}
	const rootIdentity = identityOf(rootStat);
	if (rootStat.isFile()) {
		return rootIdentity === null ? [] : [rootIdentity];
	}
	if (!rootStat.isDirectory()) {
		return [];
	}

	const identities: FileIdentity[] = [];
	const visitedIdentities = new Set<string>();
	const visitedPaths = new Set<string>([resolve(root)]);
	if (rootIdentity !== null) {
		visitedIdentities.add(identityKey(rootIdentity));
	}
	const directories: string[] = [root];
	while (directories.length > 0) {
		const directory = directories.pop();
		if (directory === undefined) {
			break;
		}
		for (const entry of await readdir(directory, { withFileTypes: true })) {
			const path = join(directory, entry.name);
			const observed = await statOrNull(path);
			if (observed === null) {
				continue;
			}
			const identity = identityOf(observed);
			if (observed.isDirectory()) {
				if (identity !== null) {
					const key = identityKey(identity);
					if (visitedIdentities.has(key)) {
						continue;
					}
					visitedIdentities.add(key);
				} else {
					const absolute = resolve(path);
					if (visitedPaths.has(absolute)) {
						continue;
					}
					visitedPaths.add(absolute);
				}
				directories.push(path);
				continue;
			}
			if (observed.isFile() && identity !== null) {
				identities.push(identity);
			}
		}
	}
	return identities;
}

async function lstatOrNull(path: string) {
	try {
		return await lstat(path);
	} catch (error) {
		if (isMissing(error)) {
			return null;
		}
		throw error;
	}
}

async function statOrNull(path: string) {
	try {
		return await stat(path, { bigint: true });
	} catch (error) {
		if (isMissing(error)) {
			return null;
		}
		throw error;
	}
}

function identityOf(observed: BigIntStats | null): FileIdentity | null {
	if (observed === null || observed.ino === 0n) {
		return null;
	}
	return { device: observed.dev, inode: observed.ino };
}

function identityKey(identity: FileIdentity): string {
	return `${identity.device.toString()}:${identity.inode.toString()}`;
}

/**
 * Resolve a path with every symlink followed, without requiring it to exist.
 *
 * The nearest existing ancestor is resolved by the platform and the remaining
 * segments are appended, so a target that does not exist yet is still located —
 * which is exactly the escape and source-containment checks' question.
 */
async function realPathOf(path: string): Promise<string> {
	try {
		return await realpath(path);
	} catch (error) {
		if (!isMissing(error)) {
			throw error;
		}
		const parent = dirname(path);
		if (parent === path) {
			return path;
		}
		return join(await realPathOf(parent), basename(path));
	}
}
