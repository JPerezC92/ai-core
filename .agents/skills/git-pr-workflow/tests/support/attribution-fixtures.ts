/** Factories for attribution scanner test data and policy-derived test lines. */

import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type {
  Artifact,
  AttributionPolicy,
  ChangedFile,
  Snapshot,
} from "#scripts/attribution_scan/domain/records.ts";
import { PolicyValidationError } from "#scripts/attribution_scan/domain/records.ts";
import { validatePolicy } from "#scripts/attribution_scan/domain/validation.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

/** The head object id every synthetic fixture carries. */
const HEAD_SHA = "a".repeat(40);

/**
 * Load the checked-in policy as a test input.
 *
 * A broken approved-policy fixture fails here instead of surfacing as an
 * unrelated rejection assertion in the cases that use it.
 */
export function loadApprovedPolicy(): AttributionPolicy {
  const policyPath = resolve(skillRoot, "references", "_attribution-patterns.json");
  const value: unknown = JSON.parse(readFileSync(policyPath, "utf8"));
  const policy = validatePolicy(value);
  if (policy instanceof PolicyValidationError) {
    throw new Error("the approved attribution policy must validate");
  }
  return policy;
}

/** Build a synthetic policy whose values carry no approved policy text. */
export function makeSyntheticPolicy(): AttributionPolicy {
  return {
    schema: 1,
    self_excluded_file: "policy.json",
    markers: ["Synthetic attribution:"],
    identities: ["Synthetic author"],
  };
}

/** Build a synthetic policy whose identity distinguishes lowercasing from case folding. */
export function makeCaseFoldedIdentityPolicy(): AttributionPolicy {
  return { ...makeSyntheticPolicy(), identities: ["Straße"] };
}

/**
 * Build the full-case-folded spelling of a matching line.
 *
 * Full case folding maps `ß` to `ss`, so this line differs from the policy
 * identity only where lowercasing and full folding diverge.
 */
export function makeCaseFoldedAttributionLine(policy: AttributionPolicy): string {
  const marker = policy.markers[0];
  if (marker === undefined) throw new Error("the synthetic policy carries no marker");
  return `${marker} STRASSE`;
}

/** Build a matching line from approved values without embedding policy text. */
export function makeAttributionLine(
  policy: AttributionPolicy,
  markerIndex = 0,
  identityIndex = 0,
): string {
  const marker = policy.markers[markerIndex];
  const identity = policy.identities[identityIndex];
  if (marker === undefined || identity === undefined) {
    throw new Error("the approved policy carries no such marker or identity");
  }
  return `${marker} ${identity}`;
}

/** Build prose mentioning a policy identity without an attribution marker. */
export function makeOrdinaryIdentityMention(policy: AttributionPolicy): string {
  const identity = policy.identities[0];
  if (identity === undefined) throw new Error("the approved policy carries no identity");
  return `Documentation mentions ${identity} here.`;
}

/** Swap the case of every ASCII letter, so a matching line differs in case only. */
function swapCase(text: string): string {
  return text.replace(/[a-zA-Z]/gu, (character) =>
    character === character.toLowerCase() ? character.toUpperCase() : character.toLowerCase(),
  );
}

/** Build artifact and file bodies with a matching line at known positions. */
export function makeMultilineMatchingContents(policy: AttributionPolicy): {
  artifactContent: string;
  fileContent: string;
} {
  const line = swapCase(makeAttributionLine(policy));
  return { artifactContent: `intro\n\n${line}`, fileContent: `first\n${line}` };
}

/** Build one typed changed-file entry for a scanner snapshot. */
export function makeChangedFile(path = "README.md", content = ""): ChangedFile {
  return { path, content };
}

/** Collect changed-file entries without inline snapshot payloads in tests. */
export function makeChangedFiles(...entries: ChangedFile[]): ChangedFile[] {
  return [...entries];
}

/** Build a typed baseline snapshot for scanner tests. */
export function makeSnapshot(
  changedFiles: readonly ChangedFile[] = [],
  artifactContent?: { readonly surface: string; readonly content: string },
): Snapshot {
  const artifacts: Array<{ surface: string; source: string; content: string }> = [
    { surface: "pr-title", source: "PR #80 title", content: "Routine update" },
    { surface: "pr-body", source: "PR #80 body", content: "" },
    { surface: "commit-message", source: HEAD_SHA, content: "Routine update" },
  ];
  if (artifactContent !== undefined) {
    for (const artifact of artifacts) {
      if (artifact.surface === artifactContent.surface) {
        artifact.content = artifactContent.content;
        break;
      }
    }
  }
  return {
    schema: 1,
    pr_number: 80,
    head_sha: HEAD_SHA,
    base: "origin/main",
    artifacts,
    changed_files: [...changedFiles],
  };
}

