import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import type { Publication, PublicationError } from "#scripts/pr_content/domain/records.ts";
import {
	createArtifact,
	readPublicationInput,
	reserveArtifact,
} from "#scripts/pr_content/infrastructure/filesystem.ts";
import { makeCreationDocument, makeReviewDocument, makeReviewInput } from "#tests/support/publication-fixtures.ts";

const roots: string[] = [];

function root(): string {
	const path = mkdtempSync(join(tmpdir(), "git-pr-filesystem-test-"));
	roots.push(path);
	return path;
}

/** Write one supplied document to a temporary file and read it back through the adapter. */
function readDocument(value: unknown): Publication | PublicationError {
	const source = join(root(), "publication.json");
	writeFileSync(source, typeof value === "string" ? value : JSON.stringify(value));
	return readPublicationInput(source);
}

/** Return the error raised by the adapter, failing when it returns instead of throwing. */
function thrownBy(action: () => void): NodeJS.ErrnoException {
	try {
		action();
	} catch (error) {
		return error as NodeJS.ErrnoException;
	}
	throw new Error("expected the adapter to throw");
}

afterEach(() => {
	for (const path of roots.splice(0)) rmSync(path, { recursive: true, force: true });
});

describe("reading the supplied publication input", () => {
	it("maps the supplied JSON file into typed records", () => {
		const source = join(root(), "publication.json");
		writeFileSync(source, makeReviewInput());

		const result = readPublicationInput(source);

		expect("code" in result).toBe(false);
		if ("code" in result) return;
		expect(result.title).toBe("feat(review): prepare publication");
		expect(result.review?.prNumber).toBe(12);
		expect(result.review?.verdict?.kind).toBe("PASS");
		expect(result.testPlan[0]?.evidence?.executor).toBe("Cipher");
		expect(result.testPlan[1]?.decision?.actor).toBe("author");
	});

	it("maps a creation-stage document into typed records", () => {
		const mapped = readDocument(makeCreationDocument());

		expect("code" in mapped).toBe(false);
		if ("code" in mapped) return;
		expect(mapped.title).toBe("feat(review): prepare publication");
		expect(mapped.testPlan).toHaveLength(2);
		expect(mapped.testPlan[0]?.status).toBe("PENDING");
		expect(mapped.review).toBeUndefined();
	});

	it("refuses an input that is not decodable JSON", () => {
		const source = join(root(), "publication.json");
		writeFileSync(source, "not json");

		expect(readPublicationInput(source)).toMatchObject({ code: "INPUT_INVALID" });
	});

	it("refuses unknown fields at every level", () => {
		const creation = makeCreationDocument();
		const review = makeReviewDocument();
		const documents: unknown[] = [
			{ ...creation, extra: true },
			{ ...creation, testPlan: [{ ...creation.testPlan[0]!, extra: true }, creation.testPlan[1]!] },
			{ ...creation, breakingChanges: { description: "a", migration: "b", extra: true } },
			{ ...review, review: { ...review.review, extra: true } },
			{
				...review,
				review: {
					...review.review,
					findings: [
						{
							id: "F1",
							severity: "BLOCK",
							status: "OPEN",
							evidence: "e",
							resolution: "r",
							extra: true,
						},
					],
				},
			},
		];

		for (const document of documents) expect(readDocument(document)).toMatchObject({ code: "INPUT_INVALID" });
	});

	it("refuses wrong types and unsupported enumerations", () => {
		const creation = makeCreationDocument();
		const documents: unknown[] = [
			"not an object",
			{ ...creation, schemaVersion: 2 },
			{ ...creation, title: 42 },
			{ ...creation, summary: "one bullet" },
			{ ...creation, summary: [42] },
			{ ...creation, testPlan: "two items" },
			{ ...creation, testPlan: [{ text: "first", status: "DONE" }, creation.testPlan[1]!] },
			{ ...creation, testPlan: [{ text: "first", status: ["PENDING"] }, creation.testPlan[1]!] },
			{
				...creation,
				review: { prNumber: "12", headSha: "abc1234", baseRef: "main", findings: [], debt: [] },
			},
			{
				...creation,
				review: {
					prNumber: 12,
					headSha: "abc1234",
					baseRef: "main",
					findings: [],
					debt: [],
					verdict: { kind: "MAYBE", basis: "b" },
				},
			},
		];

		for (const document of documents) expect(readDocument(document)).toMatchObject({ code: "INPUT_INVALID" });
	});

	it("refuses malformed evidence and decision shapes", () => {
		const creation = makeCreationDocument();
		const documents: unknown[] = [
			{
				...creation,
				testPlan: [
					{ text: "first", status: "PASSED", evidence: { action: "run", result: "ok" } },
					creation.testPlan[1]!,
				],
			},
			{
				...creation,
				testPlan: [
					{
						text: "first",
						status: "PASSED",
						evidence: { action: "run", result: "ok", executor: "author", extra: true },
					},
					creation.testPlan[1]!,
				],
			},
			{
				...creation,
				testPlan: [
					{ text: "first", status: "NOT_APPLICABLE", decision: { actor: "author" } },
					creation.testPlan[1]!,
				],
			},
			{
				...creation,
				testPlan: [
					{
						text: "first",
						status: "NOT_APPLICABLE",
						decision: {
							actor: "author",
							date: "2026-11-20",
							statement: "reason",
							evidence: "source",
							destination: 7,
						},
					},
					creation.testPlan[1]!,
				],
			},
		];

		for (const document of documents) expect(readDocument(document)).toMatchObject({ code: "INPUT_INVALID" });
	});

	it("throws for a missing input path instead of returning a value", () => {
		const error = thrownBy(() => readPublicationInput(join(root(), "absent.json")));

		expect(error.code).toBe("ENOENT");
	});
});

