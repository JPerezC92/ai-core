import { describe, expect, it, vi } from "vitest";

import { PreparePublication } from "#scripts/pr_content/application/prepare_publication.ts";
import { renderPublication } from "#scripts/pr_content/domain/rendering.ts";
import { isPublicationError } from "#scripts/pr_content/domain/records.ts";
import type { Publication, PublicationError } from "#scripts/pr_content/domain/records.ts";
import type { PublicationRenderer, ReservedArtifact } from "#scripts/pr_content/domain/ports.ts";
import { encodePreparationReceipt } from "#scripts/pr_content/infrastructure/adapters/prepared_receipt.ts";
import {
	makeAdvisoryFinding,
	makeCreationPublication,
	makeDecision,
	makeReviewPublication,
	TITLE,
} from "#tests/support/publication-fixtures.ts";

interface Preparation {
	readonly result: PublicationError | { readonly status: "prepared"; readonly title: string };
	readonly bodies: string[];
	readonly receipts: string[];
	readonly released: number;
}

/** Run the operation with doubled collaborators and record what it wrote. */
function prepare(
	publication: Publication | PublicationError,
	renderer: PublicationRenderer = renderPublication,
): Preparation {
	const bodies: string[] = [];
	const receipts: string[] = [];
	let released = 0;
	const reservation = (): ReservedArtifact => ({
		commit(content: string): void {
			receipts.push(content);
		},
		release(): void {
			released += 1;
		},
	});
	const result = new PreparePublication(
		() => publication,
		(_path: string, content: string) => {
			bodies.push(content);
		},
		() => reservation(),
		renderer,
		encodePreparationReceipt,
	).execute({ inputPath: "publication.json", bodyPath: "body.md", receiptPath: "body.md.receipt.json" });
	return { result, bodies, receipts, released };
}

describe("preparing one publication", () => {
	it("creates the body and its receipt from a valid creation input", () => {
		const preparation = prepare(makeCreationPublication());

		expect(preparation.result).toEqual({ status: "prepared", title: TITLE });
		expect(preparation.bodies).toHaveLength(1);
		expect(preparation.receipts).toEqual([encodePreparationReceipt({ status: "prepared", title: TITLE })]);
	});

	it("renders the canonical body of a review input", () => {
		const preparation = prepare(makeReviewPublication());

		expect(preparation.bodies[0]).toContain("## Findings / blockers");
		expect(preparation.bodies[0]).toContain("## Test evidence");
		expect(preparation.bodies[0]).toContain("- Immutable head SHA: `abc1234def5678abc1234def5678abc1234def56`");
		expect(preparation.bodies[0]).toContain("[PASS] — Zero open findings; every required check is verified\\.");
	});

	it("renders the findings table and the open debt of a deferred finding", () => {
		const base = makeReviewPublication();
		const deferral = makeDecision({ actor: "user", destination: "debt.md DEBT-070" });
		const preparation = prepare({
			...base,
			review: {
				...base.review!,
				findings: [makeAdvisoryFinding({ status: "DEFERRED", acceptance: deferral, deferral })],
				verdict: { kind: "ADVISORY", basis: "user 2026-11-20" },
			},
		});

		expect(preparation.result).toEqual({ status: "prepared", title: TITLE });
		expect(preparation.bodies[0]).toContain("| F1 | `ADVISORY` | `DEFERRED` |");
		expect(preparation.bodies[0]).toContain(
			"## Open debt\n\n- F1 — debt\\.md DEBT-070, authorized by user on 2026-11-20",
		);
		expect(preparation.bodies[0]).toContain("[ADVISORY] — user 2026-11-20");
	});

	it("returns the reader's refusal without creating an artifact", () => {
		const preparation = prepare({ code: "INPUT_INVALID", message: "valid JSON publication required" });

		expect(preparation.result).toEqual({ code: "INPUT_INVALID", message: "valid JSON publication required" });
		expect(preparation.bodies).toEqual([]);
		expect(preparation.receipts).toEqual([]);
	});

	it("refuses a body that does not match the canonical body format", () => {
		const preparation = prepare(makeCreationPublication(), () => "not a canonical body");

		expect(isPublicationError(preparation.result) ? preparation.result.code : "").toBe("BODY_INVALID");
		expect(preparation.bodies).toEqual([]);
		expect(preparation.receipts).toEqual([]);
	});

	it("releases the receipt reservation when the body cannot be created", () => {
		const failure = new Error("occupied");
		const released = vi.fn();
		const operation = new PreparePublication(
			() => makeCreationPublication(),
			() => {
				throw failure;
			},
			() => ({ commit: vi.fn(), release: released }),
			renderPublication,
			encodePreparationReceipt,
		);

		expect(() =>
			operation.execute({
				inputPath: "publication.json",
				bodyPath: "body.md",
				receiptPath: "body.md.receipt.json",
			}),
		).toThrow(failure);
		expect(released).toHaveBeenCalledOnce();
	});
});
