/**
 * Domain: the editor profiles a destination can be enrolled for.
 *
 * An editor profile decides where a cleared source lands in a destination and
 * whether that editor receives it at all. The closed set is the synchronization
 * contract's own vocabulary, so it lives with the rules that use it (P1).
 *
 * The rules are pure: they read the enrolled editor and the requested one and
 * return a decision, so no adapter re-decides which editor a destination is.
 */

import { type SynchronizationFailure, invalid } from "./failures.ts";

/** The editors a destination can be enrolled for. */
export const EDITOR_PROFILES = ["opencode", "cursor"] as const;

/** One editor profile. */
export type EditorProfile = (typeof EDITOR_PROFILES)[number];

/**
 * The editor a destination that records none is read as.
 *
 * It is the only profile that existed before editor profiles were introduced,
 * so an enrollment that predates them keeps its meaning.
 */
export const DEFAULT_EDITOR_PROFILE: EditorProfile = "opencode";

/** What one editor receives from a cleared source. */
export type EditorDelivery =
  | { readonly kind: "delivered"; readonly destination: string }
  | { readonly kind: "omitted" };

/** Report whether a value names an editor profile. */
export function isEditorProfile(value: string): value is EditorProfile {
  return (EDITOR_PROFILES as readonly string[]).includes(value);
}

/**
 * Decide which editor a run acts for.
 *
 * An explicit request always wins; otherwise the destination's own record does,
 * and a destination that records none is read as the default profile.
 */
export function effectiveEditor(
  requested: EditorProfile | undefined,
  enrolled: EditorProfile | null,
): EditorProfile {
  if (requested !== undefined) {
    return requested;
  }
  return enrolled ?? DEFAULT_EDITOR_PROFILE;
}

/**
 * Return the refusal an enrolled editor earns when a run asks for another one.
 *
 * A destination's editor is fixed by its enrollment: the files it holds were
 * placed for that editor, so a run for another one would deliver the wrong
 * payload and claim the wrong target. Changing it is a destination-owned
 * migration, not something a synchronization performs.
 *
 * A destination that records no editor is read as the default profile, so a run
 * for another editor is refused rather than delivered to the wrong target.
 */
export function editorMismatch(
  enrolled: EditorProfile | null,
  requested: EditorProfile | undefined,
): SynchronizationFailure | null {
  if (requested === undefined) {
    return null;
  }
  const destinationEditor = enrolled ?? DEFAULT_EDITOR_PROFILE;
  if (destinationEditor === requested) {
    return null;
  }
  return invalid(
    `destination is enrolled for editor '${destinationEditor}'; this run requested '${requested}'. ` +
      "Changing an enrolled destination's editor is a destination-owned migration: " +
      "enroll the destination again under the new editor, or move its files yourself. " +
      "Nothing was written.",
  );
}
