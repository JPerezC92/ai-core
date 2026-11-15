export class AstGrepError {
  readonly code: string;
  readonly message: string;

  constructor(code: string, message: string) {
    this.code = code;
    this.message = message;
  }
}

export const NO_MATCH_MESSAGE =
  'No matches found for the given code and rule. Try adding `stopBy: end` to your inside/has rule.';

export function isAstGrepError(value: unknown): value is AstGrepError {
  return value instanceof AstGrepError;
}
