import { describe, expect, it } from "vitest";
import { misplacedDelimiter, readFenceStructure } from "#scripts/markdown/fences.ts";

/** The 1-based line numbers of every fence the reader reports as unclosed. */
function unclosedLines(lines: readonly string[]): number[] {
	return readFenceStructure(lines).unclosed.map((fence) => fence.line);
}

/** The Log-entry-looking lines the reader leaves outside every fenced block. */
function visibleEntries(lines: readonly string[]): string[] {
	return readFenceStructure(lines).unfencedLines.filter((line) => /^- L\d/u.test(line));
}

describe("readFenceStructure delimiters", () => {
	it("pairs a backtick block and a tilde block", () => {
		expect(unclosedLines(["```text", "inside", "```"])).toStrictEqual([]);
		expect(unclosedLines(["~~~text", "inside", "~~~"])).toStrictEqual([]);
	});

	it("reports a delimiter that is never closed", () => {
		expect(unclosedLines(["```text", "inside"])).toStrictEqual([1]);
		expect(unclosedLines(["~~~text", "- L1 — swallowed"])).toStrictEqual([1]);
	});

	it("requires a closer at least as long as the opener and of the same character", () => {
		expect(unclosedLines(["````text", "inside", "```"])).toStrictEqual([1]);
		expect(unclosedLines(["````text", "inside", "````"])).toStrictEqual([]);
		expect(unclosedLines(["```text", "inside", "~~~"])).toStrictEqual([1]);
	});

	it("does not accept a closer followed by other text", () => {
		// The documented pre-3dd918c shape: a four-backtick opener and a guillemet closer.
		expect(unclosedLines(["````", "root = true", "```»"])).toStrictEqual([1]);
	});

	it("does not accept a backtick opener whose info string carries a backtick", () => {
		expect(unclosedLines(["``` `x` ", "- L1 — a"])).toStrictEqual([]);
	});
});

describe("readFenceStructure opaque content", () => {
	it("treats embedded shorter delimiters, headings, Log entries and comments as content", () => {
		const lines = [
			"````markdown",
			"```",
			"## Log",
			"- L2 — Close: quoted",
			"<!--",
			"    indented code with ``` inside",
			"````",
			"- L1 — a",
		];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a"]);
	});

	it("keeps delimiter-shaped content with a container prefix opaque", () => {
		// A prefixed delimiter inside a column-zero block is content: it neither closes the block
		// nor is it reported as a misplaced delimiter, and the whole block stays opaque.
		const lines = ["````markdown", "> ````", "- L2 — kept", "    ```", "````", "- L3 — a"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L3 — a"]);
		expect(readFenceStructure(lines).delimiterLines).toStrictEqual([1, 5]);
	});

	it("keeps a delimiter longer than the content's own runs open until its own closer", () => {
		expect(unclosedLines(["`````", "````", "```", "`````"])).toStrictEqual([]);
		expect(unclosedLines(["`````", "````", "```"])).toStrictEqual([1]);
	});

	it("projects one entry per line and preserves unfenced bytes", () => {
		const lines = ["# Title", "", "- L1 — a", "  trailing  ", "```", "code", "```"];
		expect(readFenceStructure(lines).unfencedLines).toStrictEqual([
			"# Title",
			"",
			"- L1 — a",
			"  trailing  ",
			"",
			"",
			"",
		]);
	});
});

describe("misplacedDelimiter", () => {
	it("accepts a delimiter at column zero", () => {
		expect(misplacedDelimiter("```text")).toBe(false);
		expect(misplacedDelimiter("~~~~")).toBe(false);
	});

	it("reports a delimiter after indentation, a block-quote marker or a list marker", () => {
		expect(misplacedDelimiter("  ```text")).toBe(true);
		expect(misplacedDelimiter("     ```")).toBe(true);
		expect(misplacedDelimiter("> ```")).toBe(true);
		expect(misplacedDelimiter("  > ```")).toBe(true);
		expect(misplacedDelimiter("- ```markdown")).toBe(true);
		expect(misplacedDelimiter("1. ```json")).toBe(true);
	});

	it("does not report ordinary content that mentions a delimiter later in the line", () => {
		expect(misplacedDelimiter("the fence is ``` inline")).toBe(false);
		expect(misplacedDelimiter("- L1 — a ``` b")).toBe(false);
		expect(misplacedDelimiter("- ```text``` is how you write it")).toBe(false);
	});

	it("keeps a legacy list-item delimiter opaque and reports it", () => {
		const lines = ["- ```markdown", "- L2 — Close: quoted", "- ```", "- L3 — a"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L3 — a"]);
	});

	it("keeps a legacy indented delimiter opaque so a historical quotation stays unread", () => {
		const lines = ["1. Add this permission:", "", "     ```json", "     <DATE>", "     ```", "- L2 — b"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(readFenceStructure(lines).unfencedLines[3]).toBe("");
	});
});
