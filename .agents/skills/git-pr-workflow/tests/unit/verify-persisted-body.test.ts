import { describe, expect, it } from "vitest";
import { VerifyPersistedBody } from "../../scripts/pr_review/application/verify_persisted_body.ts";
import { PreparedBody, ReviewPreparationError } from "../../scripts/pr_review/domain/records.ts";
import {
  createBody,
  createDivergence,
  createMetadata,
  createMetadataWithUndeclaredKey,
} from "../support/review-fixtures.ts";

/** Run the verification operation over one capture pair. */
function verify(expected: unknown, persisted: unknown, body = createBody()): unknown {
  return new VerifyPersistedBody().execute(expected, persisted, body);
}

describe("VerifyPersistedBody.execute", () => {
  it("accepts an exact readback of the intended body", () => {
    const result = verify(createMetadata(), createMetadata());

    expect(result).toBeInstanceOf(PreparedBody);
    expect(result).toMatchObject({ body: createBody() });
  });

  it("detects a changed persisted body", () => {
    const result = verify(createMetadata(), createMetadata({ body: "Changed remotely" }));

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({ code: "READBACK_DIVERGED" });
  });

  it("reports a baseline key the persisted capture lacks", () => {
    const result = verify(createMetadataWithUndeclaredKey(), createMetadata());

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({ code: "READBACK_DIVERGED" });
  });

  it("reports a persisted field the intended capture lacks", () => {
    const result = verify(createMetadata(), createMetadataWithUndeclaredKey());

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({ code: "READBACK_DIVERGED" });
    expect((result as ReviewPreparationError).message).toContain("url");
  });

  it("reports an intended capture field the persisted capture lacks", () => {
    const intended = createMetadata();
    const persisted = { ...intended };
    delete persisted["title"];

    const result = verify(intended, persisted);

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({ code: "READBACK_DIVERGED" });
    expect((result as ReviewPreparationError).message).toContain("title");
  });

  it("accepts two captures that carry the same undeclared field", () => {
    const capture = createMetadataWithUndeclaredKey();

    const result = verify(capture, { ...capture });

    expect(result).toBeInstanceOf(PreparedBody);
    expect(result).toMatchObject({ body: createBody() });
  });

  it("blocks a divergent readback without repairing it", () => {
    for (const field of ["number", "headRefOid", "body"] as const) {
      const persisted = createDivergence(field);
      const original = { ...persisted };

      const result = verify(createMetadata(), persisted);

      expect(result).toBeInstanceOf(ReviewPreparationError);
      expect(result).toMatchObject({ code: "READBACK_DIVERGED" });
      expect(persisted).toEqual(original);
    }
  });

  it("rejects captures that are not objects", () => {
    const result = verify("not an object", createMetadata());

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({
      code: "READBACK_DIVERGED",
      message: "baseline and persisted captures must be objects",
    });
  });
});
