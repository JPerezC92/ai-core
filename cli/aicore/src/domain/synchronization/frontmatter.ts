/**
 * Leading YAML frontmatter split and refresh (pure).
 *
 * A region write refreshes the destination's frontmatter identity keys from the
 * source: a key the source defines takes the source's own raw lines, a
 * source-only key is appended in source order, and a destination-only key keeps
 * its exact bytes — which is what stops `local-version` from being reset. The
 * merge is surgical, so no value is ever rewritten through a parser and a
 * destination scalar such as `version: 1.10` cannot be re-emitted as `1.1`.
 *
 * `metadata` merges one level down under the same source-wins rule, so a
 * destination-only child survives.
 */

import { FRONTMATTER_DELIMITER } from "./constants.ts";
import {
  lineWithoutTerminator,
  splitLinesWithTerminators,
  unfencedLineIndices,
} from "./markers.ts";

/** One raw frontmatter run: a key's own lines, or a comment run with no key. */
type FrontmatterSegment = {
  readonly key: string | null;
  readonly text: string;
};

/** A parsed frontmatter and the raw lines each of its keys occupies. */
type FrontmatterLayout = {
  readonly opening: string;
  readonly segments: readonly FrontmatterSegment[];
  readonly trailing: string;
  readonly closing: string;
};

/** Refreshed frontmatter text, and why part of it stayed as it was. */
export type RefreshedFrontmatter = {
  readonly text: string;
  /** Empty when everything the source defines was applied. */
  readonly skipped: string;
};

/** A frontmatter's opening block, and the body after it. */
export type FrontmatterSplit = {
  readonly frontmatter: string;
  readonly body: string;
};

const METADATA_KEY = "metadata";
const MERGE_KEY = "<<";

/**
 * Split leading YAML frontmatter from the body, preserving both verbatim.
 *
 * A delimiter is an exact `---` line with no leading or trailing whitespace,
 * and a `---` line inside a fenced code block does not delimit.
 */
export function splitFrontmatter(content: string): FrontmatterSplit {
  const lines = splitLinesWithTerminators(content);
  const first = lines[0];
  if (first === undefined || lineWithoutTerminator(first) !== FRONTMATTER_DELIMITER) {
    return { frontmatter: "", body: content };
  }
  for (const index of unfencedLineIndices(lines)) {
    if (index === 0) {
      continue;
    }
    if (lineWithoutTerminator(lines[index] ?? "") === FRONTMATTER_DELIMITER) {
      return {
        frontmatter: lines.slice(0, index + 1).join(""),
        body: lines.slice(index + 1).join(""),
      };
    }
  }
  return { frontmatter: "", body: content };
}

/**
 * Return a destination frontmatter refreshed with the source's keys.
 *
 * A destination that cannot be read is returned unchanged with the reason in
 * `skipped`, so an unreadable document is never rewritten and the caller can
 * report why.
 */
export function refreshFrontmatter(
  frontmatter: string,
  sourceFrontmatter: string,
): RefreshedFrontmatter {
  if (frontmatter === "" || sourceFrontmatter === "") {
    return { text: frontmatter, skipped: "" };
  }
  const destination = layout(frontmatter);
  if (!destination.ok) {
    return { text: frontmatter, skipped: destination.reason };
  }
  const source = layout(sourceFrontmatter);
  if (!source.ok) {
    return { text: frontmatter, skipped: source.reason };
  }
  const merged = mergeLayouts(destination.layout, source.layout);
  if (merged.text === frontmatter) {
    return { text: frontmatter, skipped: merged.skipped };
  }
  // Lay the result out again before returning it: a merge that produced an
  // unreadable document must not be written.
  if (!layout(merged.text).ok) {
    return { text: frontmatter, skipped: "merged frontmatter is not a readable YAML mapping" };
  }
  return { text: merged.text, skipped: merged.skipped };
}

/**
 * Return whether a destination frontmatter already says what a write emits.
 *
 * The one comparison the read path uses, so `check` and a write cannot
 * disagree. Terminators are normalized because the write path emits LF only.
 */
export function frontmatterIsCurrent(
  frontmatter: string,
  sourceFrontmatter: string,
): boolean {
  const refreshed = refreshFrontmatter(frontmatter, sourceFrontmatter).text;
  return toLf(refreshed) === toLf(frontmatter);
}

type LayoutResult =
  | { readonly ok: true; readonly layout: FrontmatterLayout }
  | { readonly ok: false; readonly reason: string };

