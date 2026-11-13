/**
 * Domain port: the path and file-tree questions a reconciliation proposal asks.
 *
 * Read-only by construction. Path composition, file existence and enumeration
 * over one root are all an inspection needs; ensuring a directory and rewriting
 * a blocker are not capabilities this operation may hold, because a proposal
 * changes nothing under the destination. The engine's wider `FilesystemLayout`
 * satisfies this port structurally.
 */

export interface PathInspection {
  /** Report whether the path exists as a regular file. */
  isFile(path: string): Promise<boolean>;
  /** Join a relative POSIX path onto a root path. */
  join(root: string, relative: string): string;
  /** Every regular file under `root`, as root-relative POSIX paths. */
  enumerateFilesUnder(root: string): Promise<readonly string[]>;
}
