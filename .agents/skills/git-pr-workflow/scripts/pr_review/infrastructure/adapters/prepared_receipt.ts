/** Map a decoded publication receipt to the generated title it carries. */

import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";

/** Report whether a decoded value is a JSON object. */
function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * Read the generated title from a prepared artifact receipt.
 *
 * The receipt is the only source of the title in this workflow: it carries exactly a prepared
 * status and the title, and no byte identity of any earlier or later artifact.
 */
export function publicationTitle(receipt: unknown): string | ReviewPreparationError {
	const error = new ReviewPreparationError(
		"PUBLICATION_DIVERGED",
		"generated publication receipt must carry exactly a prepared status and a title",
	);
	if (!isRecord(receipt)) return error;
	const fields = ["status", "title"];
	if (Object.keys(receipt).length !== fields.length || fields.some((key) => !Object.hasOwn(receipt, key)))
		return error;
	if (receipt.status !== "prepared" || typeof receipt.title !== "string") return error;
	if (receipt.title.trim() === "" || /[\r\n]/u.test(receipt.title)) return error;
	return receipt.title;
}