function layout(frontmatter: string): LayoutResult {
  const lines = splitLinesWithTerminators(frontmatter);
  if (lines.length < 2) {
    return { ok: false, reason: "frontmatter is not a `---` delimiter pair" };
  }
  const opening = lines[0] ?? "";
  const closing = lines[lines.length - 1] ?? "";
  if (
    lineWithoutTerminator(opening) !== FRONTMATTER_DELIMITER ||
    lineWithoutTerminator(closing) !== FRONTMATTER_DELIMITER
  ) {
    return { ok: false, reason: "frontmatter is not a `---` delimiter pair" };
  }
  const segments = segmentsOf(lines.slice(1, -1), "");
  if (!segments.ok) {
    return { ok: false, reason: segments.reason };
  }
  return {
    ok: true,
    layout: {
      opening,
      segments: segments.segments,
      trailing: segments.trailing,
      closing,
    },
  };
}

type SegmentsResult =
  | {
      readonly ok: true;
      readonly segments: readonly FrontmatterSegment[];
      readonly trailing: string;
    }
  | { readonly ok: false; readonly reason: string };

/**
 * Split lines into key blocks and verbatim comment runs at `indent`.
 *
 * A key's block runs from its key line to the line before the next key at the
 * same indent, so continuation lines, nested values and blank lines stay with
 * the key they belong to. A comment at exactly the member indent cannot sit
 * inside any value, so it becomes its own verbatim segment and is never
 * absorbed by a replaced key. A line at that indent that declares no key, a
 * YAML merge key, or a repeated key makes the document unmappable: nothing may
 * be rewritten positionally against keys it cannot trust.
 */
function segmentsOf(lines: readonly string[], indent: string): SegmentsResult {
  const segments: FrontmatterSegment[] = [];
  let separator: string[] = [];
  let current: string[] | null = null;
  let currentKey: string | null = null;
  const seen = new Set<string>();

  const closeMember = (): void => {
    if (current !== null) {
      segments.push({ key: currentKey, text: current.join("") });
      current = null;
      currentKey = null;
    }
  };

  for (const line of lines) {
    if (isMemberLine(line, indent)) {
      const key = readMemberKey(line, indent);
      if (key === null) {
        return { ok: false, reason: "frontmatter key lines cannot be mapped to their keys" };
      }
      if (key === MERGE_KEY) {
        return { ok: false, reason: "frontmatter declares a YAML merge key" };
      }
      if (seen.has(key)) {
        return { ok: false, reason: `frontmatter repeats the key ${JSON.stringify(key)}` };
      }
      seen.add(key);
      closeMember();
      if (separator.length > 0) {
        segments.push({ key: null, text: separator.join("") });
        separator = [];
      }
      current = [line];
      currentKey = key;
      continue;
    }
    if (isCommentLine(line, indent)) {
      closeMember();
      separator.push(line);
      continue;
    }
    if (current === null) {
      separator.push(line);
    } else {
      current.push(line);
    }
  }
  closeMember();
  return { ok: true, segments, trailing: separator.join("") };
}

type MergedLayout = { readonly text: string; readonly skipped: string };

function mergeLayouts(
  destination: FrontmatterLayout,
  source: FrontmatterLayout,
): MergedLayout {
  const sourceTexts = textsByKey(source.segments);
  const destinationKeys = new Set(textsByKey(destination.segments).keys());
  const notes: string[] = [];
  const parts: string[] = [destination.opening];
  for (const segment of destination.segments) {
    const key = segment.key;
    const sourceText = key === null ? undefined : sourceTexts.get(key);
    if (key === null || sourceText === undefined) {
      parts.push(segment.text);
      continue;
    }
    const replacement = replacementText(key, segment.text, sourceText);
    if (replacement.skipped !== "") {
      notes.push(replacement.skipped);
    }
    parts.push(replacement.text);
  }
  for (const segment of source.segments) {
    if (segment.key !== null && !destinationKeys.has(segment.key)) {
      parts.push(segment.text);
    }
  }
  parts.push(destination.trailing, destination.closing);
  return { text: parts.join(""), skipped: notes.join("; ") };
}

function replacementText(
  key: string,
  destinationText: string,
  sourceText: string,
): MergedLayout {
  if (key === METADATA_KEY) {
    const destinationBlock = blockOf(destinationText);
    const sourceBlock = blockOf(sourceText);
    if (
      destinationBlock !== null &&
      sourceBlock !== null &&
      destinationBlock.segments.length > 0 &&
      sourceBlock.segments.length > 0
    ) {
      return { text: choose(destinationText, mergeBlock(destinationBlock, sourceBlock)), skipped: "" };
    }
  }
  return { text: choose(destinationText, sourceText), skipped: "" };
}

