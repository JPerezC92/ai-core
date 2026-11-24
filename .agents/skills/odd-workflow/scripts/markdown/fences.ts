/**
 * Reads a document's fenced-block structure once, so every consumer that must tell code
 * from structure reads the same interpretation.
 *
 * The reader models the containers a fenced block depends on — block-quote levels and
 * list-item content columns — and whether a fence was closed explicitly. Indentation is
 * measured relative to the containing block at each step, so a marker indented four or more
 * columns past its container is indented code rather than a container, a fence inside a list
 * item is a fence, and fence-like text inside an indented code block is not.
 *
 * It is deliberately not a Markdown parser. It decides fence delimiters, HTML-comment spans
 * and container geometry — exactly what the validators need — and interprets no other
 * Markdown construct.
 */

/** A fence whose closing marker was never found. */
export type UnclosedFence = {
	/** 1-based line number of the opening delimiter. */
	readonly line: number;
	readonly marker: "`" | "~";
	readonly length: number;
};

/** The document's fenced structure: what never closed, and what lies outside code. */
export type FenceStructure = {
	readonly unclosed: readonly UnclosedFence[];
	/**
	 * One entry per input line, in order. A line that belongs to a fenced block — its
	 * delimiters included — becomes an empty string; every other line is returned
	 * unchanged, so positions keep their original line numbers.
	 */
	readonly unfencedLines: readonly string[];
};

/** A list item opened by one line: its content column and the quote level it sits at. */
type OpenedItem = {
	readonly column: number;
	readonly quoteDepth: number;
};

type LineShape = {
	/** The line from the end of its container prefix, with no quote or list marker left. */
	readonly rest: string;
	readonly quoteDepth: number;
	/** List items this line opens, outermost first. */
	readonly openedItems: readonly OpenedItem[];
	/** The line's content, with its container prefixes and leading whitespace removed. */
	readonly body: string;
	/** The column at which `body` begins. */
	readonly bodyColumn: number;
	/** Columns of the line's own leading whitespace, before any container prefix. */
	readonly lineColumn: number;
	/** True when the line opens at least one list item, so its markers are structure. */
	readonly opensListItem: boolean;
};

type OpenFence = {
	readonly line: number;
	readonly marker: "`" | "~";
	readonly length: number;
	readonly quoteDepth: number;
	readonly containerColumn: number;
};

