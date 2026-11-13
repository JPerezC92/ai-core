/** Typed records and outcomes for durable feature-file validation. */

export type FeatureStatus = "achieved" | "partial" | "not started";

export class FeatureRequirement {
  readonly number: string;
  readonly mark: string;
  readonly wording: string;
  readonly ticked: boolean;

  constructor(number: string, mark: string, wording: string, ticked: boolean) {
    this.number = number;
    this.mark = mark;
    this.wording = wording;
    this.ticked = ticked;
  }
}

export class FeatureFileAssessment {
  readonly findings: readonly string[];
  readonly status: FeatureStatus | null;

  constructor(findings: readonly string[], status: FeatureStatus | null) {
    this.findings = [...findings];
    this.status = status;
  }
}

export class ValidFeatureFile {
  readonly path: string;
  readonly status: FeatureStatus;

  constructor(path: string, status: FeatureStatus) {
    this.path = path;
    this.status = status;
  }
}

export class InvalidFeatureFileError {
  readonly path: string;
  readonly findings: readonly string[];
  readonly code = "FEATURE_FILE_INVALID";
  readonly message = "feature file is invalid";

  constructor(path: string, findings: readonly string[]) {
    this.path = path;
    this.findings = [...findings];
  }
}

export class NoFeatureFileDocumentsError {
  readonly code = "NO_FEATURE_FILE_DOCUMENTS";
  readonly message = "no feature files found";
}

export type FeatureFileValidationResult =
  | ValidFeatureFile
  | InvalidFeatureFileError
  | NoFeatureFileDocumentsError;
