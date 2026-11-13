/**
 * Typed synchronization failures and operation outcomes (C5, C8).
 *
 * A business rejection is a value, never a thrown exception, and carries a
 * stable code plus the diagnostic the operator reads. Boundary exceptions —
 * unreadable directories, exhausted descriptors — stay exceptions at the IO
 * adapter and are never converted into a fabricated synchronization result.
 */

/** The stable codes the exit contract distinguishes. */
export type FailureCode = "drift" | "invalid";

/** One expected business rejection. */
export type SynchronizationFailure = {
  readonly code: FailureCode;
  readonly message: string;
};

/** What one command produced: a success word, or a typed failure. */
export type OperationOutcome =
  | { readonly ok: true; readonly message: string }
  | { readonly ok: false; readonly failure: SynchronizationFailure };

/** Build a drift failure: the destination is not current. */
export function drift(message: string): SynchronizationFailure {
  return { code: "drift", message };
}

/** Build a malformed-input failure: the command cannot be attempted. */
export function invalid(message: string): SynchronizationFailure {
  return { code: "invalid", message };
}

/** Report a completed command. */
export function succeeded(message: string): OperationOutcome {
  return { ok: true, message };
}

/** Report a refused command. */
export function failed(failure: SynchronizationFailure): OperationOutcome {
  return { ok: false, failure };
}
