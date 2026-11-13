/** Compare supplied post-upload state with the exact intended review body. */

import { PreparedBody, ReviewPreparationError } from "../domain/records.ts";

/** Report whether a decoded value is a JSON object. */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Report whether two decoded values carry the same content. */
function sameValue(left: unknown, right: unknown): boolean {
  if (left === right) return true;
  if (Array.isArray(left) && Array.isArray(right)) {
    return left.length === right.length && left.every((item, index) => sameValue(item, right[index]));
  }
  if (isRecord(left) && isRecord(right)) {
    const leftKeys = Object.keys(left).sort();
    const rightKeys = Object.keys(right).sort();
    return (
      leftKeys.length === rightKeys.length &&
      leftKeys.every((key, index) => key === rightKeys[index] && sameValue(left[key], right[key]))
    );
  }
  return false;
}

export class VerifyPersistedBody {
  /** Return divergence without publishing, repairing, or retrying anything. */
  execute(expected: unknown, persisted: unknown, body: string): PreparedBody | ReviewPreparationError {
    if (!isRecord(expected) || !isRecord(persisted)) {
      return new ReviewPreparationError(
        "READBACK_DIVERGED",
        "baseline and persisted captures must be objects",
      );
    }
    const expectedKeys = new Set(Object.keys(expected));
    const persistedKeys = new Set(Object.keys(persisted));
    const unmatched = [...new Set([...expectedKeys, ...persistedKeys])]
      .filter((key) => !expectedKeys.has(key) || !persistedKeys.has(key))
      .sort();
    if (unmatched.length > 0) {
      return new ReviewPreparationError(
        "READBACK_DIVERGED",
        "persisted capture field set differs from the intended publication: " + unmatched.join(", "),
      );
    }
    const divergent = Object.keys(expected).filter(
      (key) => key !== "body" && !sameValue(persisted[key], expected[key]),
    );
    if (divergent.length > 0) {
      return new ReviewPreparationError(
        "READBACK_DIVERGED",
        "persisted capture fields differ from the intended publication: " +
          divergent.sort().join(", "),
      );
    }
    if (persisted["body"] !== body) {
      return new ReviewPreparationError(
        "READBACK_DIVERGED",
        "persisted body differs from the intended publication",
      );
    }
    return new PreparedBody(body);
  }
}
