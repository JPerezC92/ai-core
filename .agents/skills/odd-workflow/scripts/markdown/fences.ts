/**
 * Reads a document's fenced-block structure once, so every consumer that must tell code from
 * structure reads the same interpretation.
 *
 * The model is one ordered stack of container frames. A frame is a block quote or a list item,
 * and it carries the width of its own content prefix measured against its parent's content
 * column, so indentation is always compared in one coordinate system: the innermost container's.
 * A fenced block or an HTML comment records the stack depth that owns it and ends when the stack
 * shrinks below that depth, so a literal can never outlive the container that opened it.
 *
 * It is deliberately not a Markdown parser. It decides fence delimiters, HTML-comment spans and
 * container geometry — exactly what the validators need — and interprets no other construct. A
 * construct it does not model is read as ordinary text, which never changes the fence or comment
 * extents; indented code in particular is text here, and that is deliberate: it must never open a
 * literal span, while its content stays readable to the record rules.
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
	 * One entry per input line, in order. A line that belongs to a fenced block or an HTML
	 * comment — its delimiters included — becomes an empty string; every other line is returned
	 * unchanged, so positions keep their original line numbers.
	 */
	readonly unfencedLines: readonly string[];
};

/** One open container: a block quote, or a list item whose content width is relative to its parent. */
type Frame = {
	readonly kind: "quote" | "item";
	/** A list item's content width measured from the parent's content column; 0 for a quote. */
	readonly width: number;
};

/** A literal span owned by a container: it ends with its container, not only with its own closer. */
type Literal =
	| {
			readonly kind: "fence";
			readonly ownerDepth: number;
			readonly line: number;
			readonly marker: "`" | "~";
			readonly length: number;
	  }
	| { readonly kind: "comment"; readonly ownerDepth: number };

