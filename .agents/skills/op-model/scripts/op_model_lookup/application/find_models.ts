/** Application use case: select the models matching a query from a model source. */

import type { LookupOutcome, ModelSource } from '#scripts/op_model_lookup/domain/catalog.ts';
import { matches, noMatchingModels, noModelsAvailable } from '#scripts/op_model_lookup/domain/catalog.ts';

/**
 * Return the matching models in encounter order, or a typed business outcome.
 *
 * An empty source returns the no-models outcome; a non-empty query without any
 * match returns the no-match outcome. Boundary failures from the source are not
 * business outcomes and propagate to the delivery edge.
 */
export function execute(query: string, source: ModelSource): LookupOutcome {
  const records = source.fetch();
  if (records.length === 0) return noModelsAvailable();
  const selection = records.filter(record => matches(query, record));
  if (query !== '' && selection.length === 0) return noMatchingModels(query);
  return selection;
}