/** Return a valid snapshot with one empty changed-file body. */
export function makeCompleteSnapshot(): Snapshot {
  return makeSnapshot(makeChangedFiles(makeChangedFile()));
}

/** Build a snapshot with one selected artifact body replaced. */
export function makeSnapshotWithArtifactContent(
  surface: string,
  content: string,
  changedFiles: readonly ChangedFile[] = [],
): Snapshot {
  return makeSnapshot(changedFiles, { surface, content });
}

/** Build a structurally valid snapshot missing the required file body. */
export function makeSnapshotWithoutChangedFiles(): Snapshot {
  return makeSnapshot([]);
}

/**
 * Build snapshot JSON text whose schema is written as `1.0`.
 *
 * A serializer cannot express a floating-point schema, so the documented
 * input-shape case writes the raw text instead.
 */
export function makeFloatSchemaSnapshotText(): string {
  const text = JSON.stringify(makeCompleteSnapshot()).replace('"schema":1', '"schema":1.0');
  if (!text.includes('"schema":1.0')) {
    throw new Error("the raw snapshot text must carry a floating-point schema");
  }
  return text;
}

/** Build a snapshot whose schema value is not the documented whole number. */
export function makeWrongSchemaSnapshot(): Record<string, unknown> {
  return { ...makeSnapshot(makeChangedFiles(makeChangedFile())), schema: 2 };
}

/** Build a snapshot that repeats the PR title and omits the PR body. */
export function makeUnbalancedSurfaceSnapshot(): Record<string, unknown> {
  return {
    ...makeSnapshot(makeChangedFiles(makeChangedFile())),
    artifacts: [
      { surface: "pr-title", source: "PR #80 title", content: "Routine update" },
      { surface: "pr-title", source: "PR #80 title copy", content: "Routine update" },
      { surface: "commit-message", source: HEAD_SHA, content: "Routine update" },
    ],
  };
}

/** Build a snapshot whose named collection is not a JSON list. */
export function makeNonListCollectionSnapshot(
  field: "artifacts" | "changed_files",
): Record<string, unknown> {
  return { ...makeSnapshot(makeChangedFiles(makeChangedFile())), [field]: "not a list" };
}

/** Build a malformed JSON object whose first artifact content is not a string. */
export function makeMalformedContentSnapshot(): Record<string, unknown> {
  const snapshot = makeSnapshot(makeChangedFiles(makeChangedFile())) as unknown as Record<
    string,
    unknown
  >;
  const artifacts = snapshot["artifacts"] as Array<Record<string, unknown>>;
  const first = artifacts[0];
  if (first === undefined) throw new Error("the malformed snapshot carries no artifact");
  first["content"] = ["not", "text"];
  return snapshot;
}

/** Build an intentionally malformed JSON object for input-validation checks. */
export function makeMalformedSnapshot(): Record<string, unknown> {
  return { schema: 1 };
}

/** Build a malformed JSON object whose first artifact surface is not a string. */
export function makeMalformedSurfaceSnapshot(): Record<string, unknown> {
  const snapshot = makeSnapshot(makeChangedFiles(makeChangedFile())) as unknown as Record<
    string,
    unknown
  >;
  const artifacts = snapshot["artifacts"] as Array<Record<string, unknown>>;
  const first = artifacts[0];
  if (first === undefined) throw new Error("the malformed snapshot carries no artifact");
  first["surface"] = [];
  return snapshot;
}

/** Build a malformed JSON policy object with one required list emptied. */
export function makeMalformedPolicy(
  policy: AttributionPolicy,
  emptyField: "markers" | "identities" = "markers",
): Record<string, unknown> {
  const malformed: Record<string, unknown> = { ...policy };
  malformed[emptyField] = [];
  return malformed;
}

/** Return empty, traversing, and absolute paths rejected by validation. */
export function invalidPaths(): string[] {
  return ["", "../outside.py", "src/../../outside.py", "/absolute.py", "C:\\absolute.py"];
}

/** Build a complete snapshot carrying the requested invalid changed-file path. */
export function makeInvalidPathSnapshot(path: string): Snapshot {
  return makeSnapshot(makeChangedFiles(makeChangedFile(path)));
}

/** The head object id every synthetic fixture carries. */
export const FIXTURE_HEAD_SHA = HEAD_SHA;
