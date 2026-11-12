/**
 * Domain port: filesystem questions about a destination.
 *
 * Read-only. One capability per module (P4, C2).
 */

export interface FilesystemProbe {
  /** Resolve a supplied path against the current directory. */
  resolve(path: string): string;
  /** Report whether the path exists and is a directory. */
  isDirectory(path: string): Promise<boolean>;
  /** Report whether the path exists as a regular file. */
  isFile(path: string): Promise<boolean>;
  /** Report whether the path is inside the AICore checkout root. */
  isInside(root: string, path: string): boolean;
}
