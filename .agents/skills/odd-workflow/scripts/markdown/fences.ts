/**
 * Reads a document's fenced-block structure: which lines are verbatim content, and which fence
 * was never closed.
 *
 * The ODD record format is controlled, so this reads exactly one thing: a delimiter opens a block
 * of opaque content, and the block ends at a matching delimiter of the same level. There is no
 * container interpretation, no nested Markdown parsing and no indented-code model.
 *
 * A delimiter belongs at column zero. One written after indentation, a block-quote marker or a
 * list marker is still honoured here — so a historical record's quoted content stays opaque — and
 * `misplacedDelimiter` reports it, so the contract rejects that shape for newly authored records
 * instead of the reader resolving it.
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
	 * 1-based line numbers of the lines that opened or closed a block. The authoring contract is
	 * checked against these lines only, so delimiter-shaped content stays opaque.
	 */
	readonly delimiterLines: readonly number[];
};

type Delimiter = {
	readonly marker: "`" | "~";
	readonly length: number;
	/** True when the delimiter was not written at column zero. */
	readonly misplaced: boolean;
	/** Text after the delimiter run, used to recognise a closer. */
	readonly rest: string;
};

const DELIMITER = /^(`{3,}|~{3,})(.*)$/u;
/** Whitespace plus any block-quote or list marker a line may carry before its content. */
const CONTAINER_PREFIX = /^(?:[ \t]+|>[ \t]?|[-*+][ \t]+|\d{1,9}[.)][ \t]+)+/u;

/** The delimiter a line carries, or `null` when it carries none. */
function delimiterOf(line: string): Delimiter | null {
	const atColumnZero = DELIMITER.exec(line);
	if (atColumnZero !== null) {
		// A backtick delimiter's info string may not contain a backtick, so inline code is never
		// mistaken for a block delimiter.
		if (atColumnZero[1]![0] === "`" && atColumnZero[2]!.includes("`")) return null;
		return {
			marker: atColumnZero[1]![0] as "`" | "~",
			length: atColumnZero[1]!.length,
			misplaced: false,
			rest: atColumnZero[2]!,
		};
	}
	const prefixed = withoutPrefix(line);
	const afterPrefix = DELIMITER.exec(prefixed);
	if (afterPrefix === null) return null;
	if (afterPrefix[1]![0] === "`" && afterPrefix[2]!.includes("`")) return null;
	return {
		marker: afterPrefix[1]![0] as "`" | "~",
		length: afterPrefix[1]!.length,
		misplaced: prefixed !== line,
		rest: afterPrefix[2]!,
	};
}

/** A line's content with any leading whitespace, block-quote marker or list marker removed. */
function withoutPrefix(line: string): string {
	const prefix = CONTAINER_PREFIX.exec(line);
	return prefix === null ? line : line.slice(prefix[0].length);
}

/**
 * Whether a line carries a fence delimiter that the authoring contract does not allow.
 *
 * A delimiter belongs at column zero. Reporting a misplaced one is what keeps this reader small:
 * the contract removes the ambiguity instead of the reader resolving it.
 */
export function misplacedDelimiter(line: string): boolean {
	return delimiterOf(line)?.misplaced === true;
}

export function readFenceStructure(lines: readonly string[]): FenceStructure {
	const unclosed: UnclosedFence[] = [];
	const unfencedLines: string[] = [];
	const delimiterLines: number[] = [];
	let open: {
		readonly line: number;
		readonly marker: "`" | "~";
		readonly length: number;
		readonly misplaced: boolean;
	} | null = null;

	for (let index = 0; index < lines.length; index += 1) {
		const line = lines[index]!;

		if (open !== null) {
			// Inside a block every line is opaque content. Only a delimiter at the opener's own level
			// ends it, so a delimiter-shaped line inside a column-zero block stays content.
			const closer = delimiterOf(line);
			const closes =
				closer !== null &&
				closer.misplaced === open.misplaced &&
				closer.marker === open.marker &&
				closer.length >= open.length &&
				closer.rest.trim().length === 0;
			unfencedLines.push("");
			if (closes) {
				delimiterLines.push(index + 1);
				open = null;
			}
			continue;
		}

		const opener = delimiterOf(line);
		if (opener !== null) {
			delimiterLines.push(index + 1);
			open = { line: index + 1, marker: opener.marker, length: opener.length, misplaced: opener.misplaced };
			unfencedLines.push("");
			continue;
		}

		unfencedLines.push(line);
	}

	if (open !== null) unclosed.push({ line: open.line, marker: open.marker, length: open.length });

	return { unclosed, unfencedLines, delimiterLines };
}
