/** Apply the publication rules to one supplied publication record. */

import { publicationError } from "#scripts/pr_content/domain/records.ts";
import type {
	Publication,
	PublicationDecision,
	PublicationError,
	PublicationFinding,
	ReviewRecord,
	TestPlanItem,
} from "#scripts/pr_content/domain/records.ts";

const TITLE =
	/^(?:build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)\([a-z0-9]+(?:-[a-z0-9]+)*\): [a-z].*[^.]$/u;
const HEAD_SHA = /^[0-9a-fA-F]{7,64}$/u;
const BASE_REF = /^[a-zA-Z0-9][a-zA-Z0-9._/-]*$/u;
const FINDING_ID = /^F[1-9][0-9]*$/u;
const CALENDAR_DATE = /^\d{4}-\d{2}-\d{2}$/u;

/** One line of authored prose without control characters. */
function plainText(value: string): boolean {
	if (value.trim() === "") return false;
	for (const character of value) {
		const code = character.codePointAt(0) ?? 0;
		if (code < 0x20 || code === 0x7f) return false;
	}
	return true;
}

/** A real calendar date in the documented form. */
function calendarDate(value: string): boolean {
	if (!CALENDAR_DATE.test(value)) return false;
	const [year, month, day] = value.split("-").map(Number) as [number, number, number];
	const date = new Date(Date.UTC(year, month - 1, day));
	return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

/** A decision carries complete provenance and, when required, a destination. */
function validDecision(decision: PublicationDecision, destinationRequired = false): boolean {
	return (
		plainText(decision.actor) &&
		calendarDate(decision.date) &&
		plainText(decision.statement) &&
		plainText(decision.evidence) &&
		(decision.destination === undefined || plainText(decision.destination)) &&
		(!destinationRequired || decision.destination !== undefined)
	);
}

/** A test item carries exactly the evidence or decision its status requires. */
function validItem(item: TestPlanItem): boolean {
	if (!plainText(item.text)) return false;
	if (item.status === "PASSED" || item.status === "FAILED") {
		return (
			item.evidence !== undefined &&
			item.decision === undefined &&
			plainText(item.evidence.action) &&
			plainText(item.evidence.result) &&
			plainText(item.evidence.executor)
		);
	}
	if (item.status === "NOT_APPLICABLE") {
		return item.evidence === undefined && item.decision !== undefined && validDecision(item.decision);
	}
	return item.status === "PENDING" && item.evidence === undefined && item.decision === undefined;
}

/** A finding carries its identity, its disposition and the decisions that apply to it. */
function validFinding(finding: PublicationFinding, index: number): boolean {
	if (finding.id !== `F${index + 1}` || !FINDING_ID.test(finding.id)) return false;
	if (!plainText(finding.evidence) || !plainText(finding.resolution)) return false;
	if ((finding.status === "DEFERRED") !== (finding.deferral !== undefined)) return false;
	if (finding.deferral !== undefined && !validDecision(finding.deferral, true)) return false;
	if (finding.acceptance !== undefined) {
		if (finding.severity !== "ADVISORY" || finding.status === "FIXED" || finding.status === "REJECTED")
			return false;
		if (!validDecision(finding.acceptance)) return false;
	}
	return true;
}

/** A verdict states readiness that the current findings and test states support. */
function validVerdict(review: ReviewRecord, testPlan: readonly TestPlanItem[]): boolean {
	const verdict = review.verdict;
	if (verdict === undefined) return true;
	if (!plainText(verdict.basis)) return false;
	if (verdict.kind === "BLOCK") return false;
	const unresolved = review.findings.filter((finding) => finding.status !== "FIXED" && finding.status !== "REJECTED");
	if (testPlan.some((item) => item.status === "PENDING" || item.status === "FAILED")) return false;
	if (verdict.kind === "PASS") return unresolved.length === 0;
	if (unresolved.length === 0) return false;
	for (const finding of unresolved) {
		if (finding.severity !== "ADVISORY" || finding.acceptance === undefined) return false;
		if (!verdict.basis.includes(finding.acceptance.actor)) return false;
		if (!verdict.basis.includes(finding.acceptance.date)) return false;
	}
	return true;
}

/** A review record carries its identity, its findings, its debt and its verdict. */
function validReview(review: ReviewRecord, testPlan: readonly TestPlanItem[]): boolean {
	if (
		!Number.isInteger(review.prNumber) ||
		review.prNumber < 1 ||
		!HEAD_SHA.test(review.headSha) ||
		!BASE_REF.test(review.baseRef) ||
		review.baseRef.includes("..")
	)
		return false;
	if (review.findings.some((finding, index) => !validFinding(finding, index))) return false;
	const findingIds = new Set(review.findings.map((finding) => finding.id));
	if (
		new Set(review.debt.map((entry) => entry.target)).size !== review.debt.length ||
		review.debt.some(
			(entry) => !plainText(entry.target) || !validDecision(entry, true) || findingIds.has(entry.target),
		)
	)
		return false;
	return validVerdict(review, testPlan);
}

/**
 * Validate one supplied publication record against the publication rules.
 *
 * The record's own assertions are never treated as proof of authority; this check only proves
 * that the record is internally consistent and complete enough to render a body.
 */
export function validatePublication(publication: Publication): Publication | PublicationError {
	if (
		publication.schemaVersion !== 1 ||
		!plainText(publication.title) ||
		publication.title.length >= 70 ||
		!TITLE.test(publication.title)
	)
		return publicationError("INPUT_INVALID", "conventional title under 70 characters required");
	if (publication.summary.length < 1 || publication.summary.length > 3 || !publication.summary.every(plainText))
		return publicationError("INPUT_INVALID", "one to three summary bullets required");
	if (
		publication.breakingChanges !== undefined &&
		(!plainText(publication.breakingChanges.description) || !plainText(publication.breakingChanges.migration))
	)
		return publicationError("INPUT_INVALID", "breaking changes require a description and a migration");
	if (
		publication.testPlan.length < 2 ||
		new Set(publication.testPlan.map((item) => item.text)).size !== publication.testPlan.length
	)
		return publicationError("INPUT_INVALID", "at least two unique test-plan items required");
	for (const item of publication.testPlan) {
		if (!plainText(item.text)) return publicationError("INPUT_INVALID", "test-plan items require one line of text");
		if (!validItem(item))
			return publicationError("INPUT_INVALID", "test item status requires its matching evidence or decision");
	}
	if (publication.review === undefined) {
		if (publication.testPlan.some((item) => item.status !== "PENDING"))
			return publicationError("INPUT_INVALID", "a creation input carries only pending test items");
		return publication;
	}
	if (!validReview(publication.review, publication.testPlan)) {
		if (publication.review.verdict?.kind === "BLOCK")
			return publicationError("INPUT_INVALID", "a blocked review produces no publication body");
		return publicationError("INPUT_INVALID", "review record must match its findings, debt and test states");
	}
	return publication;
}
