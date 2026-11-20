/** Apply the business rules to typed attribution inputs, returning business-error values. */

import { PolicyValidationError, SnapshotValidationError } from "./records.ts";
import type { AttributionPolicy, Snapshot } from "./records.ts";

/** The only hexadecimal run a head object id may carry. */
const HEAD_SHA_PATTERN = /^[0-9a-fA-F]{7,64}$/u;

/** The three artifact surfaces a complete snapshot may carry. */
const ARTIFACT_SURFACES = ["pr-title", "pr-body", "commit-message"] as const;

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

/** Require one policy list to be non-empty, trimmed, and unique ignoring case. */
function validateEntries(
	name: "markers" | "identities",
	entries: readonly string[],
): PolicyValidationError | undefined {
	if (entries.length === 0) {
		return new PolicyValidationError(`policy ${name} must be a non-empty string list`);
	}
	if (entries.some((entry) => entry === "" || entry !== entry.trim())) {
		return new PolicyValidationError(`policy ${name} entries must be non-empty and trimmed`);
	}
	const folded = entries.map((entry) => entry.toLowerCase());
	if (new Set(folded).size !== folded.length) {
		return new PolicyValidationError(`policy ${name} entries must be unique ignoring case`);
	}
	return undefined;
}

/** Validate a typed policy without performing filesystem access. */
export function validatePolicy(policy: AttributionPolicy): PolicyValidationError | undefined {
	if (policy.schema !== 1) return new PolicyValidationError("policy schema must be 1");
	if (policy.self_excluded_file === "") {
		return new PolicyValidationError("policy self_excluded_file must be a non-empty string");
	}
	return validateEntries("markers", policy.markers) ?? validateEntries("identities", policy.identities);
}

/** Validate snapshot completeness against the typed snapshot's own business rules. */
export function validateSnapshot(snapshot: Snapshot): SnapshotValidationError | undefined {
	if (snapshot.schema !== 1) return new SnapshotValidationError("snapshot schema must be 1");
	if (!Number.isInteger(snapshot.pr_number) || snapshot.pr_number < 1) {
		return new SnapshotValidationError("snapshot pr_number must be a positive integer");
	}
	if (!HEAD_SHA_PATTERN.test(snapshot.head_sha)) {
		return new SnapshotValidationError("snapshot head_sha must contain 7 to 64 hexadecimal characters");
	}
	if (snapshot.base.trim() === "") {
		return new SnapshotValidationError("snapshot base must be a non-empty string");
	}

	const surfaces = new Map<string, number>(ARTIFACT_SURFACES.map((surface) => [surface, 0]));
	for (const artifact of snapshot.artifacts) {
		if (!ARTIFACT_SURFACES.some((surface) => surface === artifact.surface)) {
			return new SnapshotValidationError("artifact surface must be pr-title, pr-body, or commit-message");
		}
		if (artifact.source.trim() === "") {
			return new SnapshotValidationError("artifact source must be a non-empty string");
		}
		surfaces.set(artifact.surface, (surfaces.get(artifact.surface) ?? 0) + 1);
	}
	if (surfaces.get("pr-title") !== 1 || surfaces.get("pr-body") !== 1 || (surfaces.get("commit-message") ?? 0) < 1) {
		return new SnapshotValidationError(
			"snapshot requires one PR title, one PR body, and at least one commit message",
		);
	}

	if (snapshot.changed_files.length === 0) {
		return new SnapshotValidationError("snapshot requires at least one changed-file body");
	}
	for (const changedFile of snapshot.changed_files) {
		if (changedFile.path === "" || !isRootRelativePath(changedFile.path)) {
			return new SnapshotValidationError(
				"changed-file path must be a non-empty root-relative path without parent traversal",
			);
		}
	}
	return undefined;
}
