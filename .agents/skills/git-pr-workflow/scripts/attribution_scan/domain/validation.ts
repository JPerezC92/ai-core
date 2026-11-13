/** Validate decoded attribution inputs with returned business-error values. */

import { PolicyValidationError, SnapshotValidationError } from "./records.ts";
import type { AttributionPolicy, Snapshot } from "./records.ts";

/** The only hexadecimal run a head object id may carry. */
const HEAD_SHA_PATTERN = /^[0-9a-fA-F]{7,64}$/u;

/** The three artifact surfaces a complete snapshot may carry. */
const ARTIFACT_SURFACES = ["pr-title", "pr-body", "commit-message"] as const;

/** The same surfaces as a membership test that accepts any decoded string. */
const ARTIFACT_SURFACE_SET: ReadonlySet<string> = new Set(ARTIFACT_SURFACES);

/** Report whether a decoded value is a JSON object. */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Report whether a decoded value is a whole number. */
function isWholeNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value);
}

/** Report whether a decoded value is a list of strings. */
function isStringList(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

/** Return the drive or UNC prefix a path carries, or an empty string. */
function windowsDrive(path: string): string {
  const unc = /^[\\/]{2}[^\\/]+/u.exec(path);
  if (unc) return unc[0] ?? "";
  const drive = /^[A-Za-z]:/u.exec(path);
  return drive?.[0] ?? "";
}

/** Report whether a path stays inside the repository root. */
function isRootRelativePath(path: string): boolean {
  const normalized = path.replace(/\\/gu, "/");
  if (normalized.startsWith("/")) return false;
  if (windowsDrive(path) !== "") return false;
  return !normalized.split("/").includes("..");
}

/** Validate a decoded policy without performing filesystem access. */
export function validatePolicy(value: unknown): AttributionPolicy | PolicyValidationError {
  if (!isRecord(value)) return new PolicyValidationError("policy must be a JSON object");
  if (!isWholeNumber(value["schema"]) || value["schema"] !== 1) {
    return new PolicyValidationError("policy schema must be 1");
  }
  const excluded = value["self_excluded_file"];
  if (typeof excluded !== "string" || excluded === "") {
    return new PolicyValidationError("policy self_excluded_file must be a non-empty string");
  }
  const groups: ReadonlyArray<readonly [string, unknown]> = [
    ["markers", value["markers"]],
    ["identities", value["identities"]],
  ];
  for (const [name, entries] of groups) {
    if (!isStringList(entries) || entries.length === 0) {
      return new PolicyValidationError(`policy ${name} must be a non-empty string list`);
    }
    if (entries.some((entry) => entry === "" || entry !== entry.trim())) {
      return new PolicyValidationError(`policy ${name} entries must be non-empty and trimmed`);
    }
    const folded = entries.map((entry) => entry.toLowerCase());
    if (new Set(folded).size !== folded.length) {
      return new PolicyValidationError(`policy ${name} entries must be unique ignoring case`);
    }
  }
  return value as unknown as AttributionPolicy;
}

/** Validate snapshot completeness and shape without performing IO. */
export function validateSnapshot(value: unknown): Snapshot | SnapshotValidationError {
  if (!isRecord(value)) return new SnapshotValidationError("snapshot must be a JSON object");
  if (!isWholeNumber(value["schema"]) || value["schema"] !== 1) {
    return new SnapshotValidationError("snapshot schema must be 1");
  }
  const prNumber = value["pr_number"];
  if (!isWholeNumber(prNumber) || prNumber < 1) {
    return new SnapshotValidationError("snapshot pr_number must be a positive integer");
  }
  const headSha = value["head_sha"];
  if (typeof headSha !== "string" || !HEAD_SHA_PATTERN.test(headSha)) {
    return new SnapshotValidationError(
      "snapshot head_sha must contain 7 to 64 hexadecimal characters",
    );
  }
  const base = value["base"];
  if (typeof base !== "string" || base.trim() === "") {
    return new SnapshotValidationError("snapshot base must be a non-empty string");
  }

  const artifacts = value["artifacts"];
  if (!Array.isArray(artifacts)) {
    return new SnapshotValidationError("snapshot artifacts must be a list");
  }
  const surfaces = new Map<string, number>(ARTIFACT_SURFACES.map((surface) => [surface, 0]));
  for (const artifact of artifacts) {
    if (!isRecord(artifact)) {
      return new SnapshotValidationError("each artifact must be a JSON object");
    }
    const surface = artifact["surface"];
    const source = artifact["source"];
    const content = artifact["content"];
    if (typeof surface !== "string" || !ARTIFACT_SURFACE_SET.has(surface)) {
      return new SnapshotValidationError(
        "artifact surface must be pr-title, pr-body, or commit-message",
      );
    }
    if (typeof source !== "string" || source.trim() === "") {
      return new SnapshotValidationError("artifact source must be a non-empty string");
    }
    if (typeof content !== "string") {
      return new SnapshotValidationError("artifact content must be a string");
    }
    surfaces.set(surface, (surfaces.get(surface) ?? 0) + 1);
  }
  if (
    surfaces.get("pr-title") !== 1 ||
    surfaces.get("pr-body") !== 1 ||
    (surfaces.get("commit-message") ?? 0) < 1
  ) {
    return new SnapshotValidationError(
      "snapshot requires one PR title, one PR body, and at least one commit message",
    );
  }

  const changedFiles = value["changed_files"];
  if (!Array.isArray(changedFiles)) {
    return new SnapshotValidationError("snapshot changed_files must be a list");
  }
  if (changedFiles.length === 0) {
    return new SnapshotValidationError("snapshot requires at least one changed-file body");
  }
  for (const changedFile of changedFiles) {
    if (!isRecord(changedFile)) {
      return new SnapshotValidationError("each changed file must be a JSON object");
    }
    const path = changedFile["path"];
    const content = changedFile["content"];
    if (typeof path !== "string" || path === "" || !isRootRelativePath(path)) {
      return new SnapshotValidationError(
        "changed-file path must be a non-empty root-relative path without parent traversal",
      );
    }
    if (typeof content !== "string") {
      return new SnapshotValidationError("changed-file content must be a string");
    }
  }
  return value as unknown as Snapshot;
}
