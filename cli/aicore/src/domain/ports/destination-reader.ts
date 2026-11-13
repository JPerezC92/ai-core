/**
 * Domain port: reading a destination's files.
 *
 * Read-only by construction. A reconciliation proposal compares what a
 * destination holds with what its sources declare, so it is given a capability
 * that cannot write, create or delete anything under the destination. The
 * engine's wider `DestinationFiles` satisfies this port structurally.
 */

export interface DestinationReader {
  /** Read a file as UTF-8 text without newline translation; `null` when absent. */
  readText(path: string): Promise<string | null>;
  /** Read a file's bytes verbatim, or `null` when absent. */
  readBytes(path: string): Promise<Uint8Array | null>;
}
