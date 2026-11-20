/** Decode a supplied pull-request capture into its typed field set. */

import { z } from "zod";

import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import type { Capture, CaptureValue } from "#scripts/pr_review/domain/records.ts";

/**
 * A capture's values are the JSON values its owner supplied.
 *
 * The workflow never redeclares the capture's field schema: the persisted capture inherits the
 * field set its owner produced, so this adapter types the values and preserves every field.
 */
const captureDocumentSchema = z.record(z.string(), z.json());

/** Map a decoded capture document into the typed capture it carries. */
function toCapture(document: Readonly<Record<string, CaptureValue>>): Capture {
	return { fields: { ...document } };
}

/** Decode one supplied capture into typed data or a business rejection. */
export function decodeCapture(value: unknown): Capture | ReviewPreparationError {
	const parsed = captureDocumentSchema.safeParse(value);
	if (!parsed.success) {
		return new ReviewPreparationError("READBACK_DIVERGED", "baseline and persisted captures must be objects");
	}
	return toCapture(parsed.data);
}
