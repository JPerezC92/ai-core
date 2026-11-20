/** The generated title the workflow reads from a prepared publication receipt. */

import { describe, expect, it } from "vitest";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import { publicationTitle } from "#scripts/pr_review/infrastructure/adapters/prepared_receipt.ts";
import { createLocalTitle, createPublicationHandoff } from "#tests/support/review-fixtures.ts";

describe("reading the generated title from a prepared receipt", () => {
	it("reads the title the prepared receipt carries", () => {
		const handoff = createPublicationHandoff();

		const result = publicationTitle(JSON.parse(handoff.receipt));

		expect(result).not.toBeInstanceOf(ReviewPreparationError);
		expect(result).toBe(createLocalTitle());
	});

	it("rejects a receipt that is not exactly the prepared status and title pair", () => {
		const receipts: unknown[] = [
			{ title: "no receipt" },
			{ status: "prepared" },
			{ status: "published", title: "feat(release): prepare local review" },
			{ status: "prepared", title: "   " },
			{ status: "prepared", title: "feat(release): prepare\nlocal review" },
			{ status: "prepared", title: "feat(release): prepare local review", bodySha256: "f".repeat(64) },
		];

		for (const receipt of receipts) {
			const result = publicationTitle(receipt);

			expect(result, JSON.stringify(receipt)).toBeInstanceOf(ReviewPreparationError);
			expect(result).toMatchObject({
				code: "PUBLICATION_DIVERGED",
				message: "generated publication receipt must carry exactly a prepared status and a title",
			});
		}
	});
});
