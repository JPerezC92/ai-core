import { describe, expect, it } from "vitest";
import { readFenceStructure } from "#scripts/markdown/fences.ts";

/** The 1-based line numbers of every fence the reader reports as unclosed. */
function unclosedLines(lines: readonly string[]): number[] {
	return readFenceStructure(lines).unclosed.map((fence) => fence.line);
}

/** The Log-entry-looking lines the reader leaves outside every fenced block. */
function visibleEntries(lines: readonly string[]): string[] {
	return readFenceStructure(lines).unfencedLines.filter((line) => /^- L\d/u.test(line));
}

describe("readFenceStructure list markers that are not containers", () => {
	it("treats a marker four columns from the container as indented code, not a fence", () => {
		// Reported by external review: four columns past its container is an indented code
		// block, so the marker and the fence-like text are literal.
		expect(unclosedLines(["    - ```"])).toStrictEqual([]);
		expect(unclosedLines(["    - ```", "    - inside"])).toStrictEqual([]);
		const lines = ["    - ```"];
		expect(readFenceStructure(lines).unfencedLines).toStrictEqual(["    - ```"]);
	});

	it("treats five or more columns after a marker as an indented code block inside the item", () => {
		// Reported by external review: the item's first block is indented code, so the fence
		// never opens and the trailing padding stays content indentation.
		expect(unclosedLines(["-     ```"])).toStrictEqual([]);
		expect(unclosedLines(["-      ```"])).toStrictEqual([]);
		const lines = ["-     ```"];
		expect(readFenceStructure(lines).unfencedLines).toStrictEqual(["-     ```"]);
	});

	it("still reads a fence whose marker padding is one to four columns", () => {
		expect(unclosedLines(["-    ```", "     x", "     ```"])).toStrictEqual([]);
		expect(unclosedLines(["-\t```", "\t x", "\t ```"])).toStrictEqual([]);
	});

	it("reads quote and list markers that appear together on one line", () => {
		expect(unclosedLines(["> - ```", ">   x", ">   ```", "- L1 — b"])).toStrictEqual([]);
		expect(unclosedLines(["- > ```", "  > x", "  > ```", "- L1 — b"])).toStrictEqual([]);
	});

	it("reads a fence inside a nested item at that item's own content column", () => {
		const lines = ["- a", "  - ```text", "    x", "    ```", "- L1 — b"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — b"]);
	});
});

describe("readFenceStructure container geometry", () => {
	it("treats fence-like lines inside a top-level indented code block as code, not fences", () => {
		const lines = [
			"Top-level paragraph at column zero.",
			"",
			"    a four-space indented code sample",
			"    ```",
			"    - L9 — inside code",
			"    ~~~",
			"",
			"- L1 — a",
			"- L2 — b",
		];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — b"]);
	});

	it("reads a fence inside an unordered list item at its content column", () => {
		const lines = ["- L1 — a", "", "  ```text", "  - L9 — inside", "  ```", "- L2 — b"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — b"]);
	});

	it("reads a fence inside an ordered list item indented five columns", () => {
		const lines = [
			"- L1 — a",
			"",
			"  1. Approve this:",
			"",
			"     ```json",
			'     { "effect": "allow" }',
			"     ```",
			"",
			"  2. Then continue.",
			"- L2 — b",
		];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — b"]);
	});

	it("reads a fence that begins on the list marker's own line", () => {
		const lines = ["- ```text", "  - L9 — inside", "  ```", "- L2 — b"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L2 — b"]);
	});

	it("reads a fence inside nested list and blockquote containers", () => {
		const lines = [
			"- L1 — a",
			"  - nested",
			"",
			"    > quote",
			"    > ```text",
			"    > - L9 — inside",
			"    > ```",
			"",
			"- L2 — b",
		];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — b"]);
		// The block-quote markers at the nested container's column must be consumed, so the
		// three quoted lines are code rather than document text.
		expect(readFenceStructure(lines).unfencedLines.slice(3, 7)).toStrictEqual(["    > quote", "", "", ""]);
	});

	it("rejects an unbalanced fence inside a blockquote nested in a list item", () => {
		// A quote marker past column 3 is a quote relative to its container, not literal text.
		const lines = ["- L1 — a", "    > ```text", "    > swallowed", "- L2 — b"];
		expect(unclosedLines(lines)).toStrictEqual([2]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — b"]);
	});

	it("accepts a balanced fence inside a blockquote nested in a list item", () => {
		const lines = ["- L1 — a", "    > ```text", "    > inside", "    > ```", "- L2 — b"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — b"]);
	});

	it("closes a fence only when the closer is within three columns of the opener's container", () => {
		// A fence-like line four columns past the opener's container is indented code, so it
		// is content and the fence stays open; three columns past it is still a closer.
		expect(unclosedLines(["- a", "  ```", "  x", "      ```", "- L1 — b"])).toStrictEqual([2]);
		expect(unclosedLines(["- a", "  ```", "  x", "     ```", "- L1 — b"])).toStrictEqual([]);
		expect(unclosedLines(["- a", "  ```", "  x", "    ```", "- L1 — b"])).toStrictEqual([]);
		expect(unclosedLines(["- a", "  ```", "  x", "   ```", "- L1 — b"])).toStrictEqual([]);
	});

	it("does not keep a list container alive past the end of its blockquote", () => {
		// The block quote ends at line 2, so the fence that follows is top level: both its
		// delimiters and its content are read at absolute indentation, not the list's column.
		const lines = ["> - a", "  ```", "code", "  ```", "- L1 — b"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — b"]);
	});

	it("treats a fence-like line 4+ columns past its container as content, not a closer", () => {
		expect(unclosedLines(["```text", "    ```", "```", "- L1 — a"])).toStrictEqual([]);
	});

	it("keeps sibling list items independent across container transitions", () => {
		const lines = ["- a", "  ```text", "  one", "  ```", "- b", "  ```text", "  two", "  ```", "- L1 — c"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — c"]);
	});

	it("reads a tab-indented fence inside a list item and not a tab-indented code block", () => {
		expect(unclosedLines(["- L1 — a", "", "  \t```text", "  \tinside", "  \t```", "- L2 — b"])).toStrictEqual([]);
		expect(unclosedLines(["Top-level text.", "", "\t```", "\tinside", "", "- L1 — a"])).toStrictEqual([]);
	});
});

describe("readFenceStructure delimiters", () => {
	it("accepts backtick and tilde fences", () => {
		expect(unclosedLines(["```text", "inside", "```"])).toStrictEqual([]);
		expect(unclosedLines(["~~~text", "inside", "~~~"])).toStrictEqual([]);
		expect(unclosedLines(["~~~text", "inside"])).toStrictEqual([1]);
	});

	it("requires a closing marker at least as long as the opening one", () => {
		expect(unclosedLines(["````text", "inside", "```"])).toStrictEqual([1]);
		expect(unclosedLines(["````text", "inside", "````"])).toStrictEqual([]);
	});

	it("keeps a shorter fence-like line inside a longer fence", () => {
		expect(unclosedLines(["````text", "```", "- L9 — inside", "````", "- L1 — a"])).toStrictEqual([]);
	});

	it("does not open a backtick fence whose info string contains a backtick", () => {
		expect(unclosedLines(["``` `x` ", "- L1 — a"])).toStrictEqual([]);
	});

	it("does not accept a closing marker followed by other text", () => {
		expect(unclosedLines(["```text", "inside", "```»"])).toStrictEqual([1]);
	});

	it("rejects the documented pre-3dd918c shape", () => {
		const lines = [
			"- L1 — Pedido original, verbatim: «... como el siguiente",
			"",
			"````",
			"root = true",
			"",
			"[*.md]",
			"trim_trailing_whitespace = false",
			"```»",
			"- L2 — a swallowed entry",
		];
		expect(unclosedLines(lines)).toStrictEqual([3]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — Pedido original, verbatim: «... como el siguiente"]);
	});
});

describe("readFenceStructure explicit closure", () => {
	it("reports a fence ended by the end of its blockquote rather than by a closer", () => {
		const lines = ["  > text", "  > ```json", "  > { }", "```", "", "- L1 — a"];
		expect(unclosedLines(lines)).toStrictEqual([2, 4]);
	});

	it("reports a fence ended by a sibling list item rather than by a closer", () => {
		expect(unclosedLines(["- a", "  ```text", "  inside", "- L1 — b"])).toStrictEqual([2]);
	});

	it("reports a fence left open at end of file", () => {
		expect(unclosedLines(["```text", "inside"])).toStrictEqual([1]);
	});
});

describe("readFenceStructure literal content inside a fence", () => {
	it("does not close a fence on a list-marker-prefixed fence-like line", () => {
		const lines = ["```text", "- ```", "- L9 — quoted", "```", "- L1 — a"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a"]);
	});

	it("does not close a fence on an ordered-marker-prefixed fence-like line", () => {
		expect(unclosedLines(["```text", "1. ```", "```", "- L1 — a"])).toStrictEqual([]);
	});

	it("does not close a fence on a blockquote-prefixed fence-like line", () => {
		expect(unclosedLines(["```text", "> ```", "```", "- L1 — a"])).toStrictEqual([]);
	});

	it("does not close a tilde fence on a list-marker-prefixed tilde line", () => {
		expect(unclosedLines(["~~~text", "- ~~~", "~~~", "- L1 — a"])).toStrictEqual([]);
	});

	it("keeps quoted Close entries inside such a fence invisible to the Log", () => {
		const lines = ["- L1 — a", "- L2 — quoted:", "", "```text", "- ```", "- L3 — Close: quoted", "```"];
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — quoted:"]);
	});
});

describe("readFenceStructure HTML comments", () => {
	it("ignores fence-like text inside an HTML comment", () => {
		const lines = ["<!--", "```", "-->", "- L1 — a"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a"]);
	});

	it("treats comment markers inside a fence as literal code", () => {
		const lines = ["```html", "<!--", "-->", "```", "- L1 — a"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a"]);
	});

	it("keeps an inline comment that closes on its own line as document text", () => {
		expect(visibleEntries(["<!-- a note -->", "- L1 — a"])).toStrictEqual(["- L1 — a"]);
	});

	it("does not treat an indented comment marker as an HTML comment", () => {
		// Four columns past its container is an indented code block, so the marker is text
		// and it must not swallow the entries that follow.
		const lines = ["Top-level text.", "", "    <!--", "", "- L1 — a", "- L2 — b"];
		expect(unclosedLines(lines)).toStrictEqual([]);
		expect(visibleEntries(lines)).toStrictEqual(["- L1 — a", "- L2 — b"]);
	});

	it("does not treat an indented closed comment marker as an HTML block", () => {
		const lines = ["Top-level text.", "", "    <!-- note -->", "", "- L1 — a"];
		expect(readFenceStructure(lines).unfencedLines).toStrictEqual([
			"Top-level text.",
			"",
			"    <!-- note -->",
			"",
			"- L1 — a",
		]);
	});
});

describe("readFenceStructure projection", () => {
	it("returns one entry per input line so positions keep their line numbers", () => {
		const lines = ["a", "```", "b", "```", "c"];
		expect(readFenceStructure(lines).unfencedLines).toStrictEqual(["a", "", "", "", "c"]);
	});

	it("preserves every unfenced line byte for byte", () => {
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
