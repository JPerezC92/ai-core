/** Validate supplied remote freshness and a conservative completed review body. */

import { validateBody } from '#scripts/pr_content/domain/body_validation.ts';
import type { PreparedBody, ReviewPreparationError } from '#scripts/pr_content/domain/records.ts';
import { metadataMatches, parseMetadata, reviewError } from '#scripts/pr_content/domain/records.ts';
import { validatePreservation } from '#scripts/pr_content/domain/review_content_preservation.ts';
import { parseDecisions } from '#scripts/pr_content/domain/review_decisions.ts';

export interface ValidateFinalBodyInput {
  readonly baseline: unknown;
  readonly current: unknown;
  readonly body: string;
  readonly decisions?: unknown;
}

/** Reject stale supplied metadata before checking body structure. */
export function execute(input: ValidateFinalBodyInput): PreparedBody | ReviewPreparationError {
  const accepted = parseMetadata(input.baseline);
  if ('code' in accepted) return accepted;
  const observed = parseMetadata(input.current);
  if ('code' in observed) return observed;
  if (!metadataMatches(accepted, observed)) {
    return reviewError('REMOTE_DIVERGED', 'remote metadata differs from accepted baseline');
  }

  const supplied = parseDecisions(input.decisions ?? null, observed);
  if ('code' in supplied) return supplied;

  const failure = validateBody(input.body, observed, supplied);
  if (failure !== undefined) return failure;

  const preserved = validatePreservation(accepted.body, input.body);
  if (preserved !== undefined) return preserved;
  return { body: input.body };
}