describe("exclusive artifact creation", () => {
	it("writes the supplied content as the artifact's exact bytes", () => {
		const path = join(root(), "body.md");
		const content = "## Summary\n\n- one bullet\n";

		createArtifact(path, content);

		expect(readFileSync(path)).toEqual(Buffer.from(content, "utf8"));
	});

	it("refuses an existing artifact and leaves its bytes unchanged", () => {
		const path = join(root(), "body.md");
		createArtifact(path, "existing body\n");

		const error = thrownBy(() => createArtifact(path, "replacement body\n"));

		expect(error.code).toBe("EEXIST");
		expect(readFileSync(path, "utf8")).toBe("existing body\n");
	});

	it("throws and creates nothing when the parent directory is missing", () => {
		const directory = root();
		const path = join(directory, "absent", "body.md");

		const error = thrownBy(() => createArtifact(path, "content\n"));

		expect(error.code).toBe("ENOENT");
		expect(existsSync(path)).toBe(false);
		expect(readdirSync(directory)).toEqual([]);
	});
});

describe("reserving an artifact path", () => {
	it("reserves the path exclusively and commits its content", () => {
		const path = join(root(), "body.md.receipt.json");

		const reservation = reserveArtifact(path);
		reservation.commit('{"status":"prepared"}\n');

		expect(readFileSync(path, "utf8")).toBe('{"status":"prepared"}\n');
	});

	it("refuses a path that is already occupied", () => {
		const path = join(root(), "body.md.receipt.json");
		writeFileSync(path, "previous receipt\n");

		const error = thrownBy(() => reserveArtifact(path));

		expect(error.code).toBe("EEXIST");
		expect(readFileSync(path, "utf8")).toBe("previous receipt\n");
	});

	it("releases the reservation without leaving an artifact behind", () => {
		const directory = root();
		const path = join(directory, "body.md.receipt.json");

		const reservation = reserveArtifact(path);
		reservation.release();

		expect(existsSync(path)).toBe(false);
		expect(readdirSync(directory)).toEqual([]);
	});
});
