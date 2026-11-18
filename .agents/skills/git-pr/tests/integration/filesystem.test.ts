import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import { createText, readText } from "#scripts/pr_content/infrastructure/filesystem.ts";
import { makeCompletedBody, makeCrlfBody, makeMultibyteBody } from "#tests/support/review-content-fixtures.ts";

const roots: string[] = [];

function root(): string {
	const path = mkdtempSync(join(tmpdir(), "git-pr-filesystem-test-"));
	roots.push(path);
	return path;
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

describe("exclusive artifact creation", () => {
	it("writes the supplied content as the artifact's exact bytes", () => {
		const path = join(root(), "working-body.md");
		const content = makeCompletedBody();

		createText(path, content);

		expect(readFileSync(path)).toEqual(Buffer.from(content, "utf8"));
	});

	it("refuses an existing artifact and leaves its bytes unchanged", () => {
		const directory = root();
		const path = join(directory, "working-body.md");
		const existing = makeCompletedBody();
		createText(path, existing);

		const error = thrownBy(() => createText(path, makeCrlfBody()));

		expect(error.code).toBe("EEXIST");
		expect(readFileSync(path, "utf8")).toBe(existing);
	});

	it("throws and creates nothing when the parent directory is missing", () => {
		const directory = root();
		const path = join(directory, "absent", "working-body.md");

		const error = thrownBy(() => createText(path, makeCompletedBody()));

		expect(error.code).toBe("ENOENT");
		expect(existsSync(path)).toBe(false);
		expect(readdirSync(directory)).toEqual([]);
	});
});

describe("supplied text reading", () => {
	it("returns the stored bytes without newline translation", () => {
		const path = join(root(), "working-body.md");
		const content = makeCrlfBody();
		writeFileSync(path, content, "utf8");

		expect(readText(path)).toBe(content);
		expect(content.includes("\r\n")).toBe(true);
	});

	it("throws ENOENT for a missing path instead of returning a value", () => {
		const directory = root();

		const error = thrownBy(() => readText(join(directory, "absent.md")));

		expect(error.code).toBe("ENOENT");
	});

	it("decodes multi-byte UTF-8 content exactly", () => {
		const path = join(root(), "working-body.md");
		const content = makeMultibyteBody();
		writeFileSync(path, content, "utf8");

		expect(readText(path)).toBe(content);
		expect(Buffer.byteLength(content, "utf8")).toBeGreaterThan(content.length);
	});
});
