/** The snapshot input validation the scanner operation applies to decoded JSON. */

import { describe, expect, it } from "vitest";
import { SnapshotValidationError } from "#scripts/attribution_scan/domain/records.ts";
import {
	invalidPaths,
	makeInvalidPathSnapshot,
	makeMalformedContentSnapshot,
	makeMalformedSurfaceSnapshot,
	makeNonListCollectionSnapshot,
	makeSnapshotWithoutChangedFiles,
	makeSyntheticPolicy,
	makeUnbalancedSurfaceSnapshot,
	makeWrongSchemaSnapshot,
	scanDecision,
} from "#tests/support/attribution-fixtures.ts";

/** Run the scanner over one snapshot value and a valid policy. */
function scan(snapshotValue: unknown): unknown {
	return scanDecision(snapshotValue, makeSyntheticPolicy());
}

describe("snapshot input rejection", () => {
	it("requires at least one changed-file body", () => {
		const result = scan(makeSnapshotWithoutChangedFiles());

		expect(result).toBeInstanceOf(SnapshotValidationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "snapshot requires at least one changed-file body",
		});
	});

	it("rejects empty, absolute and traversing changed-file paths", () => {
		for (const path of invalidPaths()) {
			const result = scan(makeInvalidPathSnapshot(path));

			expect(result).toBeInstanceOf(SnapshotValidationError);
			expect(result).toMatchObject({
				code: "SNAPSHOT_INVALID",
				message: "changed-file path must be a non-empty root-relative path without parent traversal",
			});
		}
	});

	it("rejects a schema value that is not the documented whole number", () => {
		const result = scan(makeWrongSchemaSnapshot());

		expect(result).toBeInstanceOf(SnapshotValidationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "snapshot schema must be 1",
		});
	});

	it("requires exactly one title, exactly one body, and at least one commit message", () => {
		const result = scan(makeUnbalancedSurfaceSnapshot());

		expect(result).toBeInstanceOf(SnapshotValidationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "snapshot requires one PR title, one PR body, and at least one commit message",
		});
	});

	it("rejects an artifact whose surface is not one of the three supported surfaces", () => {
		const result = scan(makeMalformedSurfaceSnapshot());

		expect(result).toBeInstanceOf(SnapshotValidationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "artifact surface must be pr-title, pr-body, or commit-message",
		});
	});

	it("rejects artifact and changed-file collections that are not lists", () => {
		const expected = {
			artifacts: "snapshot artifacts must be a list",
			changed_files: "snapshot changed_files must be a list",
		} as const;

		for (const field of ["artifacts", "changed_files"] as const) {
			const result = scan(makeNonListCollectionSnapshot(field));

			expect(result).toBeInstanceOf(SnapshotValidationError);
			expect(result).toMatchObject({ code: "SNAPSHOT_INVALID", message: expected[field] });
		}
	});

	it("rejects artifact content that is not a string", () => {
		const result = scan(makeMalformedContentSnapshot());

		expect(result).toBeInstanceOf(SnapshotValidationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "artifact content must be a string",
		});
	});
});
