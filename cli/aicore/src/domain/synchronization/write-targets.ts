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
 */

import type { CommandName } from "./constants.ts";
import { type SynchronizationFailure, invalid } from "./failures.ts";

/** What a write target is for, as the diagnostics name it. */
export type WriteTargetKind = "root" | "destination payload" | "bindings" | "report";

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
  if (
    isWithin(facts.sourceRoot, facts.destinationRoot) ||
    isWithin(facts.destinationRoot, facts.sourceRoot)
  ) {
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
    if (target.exists && !target.regularFile) {
      return refuse(`${target.kind} write target is not a regular file: ${target.path}`);
    }
    const previous = resolvedTargets.get(target.resolvedPath);
    if (previous !== undefined) {
      if (previous.kind === "root" && target.kind === "destination payload" && isNonRegion(facts, target)) {
        return refuse(`root write target aliases non-region destination: ${target.path}`);
      }
      if (!sameRootRegionTarget(previous, target, facts)) {
        return refuse(
          `distinct write targets alias after resolution: ${previous.path} and ${target.path}`,
        );
      }
    } else {
      resolvedTargets.set(target.resolvedPath, target);
    }
    if (isWithin(target.resolvedPath, facts.sourceRoot)) {
      return refuse(`${target.kind} write target resolves inside source tree: ${target.path}`);
    }
    if (
      (target.kind === "root" || target.kind === "destination payload") &&
      !isWithin(target.resolvedPath, facts.destinationRoot)
    ) {
      return refuse(`${target.kind} write target escapes destination root: ${target.path}`);
    }
    if (target.identity !== null) {
      const key = identityKey(target.identity);
      if (sourceIdentities.has(key)) {
        return refuse(`${target.kind} write target shares a source-tree file inode: ${target.path}`);
      }
      const previousTarget = targetIdentities.get(key);
      if (previousTarget !== undefined) {
        if (!sameRootRegionTarget(previousTarget, target, facts)) {
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
  return facts.nonRegionDestinations.some(
    (destination) => destination.resolvedPath === target.resolvedPath,
  );
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

/** Return whether `path` is `root` or nested under it, lexically. */
export function isWithin(path: string, root: string): boolean {
  const normalizedPath = normalizeSeparators(path);
  const normalizedRoot = normalizeSeparators(root).replace(/\/+$/u, "");
  return normalizedPath === normalizedRoot || normalizedPath.startsWith(`${normalizedRoot}/`);
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
