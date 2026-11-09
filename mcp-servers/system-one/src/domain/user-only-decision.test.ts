import { describe, expect, it } from "vitest";
import { classifyUserOnlyDecision } from "./user-only-decision.ts";
import {
  absent,
  present,
  unknown,
} from "../test/helpers/evidence.factory.ts";

describe("classify user-only decision evidence", () => {
  it("returns present when explicit authorization evidence is present", () => {
    expect(classifyUserOnlyDecision(present())).toBe("present");
  });

  it("returns absent when authorization evidence is absent", () => {
    expect(classifyUserOnlyDecision(absent())).toBe("absent");
  });

  it("returns unknown when authorization evidence is unknown", () => {
    expect(classifyUserOnlyDecision(unknown())).toBe("unknown");
  });
});
