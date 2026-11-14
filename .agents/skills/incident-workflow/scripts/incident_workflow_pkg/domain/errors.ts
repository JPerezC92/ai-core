/**
 * A rejected input value: malformed, missing or structurally invalid supplied
 * content. This is the replacement for the reference implementation's
 * `ValueError` boundary, so callers can convert it into a reported validator
 * rejection while every other error — a programming defect or a genuine
 * unexpected failure — keeps propagating.
 */
export class InputError extends Error {
  override name = 'InputError';
}
