/**
 * The clearance registry: its version-1 schema, and directory-root expansion.
 *
 * A cleared path is a file record (`mode`, optional `role`) or a directory root (a
 * key ending in `/` with a default `mode` and optional root-relative
 * `region_files`). Expansion over enumerated paths is pure: the enumeration is
 * infrastructure's, the mode decision is this module's.
 */

import {
  BINDING_MODES,
  type BindingMode,
  CLEARANCE_SCHEMA,
  MODE_REGION,
  ROLE_ROOT,
} from "./constants.ts";
import { isAbsolutePath, isSafeRelativePath } from "./paths.ts";

/** One cleared source path with its mode and optional root role. */
export type ClearanceRecord = {
  readonly kind: "file";
  readonly mode: BindingMode;
  readonly role: typeof ROLE_ROOT | null;
};

/** One cleared directory root: a default mode plus root-relative region files. */
export type ClearanceDirectoryRoot = {
  readonly kind: "directory-root";
  readonly mode: BindingMode;
  readonly regionFiles: readonly string[];
};

/** One cleared entry of the registry. */
export type ClearanceEntry = ClearanceRecord | ClearanceDirectoryRoot;

/** A parsed registry, or the reason it is unreadable. */
export type ClearanceParse =
  | { readonly ok: true; readonly entries: ReadonlyMap<string, ClearanceEntry> }
  | { readonly ok: false; readonly reason: string };

const RECORD_FIELDS: ReadonlySet<string> = new Set(["mode", "role"]);
const DIRECTORY_ROOT_FIELDS: ReadonlySet<string> = new Set(["mode", "region_files"]);
const DOCUMENT_FIELDS: ReadonlySet<string> = new Set(["schema", "cleared"]);

/**
 * Validate a parsed clearance registry.
 *
 * Only the current schema label is accepted; there is no legacy or migration
 * path. Every unknown field, invalid mode, unsafe path, second root role or
 * mis-scoped `region_files` member is reported as unreadable, so a partially
 * understood registry is never used to decide what ships.
 */
export function parseClearanceDocument(data: unknown): ClearanceParse {
  if (!isRecord(data)) {
    return { ok: false, reason: "clearance document must be a JSON object" };
  }
  const schema = data["schema"];
  if (typeof schema !== "number" || !Number.isInteger(schema)) {
    return { ok: false, reason: `clearance schema must be an integer: ${String(schema)}` };
  }
  if (schema !== CLEARANCE_SCHEMA) {
    return {
      ok: false,
      reason: `unsupported clearance schema: ${String(schema)} (expected ${String(CLEARANCE_SCHEMA)})`,
    };
  }
  const unknownDocumentField = Object.keys(data).find((key) => !DOCUMENT_FIELDS.has(key));
  if (unknownDocumentField !== undefined) {
    return { ok: false, reason: `clearance document has unknown fields: ${unknownDocumentField}` };
  }
  const rawCleared = data["cleared"];
  if (!isRecord(rawCleared)) {
    return { ok: false, reason: "clearance 'cleared' must be a path-keyed JSON object" };
  }

  const entries = new Map<string, ClearanceEntry>();
  let rootPath: string | null = null;
  for (const [path, rawRecord] of Object.entries(rawCleared)) {
    const parsed = path.endsWith("/")
      ? readDirectoryRoot(path, rawRecord)
      : readRecord(path, rawRecord);
    if (typeof parsed === "string") {
      return { ok: false, reason: parsed };
    }
    if (parsed.kind === "file" && parsed.role === ROLE_ROOT) {
      if (rootPath !== null) {
        return { ok: false, reason: `multiple root roles: ${rootPath} and ${path}` };
      }
      rootPath = path;
    }
    entries.set(path, parsed);
  }
  return { ok: true, entries };
}

/**
 * Map every cleared path, and every enumerated file under a cleared directory
 * root, to its distribution mode.
 *
 * A `region_files` member delivers its core region; every other enumerated file
 * under that root uses the root's default mode. Interpreter caches never join.
 */
