/**
 * Infrastructure: path and layout questions about the two roots.
 *
 * Path composition, the root runtime file's resolution, directory enumeration
 * and the blocker write live here; what the blocker says and how a file is
 * spliced stay in the domain.
 */

import { readdir, stat } from "node:fs/promises";
import { dirname, join, relative, sep } from "node:path";

import { ROOT_CANDIDATES } from "#domain/synchronization/constants.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import { effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import { syncReconciliationBlocker } from "#domain/synchronization/reconciliation.ts";
import type { FilesystemLayout } from "#domain/synchronization/ports.ts";

import { ensureDirectory, isMissing, readTextFile, writeTextFile } from "./local-files.ts";

/** A path's kind, as the preflight and the readers need to know it. */
export type PathKind = "absent" | "file" | "other";

export class LocalFilesystemLayout implements FilesystemLayout {
  async exists(path: string): Promise<boolean> {
    return (await readKind(path)) !== "absent";
  }

  async isFile(path: string): Promise<boolean> {
    return (await readKind(path)) === "file";
  }

  async ensureDirectory(path: string): Promise<void> {
    await ensureDirectory(path);
  }

  join(root: string, relativePath: string): string {
    return relativePath === "" ? root : join(root, relativePath);
  }

  parent(path: string): string {
    return dirname(path);
  }

  async enumerateFilesUnder(root: string): Promise<readonly string[]> {
    const collected: string[] = [];
    if (!(await this.exists(root))) {
      return collected;
    }
    const walk = async (current: string): Promise<void> => {
      for (const entry of await readdir(current, { withFileTypes: true })) {
        const absolute = join(current, entry.name);
        if (entry.isDirectory()) {
          if (entry.name === "__pycache__") {
            continue;
          }
          await walk(absolute);
          continue;
        }
        if (entry.name.endsWith(".pyc")) {
          continue;
        }
        collected.push(relative(root, absolute).split(sep).join("/"));
      }
    };
    await walk(root);
    return collected.sort();
  }

  async resolveRootFile(
    destinationRoot: string,
    document: BindingsDocument,
  ): Promise<string> {
    if (document.root !== null) {
      return join(destinationRoot, document.root);
    }
    const detected = await this.detectRootFile(destinationRoot);
    if (detected !== null) {
      return join(destinationRoot, detected);
    }
    return join(
      destinationRoot,
      ROOT_CANDIDATES[ROOT_CANDIDATES.length - 1] ?? "instructions.md",
    );
  }

  async detectRootFile(destinationRoot: string): Promise<string | null> {
    for (const candidate of ROOT_CANDIDATES) {
      if ((await readKind(join(destinationRoot, candidate))) === "file") {
        return candidate;
      }
    }
    return null;
  }

  async syncBlocker(
    destinationRoot: string,
    document: BindingsDocument,
    pending: readonly string[],
  ): Promise<void> {
    const rootPath = await this.resolveRootFile(destinationRoot, document);
    const text = await readTextFile(rootPath);
    if (text === null) {
      return;
    }
    const next = syncReconciliationBlocker(
      text,
      pending,
      effectiveEditor(undefined, document.editor),
    );
    if (next !== text) {
      await writeTextFile(rootPath, next);
    }
  }
}

/** Read a path's kind: absent, a regular file, or something else. */
export async function readKind(path: string): Promise<PathKind> {
  try {
    const observed = await stat(path);
    return observed.isFile() ? "file" : "other";
  } catch (error) {
    if (isMissing(error)) {
      return "absent";
    }
    throw error;
  }
}
