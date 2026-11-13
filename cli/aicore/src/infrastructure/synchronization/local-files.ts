/**
 * Infrastructure: local file IO at the engine's boundary.
 *
 * One place owns the write contract: text is written UTF-8 with LF terminators
 * only, while bytes are written exactly as given, so a raw payload is never
 * line-ending transformed. A read that cannot be performed answers `null`; only
 * genuine absence is `null`, and every other failure propagates as a boundary
 * exception (C5).
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname } from "node:path";

/** Read a file as UTF-8 text without newline translation, or `null`. */
export async function readTextFile(path: string): Promise<string | null> {
  try {
    return await readFile(path, "utf8");
  } catch (error) {
    if (isUnreadableAsFile(error)) {
      return null;
    }
    throw error;
  }
}

/** Read a file's bytes verbatim, or `null`. */
export async function readBytesFile(path: string): Promise<Uint8Array | null> {
  try {
    return await readFile(path);
  } catch (error) {
    if (isUnreadableAsFile(error)) {
      return null;
    }
    throw error;
  }
}

/**
 * Write UTF-8 text, terminating every line in LF.
 *
 * This is the engine's single line-ending normalization point: `\r\n` and any
 * surviving lone `\r` become `\n` before the write.
 */
export async function writeTextFile(path: string, content: string): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, content.replaceAll("\r\n", "\n").replaceAll("\r", "\n"), "utf8");
}

/** Write bytes exactly as given, creating the parent directory when absent. */
export async function writeBytesFile(path: string, content: Uint8Array): Promise<void> {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, content);
}

/** Create a directory and any missing parent. */
export async function ensureDirectory(path: string): Promise<void> {
  await mkdir(path, { recursive: true });
}

/** Return whether a `readFile`/`stat` failure means "the path is not there". */
export function isMissing(error: unknown): boolean {
  const code = (error as { code?: string }).code;
  return code === "ENOENT" || code === "ENOTDIR";
}

/**
 * The codes the platform raises when the filesystem itself refuses an
 * operation — the failure class the reference engine handles as an I/O result.
 */
const FILE_SYSTEM_ERROR_CODES: ReadonlySet<string> = new Set([
  "EACCES",
  "EBUSY",
  "EDQUOT",
  "EIO",
  "EISDIR",
  "ELOOP",
  "EMFILE",
  "ENAMETOOLONG",
  "ENFILE",
  "ENOENT",
  "ENOSPC",
  "ENOTDIR",
  "ENOTEMPTY",
  "EOVERFLOW",
  "EPERM",
  "EROFS",
  "ETXTBSY",
  "EXDEV",
]);

/**
 * Return whether a failure is a genuine filesystem condition.
 *
 * A failure outside this set (a `TypeError`, a range or shape fault) is a
 * programming fault and must surface as one, never as a business outcome (C5).
 */
export function isFileSystemError(error: unknown): boolean {
  const code = (error as { code?: unknown }).code;
  return typeof code === "string" && FILE_SYSTEM_ERROR_CODES.has(code);
}

/**
 * Return whether a read failure means "this path is not a readable file".
 *
 * A directory where a file is expected reads as nothing rather than crashing the
 * command, so the caller reports the destination it could not read instead of a
 * transport fault.
 */
function isUnreadableAsFile(error: unknown): boolean {
  return isMissing(error) || (error as { code?: string }).code === "EISDIR";
}