export function expandClearance(
  entries: ReadonlyMap<string, ClearanceEntry>,
  enumerated: ReadonlyMap<string, readonly string[]>,
): ReadonlyMap<string, BindingMode> {
  const modes = new Map<string, BindingMode>();
  for (const [path, entry] of entries) {
    if (entry.kind === "file") {
      modes.set(path, entry.mode);
      continue;
    }
    const regionFiles = new Set(entry.regionFiles);
    for (const relativePath of enumerated.get(path) ?? []) {
      if (isInterpreterCache(relativePath)) {
        continue;
      }
      modes.set(path + relativePath, regionFiles.has(relativePath) ? MODE_REGION : entry.mode);
    }
  }
  return modes;
}

function readRecord(path: string, rawRecord: unknown): ClearanceRecord | string {
  if (!isSafeRelativePath(path)) {
    return `cleared path is not a safe relative path: ${path}`;
  }
  if (!isRecord(rawRecord)) {
    return `cleared record for ${path} must be a JSON object`;
  }
  const unknown = Object.keys(rawRecord).find((key) => !RECORD_FIELDS.has(key));
  if (unknown !== undefined) {
    return `cleared record for ${path} has an unknown field: ${unknown}`;
  }
  const mode = BINDING_MODES.find((candidate) => candidate === rawRecord["mode"]);
  if (mode === undefined) {
    return `cleared record for ${path} requires mode in ${BINDING_MODES.join(", ")}`;
  }
  const rawRole = rawRecord["role"];
  if (rawRole !== undefined && rawRole !== ROLE_ROOT) {
    return `cleared record for ${path} has an invalid role: ${String(rawRole)}`;
  }
  if (rawRole === ROLE_ROOT && mode !== MODE_REGION) {
    return `root role for ${path} must use region mode`;
  }
  return { kind: "file", mode, role: rawRole === ROLE_ROOT ? ROLE_ROOT : null };
}

function readDirectoryRoot(path: string, rawRecord: unknown): ClearanceDirectoryRoot | string {
  if (!path.endsWith("/") || !isSafeRelativePath(path.slice(0, -1))) {
    return `directory-root key is not a safe relative directory path: ${path}`;
  }
  if (!isRecord(rawRecord)) {
    return `cleared record for ${path} must be a JSON object`;
  }
  const unknown = Object.keys(rawRecord).find((key) => !DIRECTORY_ROOT_FIELDS.has(key));
  if (unknown !== undefined) {
    return `cleared record for ${path} has an unknown field: ${unknown}`;
  }
  const mode = BINDING_MODES.find((candidate) => candidate === rawRecord["mode"]);
  if (mode === undefined) {
    return `cleared record for ${path} requires mode in ${BINDING_MODES.join(", ")}`;
  }
  const rawRegionFiles = rawRecord["region_files"] ?? [];
  if (!Array.isArray(rawRegionFiles)) {
    return `directory-root entry for ${path} requires a region_files list`;
  }
  const regionFiles: string[] = [];
  for (const member of rawRegionFiles) {
    if (typeof member !== "string") {
      return `directory-root entry for ${path} has a non-string region_files member`;
    }
    if (member === "") {
      return `directory-root entry for ${path} has an empty region_files member`;
    }
    if (member.split("/").includes("..") || isAbsolutePathLike(member)) {
      return `region_files member contains '..' or is absolute: ${member}`;
    }
    if (!isSafeRelativePath(member)) {
      return `region_files member is not under directory root ${path}: ${member}`;
    }
    regionFiles.push(member);
  }
  return { kind: "directory-root", mode, regionFiles };
}

function isAbsolutePathLike(path: string): boolean {
  return isAbsolutePath(path);
}

function isInterpreterCache(path: string): boolean {
  return path.split("/").includes("__pycache__") || path.endsWith(".pyc");
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
