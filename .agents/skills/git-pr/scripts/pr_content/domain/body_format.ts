/** Define the canonical pull-request body format and check a generated body against it. */

import { publicationError } from "#scripts/pr_content/domain/records.ts";
import type {
	Publication,
	PublicationDebt,
	PublicationError,
	ReviewRecord,
} from "#scripts/pr_content/domain/records.ts";

/** The canonical section names of the generated body, in their canonical order. */
const CANONICAL_SECTIONS = [
	"Summary",
	"Breaking changes",
	"Test plan",
	"Findings / blockers",
	"Test evidence",
	"Open debt",
] as const;

/** One canonical section name of the generated body. */
export type CanonicalSection = (typeof CANONICAL_SECTIONS)[number];

/** The sections every generated body carries. */
const REQUIRED_SECTIONS: readonly CanonicalSection[] = ["Summary", "Test plan", "Findings / blockers"];

/** The header row of the findings table. */
const FINDING_HEADER = "| ID | Severity | Status | Evidence | Owner / resolution |";

/** The header row of the test-evidence table. */
const EVIDENCE_HEADER = "| Test-plan item | Literal action/input | Observed result | Executor |";

/** The verdict line the canonical body ends with. */
const VERDICT_LINE = /^\[(PASS|ADVISORY|BLOCK)\] — (.*)$/;

