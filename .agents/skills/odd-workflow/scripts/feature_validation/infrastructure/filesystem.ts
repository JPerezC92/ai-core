/** Read feature candidates and strict UTF-8 contents from the local filesystem. */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, normalize, parse, sep } from "node:path";
import { TextDecoder } from "node:util";
import type { FeatureSource } from "#scripts/feature_validation/domain/ports.ts";

function normalizeReference(reference: string): string {
  const normalized = normalize(reference);
  const root = parse(normalized).root;
  if (!root && normalized === ".") return normalized;
  if (normalized === root) return normalized;
  return normalized.replace(new RegExp(`${sep.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&")}{1,}$`, "u"), "");
}

function isDirectory(target: string): boolean {
  try {
    return statSync(target).isDirectory();
  } catch {
    // Path.is_dir() reports false on stat errors; the subsequent read preserves the IO failure.
    return false;
  }
}

export class FilesystemFeatureSource implements FeatureSource {
  discover(target: string): string[] {
    if (isDirectory(target)) {
      const caseInsensitive = process.platform === "win32";
      return readdirSync(target)
        .filter((name) =>
          caseInsensitive ? name.toLowerCase().endsWith(".md") : name.endsWith(".md"),
        )
        .map((name) => normalizeReference(join(target, name)));
    }
    return [normalizeReference(target)];
  }

  read(reference: string): string {
    return new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(
      readFileSync(reference),
    );
  }
}
