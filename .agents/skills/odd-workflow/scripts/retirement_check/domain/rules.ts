/**
 * Pure retirement rules.
 *
 * The closure date is the only age source: no timestamp is recorded and none is
 * required. Calendar arithmetic is performed on UTC midnights so the result does
 * not depend on the host time zone or on the current clock.
 */

import { readFenceStructure } from "#scripts/markdown/fences.ts";
import { splitLines } from "#scripts/feature_validation/domain/rules.ts";
import { REQUIRED_COMPLETE_DAYS } from "#scripts/retirement_check/domain/records.ts";
import type { RetirementDecision } from "#scripts/retirement_check/domain/records.ts";

const STATUS_CLOSED_RE = /^> \*\*Status:\*\* closed$/u;
const STATUS_ANY_RE = /^> \*\*Status:\*\* (.*)$/u;
const CLOSED_DATE_RE = /^> \*\*Closed:\*\* ?(.*)$/u;
/** Header metadata sits at column zero; an indented copy is a quoted example, not the header. */
const HEADER_AT_COLUMN_ZERO = /^> /u;
const CALENDAR_DATE_RE = /^\d{4}-\d{2}-\d{2}$/u;
const DAY_MS = 86_400_000;

/** Parses a `YYYY-MM-DD` calendar date to its UTC midnight, or `null` when it is not a real date. */
export function parseCalendarDate(value: string): number | null {
	if (!CALENDAR_DATE_RE.test(value)) return null;
	const year = Number(value.slice(0, 4));
	const month = Number(value.slice(5, 7));
	const day = Number(value.slice(8, 10));
	const time = Date.UTC(year, month - 1, day);
	const parsed = new Date(time);
	if (parsed.getUTCFullYear() !== year || parsed.getUTCMonth() !== month - 1 || parsed.getUTCDate() !== day) {
		return null;
	}
	return time;
}

/** Whole calendar days between two UTC midnights. */
export function calendarDaysBetween(fromMs: number, toMs: number): number {
	return Math.trunc((toMs - fromMs) / DAY_MS);
}

/**
 * Decides whether one record is a deletion candidate as of `asOfDate`.
 *
 * Eligibility is the status `closed` plus at least `REQUIRED_COMPLETE_DAYS` complete calendar
 * days since the recorded closure date. Status and closure date are read only from
 * column-zero header lines and only from text outside fenced blocks, so a quoted example can
 * neither state closure nor shorten the retention period. A record that an unclosed fence,
 * ambiguous metadata or a non-calendar date makes untrustworthy is never a candidate.
 */
export function evaluateRetirement(text: string, asOfDate: string): RetirementDecision {
	const structure = readFenceStructure(splitLines(text));
	// A document whose fence never closes has no trustworthy structure, so it is never a
	// deletion candidate: the code after the opening fence may be prose the reader cannot see.
	if (structure.unclosed.length > 0) {
		return { kind: "excluded", reason: "unbalanced code fence" };
	}
	// Only text outside fenced blocks states closure: a quoted example cannot make a record
	// eligible for deletion.
	const lines = structure.unfencedLines;

	// Header metadata sits at column zero in the record's own header region — every line before
	// the first second-level heading. An indented copy is quoted content, and a column-zero copy
	// inside Specs, Tasks or the Log is body text, so neither can state closure.
	const firstHeading = lines.findIndex((line) => line.startsWith("## "));
	const preamble = firstHeading < 0 ? lines : lines.slice(0, firstHeading);
	const headerLines = preamble.filter((line) => HEADER_AT_COLUMN_ZERO.test(line));

	const statusValues = headerLines
		.map((line) => STATUS_ANY_RE.exec(line))
		.filter((match) => match !== null)
		.map((match) => match[1]?.trim() ?? "");
	if (statusValues.length > 1) {
		return { kind: "excluded", reason: "ambiguous closure metadata" };
	}
	if (!headerLines.some((line) => STATUS_CLOSED_RE.test(line))) {
		return { kind: "excluded", reason: "status is not closed" };
	}

	const closedValues = headerLines
		.map((line) => CLOSED_DATE_RE.exec(line))
		.filter((match) => match !== null)
		.map((match) => match[1]?.trim() ?? "");
	const distinct = [...new Set(closedValues)];
	if (distinct.length > 1) {
		return { kind: "excluded", reason: "ambiguous closure metadata" };
	}
	const closedOn = distinct[0] ?? "";
	if (closedOn.length === 0) {
		return { kind: "excluded", reason: "no recorded closure date" };
	}

	const closedAt = parseCalendarDate(closedOn);
	if (closedAt === null) {
		return { kind: "excluded", reason: "closure date is not a calendar date" };
	}

	const asOfAt = parseCalendarDate(asOfDate);
	if (asOfAt === null) {
		return { kind: "excluded", reason: "as-of date is not a calendar date" };
	}

	const ageDays = calendarDaysBetween(closedAt, asOfAt);
	if (ageDays < 0) {
		return { kind: "excluded", reason: "closure date is after the as-of date" };
	}
	if (ageDays < REQUIRED_COMPLETE_DAYS) {
		return {
			kind: "excluded",
			reason: `${ageDays} complete calendar days since closure; ${REQUIRED_COMPLETE_DAYS} required`,
		};
	}

	return { kind: "candidate", closedOn, ageDays };
}