/** Encode authored prose as literal Markdown text, not HTML or Markdown control. */
export function escapeMarkdownText(text: string): string {
	return text
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replace(/[\\`*_{}[\]()#+.|~]/gu, "\\$&");
}

/** The authorized follow-ups of one review, deferred findings first. */
function debtEntries(review: ReviewRecord): readonly PublicationDebt[] {
	const deferred = review.findings.flatMap((finding) =>
		finding.deferral === undefined
			? []
			: [
					{
						target: finding.id,
						actor: finding.deferral.actor,
						date: finding.deferral.date,
						statement: finding.deferral.statement,
						evidence: finding.deferral.evidence,
						destination: finding.deferral.destination!,
					},
				],
	);
	return [...deferred, ...review.debt];
}

/** The canonical heading of one section. */
export function sectionHeading(name: CanonicalSection): string {
	return `## ${name}`;
}

/** The canonical section names the current record produces, in their canonical order. */
export function expectedSectionNames(publication: Publication): readonly CanonicalSection[] {
	const names: CanonicalSection[] = ["Summary"];
	if (publication.breakingChanges !== undefined) names.push("Breaking changes");
	names.push("Test plan", "Findings / blockers");
	if (publication.review !== undefined && publication.testPlan.some((item) => item.status === "PASSED")) {
		names.push("Test evidence");
	}
	if (publication.review !== undefined && debtEntries(publication.review).length > 0) names.push("Open debt");
	return names;
}

/** The canonical content lines of the findings section. */
function findingsContent(publication: Publication): string[] {
	const review = publication.review;
	if (review === undefined) return ["No review findings yet."];
	if (review.findings.length === 0) return ["No findings."];
	return [
		FINDING_HEADER,
		"|---|---|---|---|---|",
		...review.findings.map(
			(finding) =>
				`| ${finding.id} | \`${finding.severity}\` | \`${finding.status}\` | ${escapeMarkdownText(finding.evidence)} | ${escapeMarkdownText(finding.resolution)} |`,
		),
	];
}

/** The canonical content lines of the test-evidence section. */
function evidenceContent(publication: Publication): string[] {
	const review = publication.review;
	if (review === undefined) return [];
	const passed = publication.testPlan.filter((item) => item.status === "PASSED");
	if (passed.length === 0) return [];
	const base = review.baseRef.startsWith("origin/") ? review.baseRef : `origin/${review.baseRef}`;
	return [
		`- PR: \`#${review.prNumber}\``,
		`- Immutable head SHA: \`${review.headSha}\``,
		`- Base: \`${base}\``,
		`- Scope command: \`git diff "${base}"...${review.headSha}\``,
		"",
		EVIDENCE_HEADER,
		"|---|---|---|---|",
		...passed.map(
			(item) =>
				`| ${escapeMarkdownText(item.text)} | ${escapeMarkdownText(item.evidence!.action)} | ${escapeMarkdownText(item.evidence!.result)} | ${escapeMarkdownText(item.evidence!.executor)} |`,
		),
	];
}

/** The canonical content lines of the open-debt section. */
function debtContent(publication: Publication): string[] {
	const review = publication.review;
	if (review === undefined) return [];
	return debtEntries(review).map(
		(entry) =>
			`- ${escapeMarkdownText(entry.target)} — ${escapeMarkdownText(entry.destination)}, authorized by ${escapeMarkdownText(entry.actor)} on ${entry.date}`,
	);
}

/** The canonical content lines of one section. */
export function sectionContent(publication: Publication, name: CanonicalSection): string[] {
	switch (name) {
		case "Summary":
			return publication.summary.map((entry) => `- ${escapeMarkdownText(entry)}`);
		case "Breaking changes": {
			const change = publication.breakingChanges;
			return change === undefined
				? []
				: [
						`- ${escapeMarkdownText(change.description)}`,
						`- Migration: ${escapeMarkdownText(change.migration)}`,
					];
		}
		case "Test plan":
			return publication.testPlan.map(
				(item) => `- [${item.status === "PASSED" ? "x" : " "}] ${escapeMarkdownText(item.text)}`,
			);
		case "Findings / blockers":
			return findingsContent(publication);
		case "Test evidence":
			return evidenceContent(publication);
		case "Open debt":
			return debtContent(publication);
	}
}

/** Split unique canonical headings while retaining section content verbatim. */
function parseSections(body: string): Record<string, string> | undefined {
	const matches = [...body.matchAll(/^## ([^\r\n]+)(?:\r?\n|$)/gm)];
	if (matches.length === 0 || matches[0]!.index !== 0) return undefined;
	const names = matches.map((match) => match[1]!);
	if (new Set(names).size !== names.length) return undefined;
	if (names.some((name) => !CANONICAL_SECTIONS.includes(name as CanonicalSection))) return undefined;
	const sorted = [...names].sort(
		(left, right) =>
			CANONICAL_SECTIONS.indexOf(left as CanonicalSection) -
			CANONICAL_SECTIONS.indexOf(right as CanonicalSection),
	);
	if (names.some((name, index) => name !== sorted[index])) return undefined;
	if (REQUIRED_SECTIONS.some((name) => !names.includes(name))) return undefined;

	const sections: Record<string, string> = {};
	for (const [index, match] of matches.entries()) {
		const start = match.index! + match[0].length;
		const end = index + 1 < matches.length ? matches[index + 1]!.index! : body.length;
		const content = body.slice(start, end);
		if (content.trim() === "") return undefined;
		sections[match[1]!] = content;
	}
	return sections;
}

/** The non-empty lines of one section. */
function sectionLines(content: string): string[] {
	return content
		.split(/\r\n|\n|\r/u)
		.map((line) => line.trim())
		.filter((line) => line !== "");
}

/** The non-empty lines of one canonical section content. */
function contentLines(lines: readonly string[]): string[] {
	return lines.map((line) => line.trim()).filter((line) => line !== "");
}

/** Report whether two line lists carry the same content. */
function sameLines(actual: readonly string[], expected: readonly string[]): boolean {
	return actual.length === expected.length && actual.every((line, index) => line === expected[index]);
}

/**
 * Check that a generated body is the canonical body of the current publication record.
 *
 * The check proves correspondence between the generated text and the current record; it never
 * compares the body with any earlier body, capture or published state.
 */
export function validateGeneratedBody(body: string, publication: Publication): PublicationError | undefined {
	const failure = publicationError("BODY_INVALID", "generated body must match the canonical body format");
	const trimmed = body.replace(/\n$/, "");
	const lines = trimmed.split("\n");
	const verdictMatch = VERDICT_LINE.exec(lines[lines.length - 1] ?? "");
	const verdict = publication.review?.verdict;
	if (verdict === undefined) {
		if (verdictMatch !== null) return failure;
		if (lines.some((line) => VERDICT_LINE.test(line))) return failure;
	} else {
		if (verdictMatch === null) return failure;
		if (verdictMatch[1] !== verdict.kind || verdictMatch[2] !== escapeMarkdownText(verdict.basis)) return failure;
	}

	const content = verdictMatch === null ? trimmed : lines.slice(0, -1).join("\n");
	const sections = parseSections(content);
	if (sections === undefined) return failure;
	const names = expectedSectionNames(publication);
	if (Object.keys(sections).length !== names.length || names.some((name) => !(name in sections))) return failure;

	for (const name of names) {
		if (!sameLines(sectionLines(sections[name] ?? ""), contentLines(sectionContent(publication, name)))) {
			return failure;
		}
	}
	return undefined;
}
