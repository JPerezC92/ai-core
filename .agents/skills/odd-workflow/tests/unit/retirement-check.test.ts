import { describe, expect, it } from "vitest";
import {
  calendarDaysBetween,
  evaluateRetirement,
  parseCalendarDate,
} from "#scripts/retirement_check/domain/rules.ts";
import { makeTaskRecord } from "#tests/support/retirement-fixtures.ts";

const AS_OF = "2026-11-14";

describe("parseCalendarDate", () => {
  it("returns the UTC midnight of a real calendar date", () => {
    expect(parseCalendarDate("2026-11-01")).toBe(Date.UTC(2026, 10, 1));
  });

  it("rejects a value that is not a calendar date", () => {
    expect(parseCalendarDate("2026-13-01")).toBeNull();
    expect(parseCalendarDate("2026-11-31")).toBeNull();
    expect(parseCalendarDate("2026-02-30")).toBeNull();
    expect(parseCalendarDate("1 November 2026")).toBeNull();
    expect(parseCalendarDate("")).toBeNull();
  });
});

describe("calendarDaysBetween", () => {
  it("counts whole calendar days across a month boundary", () => {
    expect(
      calendarDaysBetween(parseCalendarDate("2026-12-28")!, parseCalendarDate("2027-01-04")!),
    ).toBe(7);
  });
});

describe("evaluateRetirement", () => {
  it("excludes a record closed six complete calendar days before the report date", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: "2026-11-08" }), AS_OF)).toEqual({
      kind: "excluded",
      reason: "6 complete calendar days since closure; 7 required",
    });
  });

  it("reports a record closed exactly seven complete calendar days before the report date", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: "2026-11-07" }), AS_OF)).toEqual({
      kind: "candidate",
      closedOn: "2026-11-07",
      ageDays: 7,
    });
  });

  it("reports a record closed eight complete calendar days before the report date", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: "2026-11-06" }), AS_OF)).toEqual({
      kind: "candidate",
      closedOn: "2026-11-06",
      ageDays: 8,
    });
  });

  it("reports a record at the seven-day boundary across a year change", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: "2026-12-28" }), "2027-01-04")).toEqual({
      kind: "candidate",
      closedOn: "2026-12-28",
      ageDays: 7,
    });
  });

  it("reports a record at the seven-day boundary across a leap day", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: "2028-02-24" }), "2028-03-02")).toEqual({
      kind: "candidate",
      closedOn: "2028-02-24",
      ageDays: 7,
    });
  });

  it("excludes a record whose status is not closed", () => {
    expect(evaluateRetirement(makeTaskRecord({ status: "active", closedOn: null }), AS_OF)).toEqual(
      { kind: "excluded", reason: "status is not closed" },
    );
  });

  it("excludes a closed record with no recorded closure date", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: null }), AS_OF)).toEqual({
      kind: "excluded",
      reason: "no recorded closure date",
    });
  });

  it("excludes a closed record whose closure date is not a calendar date", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: "2026-02-30" }), AS_OF)).toEqual({
      kind: "excluded",
      reason: "closure date is not a calendar date",
    });
  });

  it("excludes a record whose closure date is after the report date", () => {
    expect(evaluateRetirement(makeTaskRecord({ closedOn: "2026-11-20" }), AS_OF)).toEqual({
      kind: "excluded",
      reason: "closure date is after the as-of date",
    });
  });

  it("reports a closed record even when a task row is unfinished, because the policy has two conditions", () => {
    expect(evaluateRetirement(makeTaskRecord({ taskStatus: "in progress" }), AS_OF)).toEqual({
      kind: "candidate",
      closedOn: "2026-11-01",
      ageDays: 13,
    });
  });

  it("reports a closed record even without a Close log entry, because the policy has two conditions", () => {
    expect(evaluateRetirement(makeTaskRecord({ closeEntry: false }), AS_OF)).toEqual({
      kind: "candidate",
      closedOn: "2026-11-01",
      ageDays: 13,
    });
  });

  it("excludes every record when the report date is not a calendar date", () => {
    expect(evaluateRetirement(makeTaskRecord(), "14 November 2026")).toEqual({
      kind: "excluded",
      reason: "as-of date is not a calendar date",
    });
  });
});
