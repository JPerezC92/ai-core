/**
 * Pure retirement rules.
 *
 * The closure date is the only age source: no timestamp is recorded and none is
 * required. Calendar arithmetic is performed on UTC midnights so the result does
 * not depend on the host time zone or on the current clock.
 */

import { splitLines } from "#scripts/feature_validation/domain/rules.ts";
import { REQUIRED_COMPLETE_DAYS } from "#scripts/retirement_check/domain/records.ts";
import type { RetirementDecision } from "#scripts/retirement_check/domain/records.ts";

const STATUS_CLOSED_RE = /^> \*\*Status:\*\* closed$/u;
const CLOSED_DATE_RE = /^> \*\*Closed:\*\* ?(.*)$/u;
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
  if (
    parsed.getUTCFullYear() !== year ||
    parsed.getUTCMonth() !== month - 1 ||
    parsed.getUTCDate() !== day
  ) {
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
 * The policy has exactly two conditions: the status is `closed`, and at least
 * `REQUIRED_COMPLETE_DAYS` complete calendar days have passed since the recorded
 * closure date. Nothing else is an eligibility criterion. An unreadable record, a
 * record whose status is not `closed`, a record with no recorded closure date and a
 * record whose closure date is not a real calendar date are never candidates.
 */
export function evaluateRetirement(text: string, asOfDate: string): RetirementDecision {
  const lines = splitLines(text);

  if (!lines.some((line) => STATUS_CLOSED_RE.test(line.trim()))) {
    return { kind: "excluded", reason: "status is not closed" };
  }

  const closedField = lines
    .map((line) => CLOSED_DATE_RE.exec(line.trim()))
    .find((match) => match !== null);
  const closedOn = closedField?.[1]?.trim() ?? "";
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
