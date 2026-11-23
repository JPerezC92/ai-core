/**
 * The write-target preflight rule (pure).
 *
 * Synchronization distributes ordinary files and directories; a symbolic link is
 * never an artifact. A managed write path that contains a link is refused
 * before the destination is modified: the link itself, or a path that resolves
 * through one into the source tree or out of the destination root.
 *
 * Nothing is written until every target a command could write is proven safe: a
 * symlink, a non-regular file, a target that resolves inside the source tree, a
 * target sharing an inode with a source file or with another target, and a target
 * escaping the destination root are all refused before the first mutation. The
 * facts — resolved paths, regular-file kind, device/inode identity — are read by
 * the infrastructure adapter; the decision and its diagnostics live here.
 *
 * Beside the preflight rule this module owns the path identity every comparison
 * shares, and the one rule that says what a pending write leaves behind, so the
 * planner and the executor cannot disagree about a file's content.
 */

import type { CommandName } from "./constants.ts";
import { type SynchronizationFailure, invalid } from "./failures.ts";
import type { PlannedPayload } from "./ports.ts";

/**
 * Who owns the destination path a planned mutation changes.
 *
 * The owner names what the path is for, not what the mutation does: the root
 * runtime file, a payload destination, the bindings document, the
 * reconciliation report, the secret material, or the secret directory.
 */
export type MutationOwner = "root" | "payload" | "bindings" | "report" | "secret" | "directory";

/** What a write target is for, as the diagnostics name it. */
export type WriteTargetKind = "root" | "destination payload" | "bindings" | "report" | "secret" | "directory";

/** The diagnostic name each mutation owner is reported under. */
const OWNER_KINDS: Readonly<Record<MutationOwner, WriteTargetKind>> = {
	root: "root",
	payload: "destination payload",
	bindings: "bindings",
	report: "report",
	secret: "secret",
	directory: "directory",
};

/** Return the diagnostic kind a mutation owner is reported under. */
export function writeTargetKind(owner: MutationOwner): WriteTargetKind {
	return OWNER_KINDS[owner];
}

/** Whether a kind names a path the destination's own content lives in. */
function isDestinationContent(kind: WriteTargetKind): boolean {
	return kind === "root" || kind === "destination payload" || kind === "secret" || kind === "directory";
}

/** A filesystem object's device/inode identity. */
export type FileIdentity = {
	readonly device: bigint;
	readonly inode: bigint;
};

/** One observed write target. */
export type WriteTargetObservation = {
	readonly kind: WriteTargetKind;
	/** The target path as the command named it, for diagnostics. */
	readonly path: string;
	/** The target with every symlink resolved. */
	readonly resolvedPath: string;
	/** The target as an absolute lexical path, without resolving links. */
	readonly lexicalPath: string;
	readonly symbolicLink: boolean;
	readonly exists: boolean;
	readonly regularFile: boolean;
	readonly identity: FileIdentity | null;
	/** A directory creation requires a directory rather than a regular file. */
	readonly directoryTarget?: boolean;
	/** Whether the target exists as a directory. */
	readonly directory: boolean;
};

/** One observed destination that is raw- or merge-bound. */
export type NonRegionDestinationObservation = {
	readonly path: string;
	readonly resolvedPath: string;
	readonly exists: boolean;
	readonly regularFile: boolean;
	readonly identity: FileIdentity | null;
};

/** One raw target `init` plans to create. */
export type PlannedRawCreation = {
	readonly path: string;
	readonly resolvedPath: string;
	readonly exists: boolean;
	readonly parentIsDirectory: boolean;
};

/** The default root runtime file `init` would fall back to. */
export type ImplicitRootObservation = {
	readonly path: string;
	readonly resolvedPath: string;
	readonly regularFile: boolean;
};

/** Everything the preflight rule needs, already observed. */
export type WriteTargetFacts = {
	readonly command: CommandName;
	readonly sourceRoot: string;
	readonly destinationRoot: string;
	readonly sourceFileIdentities: readonly FileIdentity[];
	readonly targets: readonly WriteTargetObservation[];
	readonly nonRegionDestinations: readonly NonRegionDestinationObservation[];
	/** Present only for `init` when the bindings name no explicit root. */
	readonly implicitRoot: ImplicitRootObservation | null;
	readonly plannedRawCreations: readonly PlannedRawCreation[];
};