const QUOTE_MARKER = /^ {0,3}>[ \t]?/u;
const LIST_MARKER = /^( {0,3})(?:[-*+]|\d{1,9}[.)])([ \t]+)/u;
const DELIMITER = /^(`{3,}|~{3,})(.*)$/u;
const LEADING_WHITESPACE = /^[ \t]*/u;
/** A thematic break such as `* * *`, `- - -` or `___`, which never opens a container. */
const THEMATIC_BREAK = /^ {0,3}(?:(?:\*[ \t]*){3,}|(?:-[ \t]*){3,}|(?:_[ \t]*){3,})$/u;
const COMMENT_OPEN = "<!--";
const COMMENT_CLOSE = "-->";
/** A container or a literal span opens only within this many columns of its container's content. */
const MAX_INDENT = 3;

/** Counts the columns a run of spaces and tabs occupies, starting at `startColumn`, on four-column tab stops. */
function countColumns(text: string, startColumn = 0): number {
	let columns = startColumn;
	for (const character of text) {
		if (character === " ") columns += 1;
		else if (character === "\t") columns += 4 - (columns % 4);
		else break;
	}
	return columns - startColumn;
}

/** The absolute column at which `index` sits, expanding any tab inside the prefix. */
function columnAt(line: string, index: number): number {
	let column = 0;
	for (let cursor = 0; cursor < index; cursor += 1) {
		column += line[cursor] === "\t" ? 4 - (column % 4) : 1;
	}
	return column;
}

function leadingWhitespace(text: string): string {
	const match = LEADING_WHITESPACE.exec(text);
	return match === null ? "" : match[0];
}

/**
 * Advances past whitespace until the absolute `target` column is reached.
 *
 * Returns the resulting index, or `null` when the whitespace runs out first, which is what makes
 * a list item end. A tab that overshoots the target is consumed whole; the overshoot stays as
 * content indentation rather than being partly redistributed.
 */
function advanceToColumn(line: string, cursor: number, target: number): number | null {
	let column = columnAt(line, cursor);
	let index = cursor;
	while (column < target) {
		const character = line[index];
		if (character === " ") {
			column += 1;
			index += 1;
			continue;
		}
		if (character === "\t") {
			column += 4 - (column % 4);
			index += 1;
			continue;
		}
		return null;
	}
	return index;
}

export function readFenceStructure(lines: readonly string[]): FenceStructure {
	const unclosed: UnclosedFence[] = [];
	const unfencedLines: string[] = [];
	const stack: Frame[] = [];
	let literal: Literal | null = null;

	/** Ends the current literal, reporting it when it is a fence that never closed explicitly. */
	const endLiteral = (): void => {
		if (literal !== null && literal.kind === "fence") {
			unclosed.push({ line: literal.line, marker: literal.marker, length: literal.length });
		}
		literal = null;
	};

	for (let index = 0; index < lines.length; index += 1) {
		const line = lines[index]!;

		// A blank line is inside whatever is open and never opens or closes a container.
		if (/^[ \t]*$/u.test(line)) {
			unfencedLines.push(literal === null ? line : "");
			continue;
		}

		// 1. Walk the open containers, outermost first. The first frame that cannot continue is
		//    where this line leaves the stack; everything inside it ends with it.
		let cursor = 0;
		let base = 0;
		let depth = 0;
		for (; depth < stack.length; depth += 1) {
			const frame = stack[depth]!;
			if (frame.kind === "quote") {
				const marker = QUOTE_MARKER.exec(line.slice(cursor));
				if (marker === null) break;
				cursor += marker[0].length;
				base = columnAt(line, cursor);
				continue;
			}
			const reached = advanceToColumn(line, cursor, base + frame.width);
			if (reached === null) break;
			cursor = reached;
			base += frame.width;
		}
		if (depth < stack.length) {
			stack.length = depth;
			if (literal !== null && literal.ownerDepth > stack.length) endLiteral();
		}

		// 2. A literal span swallows the line, and only its own container can close it.
		if (literal !== null) {
			if (stack.length === literal.ownerDepth) {
				const rest = line.slice(cursor);
				if (literal.kind === "fence") {
					const whitespace = leadingWhitespace(rest);
					const body = rest.slice(whitespace.length);
					const relative = columnAt(line, cursor) + countColumns(whitespace, columnAt(line, cursor)) - base;
					const delimiter = DELIMITER.exec(body);
					if (
						relative <= MAX_INDENT &&
						delimiter !== null &&
						delimiter[1]![0] === literal.marker &&
						delimiter[1]!.length >= literal.length &&
						delimiter[2]!.trim().length === 0
					) {
						literal = null;
					}
				} else if (rest.includes(COMMENT_CLOSE)) {
					literal = null;
				}
			}
			unfencedLines.push("");
			continue;
		}

		// 3. Read this line's own block starts on top of the surviving containers.
		let contentCursor = cursor;
		let contentBase = base;
		for (;;) {
			const rest = line.slice(contentCursor);
			const whitespace = leadingWhitespace(rest);
			const at = contentCursor + whitespace.length;
			const relative =
				columnAt(line, contentCursor) + countColumns(whitespace, columnAt(line, contentCursor)) - contentBase;
			if (relative > MAX_INDENT) break;
			const tail = line.slice(at);

			const quote = QUOTE_MARKER.exec(tail);
			if (quote !== null) {
				stack.push({ kind: "quote", width: 0 });
				contentCursor = at + quote[0].length;
				contentBase = columnAt(line, contentCursor);
				continue;
			}

			const item = LIST_MARKER.exec(tail);
			if (item === null || THEMATIC_BREAK.test(tail)) break;
			const markerWidth = item[0].length - item[1]!.length - item[2]!.length;
			const markerIndent = relative + item[1]!.length;
			const padding = countColumns(item[2]!, columnAt(line, at) + item[1]!.length + markerWidth);
			if (padding >= 5) {
				// Five or more columns means the item's first block is indented code: the content
				// width is the marker's end plus one, and the remaining padding stays indentation.
				stack.push({ kind: "item", width: markerIndent + markerWidth + 1 });
				contentCursor = at + item[1]!.length + markerWidth;
				contentBase = columnAt(line, contentCursor);
				break;
			}
			stack.push({ kind: "item", width: markerIndent + markerWidth + padding });
			contentCursor = at + item[0].length;
			contentBase = columnAt(line, contentCursor);
		}

		// 4. Decide what the surviving content is.
		const rest = line.slice(contentCursor);
		const whitespace = leadingWhitespace(rest);
		const bodyStart = contentCursor + whitespace.length;
		const body = line.slice(bodyStart);
		const bodyColumn = columnAt(line, bodyStart);
		const relative = bodyColumn - contentBase;
		if (body.length === 0 || relative > MAX_INDENT) {
			// A blank line, or indented code: text, never a literal span.
			unfencedLines.push(line);
			continue;
		}

		if (body.startsWith(COMMENT_OPEN)) {
			if (!body.includes(COMMENT_CLOSE)) {
				literal = { kind: "comment", ownerDepth: stack.length };
				unfencedLines.push("");
				continue;
			}
			unfencedLines.push(line);
			continue;
		}

		const delimiter = DELIMITER.exec(body);
		const backtickFenceWithBacktickInfo =
			delimiter !== null && delimiter[1]![0] === "`" && delimiter[2]!.includes("`");
		if (delimiter !== null && !backtickFenceWithBacktickInfo) {
			literal = {
				kind: "fence",
				ownerDepth: stack.length,
				line: index + 1,
				marker: delimiter[1]![0] as "`" | "~",
				length: delimiter[1]!.length,
			};
			unfencedLines.push("");
			continue;
		}

		unfencedLines.push(line);
	}

	if (literal !== null) endLiteral();

	return { unclosed, unfencedLines };
}
