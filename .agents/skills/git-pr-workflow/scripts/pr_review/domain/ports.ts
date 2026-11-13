/** Declare the domain ports the review preparation operations depend on. */

/** The read-only Git inventory this operation depends on. */
export interface GitInventoryPort {
  /** Return the object id a revision resolves to, or absence. */
  resolveCommit(revision: string): string | null;
  /** Return the common ancestor of two revisions, or absence. */
  mergeBase(first: string, second: string): string | null;
  /** Return the commit ids contained between an ancestor and a head commit. */
  listCommits(ancestor: string, head: string): readonly string[];
  /** Return one commit message. */
  readMessage(commit: string): string;
  /** Return the exact changed path inventory, including deleted paths. */
  listChangedPaths(ancestor: string, head: string): readonly string[];
  /** Return the paths the range deletes, so no body is read for them. */
  listDeletedPaths(ancestor: string, head: string): readonly string[];
  /** Return one file body as committed at the supplied commit. */
  readFile(commit: string, path: string): string;
}
