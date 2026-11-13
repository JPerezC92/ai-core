/**
 * Infrastructure: the destination's files.
 *
 * Text is written with LF terminators; bytes are written exactly as given, so a
 * raw payload keeps its own line endings.
 */

import type { DestinationFiles } from "#domain/synchronization/ports.ts";

import { readBytesFile, readTextFile, writeBytesFile, writeTextFile } from "./local-files.ts";

export class LocalDestinationFiles implements DestinationFiles {
  async readText(path: string): Promise<string | null> {
    return readTextFile(path);
  }

  async readBytes(path: string): Promise<Uint8Array | null> {
    return readBytesFile(path);
  }

  async writeText(path: string, content: string): Promise<void> {
    await writeTextFile(path, content);
  }

  async writeBytes(path: string, content: Uint8Array): Promise<void> {
    await writeBytesFile(path, content);
  }
}
