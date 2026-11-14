/** Validate selected feature documents through an injected source port. */

import type { FeatureSource } from "#scripts/feature_validation/domain/ports.ts";
import {
  InvalidFeatureError,
  NoFeatureDocumentsError,
  ValidFeature,
} from "#scripts/feature_validation/domain/records.ts";
import type { FeatureValidationResult } from "#scripts/feature_validation/domain/records.ts";
import {
  isTemplateReference,
  sortFeatureReferences,
  validateFeature,
} from "#scripts/feature_validation/domain/rules.ts";
import type { PathComparisonPolicy } from "#scripts/feature_validation/domain/rules.ts";

export class ValidateFeatures {
  private readonly source: FeatureSource;
  private readonly pathComparisonPolicy: PathComparisonPolicy;

  constructor(source: FeatureSource, pathComparisonPolicy: PathComparisonPolicy) {
    this.source = source;
    this.pathComparisonPolicy = pathComparisonPolicy;
  }

  *execute(target: string): IterableIterator<FeatureValidationResult> {
    const references = sortFeatureReferences(
      this.source.discover(target),
      this.pathComparisonPolicy,
    ).filter((reference) => !isTemplateReference(reference));
    if (references.length === 0) {
      yield new NoFeatureDocumentsError();
      return;
    }

    for (const reference of references) {
      const findings = validateFeature(this.source.read(reference));
      if (findings.length > 0) {
        yield new InvalidFeatureError(reference, findings);
      } else {
        yield new ValidFeature(reference);
      }
    }
  }
}
