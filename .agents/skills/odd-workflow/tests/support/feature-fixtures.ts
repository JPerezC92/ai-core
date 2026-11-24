/** Shared test data for the feature-document validator: documents and a fake source port. */

import type { FeatureSource } from "#scripts/feature_validation/domain/ports.ts";

/** A feature document that satisfies every anatomy rule. */
export function makeFeature(title = "Sample feature"): string {
	return [
		`# ${title}`,
		"",
		"> **Status:** active",
		"> **Owner:** Cipher (Lead Orchestrator)",
		"> **Created:** 2026-10-23",
		"",
		"## Specs",
		"",
		"- S1 — A requirement.",
		"",
		"## Tasks",
		"",
		"- T1 | S1 | route | open | commit: pending",
		"",
		"## Log",
		"",
		"- L1 — original request",
		"",
	].join("\n");
}

/**
 * A feature document carrying an unknown apostrophe-bearing heading and a
 * duplicated required heading.
 */
export function makeFeatureWithApostropheHeading(): string {
	return [
		"# Sample feature",
		"",
		"> **Status:** active",
		"> **Owner:** Cipher (Lead Orchestrator)",
		"> **Created:** 2026-10-23",
		"",
		"## Specs",
		"",
		"- S1 — A requirement.",
		"",
		"## Owner's notes",
		"",
		"- A heading value carrying an apostrophe.",
		"",
		"## Tasks",
		"",
		"- T1 | S1 | route | open | commit: pending",
		"",
		"## Tasks",
		"",
		"- T2 | S1 | route | open | commit: pending",
		"",
		"## Log",
		"",
		"- L1 — original request",
		"",
	].join("\n");
}

/** The candidate references of a fixture and the documents behind them. */
export type FeatureFixture = {
	readonly references: string[];
	readonly documents: Map<string, string>;
};

/** A directory holding a template and two documents. */
export function featureDirectoryFixture(): FeatureFixture {
	return {
		references: ["features/z.md", "features/_template.md", "features/a.md"],
		documents: new Map([
			["features/a.md", makeFeature()],
			["features/z.md", makeFeature()],
		]),
	};
}

/** A single document whose required heading appears twice. */
export function featureDuplicatedHeadingFixture(): FeatureFixture {
	return {
		references: ["features/a.md"],
		documents: new Map([["features/a.md", makeFeatureWithApostropheHeading()]]),
	};
}

/** A target with no candidate documents. */
export function featureEmptyFixture(): FeatureFixture {
	return { references: [], documents: new Map() };
}

/** A directory holding only the template. */
export function featureTemplateOnlyFixture(): FeatureFixture {
	return { references: ["features/_template.md"], documents: new Map() };
}

/** A single document with the given title. */
export function featureSingleFixture(title = "Sample feature"): FeatureFixture {
	return {
		references: ["features/a.md"],
		documents: new Map([["features/a.md", makeFeature(title)]]),
	};
}

/** Two documents whose case-sensitive order differs from their case-insensitive order. */
export function featureCaseOrderFixture(): FeatureFixture {
	return {
		references: ["features/B.md", "features/a.md"],
		documents: new Map([
			["features/B.md", makeFeature()],
			["features/a.md", makeFeature()],
		]),
	};
}

/** Two documents where reading the later one fails. */
export function featureFailingFixture(): FeatureFixture {
	return {
		references: ["features/z.md", "features/a.md"],
		documents: new Map([["features/a.md", makeFeature()]]),
	};
}

/** The reference whose read fails when a source carries a read failure. */
const FAILING_REFERENCE = "features/z.md";

/** An in-memory feature source that records the references it reads. */
export class FeatureSourceFake implements FeatureSource {
	readonly reads: string[] = [];
	private readonly references: string[];
	private readonly documents: Map<string, string>;
	private readonly readFailure: Error | undefined;

	constructor(references: string[], documents: Map<string, string>, readFailure?: Error) {
		this.references = references;
		this.documents = documents;
		this.readFailure = readFailure;
	}

	discover(_target: string): string[] {
		return [...this.references];
	}

	read(reference: string): string {
		this.reads.push(reference);
		if (reference === FAILING_REFERENCE && this.readFailure) throw this.readFailure;
		const document = this.documents.get(reference);
		if (document === undefined) throw new Error(`missing fixture: ${reference}`);
		return document;
	}
}