const QUOTE_MARKER = /^ {0,3}>[ \t]?/u;
const LIST_MARKER = /^( {0,3})(?:[-*+]|\d{1,9}[.)])([ \t]+)/u;
/** A thematic break such as `* * *`, `- - -` or `___`, which never opens a container. */
const THEMATIC_BREAK = /^ {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$/u;
const DELIMITER = /^(`{3,}|~{3,})(.*)$/u;
const LEADING_WHITESPACE = /^[ \t]*/u;
const COMMENT_OPEN = "<!--";
const COMMENT_CLOSE = "-->";
/** A container or fenced block opens only within this many columns of its container's content. */
const MAX_OPENER_INDENT = 3;

/** Counts the columns a run of spaces and tabs occupies, starting at `startColumn`, with four-column tab stops. */
function countColumns(text: string, startColumn = 0): number {
	let columns = startColumn;
	for (const character of text) {
		if (character === " ") columns += 1;
		else if (character === "\t") columns += 4 - (columns % 4);
		else break;
	}
	return columns - startColumn;
}

function leadingWhitespace(text: string): string {
	const match = LEADING_WHITESPACE.exec(text);
	return match === null ? "" : match[0];
}

/** Consumes up to `columns` columns of leading spaces and tabs, returning the column reached. */
function columnsOfLeadingWhitespace(text: string, limit: number): { readonly index: number; readonly columns: number } {
	let index = 0;
	let columns = 0;
	while (index < text.length && columns < limit) {
		const character = text[index];
		if (character === " ") columns += 1;
		else if (character === "\t") columns += 4 - (columns % 4);
		else break;
		index += 1;
	}
	return { index, columns };
}

/**
 * Reads one line's container prefix.
 *
 * The walk starts at the containing block's content column and then consumes, in the order
 * they appear, every block-quote marker and every list marker. A marker more than three
 * columns past its container is indented code, not a container, so it stops the walk — which
 * is what makes `    - ``` ` and `-     ``` ` literal code rather than a container opening a
 * fence.
 */
function shapeOf(line: string, baseContainerColumn: number): LineShape {
	// Block-quote markers are read first and each one resets the column origin, because a
	// quote opens a new content space; the containing item's column is then consumed in that
	// space. This is what lets `> - ``` ` and `- > ``` ` both resolve.
	let cursor = 0;
	let column = 0;
	let quoteDepth = 0;
	for (;;) {
		const quote = QUOTE_MARKER.exec(line.slice(cursor));
		if (quote === null) break;
		quoteDepth += 1;
		cursor += quote[0].length;
		column = 0;
	}
	const afterQuotes = line.slice(cursor);
	const lineColumn = countColumns(leadingWhitespace(afterQuotes));
	const base = columnsOfLeadingWhitespace(afterQuotes, baseContainerColumn);
	cursor += base.index;
	column = base.columns;
	const openedItems: OpenedItem[] = [];

	for (;;) {
		const remaining = line.slice(cursor);

		const quote = QUOTE_MARKER.exec(remaining);
		if (quote !== null) {
			quoteDepth += 1;
			cursor += quote[0].length;
			column = 0;
			continue;
		}

		const item = LIST_MARKER.exec(remaining);
		if (item === null) break;
		// `* * *` and `- - -` are thematic breaks, not list items: treating them as items
		// would open a phantom container that then constrains every following line.
		if (THEMATIC_BREAK.test(remaining)) break;
		const markerIndent = item[1]!.length;
		const markerWidth = item[0].length - item[1]!.length - item[2]!.length;
		const markerColumn = column + markerIndent;
		const padding = countColumns(item[2]!, markerColumn + markerWidth);
		if (padding >= 5) {
			// Five or more columns after the marker means the item's first block is an indented
			// code block: the content column is the marker's end plus one, and the remaining
			// padding stays as that block's own indentation.
			openedItems.push({ column: markerColumn + markerWidth + 1, quoteDepth });
			cursor += markerIndent + markerWidth;
			column = markerColumn + markerWidth;
			break;
		}
		const contentColumn = markerColumn + markerWidth + padding;
		openedItems.push({ column: contentColumn, quoteDepth });
		cursor += item[0].length;
		column = contentColumn;
	}

	const remaining = line.slice(cursor);
	const indentation = leadingWhitespace(remaining);
	const bodyColumn = column + countColumns(indentation, column);

	return {
		rest: remaining.slice(indentation.length),
		quoteDepth,
		openedItems,
		body: remaining.slice(indentation.length),
		bodyColumn,
		lineColumn,
		opensListItem: openedItems.length > 0,
	};
}

export function readFenceStructure(lines: readonly string[]): FenceStructure {
	const unclosed: UnclosedFence[] = [];
	const unfencedLines: string[] = [];
	/**
	 * The list items currently open, outermost first. Each entry carries its content column
	 * and the quote level it belongs to, because a list inside a block quote ends with that
	 * block quote and must not keep constraining a fence outside it.
	 */
	const containers: OpenedItem[] = [];
	let open: OpenFence | null = null;
	let inComment = false;

	const innermostColumn = (): number => (containers.length > 0 ? containers[containers.length - 1]!.column : 0);
	/**
	 * Drops every container this line has left.
	 *
	 * A container ends when the line sits in a shallower block quote than the one it was
	 * opened in, or — at the same quote level — when the line is less indented than that
	 * item's content column. A deeper quote is content inside the item, so it ends nothing.
	 */
	const dropEndedContainers = (shape: LineShape): void => {
		for (;;) {
			const tail = containers[containers.length - 1];
			if (tail === undefined) return;
			const quoteClosed = tail.quoteDepth > shape.quoteDepth;
			const lessIndented = tail.quoteDepth === shape.quoteDepth && tail.column > shape.lineColumn;
			if (!quoteClosed && !lessIndented) return;
			containers.pop();
		}
	};

	for (let index = 0; index < lines.length; index += 1) {
		const raw = lines[index]!;
		let pending = true;
		let emitted = false;

		while (pending) {
			pending = false;
			const shape = shapeOf(raw, innermostColumn());

			if (shape.body.length === 0) {
				unfencedLines.push(open === null && !inComment ? raw : "");
				emitted = true;
				break;
			}

			// A fenced block or an HTML comment is literal content, so its lines never push the
			// containers it appears to open: a list marker there is text, not structure. The
			// containers it has left are still dropped, so a fence ends with the block holding it.
			dropEndedContainers(shape);

			if (open !== null) {
				const current = open;
				const leftContainer =
					shape.quoteDepth < current.quoteDepth || innermostColumn() < current.containerColumn;
				if (leftContainer) {
					// The containing block ended before any closing marker, so the fence was
					// terminated implicitly. AICore requires an explicit closer, so this is
					// still unclosed; the current line is then read in its own context.
					unclosed.push({ line: current.line, marker: current.marker, length: current.length });
					open = null;
					pending = true;
					continue;
				}
				// Inside a fence every line is literal, so a closer must be a fence line in the
				// opener's own container, within three columns of that container's content: a
				// marker there is content, and a closer indented past that is indented code.
				const delimiter = shape.opensListItem ? null : DELIMITER.exec(shape.rest);
				const closes =
					delimiter !== null &&
					shape.quoteDepth === current.quoteDepth &&
					delimiter[1]![0] === current.marker &&
					delimiter[1]!.length >= current.length &&
					delimiter[2]!.trim().length === 0 &&
					shape.bodyColumn - current.containerColumn <= MAX_OPENER_INDENT;
				unfencedLines.push("");
				if (closes) open = null;
				emitted = true;
				break;
			}

			if (inComment) {
				unfencedLines.push("");
				if (shape.body.includes(COMMENT_CLOSE)) inComment = false;
				emitted = true;
				break;
			}

			for (const item of shape.openedItems) containers.push(item);
			const contentColumn = innermostColumn();

			if (shape.body.startsWith(COMMENT_OPEN) && shape.bodyColumn - contentColumn <= MAX_OPENER_INDENT) {
				if (!shape.body.includes(COMMENT_CLOSE)) {
					inComment = true;
					unfencedLines.push("");
					emitted = true;
					break;
				}
				unfencedLines.push(raw);
				emitted = true;
				break;
			}

			if (shape.bodyColumn - contentColumn <= MAX_OPENER_INDENT) {
				const delimiter = DELIMITER.exec(shape.body);
				const backtickFenceWithBacktickInfo =
					delimiter !== null && delimiter[1]![0] === "`" && delimiter[2]!.includes("`");
				if (delimiter !== null && !backtickFenceWithBacktickInfo) {
					open = {
						line: index + 1,
						marker: delimiter[1]![0] as "`" | "~",
						length: delimiter[1]!.length,
						quoteDepth: shape.quoteDepth,
						containerColumn: contentColumn,
					};
					unfencedLines.push("");
					emitted = true;
					break;
				}
			}

			unfencedLines.push(raw);
			emitted = true;
		}

		if (!emitted) unfencedLines.push(raw);
	}

	if (open !== null) unclosed.push({ line: open.line, marker: open.marker, length: open.length });

	return { unclosed, unfencedLines };
}
