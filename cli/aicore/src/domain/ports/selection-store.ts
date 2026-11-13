/**
 * Domain port: the last explicit destination and editor choice.
 *
 * One capability per module (P4, C2). `SavedSelection` is a data-only record.
 */

import type { SupportedEditor } from "#domain/constants.ts";

export type SavedSelection = {
  /** Absolute destination path the operator last selected explicitly. */
  readonly target: string;
  readonly editor: SupportedEditor;
};

export interface SelectionStore {
  /** Read the saved selection, or `undefined` when none is usable. */
  read(): Promise<SavedSelection | undefined>;
  /** Persist the selection an explicit run established. */
  write(selection: SavedSelection): Promise<void>;
}
