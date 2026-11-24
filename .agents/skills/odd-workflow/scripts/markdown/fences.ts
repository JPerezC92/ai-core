/**
 * Reads a document's fenced-block structure once, so every consumer that must tell code
 * from structure reads the same interpretation.
 *
 * The reader models the two things a fenced block depends on and a regular expression
 * cannot express: the container a line sits in (block-quote markers and list-item content
 * columns), and whether a fence was closed explicitly. Indentation is measured relative to
 * the containing block, so a fence inside a list item is a fence while a fence-like line
 * inside an indented code block is not.
 *
 * It is deliberately not a Markdown parser. It decides fence delimiters, HTML-comment spans
 * and container columns — exactly what the validators need — and interprets no other
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

type OpenFence = {
	readonly line: number;
	readonly marker: "`" | "~";
	readonly length: number;
	readonly quoteDepth: number;
	readonly containerColumn: number;
};

type LineShape = {
	/** The line with every leading block-quote marker removed. */
	readonly rest: string;
	/** How many block-quote markers were removed. */
	readonly quoteDepth: number;
	/** Columns occupied by the line's leading spaces and tabs. */
	readonly indentColumns: number;
	/** The line's content, with leading whitespace (and a list marker, when present) removed. */
	readonly body: string;
	/** The column at which `body` begins. */
	readonly bodyColumn: number;
	/** True when the line opens a list item, so its own content column is its body column. */
	readonly startsListItem: boolean;
	/** The content column of a list item this line opens, otherwise undefined. */
	readonly itemContentColumn: number | undefined;
};

const BLOCKQUOTE_PREFIX = /^ {0,3}>[ \t]?/u;
const LIST_ITEM_MARKER = /^(?:[-*+]|\d{1,9}[.)])([ \t]+)/u;
const DELIMITER = /^(`{3,}|~{3,})(.*)$/u;
const LEADING_WHITESPACE = /^[ \t]*/u;
const COMMENT_OPEN = "<!--";
const COMMENT_CLOSE = "-->";
/** A fenced block opens only within this many columns of its container's content. */
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

function stripBlockquoteMarkers(line: string): string {
	let rest = line;
	for (;;) {
		const marker = BLOCKQUOTE_PREFIX.exec(rest);
		if (marker === null) return rest;
		rest = rest.slice(marker[0].length);
	}
}

function quoteDepthOf(line: string): number {
	let depth = 0;
	let rest = line;
	for (;;) {
		const marker = BLOCKQUOTE_PREFIX.exec(rest);
		if (marker === null) return depth;
		rest = rest.slice(marker[0].length);
		depth += 1;
	}
}

function shapeOf(line: string): LineShape {
	const rest = stripBlockquoteMarkers(line);
	const quoteDepth = quoteDepthOf(line);
	const indentation = leadingWhitespace(rest);
	const indentColumns = countColumns(indentation);
	const afterIndent = rest.slice(indentation.length);
	const content = afterIndent;
	const item = LIST_ITEM_MARKER.exec(content);
	if (item === null) {
		return {
			rest,
			quoteDepth,
			indentColumns,
			body: content,
			bodyColumn: indentColumns,
			startsListItem: false,
			itemContentColumn: undefined,
		};
	}
	const markerWidth = item[0].length - item[1]!.length;
	const padding = countColumns(item[1]!, indentColumns + markerWidth);
	const itemContentColumn = indentColumns + markerWidth + (padding >= 5 ? 1 : padding);
	return {
		rest,
		quoteDepth,
		indentColumns,
		body: content.slice(item[0].length),
		bodyColumn: itemContentColumn,
		startsListItem: true,
		itemContentColumn,
	};
}

export function readFenceStructure(lines: readonly string[]): FenceStructure {
	const unclosed: UnclosedFence[] = [];
	const unfencedLines: string[] = [];
	/**
	 * The list items currently open, outermost first. Each entry carries its content column
	 * and the block-quote depth it belongs to, because a list inside a block quote ends with
	 * that block quote and must not keep constraining a fence outside it.
	 */
	const containers: { readonly column: number; readonly quoteDepth: number }[] = [];
	let open: OpenFence | null = null;
	let inComment = false;

	const innermostColumn = (): number => (containers.length > 0 ? containers[containers.length - 1]!.column : 0);
	/** Drops every open list item that lived inside a block quote this line has left. */
	const closeDeeperQuotes = (quoteDepth: number): void => {
		while (containers.length > 0 && containers[containers.length - 1]!.quoteDepth > quoteDepth) containers.pop();
	};

	for (let index = 0; index < lines.length; index += 1) {
		const raw = lines[index]!;
		let pending = true;
		let emitted = false;

		while (pending) {
			pending = false;
			const shape = shapeOf(raw);

			if (shape.body.length === 0) {
				unfencedLines.push(open === null && !inComment ? raw : "");
				emitted = true;
				break;
			}

			if (open !== null) {
				const leftContainer =
					shape.quoteDepth < open.quoteDepth ||
					(shape.quoteDepth === open.quoteDepth && shape.indentColumns < open.containerColumn);
				if (leftContainer) {
					// The containing block ended before any closing marker, so the fence was
					// terminated implicitly. AICore requires an explicit closer, so this is
					// still unclosed; the current line is then read in its own context.
					unclosed.push({ line: open.line, marker: open.marker, length: open.length });
					open = null;
					pending = true;
					continue;
				}
				// Inside a fence every line is literal, so a closer must be a fence line in the
				// opener's own container: a list marker there is content, never a delimiter.
				const literalContent = shape.rest.slice(leadingWhitespace(shape.rest).length);
				const delimiter = shape.startsListItem ? null : DELIMITER.exec(literalContent);
				const closes =
					delimiter !== null &&
					shape.quoteDepth === open.quoteDepth &&
					delimiter[1]![0] === open.marker &&
					delimiter[1]!.length >= open.length &&
					delimiter[2]!.trim().length === 0 &&
					shape.indentColumns - open.containerColumn <= MAX_OPENER_INDENT;
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

			// A fenced block or an HTML comment is literal content, so its lines never move
			// the container state: a list marker there is text, not structure.
			closeDeeperQuotes(shape.quoteDepth);
			if (shape.startsListItem) {
				const itemContentColumn = shape.itemContentColumn!;
				while (containers.length > 0 && containers[containers.length - 1]!.column >= itemContentColumn) {
					containers.pop();
				}
				containers.push({ column: itemContentColumn, quoteDepth: shape.quoteDepth });
			} else {
				while (containers.length > 0 && shape.indentColumns < containers[containers.length - 1]!.column) {
					containers.pop();
				}
			}
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
