import { describe, expect, it } from 'vitest';

import { isReviewError } from '#scripts/pr_content/domain/records.ts';
import { parseDecisions } from '#scripts/pr_content/domain/review_decisions.ts';
import { HEAD_SHA, makeMetadata } from '#tests/support/review-content-fixtures.ts';

function entry(overrides: Record<string, string> = {}): Record<string, string> {
  return {
    target: 'Run the focused suite',
    actor: 'Cipher',
    date: '2026-11-13',
    statement: 'not applicable for this change',
    evidence: 'diff',
    destination: '',
    ...overrides,
  };
}

function decisions(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    pr_number: 12,
    head_sha: HEAD_SHA,
    not_applicable: [],
    acceptance: [],
    debt: [],
    ...overrides,
  };
}

describe('review decision parsing', () => {
  it('accepts absent decisions', () => {
    const parsed = parseDecisions(null, makeMetadata());
    expect(isReviewError(parsed) ? {} : parsed).toEqual({ notApplicable: [], acceptance: [], debt: [] });
  });

  it('parses supplied entries bound to the same PR and head', () => {
    const parsed = parseDecisions(decisions({ not_applicable: [entry()] }), makeMetadata());
    expect(isReviewError(parsed) ? [] : parsed.notApplicable).toEqual([{
      target: 'Run the focused suite', actor: 'Cipher', date: '2026-11-13',
      statement: 'not applicable for this change', evidence: 'diff', destination: '',
    }]);
  });

  it('rejects a decision bound to another pull request', () => {
    const parsed = parseDecisions(decisions({ pr_number: 99 }), makeMetadata());
    expect(isReviewError(parsed) ? parsed.code : '').toBe('DECISIONS_INVALID');
  });

  it('rejects a decision bound to another head', () => {
    const parsed = parseDecisions(decisions({ head_sha: 'deadbeef' }), makeMetadata());
    expect(isReviewError(parsed) ? parsed.code : '').toBe('DECISIONS_INVALID');
  });

  it('rejects a duplicate decision target', () => {
    const parsed = parseDecisions(decisions({ acceptance: [entry(), entry()] }), makeMetadata());
    expect(isReviewError(parsed) ? parsed.code : '').toBe('DECISIONS_INVALID');
  });

  it('rejects a debt decision without a destination', () => {
    const parsed = parseDecisions(decisions({ debt: [entry()] }), makeMetadata());
    expect(isReviewError(parsed) ? parsed.code : '').toBe('DECISIONS_INVALID');
  });

  it('accepts a debt decision with a destination', () => {
    const parsed = parseDecisions(
      decisions({ debt: [entry({ destination: 'debt.md DEBT-050' })] }),
      makeMetadata(),
    );
    expect(isReviewError(parsed) ? '' : parsed.debt[0]?.destination).toBe('debt.md DEBT-050');
  });

  it('rejects an impossible calendar date', () => {
    const parsed = parseDecisions(decisions({ acceptance: [entry({ date: '2026-02-31' })] }), makeMetadata());
    expect(isReviewError(parsed) ? parsed.code : '').toBe('DECISIONS_INVALID');
  });

  it('rejects a missing provenance field', () => {
    const incomplete = entry();
    delete (incomplete as Record<string, string | undefined>).actor;
    const parsed = parseDecisions(decisions({ acceptance: [incomplete] }), makeMetadata());
    expect(isReviewError(parsed) ? parsed.code : '').toBe('DECISIONS_INVALID');
  });

  it('rejects metadata that is itself invalid', () => {
    const parsed = parseDecisions(decisions(), { ...makeMetadata(), state: 'CLOSED' });
    expect(isReviewError(parsed) ? parsed.code : '').toBe('DECISIONS_INVALID');
  });
});
