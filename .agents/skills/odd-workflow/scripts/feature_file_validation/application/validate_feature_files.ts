/** Validate selected durable feature files through an injected source port. */

import type { FeatureFileSource } from "#scripts/feature_file_validation/domain/ports.ts";
import {
  InvalidFeatureFileError,
  NoFeatureFileDocumentsError,
  ValidFeatureFile,
} from "#scripts/feature_file_validation/domain/records.ts";
import type { FeatureFileValidationResult } from "#scripts/feature_file_validation/domain/records.ts";
import {
  assessFeatureFile,
  isTemplateFeatureFileReference,
  sortFeatureFileReferences,
} from "#scripts/feature_file_validation/domain/rules.ts";
import type { PathComparisonPolicy } from "#scripts/feature_file_validation/domain/rules.ts";

export class ValidateFeatureFiles {
  private readonly source: FeatureFileSource;
  private readonly pathComparisonPolicy: PathComparisonPolicy;

  constructor(source: FeatureFileSource, pathComparisonPolicy: PathComparisonPolicy) {
    this.source = source;
    this.pathComparisonPolicy = pathComparisonPolicy;
  }

  *execute(target: string): IterableIterator<FeatureFileValidationResult> {
    const references = sortFeatureFileReferences(
      this.source.discover(target),
      this.pathComparisonPolicy,
    ).filter((reference) => !isTemplateFeatureFileReference(reference));
    if (references.length === 0) {
      yield new NoFeatureFileDocumentsError();
      return;
    }

    for (const reference of references) {
      const assessment = assessFeatureFile(this.source.read(reference));
      if (assessment.findings.length > 0 || assessment.status === null) {
        yield new InvalidFeatureFileError(reference, assessment.findings);
      } else {
        yield new ValidFeatureFile(reference, assessment.status);
      }
    }
  }
}
