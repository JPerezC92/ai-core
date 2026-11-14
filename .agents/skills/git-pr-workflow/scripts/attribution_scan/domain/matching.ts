/** Match attribution lines and report policy exclusions in validated snapshots. */

import type { AttributionPolicy, Exclusion, Match, ScanResult, Snapshot } from "./records.ts";

/** The line terminators the scanner treats as one line break. */
const LINE_TERMINATORS = /\r\n|[\n\v\f\r\x1c-\x1e\x85\u2028\u2029]/u;

/**
 * Split content into its lines.
 *
 * A trailing terminator does not open a new line, and empty content carries
 * no line at all, so a reported line number always names real content.
 */
export function splitLines(content: string): string[] {
  if (content === "") return [];
  const lines = content.split(LINE_TERMINATORS);
  if (lines.length > 1 && lines[lines.length - 1] === "") lines.pop();
  return lines;
}

/** Find every marker and identity pair that the same line carries. */
function scanContent(
  content: string,
  surface: string,
  source: string | null,
  path: string | null,
  policy: AttributionPolicy,
): Match[] {
  const matches: Match[] = [];
  const markers = policy.markers.map((item) => [item, item.toLowerCase()] as const);
  const identities = policy.identities.map((item) => [item, item.toLowerCase()] as const);
  let lineNumber = 0;
  for (const rawLine of splitLines(content)) {
    lineNumber += 1;
    const normalizedLine = rawLine.trim().toLowerCase();
    const matchingMarkers = markers.filter(([, folded]) => normalizedLine.startsWith(folded));
    const matchingIdentities = identities.filter(([, folded]) => normalizedLine.includes(folded));
    for (const [marker] of matchingMarkers) {
      for (const [identity] of matchingIdentities) {
        matches.push({ surface, source, path, line: lineNumber, marker, identity });
      }
    }
  }
  return matches;
}

/** Return ordered same-line matches and exclusions without validating inputs. */
export function scanValidatedSnapshot(
  snapshot: Snapshot,
  policy: AttributionPolicy,
): ScanResult {
  const matches: Match[] = [];
  const exclusions: Exclusion[] = [];
  for (const artifact of snapshot.artifacts) {
    matches.push(
      ...scanContent(artifact.content, artifact.surface, artifact.source, null, policy),
    );
  }
  for (const changedFile of snapshot.changed_files) {
    const normalized = changedFile.path.replace(/\\/gu, "/");
    const excluded = policy.self_excluded_file.replace(/\\/gu, "/");
    if (normalized === excluded) {
      exclusions.push({ path: changedFile.path, reason: "policy self-exclusion" });
      continue;
    }
    matches.push(
      ...scanContent(changedFile.content, "changed-file", null, changedFile.path, policy),
    );
  }
  return {
    pr_number: snapshot.pr_number,
    head_sha: snapshot.head_sha,
    base: snapshot.base,
    matches,
    exclusions,
  };
}
