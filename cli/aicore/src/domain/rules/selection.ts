/**
 * Domain rules: destination and editor selection.
 *
 * Pure per scripts-shape P1. The rules deciding which destination and editor a
 * run will act on live here so a wrong guess is impossible by construction.
 */

import { SUPPORTED_EDITORS, type SupportedEditor } from "#domain/constants.ts";
import { fail, succeed, type Result } from "#domain/failures.ts";
import type { SavedSelection } from "#domain/ports/selection-store.ts";

/**
 * Report whether an editor identifier names an implemented distribution target.
 *
 * The single owner of that validity rule, so no adapter re-decides it.
 */
export function isSupportedEditor(value: string): value is SupportedEditor {
  return (SUPPORTED_EDITORS as readonly string[]).includes(value);
}

/**
 * Decide which editor the destination gets.
 *
 * An explicit editor always wins. Without one, a saved editor applies only to the
 * same destination; a destination the operator never configured must state its
 * editor, because the CLI will not guess an editor for an existing project.
 */
export function resolveDestinationEditor(
  requestedEditor: SupportedEditor | undefined,
  saved: SavedSelection | undefined,
  destination: string,
  destinationIsBound: boolean,
): Result<SupportedEditor> {
  if (requestedEditor !== undefined) {
    return succeed(requestedEditor);
  }
  if (saved !== undefined && saved.target === destination) {
    return succeed(saved.editor);
  }
  const reason = destinationIsBound
    ? "no editor was supplied for this run; repeat the run with the editor this " +
      "destination is enrolled for, or with --editor"
    : "this destination has no recorded editor yet";
  return fail(
    "unknown-editor",
    `cannot choose an editor: ${reason}. Pass --editor explicitly; ` +
      "the CLI never infers an editor for a project.",
  );
}

/**
 * Decide the destination path for the run.
 *
 * Only an explicit target or the saved destination is acceptable; there is no
 * implicit current-directory destination, so a run can never enroll the checkout
 * by accident.
 */
export function resolveDestinationPath(
  requestedTarget: string | undefined,
  saved: SavedSelection | undefined,
): Result<string> {
  if (requestedTarget !== undefined) {
    return succeed(requestedTarget);
  }
  if (saved !== undefined) {
    return succeed(saved.target);
  }
  return fail(
    "unavailable-configuration",
    "no destination selected. Run once with --target <destination-path>; " +
      "later runs reuse the saved selection.",
  );
}

/**
 * Report whether this run should persist a new selection.
 *
 * A run establishes a selection only when the operator stated it explicitly, so a
 * run that merely reused the saved values never rewrites them.
 */
export function selectionToSave(
  requestedTarget: string | undefined,
  explicitEditor: SupportedEditor | undefined,
  destination: string,
  editor: SupportedEditor,
): SavedSelection | undefined {
  if (requestedTarget === undefined && explicitEditor === undefined) {
    return undefined;
  }
  return { target: destination, editor };
}
