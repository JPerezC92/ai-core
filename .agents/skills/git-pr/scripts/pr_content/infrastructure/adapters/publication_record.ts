/** Map untrusted external publication records into typed publication data. */

import { z } from "zod";

import { publicationError } from "#scripts/pr_content/domain/records.ts";
import type {
	Publication,
	PublicationDebt,
	PublicationDecision,
	PublicationError,
	PublicationFinding,
	ReviewRecord,
	TestEvidence,
	TestPlanItem,
} from "#scripts/pr_content/domain/records.ts";

/**
 * The external document's shape.
 *
 * These schemas accept the documented fields and their types only; every cross-field rule
 * (status/evidence/decision exclusivity, verdict readiness, deferral/debt, duplicate targets)
 * belongs to the domain validator and is never duplicated here.
 */
const evidenceSchema = z.strictObject({
	action: z.string(),
	result: z.string(),
	executor: z.string(),
});

const decisionSchema = z.strictObject({
	actor: z.string(),
	date: z.string(),
	statement: z.string(),
	evidence: z.string(),
	destination: z.string().optional(),
});

const testStatusSchema = z.enum(["PENDING", "PASSED", "FAILED", "NOT_APPLICABLE"]);

const itemSchema = z.strictObject({
	text: z.string(),
	status: testStatusSchema,
	evidence: evidenceSchema.optional(),
	decision: decisionSchema.optional(),
});

const severitySchema = z.enum(["BLOCK", "ADVISORY"]);
const findingStatusSchema = z.enum(["OPEN", "IN PROGRESS", "FIXED", "DEFERRED", "REJECTED"]);

const findingSchema = z.strictObject({
	id: z.string(),
	severity: severitySchema,
	status: findingStatusSchema,
	evidence: z.string(),
	resolution: z.string(),
	acceptance: decisionSchema.optional(),
	deferral: decisionSchema.optional(),
});

const debtSchema = z.strictObject({
	target: z.string(),
	actor: z.string(),
	date: z.string(),
	statement: z.string(),
	evidence: z.string(),
	destination: z.string(),
});

const verdictSchema = z.strictObject({
	kind: z.enum(["PASS", "ADVISORY", "BLOCK"]),
	basis: z.string(),
});

const reviewSchema = z.strictObject({
	prNumber: z.number(),
	headSha: z.string(),
	baseRef: z.string(),
	findings: z.array(findingSchema),
	debt: z.array(debtSchema),
	verdict: verdictSchema.optional(),
});

const documentSchema = z.strictObject({
	schemaVersion: z.literal(1),
	title: z.string(),
	summary: z.array(z.string()),
	breakingChanges: z.strictObject({ description: z.string(), migration: z.string() }).optional(),
	testPlan: z.array(itemSchema),
	review: reviewSchema.optional(),
});

type DecisionInput = z.infer<typeof decisionSchema>;
type EvidenceInput = z.infer<typeof evidenceSchema>;
type ItemInput = z.infer<typeof itemSchema>;
type FindingInput = z.infer<typeof findingSchema>;
type DebtInput = z.infer<typeof debtSchema>;
type ReviewInput = z.infer<typeof reviewSchema>;
type DocumentInput = z.infer<typeof documentSchema>;

/** Map parsed shape data into one typed decision, omitting an absent destination. */
function toDecision(value: DecisionInput): PublicationDecision {
	return {
		actor: value.actor,
		date: value.date,
		statement: value.statement,
		evidence: value.evidence,
		...(value.destination === undefined ? {} : { destination: value.destination }),
	};
}

/** Map parsed shape data into one typed observed evidence. */
function toEvidence(value: EvidenceInput): TestEvidence {
	return { action: value.action, result: value.result, executor: value.executor };
}

/** Map parsed shape data into one typed test-plan item. */
function toItem(value: ItemInput): TestPlanItem {
	return {
		text: value.text,
		status: value.status,
		...(value.evidence === undefined ? {} : { evidence: toEvidence(value.evidence) }),
		...(value.decision === undefined ? {} : { decision: toDecision(value.decision) }),
	};
}

/** Map parsed shape data into one typed finding. */
function toFinding(value: FindingInput): PublicationFinding {
	return {
		id: value.id,
		severity: value.severity,
		status: value.status,
		evidence: value.evidence,
		resolution: value.resolution,
		...(value.acceptance === undefined ? {} : { acceptance: toDecision(value.acceptance) }),
		...(value.deferral === undefined ? {} : { deferral: toDecision(value.deferral) }),
	};
}

/** Map parsed shape data into one typed debt entry. */
function toDebt(value: DebtInput): PublicationDebt {
	return {
		target: value.target,
		actor: value.actor,
		date: value.date,
		statement: value.statement,
		evidence: value.evidence,
		destination: value.destination,
	};
}

/** Map parsed shape data into one typed review record. */
function toReview(value: ReviewInput): ReviewRecord {
	return {
		prNumber: value.prNumber,
		headSha: value.headSha,
		baseRef: value.baseRef,
		findings: value.findings.map(toFinding),
		debt: value.debt.map(toDebt),
		...(value.verdict === undefined ? {} : { verdict: { kind: value.verdict.kind, basis: value.verdict.basis } }),
	};
}

/** Map parsed shape data into one typed publication record. */
function toPublication(value: DocumentInput): Publication {
	return {
		schemaVersion: 1,
		title: value.title,
		summary: [...value.summary],
		...(value.breakingChanges === undefined
			? {}
			: {
					breakingChanges: {
						description: value.breakingChanges.description,
						migration: value.breakingChanges.migration,
					},
				}),
		testPlan: value.testPlan.map(toItem),
		...(value.review === undefined ? {} : { review: toReview(value.review) }),
	};
}

/** Map one supplied JSON document into typed publication data. */
export function mapPublication(value: unknown): Publication | PublicationError {
	const parsed = documentSchema.safeParse(value);
	if (!parsed.success) return publicationError("INPUT_INVALID", "valid JSON publication required");
	return toPublication(parsed.data);
}
