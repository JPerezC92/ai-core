/** Typed publication records and the business failures they can carry. */

/** An observed result for one test-plan item. */
export interface TestEvidence {
	readonly action: string;
	readonly result: string;
	readonly executor: string;
}

/**
 * The provenance of one decision.
 *
 * A decision records a claim to verify; it never authenticates itself.
 */
export interface PublicationDecision {
	readonly actor: string;
	readonly date: string;
	readonly statement: string;
	readonly evidence: string;
	readonly destination?: string;
}

export type TestStatus = "PENDING" | "PASSED" | "FAILED" | "NOT_APPLICABLE";

/** One test-plan item and the explicit state its author recorded. */
export interface TestPlanItem {
	readonly text: string;
	readonly status: TestStatus;
	readonly evidence?: TestEvidence;
	readonly decision?: PublicationDecision;
}

export type FindingSeverity = "BLOCK" | "ADVISORY";

export type FindingStatus = "OPEN" | "IN PROGRESS" | "FIXED" | "DEFERRED" | "REJECTED";

/** One review finding and the decisions that apply to it. */
export interface PublicationFinding {
	readonly id: string;
	readonly severity: FindingSeverity;
	readonly status: FindingStatus;
	readonly evidence: string;
	readonly resolution: string;
	readonly acceptance?: PublicationDecision;
	readonly deferral?: PublicationDecision;
}

/** An authorized follow-up that is not already a deferred finding. */
export interface PublicationDebt extends PublicationDecision {
	readonly target: string;
	readonly destination: string;
}

export type VerdictKind = "PASS" | "ADVISORY" | "BLOCK";

/** The review record of one pull request at one immutable head. */
export interface ReviewRecord {
	readonly prNumber: number;
	readonly headSha: string;
	readonly baseRef: string;
	readonly findings: readonly PublicationFinding[];
	readonly debt: readonly PublicationDebt[];
	readonly verdict?: { readonly kind: VerdictKind; readonly basis: string };
}

/** The single structured publication input of one pull request. */
export interface Publication {
	readonly schemaVersion: 1;
	readonly title: string;
	readonly summary: readonly string[];
	readonly breakingChanges?: { readonly description: string; readonly migration: string };
	readonly testPlan: readonly TestPlanItem[];
	readonly review?: ReviewRecord;
}

/** A stable rejection code and explanation returned as a value. */
export interface PublicationError {
	readonly code: string;
	readonly message: string;
}

/** The receipt of one prepared publication artifact. */
export interface PreparationReceipt {
	readonly status: "prepared";
	readonly title: string;
}

export function publicationError(code: string, message: string): PublicationError {
	return { code, message };
}

/** Narrow a value to a returned business failure. */
export function isPublicationError(value: unknown): value is PublicationError {
	return (
		typeof value === "object" &&
		value !== null &&
		typeof (value as PublicationError).code === "string" &&
		typeof (value as PublicationError).message === "string"
	);
}
