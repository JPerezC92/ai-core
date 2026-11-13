/**
 * Infrastructure: the read-only source tree.
 *
 * A source's core is read as UTF-8 text without newline translation, so the
 * marker rule sees the file's own bytes; raw sources are read as bytes and never
 * decoded, and nothing here writes to the source.
 */

import { extractSourceCore } from "#domain/synchronization/regions.ts";
import type { SourceCoreRead } from "#domain/synchronization/regions.ts";
import type { SourceFiles } from "#domain/synchronization/ports.ts";

import { readBytesFile, readTextFile } from "./local-files.ts";

export class LocalSourceFiles implements SourceFiles {
  async readCore(path: string): Promise<SourceCoreRead | null> {
    const text = await readTextFile(path);
    if (text === null) {
      return null;
    }
    return extractSourceCore(text);
  }

  async readBytes(path: string): Promise<Uint8Array | null> {
    return readBytesFile(path);
  }

  async readText(path: string): Promise<string | null> {
    return readTextFile(path);
  }
}
