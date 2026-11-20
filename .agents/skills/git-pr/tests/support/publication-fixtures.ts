/** Shared fixtures for pull-request publication preparation. */

import { PreparePublication } from "#scripts/pr_content/application/prepare_publication.ts";
import { renderPublication } from "#scripts/pr_content/domain/rendering.ts";
import { isPublicationError } from "#scripts/pr_content/domain/records.ts";
import type {
	Publication,
	PublicationDebt,
	PublicationDecision,
	PublicationFinding,
	TestEvidence,
} from "#scripts/pr_content/domain/records.ts";
import { encodePreparationReceipt } from "#scripts/pr_content/infrastructure/adapters/prepared_receipt.ts";

export const HEAD_SHA = "abc1234def5678abc1234def5678abc1234def56";
export const BASE_REF = "main";
export const TITLE = "feat(review): prepare publication";
export const SUMMARY = "Adds the review preparation commands.";
export const FIRST_ITEM = "Run the focused suite";
export const SECOND_ITEM = "Confirm the import map resolves";

/** The observed result of one passed test item. */
export function makeEvidence(): TestEvidence {
	return { action: "pnpm vitest run", result: "All focused tests passed; exit 0.", executor: "Cipher" };
}

/** The provenance of one decision. */
export function makeDecision(overrides: Partial<PublicationDecision> = {}): PublicationDecision {
	return {
		actor: "author",
		date: "2026-11-20",
		statement: "not applicable for this change",
		evidence: "the author's scope assessment in the change record",
		...overrides,
	};
}

/** One advisory finding awaiting the user's acceptance. */
export function makeAdvisoryFinding(overrides: Partial<PublicationFinding> = {}): PublicationFinding {
	return {
		id: "F1",
		severity: "ADVISORY",
		status: "OPEN",
		evidence: "candidate C1 leaves the deprecated option reachable",
		resolution: "Cipher — await the user's decision",
		...overrides,
	};
}

/** One authorized follow-up that is not already a deferred finding. */
export function makeDebt(overrides: Partial<PublicationDebt> = {}): PublicationDebt {
	return {
		target: "follow-up",
		actor: "user",
		date: "2026-11-20",
		statement: "authorized follow-up",
		evidence: "the user's instruction in the delivery conversation",
		destination: "debt.md DEBT-070",
		...overrides,
	};
}

/** A creation-stage publication document. */
export interface CreationDocument {
	readonly schemaVersion: number;
	readonly title: string;
	readonly summary: string[];
	readonly testPlan: readonly { readonly text: string; readonly status: string }[];
}

/** A review-stage publication document. */
export interface ReviewDocument {
	readonly schemaVersion: number;
	readonly title: string;
	readonly summary: string[];
	readonly testPlan: readonly Record<string, unknown>[];
	readonly review: {
		readonly prNumber: number;
		readonly headSha: string;
		readonly baseRef: string;
		readonly findings: readonly Record<string, unknown>[];
		readonly debt: readonly Record<string, unknown>[];
		readonly verdict: { readonly kind: string; readonly basis: string };
	};
}

/** A creation-stage publication document. */
export function makeCreationDocument(): CreationDocument {
	return {
		schemaVersion: 1,
		title: TITLE,
		summary: [SUMMARY],
		testPlan: [
			{ text: FIRST_ITEM, status: "PENDING" },
			{ text: SECOND_ITEM, status: "PENDING" },
		],
	};
}

/** A creation-stage publication document as its JSON input. */
export function makeCreationInput(): string {
	return JSON.stringify(makeCreationDocument());
}

/** A review-stage publication document. */
export function makeReviewDocument(): ReviewDocument {
	return {
		schemaVersion: 1,
		title: TITLE,
		summary: [SUMMARY],
		testPlan: [
			{ text: FIRST_ITEM, status: "PASSED", evidence: makeEvidence() },
			{ text: SECOND_ITEM, status: "NOT_APPLICABLE", decision: makeDecision() },
		],
		review: {
			prNumber: 12,
			headSha: HEAD_SHA,
			baseRef: BASE_REF,
			findings: [],
			debt: [],
			verdict: { kind: "PASS", basis: "Zero open findings; every required check is verified." },
		},
	};
}

/** A review-stage publication document as its JSON input. */
export function makeReviewInput(): string {
	return JSON.stringify(makeReviewDocument());
}

/** A typed creation-stage publication record. */
export function makeCreationPublication(): Publication {
	return {
		schemaVersion: 1,
		title: TITLE,
		summary: [SUMMARY],
		testPlan: [
			{ text: FIRST_ITEM, status: "PENDING" },
			{ text: SECOND_ITEM, status: "PENDING" },
		],
	};
}

/** A typed review-stage publication record. */
export function makeReviewPublication(): Publication {
	return {
		schemaVersion: 1,
		title: TITLE,
		summary: [SUMMARY],
		testPlan: [
			{ text: FIRST_ITEM, status: "PASSED", evidence: makeEvidence() },
			{ text: SECOND_ITEM, status: "NOT_APPLICABLE", decision: makeDecision() },
		],
		review: {
			prNumber: 12,
			headSha: HEAD_SHA,
			baseRef: BASE_REF,
			findings: [],
			debt: [],
			verdict: { kind: "PASS", basis: "Zero open findings; every required check is verified." },
		},
	};
}

/**
 * Prepare one supplied publication record with every collaborator doubled.
 *
 * The case observes only the operation's acceptance or refusal, so the doubles record nothing and
 * the caller supplies the record it wants judged.
 */
export function refusePublication(publication: Publication): string {
	const result = new PreparePublication(
		() => publication,
		() => undefined,
		() => ({ commit: () => undefined, release: () => undefined }),
		renderPublication,
		encodePreparationReceipt,
	).execute({ inputPath: "publication.json", bodyPath: "body.md", receiptPath: "body.md.receipt.json" });
	return isPublicationError(result) ? result.code : "";
}
