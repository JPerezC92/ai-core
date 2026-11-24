/**
 * Reads a document's fenced-block structure: which lines are verbatim content, and which fence
 * was never closed.
 *
 * The ODD record format is controlled, so this reads exactly one thing: a delimiter opens a block
 * of opaque content, and the block ends at a matching delimiter. There is no container
 * interpretation, no nested Markdown parsing and no indented-code model. A delimiter belongs at
 * column zero; one that appears after indentation or a block-quote marker is still honoured here —
 * so a historical record's quoted content stays opaque — and `misplacedDelimiter` reports it, so
 * the contract rejects it for newly authored records instead of the reader resolving it.
 */

/** A fence whose closing delimiter was never found. */
export type UnclosedFence = {
	/** 1-based line number of the opening delimiter. */
	readonly line: number;
	readonly marker: "`" | "~";
	readonly length: number;
};

/** The document's fenced structure: what never closed, and what lies outside verbatim content. */
export type FenceStructure = {
	readonly unclosed: readonly UnclosedFence[];
	/**
	 * One entry per input line, in order. Lines inside a fenced block — its delimiters included —
	 * become empty strings; every other line is returned unchanged, so positions keep their
	 * original line numbers.
	 */
	readonly unfencedLines: readonly string[];
	/**
	 * 1-based line numbers of every line this reader treated as a fence delimiter, opening or
	 * closing. The authoring contract is checked against these lines only, so delimiter-shaped
	 * text inside a block stays opaque content.
	 */
	readonly delimiterLines: readonly number[];
};

const DELIMITER = /^(`{3,}|~{3,})(.*)$/u;
const CONTAINER_PREFIX = /^[ \t]*(?:>[ \t]?)*/u;

/** A line's content with any indentation and block-quote markers removed. */
function withoutPrefix(line: string): string {
	return line.slice(CONTAINER_PREFIX.exec(line)?.[0].length ?? 0);
}

/** The delimiter a line carries, at column zero or after its container prefix. */
function delimiterOf(line: string): RegExpExecArray | null {
	const atColumnZero = DELIMITER.exec(line);
	if (atColumnZero !== null) return atColumnZero;
	return DELIMITER.exec(withoutPrefix(line));
}

/**
 * Whether a line carries a fence delimiter that the authoring contract does not allow.
 *
 * A delimiter belongs at column zero. Reporting a misplaced one is what keeps this reader small:
 * the contract removes the ambiguity instead of the reader resolving it.
 */
export function misplacedDelimiter(line: string): boolean {
	return DELIMITER.test(line) ? false : DELIMITER.test(withoutPrefix(line));
}

export function readFenceStructure(lines: readonly string[]): FenceStructure {
	const unclosed: UnclosedFence[] = [];
	const unfencedLines: string[] = [];
	const delimiterLines: number[] = [];
	let open: { readonly line: number; readonly marker: "`" | "~"; readonly length: number } | null = null;

	for (let index = 0; index < lines.length; index += 1) {
		const line = lines[index]!;

		if (open !== null) {
			// Inside a fenced block every line is opaque content; only a matching delimiter ends it.
			const closer = delimiterOf(line);
			const closes =
				closer !== null &&
				closer[1]![0] === open.marker &&
				closer[1]!.length >= open.length &&
				closer[2]!.trim().length === 0;
			delimiterLines.push(index + 1);
			unfencedLines.push("");
			if (closes) open = null;
			continue;
		}

		const opener = delimiterOf(line);
		// A backtick delimiter's info string may not contain a backtick, so inline code is never
		// mistaken for a block opener.
		const usableOpener = opener !== null && !(opener[1]![0] === "`" && opener[2]!.includes("`"));
		if (usableOpener) {
			delimiterLines.push(index + 1);
			open = { line: index + 1, marker: opener[1]![0] as "`" | "~", length: opener[1]!.length };
			unfencedLines.push("");
			continue;
		}

		unfencedLines.push(line);
	}

	if (open !== null) unclosed.push({ line: open.line, marker: open.marker, length: open.length });

	return { unclosed, unfencedLines, delimiterLines };
}
