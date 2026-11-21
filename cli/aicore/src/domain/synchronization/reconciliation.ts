/**
 * The reconciliation blocker's transform (pure).
 *
 * While region-mode paths remain in `pending`, the destination root runtime file
 * carries a marker-delimited block: appended after one blank line when absent,
 * replaced in place on later runs, and removed together with its one-line
 * separator once `pending` is empty. The transform is idempotent and changes
 * nothing outside the block.
 *
 * The block's words are the enrolled editor's, not one destination's: the
 * project-configuration section describes a file only some profiles receive, so
 * a destination enrolled for another editor is never told it was merged.
 */

import {
	RECONCILE_BEGIN,
	RECONCILE_BODY_CONFIG,
	RECONCILE_BODY_HEAD,
	RECONCILE_BODY_TAIL,
	RECONCILE_END,
} from "./constants.ts";
import type { EditorProfile } from "./editor-profile.ts";
import type { AbsentSource, WithheldReason } from "./bindings.ts";
import { findReconcileBlock, splitLinesWithTerminators } from "./markers.ts";

/** The editors whose delivery includes the project-configuration file. */
const CONFIG_FILE_EDITORS: readonly EditorProfile[] = ["opencode"];

/** One destination `init` generated or refreshed for review. */
export type ReconciliationEntry = {
	readonly destination: string;
	readonly source: string;
	readonly action: string;
};

/**
 * Flatten blocked bindings into the blocker's per-destination view.
 *
 * The blocker names one line per affected destination, because that is the file
 * its reader has to reconcile.
 */
export function missingRegionSources(blocked: readonly AbsentSource[]): readonly MissingRegionSource[] {
	return blocked.flatMap((entry) =>
		entry.destinations.map((destination) => ({ source: entry.source, destination, reason: entry.reason })),
	);
}

/** A previously distributed source that can no longer be reconciled automatically. */
export type MissingRegionSource = {
	readonly source: string;
	readonly destination: string;
	readonly reason: WithheldReason;
};

/** How each reason reads in the blocker. */
const REASON_PHRASE: Readonly<Record<WithheldReason, string>> = {
	missing: "no longer exists at its registered source path",
	withdrawn: "is withdrawn from distribution for this project",
	unestablished: "has no clearance record, so its previous ownership cannot be established",
	anomaly: "still exists but is not distributable to this project",
};

/**
 * The section naming sources that are no longer distributed.
 *
 * The words follow the reason: a source that is gone or withdrawn needs its
 * correspondence established, while a source whose ownership or eligibility is
 * unresolved needs the configuration investigated before anything is touched.
 * Both keep the destination file and withhold a verified "current".
 */