type Block = {
  readonly header: string;
  readonly indent: string;
  readonly segments: readonly FrontmatterSegment[];
  readonly trailing: string;
};

function blockOf(text: string): Block | null {
  const lines = splitLinesWithTerminators(text);
  const header = lines[0];
  if (header === undefined) {
    return null;
  }
  const childIndent = firstNonBlankIndent(lines.slice(1));
  if (childIndent === null) {
    return { header, indent: "", segments: [], trailing: lines.slice(1).join("") };
  }
  const segments = segmentsOf(lines.slice(1), childIndent);
  if (!segments.ok) {
    return null;
  }
  return {
    header,
    indent: childIndent,
    segments: segments.segments,
    trailing: segments.trailing,
  };
}

function mergeBlock(destination: Block, source: Block): string {
  const sourceTexts = textsByKey(source.segments);
  const destinationKeys = new Set(textsByKey(destination.segments).keys());
  const parts: string[] = [destination.header];
  for (const segment of destination.segments) {
    const key = segment.key;
    const sourceText = key === null ? undefined : sourceTexts.get(key);
    if (key === null || sourceText === undefined) {
      parts.push(segment.text);
      continue;
    }
    parts.push(
      choose(segment.text, reindent(sourceText, source.indent, destination.indent)),
    );
  }
  for (const segment of source.segments) {
    if (segment.key !== null && !destinationKeys.has(segment.key)) {
      parts.push(reindent(segment.text, source.indent, destination.indent));
    }
  }
  parts.push(destination.trailing);
  return parts.join("");
}

function textsByKey(segments: readonly FrontmatterSegment[]): Map<string, string> {
  const texts = new Map<string, string>();
  for (const segment of segments) {
    if (segment.key !== null) {
      texts.set(segment.key, segment.text);
    }
  }
  return texts;
}

function isMemberLine(line: string, indent: string): boolean {
  if (line.trim() === "" || !line.startsWith(indent)) {
    return false;
  }
  const rest = line.slice(indent.length);
  return !/^\s/u.test(rest) && !rest.startsWith("#");
}

function isCommentLine(line: string, indent: string): boolean {
  if (!line.startsWith(indent)) {
    return false;
  }
  return line.slice(indent.length).startsWith("#");
}

/**
 * Return the key a member line declares, or `null` when it declares none.
 *
 * Only the text before the first `:` is read, so a nested value, a quoting
 * difference or a trailing comment never participates in matching.
 */
function readMemberKey(line: string, indent: string): string | null {
  const rest = line.slice(indent.length);
  const colon = rest.indexOf(":");
  if (colon <= 0) {
    return null;
  }
  const key = rest.slice(0, colon).trim();
  if (key === "") {
    return null;
  }
  return unquote(key);
}

function unquote(key: string): string {
  if (key.length >= 2) {
    const first = key.charAt(0);
    const last = key.charAt(key.length - 1);
    if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
      return key.slice(1, -1);
    }
  }
  return key;
}

function firstNonBlankIndent(lines: readonly string[]): string | null {
  for (const line of lines) {
    if (line.trim() !== "") {
      return /^[ \t]*/u.exec(line)?.[0] ?? "";
    }
  }
  return null;
}

/**
 * Return a source block with its leading indent retargeted.
 *
 * Only leading indentation changes, so quoting, spacing and scalar form are
 * copied through exactly. Text that cannot be retargeted is returned unchanged.
 */
function reindent(text: string, sourceIndent: string, destinationIndent: string): string {
  if (sourceIndent === destinationIndent) {
    return text;
  }
  const lines = splitLinesWithTerminators(text);
  if (
    !lines.every((line) => line.trim() === "" || line.startsWith(sourceIndent))
  ) {
    return text;
  }
  return lines
    .map((line) =>
      line.trim() !== "" && line.startsWith(sourceIndent)
        ? destinationIndent + line.slice(sourceIndent.length)
        : line,
    )
    .join("");
}

/** Return `destination` when `candidate` already says the same thing. */
function choose(destination: string, candidate: string): string {
  return toLf(candidate) === toLf(destination) ? destination : candidate;
}

function toLf(text: string): string {
  return text.replaceAll("\r\n", "\n").replaceAll("\r", "\n");
}
