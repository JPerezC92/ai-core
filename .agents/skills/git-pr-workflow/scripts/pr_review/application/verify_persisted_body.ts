/** Compare supplied post-upload state with the exact intended review body. */

import { PreparedBody, ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import type { Capture, CaptureValue } from "#scripts/pr_review/domain/records.ts";

/** Report whether a captured value is a JSON object rather than an array or scalar. */
function isCaptureObject(value: CaptureValue): value is { readonly [key: string]: CaptureValue } {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Report whether two captured values carry the same content. */
function sameValue(left: CaptureValue, right: CaptureValue): boolean {
	if (left === right) return true;
	if (Array.isArray(left) || Array.isArray(right)) {
		if (!Array.isArray(left) || !Array.isArray(right) || left.length !== right.length) return false;
		return left.every((item, index) => {
			const other = right[index];
			return other !== undefined && sameValue(item, other);
		});
	}
	if (!isCaptureObject(left) || !isCaptureObject(right)) return false;
	const leftFields = new Map(Object.entries(left));
	const rightFields = new Map(Object.entries(right));
	if (leftFields.size !== rightFields.size) return false;
	for (const [key, value] of leftFields) {
		const other = rightFields.get(key);
		if (other === undefined || !sameValue(value, other)) return false;
	}
	return true;
}

export class VerifyPersistedBody {
	/** Return divergence without publishing, repairing, or retrying anything. */
	execute(expected: Capture, persisted: Capture, body: string): PreparedBody | ReviewPreparationError {
		const expectedFields = new Map(Object.entries(expected.fields));
		const persistedFields = new Map(Object.entries(persisted.fields));
		const unmatched = [...new Set([...expectedFields.keys(), ...persistedFields.keys()])]
			.filter((key) => !expectedFields.has(key) || !persistedFields.has(key))
			.sort();
		if (unmatched.length > 0) {
			return new ReviewPreparationError(
				"READBACK_DIVERGED",
				"persisted capture field set differs from the intended publication: " + unmatched.join(", "),
			);
		}
		const divergent = [...expectedFields]
			.filter(([key]) => key !== "body")
			.filter(([key, value]) => {
				const other = persistedFields.get(key);
				return other === undefined || !sameValue(value, other);
			})
			.map(([key]) => key)
			.sort();
		if (divergent.length > 0) {
			return new ReviewPreparationError(
				"READBACK_DIVERGED",
				"persisted capture fields differ from the intended publication: " + divergent.join(", "),
			);
		}
		if (persistedFields.get("body") !== body) {
			return new ReviewPreparationError(
				"READBACK_DIVERGED",
				"persisted body differs from the intended publication",
			);
		}
		return new PreparedBody(body);
	}
}
