/**
 * The bindings path rule (pure).
 *
 * A persisted source or destination path must be a canonical safe relative
 * POSIX path: no NUL, no backslash, no empty/`.`/`..` component, and no Windows
 * drive or root prefix. Nothing here touches the filesystem.
 */

/**
 * Return whether `path` is a canonical safe relative POSIX path.
 *
 * `.` and `..` are rejected as components rather than resolved, because a
 * persisted path is data an operator wrote down: rewriting it silently would
 * hide a malformed document instead of reporting one.
 */
export function isSafeRelativePath(path: string): boolean {
  if (path === "" || path.includes("\u0000") || path.includes("\\")) {
    return false;
  }
  if (path.split("/").some((part) => part === "" || part === "." || part === "..")) {
    return false;
  }
  const windowsPath = splitWindowsPrefix(path);
  return windowsPath === null;
}

/**
 * Return `null` when the path carries no Windows drive or root prefix.
 *
 * A drive prefix is exactly one ASCII letter followed by `:`. A root prefix is
 * a leading `/`, which the empty-component check already rejects, so the drive
 * form is the only additional shape this rule must recognise.
 */
function splitWindowsPrefix(path: string): string | null {
  const drive = /^[A-Za-z]:/u.exec(path);
  return drive === null ? null : drive[0];
}

/**
 * Return whether `path` is a POSIX- or Windows-absolute path.
 *
 * Used by the clearance registry's `region_files` members, which must be
 * root-relative but are not themselves required to be canonical.
 */
export function isAbsolutePath(path: string): boolean {
  return path.startsWith("/") || splitWindowsPrefix(path) !== null || path.startsWith("\\");
}
