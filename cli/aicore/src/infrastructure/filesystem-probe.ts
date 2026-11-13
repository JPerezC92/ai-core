/**
 * Infrastructure: filesystem probes used to resolve paths.
 *
 * Read-only. No function here creates, modifies, or deletes anything; a
 * destination is never touched by a probe.
 */

import { stat } from "node:fs/promises";
import { resolve, sep } from "node:path";

import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";

/**
 * Report whether a `stat` failure means "the path is not there".
 *
 * Only genuine absence is answered with `false`. Every other failure — a
 * permission denial, a symlink loop, a too-long name, an exhausted descriptor
 * table — propagates as a boundary exception (contract C5), because collapsing
 * it into "absent" would let the caller choose an enrollment mode for a
 * destination it could not actually read.
 */
function isAbsent(error: unknown): boolean {
  const code = (error as { code?: string }).code;
  return code === "ENOENT" || code === "ENOTDIR";
}

export class LocalFilesystemProbe implements FilesystemProbe {
  resolve(path: string): string {
    return resolve(path);
  }

  async isDirectory(path: string): Promise<boolean> {
    try {
      return (await stat(path)).isDirectory();
    } catch (error) {
      if (isAbsent(error)) {
        return false;
      }
      throw error;
    }
  }

  async isFile(path: string): Promise<boolean> {
    try {
      return (await stat(path)).isFile();
    } catch (error) {
      if (isAbsent(error)) {
        return false;
      }
      throw error;
    }
  }

  isInside(root: string, path: string): boolean {
    const normalizedRoot = resolve(root);
    const normalizedPath = resolve(path);
    return (
      normalizedPath === normalizedRoot ||
      normalizedPath.startsWith(`${normalizedRoot}${sep}`)
    );
  }
}
