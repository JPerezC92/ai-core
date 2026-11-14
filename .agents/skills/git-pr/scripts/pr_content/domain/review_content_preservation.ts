/** Protect baseline prose, exact test items and persistent finding identities. */

import { parseFindings, parseSections } from '#scripts/pr_content/domain/body_validation.ts';
import type { ReviewPreparationError } from '#scripts/pr_content/domain/records.ts';
import { isReviewError, reviewError } from '#scripts/pr_content/domain/records.ts';

function normalizeCheckboxes(plan: string): string {
  return plan.replace(/^- \[[ x]\] /gm, '- [ ] ');
}

function findingRegion(content: string): string {
  return content.split(/^\[(?:PASS|ADVISORY|BLOCK)\] —/m)[0] ?? '';
}

/** Allow review-section updates without granting authority to rewrite prose. */
export function validatePreservation(baseline: string, candidate: string): ReviewPreparationError | undefined {
  const error = reviewError('BODY_INVALID', 'protected baseline review content changed');
  const before = parseSections(baseline);
  if (isReviewError(before)) return before;
  const after = parseSections(candidate);
  if (isReviewError(after)) return after;

  for (const heading of ['Summary', 'Breaking changes']) {
    if (before[heading] !== after[heading]) return error;
  }
  if (normalizeCheckboxes(before['Test plan'] ?? '') !== normalizeCheckboxes(after['Test plan'] ?? '')) return error;

  const previous = parseFindings(findingRegion(before['Findings / blockers'] ?? ''));
  if (isReviewError(previous)) return previous;
  const updated = parseFindings(findingRegion(after['Findings / blockers'] ?? ''));
  if (isReviewError(updated)) return updated;

  if (updated.length < previous.length) return error;
  for (const [index, original] of previous.entries()) {
    const current = updated[index]!;
    if (original.id !== current.id || original.severity !== current.severity) return error;
  }
  return undefined;
}