function unresolvedSourceSection(missing: readonly MissingRegionSource[]): readonly string[] {
	if (missing.length === 0) {
		return [];
	}
	const reasons = new Set(missing.map((item) => item.reason));
	const lines: string[] = [
		"> **🚫 RECONCILIATION REQUIRED — UNRESOLVED MANAGED SOURCE.**",
		">",
		"> One or more previously distributed sources can no longer be reconciled automatically. Every destination file named below is PRESERVED: a shared file may hold project-owned content, so none of it is deleted or overwritten automatically.",
		">",
	];
	for (const item of missing) {
		lines.push(
			`> - Source: \`${item.source}\` → Destination: \`${item.destination}\` — ${REASON_PHRASE[item.reason]}`,
		);
	}
	lines.push(">");
	if (reasons.has("missing") || reasons.has("withdrawn")) {
		lines.push(
			"> **Required action — the source is missing or withdrawn:**",
			"> 1. Investigate whether the core source file was renamed, relocated, retired, or withdrawn from this project's distribution.",
			"> 2. Identify the correct source and destination correspondence for each file listed above.",
			"> 3. Reconcile through the existing supported workflow for that file's ownership mode, as described below.",
			">",
		);
	}
	if (reasons.has("unestablished") || reasons.has("anomaly")) {
		lines.push(
			"> **Required action — ownership or eligibility is unresolved:**",
			"> 1. Investigate this project's distribution configuration and whether the source is still meant to be shared with it.",
			"> 2. Establish the file's ownership and the intended correspondence before changing anything.",
			"> 3. Reconcile through the existing supported workflow once the intent is established.",
			">",
		);
	}
	lines.push(
		"> **Reconcile each file by its ownership mode — the procedures differ:**",
		"> - A **region-managed** file holds destination-owned content between its `<!-- project:begin -->` and `<!-- project:end -->` markers. Reconcile it in that region and leave the core region untouched.",
		"> - A **merge-managed** JSON file holds destination-owned top-level keys alongside the Core-owned ones, and its own formatting and comments. Reconcile it without deleting a destination-owned key and without replacing the document with an empty or default object.",
		"> - Use only the procedure this project already supports for that mode. Do not invent a migration, a rename or a replacement path.",
		">",
		"> In every case above: preserve the file and its destination-owned content, do not guess ownership, do not delete anything silently, and never migrate destination-owned content arbitrarily. If the correct reconciliation cannot be established confidently, STOP that reconciliation attempt and ask the user.",
		">",
		"> This project's reconciliation remains outstanding until this condition is resolved, and resolving an ordinary pending region update does not resolve it.",
		">",
	);
	return lines;
}

/**
 * The blocker body one editor receives.
 *
 * One body, selected rather than rewritten: the shared opening and closing stay
 * identical, and only the configuration section an editor's delivery does not
 * contain is left out.
 */
function reconciliationBody(editor: EditorProfile, missing: readonly MissingRegionSource[]): readonly string[] {
	const head = [...RECONCILE_BODY_HEAD, ...unresolvedSourceSection(missing)];
	return CONFIG_FILE_EDITORS.includes(editor)
		? [...head, ...RECONCILE_BODY_CONFIG, ...RECONCILE_BODY_TAIL]
		: [...head, ...RECONCILE_BODY_TAIL];
}

/** The block's lines, terminators included. */
function blockLines(editor: EditorProfile, missing: readonly MissingRegionSource[]): readonly string[] {
	return [`${RECONCILE_BEGIN}\n`, `${reconciliationBody(editor, missing).join("\n")}\n`, `${RECONCILE_END}\n`];
}

/**
 * Add, refresh, or remove the blocker block in a root file's text.
 *
 * A non-empty `pending`, or a missing region-managed source, ensures the block
 * exists; when both are empty the block and one adjacent blank separator line are
 * removed.
 */
export function syncReconciliationBlocker(
	rootText: string,
	pending: readonly string[],
	editor: EditorProfile,
	missing: readonly MissingRegionSource[] = [],
): string {
	const lines = splitLinesWithTerminators(rootText);
	const block = findReconcileBlock(lines);
	if (pending.length > 0 || missing.length > 0) {
		if (block !== null) {
			return (
				lines.slice(0, block.begin).join("") +
				blockLines(editor, missing).join("") +
				lines.slice(block.end + 1).join("")
			);
		}
		return appendBlock(rootText, editor, missing);
	}
	if (block === null) {
		return rootText;
	}
	const start = block.begin > 0 && (lines[block.begin - 1] ?? "").trim() === "" ? block.begin - 1 : block.begin;
	const stop =
		block.end + 1 < lines.length && (lines[block.end + 1] ?? "").trim() === "" ? block.end + 2 : block.end + 1;
	return lines.slice(0, start).join("") + lines.slice(stop).join("");
}

/** Append the block after a single blank separator line. */
function appendBlock(rootText: string, editor: EditorProfile, missing: readonly MissingRegionSource[]): string {
	const base = rootText !== "" && !rootText.endsWith("\n") ? `${rootText}\n` : rootText;
	const separator = base === "" ? "" : "\n";
	return base + separator + blockLines(editor, missing).join("");
}
