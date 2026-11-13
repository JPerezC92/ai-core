/**
 * Exact marker lines, fenced-code awareness, and document splitting (pure).
 *
 * A marker counts only as an exact line, ignoring surrounding whitespace, that
 * is outside a fenced code block. One rule serves the core/project markers, the
 * reconciliation block's markers, and the frontmatter delimiter.
 */

import {
  CORE_BEGIN,
  CORE_END,
  PROJECT_BEGIN,
  PROJECT_END,
  RECONCILE_BEGIN,
  RECONCILE_END,
} from "./constants.ts";

/** One exact marker pair, as line indices. */
export type MarkerPair = {
  readonly begin: number;
  readonly end: number;
};

const FENCE_OPEN = /^ {0,3}(`{3,}|~{3,})[^\n]*$/u;

/**
 * Return `line` with only its trailing CR/LF terminator removed.
 *
 * No other whitespace is trimmed, so a padded line is not treated as its
 * unpadded counterpart.
 */
export function lineWithoutTerminator(line: string): string {
  return line.replace(/[\r\n]+$/u, "");
}

/**
 * Split text into lines, keeping each terminator (LF, CRLF and lone CR).
 *
 * Splitting is explicit rather than a regular-expression lookbehind so a CRLF
 * pair can never be split between its two characters.
 */
export function splitLinesWithTerminators(text: string): string[] {
  const lines: string[] = [];
  let start = 0;
  let index = 0;
  while (index < text.length) {
    const character = text.charAt(index);
    if (character === "\n") {
      lines.push(text.slice(start, index + 1));
      index += 1;
      start = index;
      continue;
    }
    if (character === "\r") {
      const width = text.charAt(index + 1) === "\n" ? 2 : 1;
      lines.push(text.slice(start, index + width));
      index += width;
      start = index;
      continue;
    }
    index += 1;
  }
  if (start < text.length) {
    lines.push(text.slice(start));
  }
  return lines;
}

/**
 * Return the indices of lines that are outside any Markdown code fence.
 *
 * A fence opens with at least three matching backticks or tildes and closes
 * with that character repeated at least as many times, with at most three
 * leading spaces and nothing but horizontal whitespace after it. A backtick
 * fence whose info string contains a backtick does not open a fence. Fence
 * delimiter lines themselves are not returned.
 */
export function unfencedLineIndices(lines: readonly string[]): readonly number[] {
  let fenceCharacter: string | null = null;
  let fenceLength = 0;
  const indices: number[] = [];
  for (const [index, line] of lines.entries()) {
    const text = lineWithoutTerminator(line);
    if (fenceCharacter !== null) {
      const closing = new RegExp(
        `^ {0,3}${escapeForRegExp(fenceCharacter)}{${String(fenceLength)},}[ \t]*$`,
        "u",
      );
      if (closing.test(text)) {
        fenceCharacter = null;
      }
      continue;
    }
    const opening = FENCE_OPEN.exec(text);
    if (opening !== null) {
      const fence = opening[1] ?? "";
      const info = opening[2] ?? "";
      const character = fence.slice(0, 1);
      if (character !== "`" || !info.includes("`")) {
        fenceCharacter = character;
        fenceLength = fence.length;
        continue;
      }
    }
    indices.push(index);
  }
  return indices;
}

/**
 * Return the indices of exact stripped `marker` lines outside code fences.
 *
 * Marker-looking lines inside a fence are ordinary text and are skipped.
 */
export function exactMarkerLineIndices(
  lines: readonly string[],
  marker: string,
): readonly number[] {
  return unfencedLineIndices(lines).filter(
    (index) => lineWithoutTerminator(lines[index] ?? "").trim() === marker,
  );
}

/**
 * Return the single valid pair of `begin`/`end` markers, or `null`.
 *
 * Missing, duplicated, and reversed pairs all answer `null`; the callers turn
 * that into the malformed-marker refusal.
 */
export function findMarkerPair(
  lines: readonly string[],
  beginMarker: string,
  endMarker: string,
): MarkerPair | null {
  const begins = exactMarkerLineIndices(lines, beginMarker);
  const ends = exactMarkerLineIndices(lines, endMarker);
  const begin = begins[0];
  const end = ends[0];
  if (begins.length !== 1 || ends.length !== 1 || begin === undefined || end === undefined) {
    return null;
  }
  if (begin > end) {
    return null;
  }
  return { begin, end };
}

/** Return the single ordered core marker pair of `content`, if it has one. */
export function findCoreMarkers(content: string): MarkerPair | null {
  return findMarkerPair(splitLinesWithTerminators(content), CORE_BEGIN, CORE_END);
}

/**
 * Return whether either exact core marker occurs outside a code fence.
 *
 * Such a document claims to be marked, so it must carry a valid pair; it is
 * never silently re-read as a markerless document.
 */
export function hasExactCoreMarkerLines(content: string): boolean {
  const lines = splitLinesWithTerminators(content);
  return (
    exactMarkerLineIndices(lines, CORE_BEGIN).length > 0 ||
    exactMarkerLineIndices(lines, CORE_END).length > 0
  );
}

/** Return whether either exact project marker occurs outside a code fence. */
export function hasExactProjectMarkerLines(content: string): boolean {
  const lines = splitLinesWithTerminators(content);
  return (
    exactMarkerLineIndices(lines, PROJECT_BEGIN).length > 0 ||
    exactMarkerLineIndices(lines, PROJECT_END).length > 0
  );
}

/** Return the single ordered reconciliation-block marker pair, if present. */
export function findReconcileBlock(lines: readonly string[]): MarkerPair | null {
  return findMarkerPair(lines, RECONCILE_BEGIN, RECONCILE_END);
}

function escapeForRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&");
}
