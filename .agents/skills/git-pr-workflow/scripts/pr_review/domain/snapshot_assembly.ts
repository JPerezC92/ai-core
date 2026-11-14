/** Reconcile supplied complete scanner snapshots to exact owner-supplied paths. */

import { SnapshotValidationError } from "#scripts/attribution_scan/domain/records.ts";
import type { Snapshot } from "#scripts/attribution_scan/domain/records.ts";
import { splitLines } from "#scripts/attribution_scan/domain/matching.ts";
import { validateSnapshot } from "#scripts/attribution_scan/domain/validation.ts";
import { ReviewPreparationError } from "./records.ts";
import type { LocalInventory } from "./records.ts";

/** The exact field set a local immutable inventory carries. */
const INVENTORY_KEYS = ["base", "changed_files", "commit_messages", "head_sha", "pr_number", "schema"];

/** The prefix a creation draft carries before its authored title. */
const TITLE_PREFIX = "Title: ";

/** Report whether a decoded value is a JSON object. */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Report whether two decoded path lists carry the same unique paths. */
function samePaths(left: ReadonlySet<string>, right: ReadonlySet<string>): boolean {
  if (left.size !== right.size) return false;
  for (const path of left) if (!right.has(path)) return false;
  return true;
}

/** Extract the authored title from a creation draft, or reject the draft. */
export function extractDraftTitle(draft: string): string | ReviewPreparationError {
  const firstLine = splitLines(draft)[0] ?? "";
  if (!firstLine.startsWith(TITLE_PREFIX)) {
    return new ReviewPreparationError(
      "DRAFT_INVALID",
      "creation draft must begin with a Title: line",
    );
  }
  return firstLine.slice(TITLE_PREFIX.length);
}

/** Validate unknown inventory and nested content through the scanner boundary. */
export function validateLocalInventory(value: unknown): LocalInventory | ReviewPreparationError {
  const error = new ReviewPreparationError(
    "SNAPSHOT_INVALID",
    "local immutable inventory required",
  );
  if (!isRecord(value)) return error;
  const keys = Object.keys(value).sort();
  if (keys.length !== INVENTORY_KEYS.length || !keys.every((key, index) => key === INVENTORY_KEYS[index])) {
    return error;
  }
  const commits = value["commit_messages"];
  if (
    !Array.isArray(commits) ||
    commits.some((commit) => !isRecord(commit) || commit["surface"] !== "commit-message")
  ) {
    return error;
  }
  const validated = validateSnapshot({
    schema: value["schema"],
    pr_number: value["pr_number"],
    head_sha: value["head_sha"],
    base: value["base"],
    artifacts: [
      { surface: "pr-title", source: "local title validation boundary", content: "" },
      { surface: "pr-body", source: "local body validation boundary", content: "" },
      ...commits,
    ],
    changed_files: value["changed_files"],
  });
  if (validated instanceof SnapshotValidationError) {
    return new ReviewPreparationError("SNAPSHOT_INVALID", validated.message);
  }
  return {
    schema: validated.schema,
    pr_number: validated.pr_number,
    head_sha: validated.head_sha,
    base: validated.base,
    commit_messages: validated.artifacts.slice(2),
    changed_files: validated.changed_files,
  };
}

/** Validate scanner shape and exact inventory, retaining deleted-file entries. */
export function assembleSnapshot(
  collected: unknown,
  exactPaths: unknown,
): Snapshot | ReviewPreparationError {
  const snapshot = validateSnapshot(collected);
  if (snapshot instanceof SnapshotValidationError) {
    return new ReviewPreparationError("SNAPSHOT_INVALID", snapshot.message);
  }
  if (
    !Array.isArray(exactPaths) ||
    !exactPaths.every((path): path is string => typeof path === "string")
  ) {
    return new ReviewPreparationError(
      "SNAPSHOT_PATHS_MISMATCH",
      "path inventory must be a string list",
    );
  }
  const paths = snapshot.changed_files.map((entry) => entry.path);
  const snapshotPaths = new Set(paths);
  const exact = new Set(exactPaths);
  if (
    snapshotPaths.size !== paths.length ||
    exact.size !== exactPaths.length ||
    !samePaths(snapshotPaths, exact)
  ) {
    return new ReviewPreparationError(
      "SNAPSHOT_PATHS_MISMATCH",
      "snapshot paths must equal the exact diff inventory",
    );
  }
  return snapshot;
}