/**
 * A feature document whose every task row is `done` while its status stays `active`.
 *
 * With `blocked`, one Log entry names the open closure prerequisite, which is the
 * documented escape from the completed-but-active finding.
 */
export function makeCompletedFeature(
	options: {
		readonly blocked?: boolean;
		readonly laterEntry?: boolean;
		readonly status?: "active" | "closed";
		readonly created?: string;
		readonly verbatimLogHeadings?: boolean;
		readonly firstFailure?: "recorded" | "not-applicable" | "absent";
	} = {},
): string {
	const status = options.status ?? "active";
	const created = options.created ?? "2026-11-14";
	const logEntries =
		options.verbatimLogHeadings === true
			? [
					'- L1 — Original request, verbatim: "# AICore — Implement All Required Improvements in ONE Pull Request',
					"",
					"## Authorization",
					"",
					'Do not merge."',
				]
			: ["- L1 — original request"];
	let next = 2;
	const push = (text: string): void => {
		logEntries.push(`- L${next} — ${text}`);
		next += 1;
	};
	if (options.blocked === true) {
		push("2026-11-14 — Blocked: the required end-to-end check is outstanding");
	}
	if (options.laterEntry === true) {
		push("2026-11-15 — the prerequisite recorded earlier was resolved");
	}
	if (status === "closed") {
		const firstFailure = options.firstFailure ?? "recorded";
		if (firstFailure === "recorded") push("2026-11-19 — First failure: the focused case reproduced the defect");
		if (firstFailure === "not-applicable")
			push("2026-11-19 — No applicable executable failure: this change is prose only");
		push("Close: delivered");
	}
	const header = [`> **Status:** ${status}`, "> **Owner:** Cipher (Lead Orchestrator)", `> **Created:** ${created}`];
	if (status === "closed") header.push("> **Closed:** 2026-11-01");
	return [
		"# Sample feature",
		"",
		...header,
		"",
		"## Specs",
		"",
		"- S1 — A requirement.",
		"",
		"## Tasks",
		"",
		"- T1 | S1 | route | done | commit: abc1234",
		"- T2 | S1 | route | done | commit: abc1234",
		"",
		"## Log",
		"",
		...logEntries,
		"",
	].join("\n");
}

/**
 * A feature document whose Log holds exactly the supplied lines.
 *
 * The record is created before every date-gated rule took effect and, when closed, carries
 * the closure shape that rule set expects for such a record, so the only finding a case can
 * produce is the one under test.
 */
export function makeFeatureWithLog(options: {
	readonly status?: "active" | "closed";
	readonly taskStatus?: "open" | "done";
	readonly log: readonly string[];
	readonly specsBeforeLog?: readonly string[];
}): string {
	const status = options.status ?? "active";
	const taskStatus = options.taskStatus ?? (status === "closed" ? "done" : "open");
	const commit = taskStatus === "done" ? "abc1234" : "pending";
	const header = ["> **Status:** " + status, "> **Owner:** Cipher (Lead Orchestrator)", "> **Created:** 2026-11-14"];
	if (status === "closed") header.push("> **Closed:** 2026-11-01");
	return [
		"# Sample feature",
		"",
		...header,
		"",
		"## Specs",
		"",
		"- S1 — A requirement.",
		"",
		...(options.specsBeforeLog ?? []),
		"## Tasks",
		"",
		`- T1 | S1 | route | ${taskStatus} | commit: ${commit}`,
		"",
		"## Log",
		"",
		...options.log,
		"",
	].join("\n");
}

/** A closed feature document that still carries an unfinished task. */ export function makeClosedFeatureWithUnfinishedTask(): string {
	return [
		"# Sample feature",
		"",
		"> **Status:** closed",
		"> **Owner:** Cipher (Lead Orchestrator)",
		"> **Created:** 2026-10-23",
		"> **Closed:** 2026-11-01",
		"",
		"## Specs",
		"",
		"- S1 — A requirement.",
		"",
		"## Tasks",
		"",
		"- T1 | S1 | route | open | commit: pending",
		"",
		"## Log",
		"",
		"- L1 — original request",
		"- L2 — Close: delivered",
		"",
	].join("\n");
}
