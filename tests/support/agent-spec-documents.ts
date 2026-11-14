/**
 * Structure of the agent runtime specifications, read for the repository contract tests.
 *
 * These helpers observe a document's own structure and never re-implement a
 * synchronization operation. The rules are the ones the runtime specifications
 * are written against: a marker counts only as an exact line outside a fenced
 * code block, a leading `---` pair delimits the frontmatter, and the core region
 * is the text between the core markers.
 */

import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const CORE_BEGIN = "<!-- core:begin -->";
export const CORE_END = "<!-- core:end -->";
export const PROJECT_BEGIN = "<!-- project:begin -->";
export const PROJECT_END = "<!-- project:end -->";
const FRONTMATTER_DELIMITER = "---";

const LINE_BREAK_RE = /\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/gu;
const LINE_BREAK_AT_END_RE = /(?:\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029])$/u;
const FENCE_OPEN_RE = /^ {0,3}(`{3,}|~{3,})(.*)$/u;

/** The checkout root, derived from this module's own location. */
export const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..");

export const AGENT_SPECS_DIR = join(REPO_ROOT, ".opencode", "agents");

/** Raised when a document claims marked regions it does not carry. */
export class MalformedSourceMarkers extends Error {
  constructor(message: string) {
    super(message);
    this.name = "MalformedSourceMarkers";
  }
}

/** Splits text into lines, dropping every line terminator. */
export function splitLines(text: string): string[] {
  if (text.length === 0) return [];
  const lines = text.split(LINE_BREAK_RE);
  if (LINE_BREAK_AT_END_RE.test(text)) lines.pop();
  return lines;
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&");
}

/**
 * Returns the indices of lines that are outside any Markdown code fence.
 *
 * A fence opens with at least three matching backticks or tildes and closes with
 * that character repeated at least as many times, with at most three leading
 * spaces and nothing but horizontal whitespace after it. A backtick fence whose
 * info string contains a backtick does not open a fence. Fence delimiter lines
 * themselves are not returned.
 */
export function unfencedLineIndices(lines: readonly string[]): number[] {
  let active: { readonly character: string; readonly length: number } | null = null;
  const indices: number[] = [];

  for (let index = 0; index < lines.length; index += 1) {
    const text = lines[index]!;
    if (active !== null) {
      const closing = new RegExp(
        `^ {0,3}${escapeRegExp(active.character)}{${active.length},}[ \\t]*$`,
        "u",
      );
      if (closing.test(text)) active = null;
      continue;
    }

    const opening = FENCE_OPEN_RE.exec(text);
    if (opening !== null) {
      const fence = opening[1]!;
      const info = opening[2] ?? "";
      if (fence[0] !== "`" || !info.includes("`")) {
        active = { character: fence[0]!, length: fence.length };
        continue;
      }
    }

    indices.push(index);
  }

  return indices;
}

/** Returns the lines of `text` that sit outside any fenced code block. */
export function unfencedLines(text: string): string[] {
  const lines = splitLines(text);
  return unfencedLineIndices(lines).map((index) => lines[index]!);
}

/** Returns the indices of exact stripped `marker` lines outside code fences. */
export function exactMarkerLineIndices(
  lines: readonly string[],
  marker: string,
): number[] {
  return unfencedLineIndices(lines).filter((index) => lines[index]!.trim() === marker);
}

/** The single valid core marker pair, or `null` when it is missing, duplicated or reversed. */
export function findCoreMarkers(text: string): { begin: number; end: number } | null {
  const lines = splitLines(text);
  const begins = exactMarkerLineIndices(lines, CORE_BEGIN);
  const ends = exactMarkerLineIndices(lines, CORE_END);
  if (begins.length !== 1 || ends.length !== 1) return null;
  if (begins[0]! > ends[0]!) return null;
  return { begin: begins[0]!, end: ends[0]! };
}

export type FrontmatterSplit = {
  readonly frontmatter: string;
  readonly body: string;
  readonly frontmatterLineCount: number;
};

/**
 * Splits leading YAML frontmatter from the body.
 *
 * A delimiter is an exact `---` line, and a `---` line inside a fenced code
 * block does not delimit. Returns an empty frontmatter when the content does not
 * open with a `---` line or has no closing delimiter.
 */
export function splitFrontmatter(text: string): FrontmatterSplit {
  const lines = splitLines(text);
  if (lines.length === 0 || lines[0] !== FRONTMATTER_DELIMITER) {
    return { frontmatter: "", body: text, frontmatterLineCount: 0 };
  }

  for (const index of unfencedLineIndices(lines)) {
    if (index === 0) continue;
    if (lines[index] === FRONTMATTER_DELIMITER) {
      return {
        frontmatter: lines.slice(0, index + 1).join("\n"),
        body: lines.slice(index + 1).join("\n"),
        frontmatterLineCount: index + 1,
      };
    }
  }

  return { frontmatter: "", body: text, frontmatterLineCount: 0 };
}

function hasExactMarkerLines(text: string, begin: string, end: string): boolean {
  const lines = splitLines(text);
  return (
    exactMarkerLineIndices(lines, begin).length > 0 ||
    exactMarkerLineIndices(lines, end).length > 0
  );
}

/**
 * Returns a source file's core bytes.
 *
 * A valid marker pair yields its region. A markerless source uses its whole
 * post-frontmatter body; a source carrying exact core or project marker lines
 * without a valid core pair is malformed, so its project content is never read
 * as core.
 */
export function extractSourceCore(text: string): string {
  const markers = findCoreMarkers(text);
  if (markers !== null) {
    return splitLines(text).slice(markers.begin + 1, markers.end).join("\n");
  }
  if (
    hasExactMarkerLines(text, CORE_BEGIN, CORE_END) ||
    hasExactMarkerLines(text, PROJECT_BEGIN, PROJECT_END)
  ) {
    throw new MalformedSourceMarkers("source core markers are malformed");
  }
  return splitFrontmatter(text).body;
}

/** Returns the text of the single optional project region. */
export function projectText(text: string): string {
  const lines = splitLines(text);
  const begins = exactMarkerLineIndices(lines, PROJECT_BEGIN);
  const ends = exactMarkerLineIndices(lines, PROJECT_END);
  if (begins.length !== 1 || ends.length !== 1) {
    throw new Error("expected exactly one project region");
  }
  return lines.slice(begins[0]! + 1, ends[0]!).join("\n");
}
