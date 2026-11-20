/** Serialize one prepared receipt as the receipt artifact's bytes. */

import type { PreparationReceipt } from "#scripts/pr_content/domain/records.ts";

/**
 * Encode one prepared receipt as its artifact content.
 *
 * The receipt is the only artifact describing the generated body, and this encoding is the only
 * representation of it that leaves the process.
 */
export function encodePreparationReceipt(receipt: PreparationReceipt): string {
	return `${JSON.stringify(receipt)}\n`;
}
