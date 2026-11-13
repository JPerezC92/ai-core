/**
 * Infrastructure: the source-side clearance registry.
 *
 * The adapter reads the registry from the source root and maps its JSON text to
 * the domain's cleared entries. A registry that is present but unreadable answers
 * `entries: null` with `exists: true` and the reason it was rejected, so the
 * domain can distinguish "absent" (drift) from "malformed" (malformed input)
 * without guessing. The text is read by a strict JSON reader that reports a
 * repeated key instead of collapsing it, because two declarations of one path
 * are two conflicting declarations, not one record.
 */

import { readFile } from "node:fs/promises";
import { join } from "node:path";

import { CLEARANCE_FILENAME } from "#domain/synchronization/constants.ts";
import { parseClearanceDocument } from "#domain/synchronization/clearance.ts";
import type { ClearanceLoad, ClearanceStore } from "#domain/synchronization/ports.ts";

import { readJsonDocument } from "./json-document.ts";

export class JsonClearanceStore implements ClearanceStore {
  async load(sourceRoot: string): Promise<ClearanceLoad> {
    const path = join(sourceRoot, CLEARANCE_FILENAME);
    let text: string;
    try {
      text = await readFile(path, "utf8");
    } catch (error) {
      // Absence is drift and an unreadable file is malformed input; the domain
      // decides which, from the two facts this adapter reports.
      const code = (error as { code?: string }).code;
      return {
        entries: null,
        exists: code !== "ENOENT" && code !== "ENOTDIR",
        reason: null,
      };
    }
    const parsed = readJsonDocument(text);
    if (parsed.kind === "duplicate-key") {
      return {
        entries: null,
        exists: true,
        reason: `duplicate key in clearance document: ${parsed.key}`,
      };
    }
    if (parsed.kind === "malformed") {
      return { entries: null, exists: true, reason: "malformed clearance JSON" };
    }
    const clearance = parseClearanceDocument(parsed.value);
    return {
      entries: clearance.ok ? clearance.entries : null,
      exists: true,
      reason: clearance.ok ? null : clearance.reason,
    };
  }
}
