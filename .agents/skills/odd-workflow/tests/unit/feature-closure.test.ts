import { describe, expect, it } from "vitest";
import {
  CLOSURE_CONSISTENCY_EFFECTIVE_FROM,
  validateFeature,
} from "#scripts/feature_validation/domain/rules.ts";
import {
  makeClosedFeatureWithUnfinishedTask,
  makeCompletedFeature,
  makeFeature,
} from "#tests/support/feature-fixtures.ts";
import { COMPLETED_BUT_ACTIVE_FINDING } from "#tests/support/retirement-fixtures.ts";

const EFFECTIVE_FROM = CLOSURE_CONSISTENCY_EFFECTIVE_FROM;

function dayBefore(isoDate: string): string {
  const time = Date.UTC(
    Number(isoDate.slice(0, 4)),
    Number(isoDate.slice(5, 7)) - 1,
    Number(isoDate.slice(8, 10)),
  );
  return new Date(time - 86_400_000).toISOString().slice(0, 10);
}

describe("validateFeature closure consistency", () => {
  it("reports an active record created on the effective date whose every task row is done", () => {
    expect(validateFeature(makeCompletedFeature({ created: EFFECTIVE_FROM }))).toEqual([
      COMPLETED_BUT_ACTIVE_FINDING,
    ]);
  });

  it("reports an active record created after the effective date", () => {
    expect(validateFeature(makeCompletedFeature({ created: "2027-01-31" }))).toEqual([
      COMPLETED_BUT_ACTIVE_FINDING,
    ]);
  });

  it("leaves a historical record alone so its status and Log are never rewritten", () => {
    expect(
      validateFeature(makeCompletedFeature({ created: dayBefore(EFFECTIVE_FROM) })),
    ).toEqual([]);
  });

  it("accepts the same record when a Log entry names the open closure prerequisite", () => {
    expect(
      validateFeature(makeCompletedFeature({ created: EFFECTIVE_FROM, blocked: true })),
    ).toEqual([]);
  });

  it("does not report a closed record whose every task row is done", () => {
    expect(
      validateFeature(makeCompletedFeature({ created: EFFECTIVE_FROM, status: "closed" })),
    ).toEqual([]);
  });

  it("does not report an active record that still carries an unfinished task", () => {
    expect(validateFeature(makeFeature())).toEqual([]);
  });

  it("keeps reporting a closed record with an unfinished task", () => {
    const findings = validateFeature(makeClosedFeatureWithUnfinishedTask());

    expect(findings).toContain(
      "closed feature has a open task: - T1 | S1 | route | open | commit: pending",
    );
    expect(findings).not.toContain(COMPLETED_BUT_ACTIVE_FINDING);
  });
});
