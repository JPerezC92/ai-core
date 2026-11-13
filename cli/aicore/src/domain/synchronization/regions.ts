/**
 * Region parsing and rendering (pure).
 *
 * A marked document splits into the bytes before, inside and after its single
 * core region. A splice replaces only the region, so the markers, the text after
 * the end marker, and the non-frontmatter pre-marker text keep their bytes; the
 * frontmatter is refreshed from the source instead.
 */

import { CORE_BEGIN, CORE_END, PROJECT_BEGIN, PROJECT_END } from "./constants.ts";
import { refreshFrontmatter, splitFrontmatter } from "./frontmatter.ts";
import {
  findCoreMarkers,
  hasExactCoreMarkerLines,
  hasExactProjectMarkerLines,
  splitLinesWithTerminators,
} from "./markers.ts";

/** A marked file split into the bytes before, inside and after its region. */
export type RegionSplit = {
  readonly before: string;
  readonly beginLine: string;
  readonly region: string;
  readonly endLine: string;
  readonly after: string;
};

/** The result of reading a source document's core. */
export type SourceCoreRead =
  | { readonly kind: "core"; readonly core: string }
  | { readonly kind: "malformed" };

/** Rebuilt region text, and why its frontmatter could not be refreshed. */
export type RenderedRegion = {
  readonly text: string;
  readonly skipped: string;
};

/**
 * Split content into the bytes around and inside its single core region.
 *
 * `null` means the document is not a valid marked document: a region-mode
 * destination must carry exactly one ordered core pair.
 */
export function splitRegions(content: string): RegionSplit | null {
  const markers = findCoreMarkers(content);
  if (markers === null) {
    return null;
  }
  const lines = splitLinesWithTerminators(content);
  return {
    before: lines.slice(0, markers.begin).join(""),
    beginLine: lines[markers.begin] ?? "",
    region: lines.slice(markers.begin + 1, markers.end).join(""),
    endLine: lines[markers.end] ?? "",
    after: lines.slice(markers.end + 1).join(""),
  };
}

/**
 * Return the bytes a region splice must never change.
 *
 * The core markers, the text after the end marker, and the pre-marker text that
 * follows the frontmatter. The region is excluded because a splice replaces it,
 * and the frontmatter is excluded because a refresh rewrites its keys.
 */
export function protectedBytes(split: RegionSplit): string {
  const { body } = splitFrontmatter(split.before);
  return body + split.beginLine + split.endLine + split.after;
}

/**
 * Return a source file's core bytes.
 *
 * A valid marker pair yields its region. A markerless source uses its whole
 * post-frontmatter body. A document that carries exact core or project marker
 * lines but no single ordered core pair is malformed: its project content is
 * never read as core.
 */
export function extractSourceCore(content: string): SourceCoreRead {
  const split = splitRegions(content);
  if (split !== null) {
    return { kind: "core", core: split.region };
  }
  if (hasExactCoreMarkerLines(content) || hasExactProjectMarkerLines(content)) {
    return { kind: "malformed" };
  }
  return { kind: "core", core: splitFrontmatter(content).body };
}

/** Return `text` with a trailing newline, adding one only when missing. */
export function ensureTrailingNewline(text: string): string {
  if (text === "" || text.endsWith("\n")) {
    return text;
  }
  return `${text}\n`;
}

/**
 * Rebuild a destination file with the source core region spliced in.
 *
 * The destination's pre-marker frontmatter is refreshed from the source, the
 * non-frontmatter pre-marker text, the marker lines and the text after the end
 * marker keep their bytes.
 */
export function renderWithRegion(
  destination: RegionSplit,
  sourceRegion: string,
  sourceFrontmatter: string,
): RenderedRegion {
  const { frontmatter, body } = splitFrontmatter(destination.before);
  const refresh = refreshFrontmatter(frontmatter, sourceFrontmatter);
  return {
    text:
      refresh.text +
      body +
      destination.beginLine +
      sourceRegion +
      destination.endLine +
      destination.after,
    skipped: refresh.skipped,
  };
}

/**
 * Rebuild a markerless destination as a core region plus a project region.
 *
 * An existing destination keeps its own frontmatter keys with the source's
 * values merged in; a destination that did not exist leads with the source
 * frontmatter instead, because there is nothing of the destination's to keep.
 * The frontmatter always ends on its own line so the core begin marker stays an
 * exact line; the source core fills the new core region; everything after the
 * frontmatter moves verbatim into the new project region.
 */
export function renderInitFile(
  destinationContent: string,
  sourceCore: string,
  sourceFrontmatter: string,
): RenderedRegion {
  const { frontmatter, body } = splitFrontmatter(destinationContent);
  const refresh =
    frontmatter === ""
      ? { text: sourceFrontmatter, skipped: "" }
      : refreshFrontmatter(frontmatter, sourceFrontmatter);
  return {
    text:
      ensureTrailingNewline(refresh.text) +
      `${CORE_BEGIN}\n` +
      ensureTrailingNewline(sourceCore) +
      `${CORE_END}\n\n` +
      `${PROJECT_BEGIN}\n` +
      ensureTrailingNewline(body) +
      `${PROJECT_END}\n`,
    skipped: refresh.skipped,
  };
}
