/** Read task-record candidates and strict UTF-8 contents from the local filesystem. */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, normalize } from "node:path";
import { TextDecoder } from "node:util";
import type { RetirementSource } from "#scripts/retirement_check/domain/ports.ts";

function isDirectory(target: string): boolean {
  try {
    return statSync(target).isDirectory();
  } catch {
    // The subsequent read preserves the IO failure for the caller.
    return false;
  }
}

export class FilesystemRetirementSource implements RetirementSource {
  discover(target: string): string[] {
    if (!isDirectory(target)) return [normalize(target)];
    return readdirSync(target)
      .filter((name) => name.toLowerCase().endsWith(".md"))
      .map((name) => normalize(join(target, name)));
  }

  read(reference: string): string {
    return new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(
      readFileSync(reference),
    );
  }
}
