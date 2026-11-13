/**
 * Typed failures for the synchronization CLI.
 *
 * Every failure is a value with a stable code and a message, per architecture
 * contract C5; the CLI never throws a business failure and never invents a
 * domain error from an unexpected exception.
 */

export type FailureCode =
  | "unavailable-configuration"
  | "unsupported-editor"
  | "unknown-editor"
  | "invalid-destination"
  | "invalid-revision"
  | "invalid-bindings";

export type Failure = {
  readonly code: FailureCode;
  readonly message: string;
};

export type Result<T> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly failure: Failure };

export function succeed<T>(value: T): Result<T> {
  return { ok: true, value };
}

export function fail<T = never>(code: FailureCode, message: string): Result<T> {
  return { ok: false, failure: { code, message } };
}
