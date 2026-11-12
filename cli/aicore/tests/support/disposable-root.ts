/**
 * Shared fixture ownership for the CLI test suites.
 *
 * A disposable root is created by `mkdtemp`, so it is unique; this module also
 * records the requirement that a test deletes only what it created. Cleanup
 * refuses any path that is not inside the operating system's temporary
 * directory and does not carry the owning prefix, so a mistaken or refactored
 * path can never become a deletion target outside the fixture.
 *
 * Deliberately not a framework: two functions, no registry, no global state.
 */

import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { basename, join, resolve, sep } from "node:path";

/** Raised when a cleanup request names a path the fixture does not own. */
export class UnsafeCleanupTargetError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "UnsafeCleanupTargetError";
  }
}

/**
 * Return `true` only when `candidate` is strictly inside the OS temporary
 * directory and its own directory name starts with `prefix`.
 *
 * Both sides are resolved first, so a relative path, a traversal segment or a
 * differently-cased spelling cannot satisfy the check by accident.
 */
export function isOwnedTemporaryRoot(candidate: string, prefix: string): boolean {
  const temporaryRoot = resolve(tmpdir());
  const target = resolve(candidate);

  if (target === temporaryRoot) {
    return false;
  }
  if (!target.startsWith(`${temporaryRoot}${sep}`)) {
    return false;
  }
  return basename(target).startsWith(prefix);
}

/**
 * Create a disposable root the fixture owns.
 *
 * The prefix is retained on the returned record so cleanup can validate
 * ownership without the caller restating it.
 */
export async function createTemporaryRoot(
  prefix: string,
): Promise<{ readonly root: string; readonly prefix: string }> {
  const root = await mkdtemp(join(tmpdir(), prefix));
  return { root, prefix };
}

/**
 * Delete a disposable root this fixture created.
 *
 * Refuses any target that fails {@link isOwnedTemporaryRoot}. The check runs
 * immediately before deletion rather than at creation time, so a value mutated
 * in between is still caught.
 */
export async function disposeTemporaryRoot(
  root: string,
  prefix: string,
): Promise<void> {
  if (!isOwnedTemporaryRoot(root, prefix)) {
    throw new UnsafeCleanupTargetError(
      `refusing to delete a path this fixture does not own: ${resolve(root)} ` +
        `(expected a directory under ${resolve(tmpdir())} whose name starts with ${prefix})`,
    );
  }
  await rm(root, { recursive: true, force: true });
}
