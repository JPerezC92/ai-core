/** Typed feature-document outcomes, independent of CLI presentation. */

export class ValidFeature {
  readonly path: string;

  constructor(path: string) {
    this.path = path;
  }
}

export class InvalidFeatureError {
  readonly path: string;
  readonly findings: readonly string[];
  readonly code = "FEATURE_INVALID";
  readonly message = "feature document is invalid";

  constructor(path: string, findings: readonly string[]) {
    this.path = path;
    this.findings = [...findings];
  }
}

export class NoFeatureDocumentsError {
  readonly code = "NO_FEATURE_DOCUMENTS";
  readonly message = "no feature documents found";
}

export type FeatureValidationResult =
  | ValidFeature
  | InvalidFeatureError
  | NoFeatureDocumentsError;
