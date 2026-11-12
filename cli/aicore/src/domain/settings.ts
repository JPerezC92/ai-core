/**
 * Domain: operator-supplied settings.
 *
 * One typed record rather than the raw process environment, so the domain never
 * carries an external representation (architecture contract C2).
 */

export type OperatorSettings = {
  /** Revision supplied by the operator or release owner; never Git-derived. */
  readonly sourceRevision: string | undefined;
  /** Explicit override for the operator-local selection file's location. */
  readonly localConfigPath: string | undefined;
};
