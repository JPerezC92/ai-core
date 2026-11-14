/** Report retirement candidates for the selected task records through an injected source port. */

import { isTemplateReference } from "#scripts/feature_validation/domain/rules.ts";
import type { RetirementSource } from "#scripts/retirement_check/domain/ports.ts";
import {
  NoTaskRecordsError,
  RetirementReport,
} from "#scripts/retirement_check/domain/records.ts";
import type { RetirementResult } from "#scripts/retirement_check/domain/records.ts";
import { evaluateRetirement } from "#scripts/retirement_check/domain/rules.ts";

export class CheckRetirements {
  private readonly source: RetirementSource;

  constructor(source: RetirementSource) {
    this.source = source;
  }

  *execute(target: string, asOfDate: string): IterableIterator<RetirementResult> {
    const references = [...this.source.discover(target)]
      .filter((reference) => !isTemplateReference(reference))
      .sort((left, right) => (left < right ? -1 : left > right ? 1 : 0));
    if (references.length === 0) {
      yield new NoTaskRecordsError();
      return;
    }

    for (const reference of references) {
      let text: string;
      try {
        text = this.source.read(reference);
      } catch (error) {
        yield new RetirementReport(reference, {
          kind: "excluded",
          reason: `cannot be read: ${error instanceof Error ? error.message : String(error)}`,
        });
        continue;
      }
      yield new RetirementReport(reference, evaluateRetirement(text, asOfDate));
    }
  }
}
