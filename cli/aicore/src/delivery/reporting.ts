/**
 * Delivery: operator-facing reporting.
 *
 * The delivery edge owns all transport encodings — operator copy, exit statuses
 * and stream selection — so the application operations stay free of them
 * (contract C6, scripts-shape P2).
 */

import {
	reportOutcome,
	synchronizationNotCurrent,
	type SynchronizationReport,
} from "#delivery/synchronization-report.ts";
import type { Failure } from "#domain/failures.ts";
import type { SynchronizeOutcome } from "#domain/outcomes.ts";
import type { OperationOutcome } from "#domain/synchronization/failures.ts";
import type { ProposalEntry, ReconciliationProposal } from "#domain/synchronization/reconciliation-proposal.ts";
import { PROPOSAL_CLASSES } from "#domain/synchronization/reconciliation-proposal.ts";

/** Process exit statuses, matching the published exit contract. */
export const EXIT_OK = 0;
export const EXIT_DRIFT = 1;
export const EXIT_INVALID = 2;

const EXIT_BY_FAILURE = {
	"unavailable-configuration": EXIT_INVALID,
	"unsupported-editor": EXIT_INVALID,
	"unknown-editor": EXIT_INVALID,
	"invalid-destination": EXIT_INVALID,
	"invalid-revision": EXIT_INVALID,
	"invalid-bindings": EXIT_INVALID,
} as const;

export function exitStatusForFailure(failure: Failure): number {
	return EXIT_BY_FAILURE[failure.code] ?? EXIT_INVALID;
}

/** Render one reported result as the lines the operator reads. */
export function renderReport(report: SynchronizationReport): {
	stdout: string[];
	stderr: string[];
	status: number;
} {
	return {
		stdout: report.stdout.trim() === "" ? [] : [report.stdout.trim()],
		stderr: report.stderr.trim() === "" ? [] : [report.stderr.trim()],
		status: report.exitCode,
	};
}

/**
 * Render a completed synchronization.
 *
 * The exit status reflects the last operation, so a failed write or a failed
 * verification is never reported as success.
 */
export function renderSync(outcome: SynchronizeOutcome): {
	stdout: string[];
	stderr: string[];
	status: number;
} {
	const stdout: string[] = [];
	const stderr: string[] = [];
	for (const run of outcome.runs) {
		const rendered = renderOutcome(run);
		stdout.push(...rendered.stdout);
		stderr.push(...rendered.stderr);
	}

	const last = outcome.runs[outcome.runs.length - 1];
	const lastStatus = last === undefined ? EXIT_DRIFT : reportOutcome(last).exitCode;

	if (outcome.current) {
		stdout.push(`sync: ${outcome.destination} is current (${outcome.editor}).`);
		return { stdout, stderr, status: EXIT_OK };
	}

	const wroteSuccessfully = last !== undefined && outcome.runs.length > 1 && lastStatus !== EXIT_OK;
	stderr.push(
		wroteSuccessfully
			? `sync: the write to ${outcome.destination} succeeded, but the engine reports the ` +
					"destination is not current. Its result above is authoritative and is not " +
					"overridden here. A freshly enrolled destination lists region files under " +
					"`pending:` until that project reconciles its own project regions; clearing " +
					"`pending:` is destination-owned and is never done by this tool."
			: synchronizationNotCurrent(outcome.destination, lastStatus),
	);

	return { stdout, stderr, status: lastStatus };
}

/** Render one operation's domain result as the lines the operator reads. */
function renderOutcome(outcome: OperationOutcome): { stdout: string[]; stderr: string[] } {
	const report = reportOutcome(outcome);
	return {
		stdout: report.stdout.trim() === "" ? [] : [report.stdout.trim()],
		stderr: report.stderr.trim() === "" ? [] : [report.stderr.trim()],
	};
}

/** Width of the action column, so a proposal reads as a table. */
const ACTION_COLUMN = 10;

/** Width of the class column, so a proposal reads as a table. */
const CLASS_COLUMN = 17;

/**
 * Render a reconciliation proposal, and its exit status.
 *
 * The proposal is standard output: it is the result the operator asked for, not
 * a diagnostic. The exit status carries the part a caller must not have to read
 * prose to learn — `0` when nothing needs the destination owner, `1` when
 * something does — so a proposal that preserves or deletes a path is never
 * mistaken for a destination that is current.
 */
export function renderReconciliation(proposal: ReconciliationProposal): {
	stdout: string[];
	stderr: string[];
	status: number;
} {
	const stdout: string[] = [`reconcile: proposal for ${proposal.destination} (read-only: nothing was written)`];

	for (const entry of proposal.entries) {
		stdout.push(
			`reconcile: ${entry.action.padEnd(ACTION_COLUMN)} ${entry.classification.padEnd(
				CLASS_COLUMN,
			)} ${entry.path} — ${entry.detail}`,
		);
	}
	if (proposal.entries.length === 0) {
		stdout.push("reconcile: no path is bound and no managed directory holds an unbound file.");
	}

	stdout.push(`reconcile: ${classCounts(proposal.entries)}.`);
	stdout.push(
		proposal.requiresAction
			? "reconcile: the destination owner must decide or act on the entries above; this tool changed nothing."
			: "reconcile: nothing requires the destination owner's action.",
	);

	return {
		stdout,
		stderr: [],
		status: proposal.requiresAction ? EXIT_DRIFT : EXIT_OK,
	};
}

/** One class's count, in the contract's own class order. */
function classCounts(entries: readonly ProposalEntry[]): string {
	return PROPOSAL_CLASSES.map(
		(classification) =>
			`${classification} ${entries.filter((entry) => entry.classification === classification).length}`,
	).join(", ");
}
