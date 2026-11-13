/**
 * The reconciliation blocker's transform (pure).
 *
 * While region-mode paths remain in `pending`, the destination root runtime file
 * carries a marker-delimited block: appended after one blank line when absent,
 * replaced in place on later runs, and removed together with its one-line
 * separator once `pending` is empty. The transform is idempotent and changes
 * nothing outside the block.
 */

import { RECONCILE_BEGIN, RECONCILE_BODY, RECONCILE_END } from "./constants.ts";
import { findReconcileBlock, splitLinesWithTerminators } from "./markers.ts";

/** One destination `init` generated or refreshed for review. */
export type ReconciliationEntry = {
  readonly destination: string;
  readonly source: string;
  readonly action: string;
};

/** The block's lines, terminators included. */
function blockLines(): readonly string[] {
  return [`${RECONCILE_BEGIN}\n`, `${RECONCILE_BODY.join("\n")}\n`, `${RECONCILE_END}\n`];
}

/**
 * Add, refresh, or remove the blocker block in a root file's text.
 *
 * A non-empty `pending` ensures the block exists; an empty `pending` removes it
 * and one adjacent blank separator line.
 */
export function syncReconciliationBlocker(
  rootText: string,
  pending: readonly string[],
): string {
  const lines = splitLinesWithTerminators(rootText);
  const block = findReconcileBlock(lines);
  if (pending.length > 0) {
    if (block !== null) {
      return (
        lines.slice(0, block.begin).join("") +
        blockLines().join("") +
        lines.slice(block.end + 1).join("")
      );
    }
    return appendBlock(rootText);
  }
  if (block === null) {
    return rootText;
  }
  const start = block.begin > 0 && (lines[block.begin - 1] ?? "").trim() === ""
    ? block.begin - 1
    : block.begin;
  const stop =
    block.end + 1 < lines.length && (lines[block.end + 1] ?? "").trim() === ""
      ? block.end + 2
      : block.end + 1;
  return lines.slice(0, start).join("") + lines.slice(stop).join("");
}

/** Append the block after a single blank separator line. */
function appendBlock(rootText: string): string {
  const base = rootText !== "" && !rootText.endsWith("\n") ? `${rootText}\n` : rootText;
  const separator = base === "" ? "" : "\n";
  return base + separator + blockLines().join("");
}
