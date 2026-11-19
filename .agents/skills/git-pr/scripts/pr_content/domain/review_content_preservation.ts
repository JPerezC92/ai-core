/** Protect baseline prose, exact test items and persistent finding identities. */

import { PROTECTED_SECTIONS, parseFindings, parseSections } from "#scripts/pr_content/domain/body_validation.ts";
import type { ReviewDecisions, ReviewPreparationError } from "#scripts/pr_content/domain/records.ts";
import { isReviewError, reviewError } from "#scripts/pr_content/domain/records.ts";

function normalizeCheckboxes(plan: string): string {
	return plan.replace(/^- \[[ x]\] /gm, "- [ ] ");
}

function findingRegion(content: string): string {
	// The verdict line follows the findings section in a completed body; strip it before the
	// findings parser runs, or a compliant body fails its own preservation check.
	return content.split(/^\[(?:PASS|ADVISORY|BLOCK)\] —/m)[0] ?? "";
}

/**
 * Allow review-section updates without granting authority to rewrite protected prose.
 *
 * A protected section is byte-preserved unless the supplied decisions file names that exact
 * section in `authorized_updates`. That record is *scope*, not proof: it carries the
 * identifier of the user instruction Herald must verify from its attributable source before
 * performing the update, and the tool cannot authenticate it. Everything the tool enforces is
 * mechanical — the changed section must be the one named, and every other protected section
 * must stay byte-identical — so a self-declared entry narrows a change but never authorizes one.
 */
export function validatePreservation(
	baseline: string,
	candidate: string,
	decisions: ReviewDecisions = { notApplicable: [], acceptance: [], debt: [], authorizedUpdates: [] },
): ReviewPreparationError | undefined {
	const error = reviewError("BODY_INVALID", "protected baseline review content changed");
	const before = parseSections(baseline);
	if (isReviewError(before)) return before;
	const after = parseSections(candidate);
	if (isReviewError(after)) return after;

	const authorized = new Set(decisions.authorizedUpdates.map((update) => update.section));
	for (const heading of PROTECTED_SECTIONS) {
		if (before[heading] === after[heading]) continue;
		if (!authorized.has(heading)) return error;
	}
	if (normalizeCheckboxes(before["Test plan"] ?? "") !== normalizeCheckboxes(after["Test plan"] ?? "")) return error;

	const previous = parseFindings(findingRegion(before["Findings / blockers"] ?? ""));
	if (isReviewError(previous)) return previous;
	const updated = parseFindings(findingRegion(after["Findings / blockers"] ?? ""));
	if (isReviewError(updated)) return updated;

	if (updated.length < previous.length) return error;
	for (const [index, original] of previous.entries()) {
		const current = updated[index]!;
		if (original.id !== current.id || original.severity !== current.severity) return error;
	}
	return undefined;
}
