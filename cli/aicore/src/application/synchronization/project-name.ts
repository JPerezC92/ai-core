/**
 * The destination's own folder name.
 *
 * Merge mode registers it as the `qmd` server's `--index` argument, on every
 * `mcp` write path and in the comparison, so each destination retrieves with its
 * own index and a renamed folder retargets on the next synchronization.
 */

/** Return the last path component of a destination root. */
export function projectName(destinationRoot: string): string {
  const normalized = destinationRoot.replaceAll("\\", "/").replace(/\/+$/u, "");
  const separator = normalized.lastIndexOf("/");
  return separator === -1 ? normalized : normalized.slice(separator + 1);
}
