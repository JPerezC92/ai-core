/**
 * What one synchronization command is asked to do.
 *
 * The four values every command needs; enrollment adds the declarations that
 * only `init` accepts.
 */

/** A read or write command's inputs. */
export type SynchronizationRequest = {
  readonly sourceRoot: string;
  readonly destinationRoot: string;
  readonly bindingsPath: string;
  readonly sourceRevision: string;
};

/** An enrollment's inputs, including its declarations. */
export type EnrollmentRequest = SynchronizationRequest & {
  readonly regionDeclarations: readonly string[];
  readonly rawDeclarations: readonly string[];
  readonly bindCleared: boolean;
  readonly rootOverride: string | null;
};