/**
 * Return the refusal this command's write targets earn, or `null` when safe.
 *
 * Ordering is part of the contract's diagnostics: roots first, then each target
 * in the order the command would write it.
 */
export function refuseWriteTargets(facts: WriteTargetFacts): SynchronizationFailure | null {
	if (isWithin(facts.sourceRoot, facts.destinationRoot) || isWithin(facts.destinationRoot, facts.sourceRoot)) {
		return refuse("source and destination roots overlap");
	}

	const sourceIdentities = new Set(facts.sourceFileIdentities.map(identityKey));
	const resolvedTargets = new Map<string, WriteTargetObservation>();
	const targetIdentities = new Map<string, WriteTargetObservation>();
	let resolvedRoot: string | null = null;

	for (const target of facts.targets) {
		if (target.symbolicLink) {
			return refuse(`${target.kind} write target is a symbolic link: ${target.path}`);
		}
		if (target.exists && !(target.directoryTarget ? target.directory : target.regularFile)) {
			// A secret-owned file write whose target already exists as a directory is
			// not refused here: the write raises the filesystem's own refusal, which
			// the exit contract classes as a write-time I/O error rather than as an
			// unsafe write target.
			if (!isSecretFileWriteOverDirectory(target)) {
				if (target.directoryTarget) {
					return refuse(`${target.kind} write target is not a directory: ${target.path}`);
				}
				return refuse(`${target.kind} write target is not a regular file: ${target.path}`);
			}
		}
		const previous = resolvedTargets.get(target.resolvedPath);
		if (previous !== undefined) {
			if (previous.kind === "root" && target.kind === "destination payload" && isNonRegion(facts, target)) {
				return refuse(`root write target aliases non-region destination: ${target.path}`);
			}
			// Two owners may not resolve to one path: the write would land on a
			// file another owner owns. The same owner may write one path twice —
			// the root runtime file is both a payload destination and the file
			// the blocker is written into.
			if (previous.kind !== target.kind && !sameRootRegionTarget(previous, target, facts)) {
				return refuse(`distinct write targets alias after resolution: ${previous.path} and ${target.path}`);
			}
		} else {
			resolvedTargets.set(target.resolvedPath, target);
		}
		if (isWithin(target.resolvedPath, facts.sourceRoot)) {
			return refuse(`${target.kind} write target resolves inside source tree: ${target.path}`);
		}
		if (isDestinationContent(target.kind) && !isWithin(target.resolvedPath, facts.destinationRoot)) {
			return refuse(`${target.kind} write target escapes destination root: ${target.path}`);
		}
		if (target.identity !== null) {
			const key = identityKey(target.identity);
			if (sourceIdentities.has(key)) {
				return refuse(`${target.kind} write target shares a source-tree file inode: ${target.path}`);
			}
			const previousTarget = targetIdentities.get(key);
			if (previousTarget !== undefined) {
				// Two targets that name one path are one file, not an aliasing pair:
				// the root runtime file is observed as the root and written as the
				// payload and as the blocker. A different path that shares the
				// inode is the aliasing the rule refuses.
				if (!samePath(previousTarget, target)) {
					return refuse(
						`distinct write targets share a filesystem inode: ${previousTarget.path} and ${target.path}`,
					);
				}
			} else {
				targetIdentities.set(key, target);
			}
		}
		if (target.kind === "root") {
			resolvedRoot = target.resolvedPath;
		}
	}

	for (const destination of facts.nonRegionDestinations) {
		if (resolvedRoot !== null && resolvedRoot === destination.resolvedPath) {
			return refuse(`root write target aliases non-region destination: ${destination.path}`);
		}
		const rootIdentity = facts.targets.find((target) => target.kind === "root")?.identity ?? null;
		if (
			destination.exists &&
			destination.regularFile &&
			rootIdentity !== null &&
			destination.identity !== null &&
			identityKey(rootIdentity) === identityKey(destination.identity)
		) {
			return refuse(`root write target aliases non-region destination: ${destination.path}`);
		}
	}

	if (facts.implicitRoot !== null && !facts.implicitRoot.regularFile) {
		for (const creation of facts.plannedRawCreations) {
			if (creation.exists || !creation.parentIsDirectory) {
				continue;
			}
			if (creation.resolvedPath === facts.implicitRoot.resolvedPath) {
				return refuse(`default root would alias newly created raw destination: ${creation.path}`);
			}
		}
	}

	return null;
}

