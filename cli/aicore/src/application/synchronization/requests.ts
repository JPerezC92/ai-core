/**
 * What one synchronization command is asked to do.
 *
 * The four values every command needs, plus the editor profile the run acts
 * for; enrollment adds the declarations that only `init` accepts.
 */

import type { EditorProfile } from "#domain/synchronization/editor-profile.ts";

/** A read or write command's inputs. */
export type SynchronizationRequest = {
  readonly sourceRoot: string;
  readonly destinationRoot: string;
  readonly bindingsPath: string;
  readonly sourceRevision: string;
  /** The requested editor profile; absent leaves the destination's own choice. */
  readonly editor: EditorProfile | undefined;
};

/** An enrollment's inputs, including its declarations. */
export type EnrollmentRequest = SynchronizationRequest & {
  readonly regionDeclarations: readonly string[];
  readonly rawDeclarations: readonly string[];
  readonly bindCleared: boolean;
  readonly rootOverride: string | null;
};
