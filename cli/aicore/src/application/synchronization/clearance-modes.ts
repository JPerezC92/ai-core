/**
 * Reading the clearance registry into the path-to-mode map every command needs.
 *
 * The clearance gate runs before any bound-source payload read or destination
 * mutation, so all three commands share this one preparation step: load the
 * registry, enumerate each directory root, expand the modes and destinations for
 * the editor this run acts for, and report whether the registry was present and
 * readable.
 */

import type { BindingMode } from "#domain/synchronization/constants.ts";
import { type ClearanceEntry, expandClearance } from "#domain/synchronization/clearance.ts";
import type { PathInspection } from "#domain/ports/path-inspection.ts";
import type { EditorProfile } from "#domain/synchronization/editor-profile.ts";
import { type SynchronizationFailure, invalid } from "#domain/synchronization/failures.ts";
import type { ClearanceStore } from "#domain/synchronization/ports.ts";

/** The clearance state one command works from. */
export type ClearanceModes = {
  readonly modes: ReadonlyMap<string, BindingMode>;
  /** The destination path of every source this editor receives. */
  readonly destinations: ReadonlyMap<string, string>;
  readonly entries: ReadonlyMap<string, ClearanceEntry> | null;
  readonly exists: boolean;
  /** Why a present registry was rejected, or `null` when it parsed. */
  readonly reason: string | null;
};

/**
 * Load the registry, enumerate its directory roots, and expand its modes.
 *
 * The layout parameter is the read-only path inspection, so this step can be
 * shared with a command that must not hold a write capability; the engine's
 * wider layout satisfies it.
 */
export async function readClearanceModes(
  clearance: ClearanceStore,
  layout: PathInspection,
  sourceRoot: string,
  editor: EditorProfile,
): Promise<ClearanceModes> {
  const loaded = await clearance.load(sourceRoot);
  if (loaded.entries === null) {
    return {
      modes: new Map<string, BindingMode>(),
      destinations: new Map<string, string>(),
      entries: null,
      exists: loaded.exists,
      reason: loaded.reason,
    };
  }
  const enumerated = new Map<string, readonly string[]>();
  for (const key of loaded.entries.keys()) {
    if (key.endsWith("/")) {
      enumerated.set(
        key,
        await layout.enumerateFilesUnder(layout.join(sourceRoot, key.slice(0, -1))),
      );
    }
  }
  const expansion = expandClearance(loaded.entries, enumerated, editor);
  return {
    modes: expansion.modes,
    destinations: expansion.destinations,
    entries: loaded.entries,
    exists: loaded.exists,
    reason: null,
  };
}

/**
 * The refusal for a registry that is present but unreadable.
 *
 * The class is malformed input; the reader's reason names what was wrong with
 * the document, so a duplicate declaration is reported as one.
 */
export function invalidClearance(
  clearancePath: string,
  clearance: ClearanceModes,
): SynchronizationFailure {
  const detail = clearance.reason === null ? "" : `: ${clearance.reason}`;
  return invalid(`invalid clearance file: ${clearancePath}${detail}`);
}