/** Return whether a payload target is bound in a raw or merge mode. */
function isNonRegion(facts: WriteTargetFacts, target: WriteTargetObservation): boolean {
	return facts.nonRegionDestinations.some((destination) => destination.resolvedPath === target.resolvedPath);
}

/**
 * Return whether this target is a secret-owned file write over a directory.
 *
 * The secret setup owns the ignore file and the credential file, and both are
 * written as ordinary files. When such a target already exists as a directory,
 * the refusal belongs to the write itself: the filesystem raises it, and the
 * exit contract classes that as a write-time I/O error.
 */
function isSecretFileWriteOverDirectory(target: WriteTargetObservation): boolean {
	return target.kind === "secret" && !target.directoryTarget && target.directory;
}

/**
 * Return whether two targets name one path.
 *
 * One path is one file, so two targets that name it are the same target however
 * many owners observe or write it.
 */
function samePath(previous: WriteTargetObservation, target: WriteTargetObservation): boolean {
	return previous.lexicalPath === target.lexicalPath;
}

/**
 * Return whether two targets are the same root/region pair.
 *
 * The root runtime file may legitimately be a region destination of its own; the
 * alias refusals exist for every other collision.
 */
function sameRootRegionTarget(
	previous: WriteTargetObservation,
	target: WriteTargetObservation,
	facts: WriteTargetFacts,
): boolean {
	const kinds = new Set<WriteTargetKind>([previous.kind, target.kind]);
	return (
		previous.lexicalPath === target.lexicalPath &&
		kinds.size === 2 &&
		kinds.has("root") &&
		kinds.has("destination payload") &&
		!isNonRegion(facts, target)
	);
}

/**
 * The last pending effect on a path, as the run's own read would see it.
 *
 * One rule for every caller: the content a pending write leaves behind is the
 * content the next read observes. A byte write is decoded exactly as the
 * destination's reader decodes it, so a byte order mark stays part of the text.
 *
 * `undefined` means no pending effect, so the file on disk is authoritative;
 * `null` means the pending effects delete the path.
 */
export function projectedPayloadText(path: string, payload: readonly PlannedPayload[]): string | null | undefined {
	const identity = pathIdentity(path);
	const effect = payload.findLast((operation) => pathIdentity(operation.path) === identity);
	if (effect === undefined) {
		return undefined;
	}
	if (effect.kind === "file-delete") {
		return null;
	}
	if (effect.kind === "text-write") {
		return effect.content.replaceAll("\r\n", "\n").replaceAll("\r", "\n");
	}
	return new TextDecoder("utf-8", { ignoreBOM: true }).decode(effect.content);
}

/** Return whether `path` is `root` or nested under it, lexically. */
export function isWithin(path: string, root: string): boolean {
	const normalizedPath = normalizeSeparators(path);
	const normalizedRoot = normalizeSeparators(root).replace(/\/+$/u, "");
	return normalizedPath === normalizedRoot || normalizedPath.startsWith(`${normalizedRoot}/`);
}

/**
 * Return the identity of a path: one absolute form every comparison shares.
 *
 * Separators are normalized, `.` and `..` components are resolved and the
 * root prefix is kept, so the payload effects, the blocker projection and the
 * secret projection all recognize the same file however it was spelled.
 */
export function pathIdentity(path: string): string {
	const normalized = path.replaceAll("\\", "/");
	const prefix = /^[A-Za-z]:\//u.exec(normalized);
	const root = prefix === null ? (normalized.startsWith("/") ? "/" : "") : `${prefix[0]}/`;
	const segments: string[] = [];
	for (const segment of normalized.slice(root.length).split("/")) {
		if (segment === "" || segment === ".") {
			continue;
		}
		if (segment === "..") {
			segments.pop();
			continue;
		}
		segments.push(segment);
	}
	return `${root}${segments.join("/")}`;
}

function normalizeSeparators(path: string): string {
	return path.replaceAll("\\", "/");
}

function identityKey(identity: FileIdentity): string {
	return `${identity.device.toString()}:${identity.inode.toString()}`;
}

function refuse(detail: string): SynchronizationFailure {
	return invalid(`invalid write target: ${detail}`);
}
