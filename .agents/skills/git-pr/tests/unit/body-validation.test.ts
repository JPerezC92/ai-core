import { describe, expect, it } from 'vitest';

import {
  extractBody, parseFindings, parseSections, validateBody,
} from '#scripts/pr_content/domain/body_validation.ts';
import { isReviewError, parseMetadata } from '#scripts/pr_content/domain/records.ts';
import type { ReviewMetadata } from '#scripts/pr_content/domain/records.ts';
import { makeCompletedBody, makeMetadata } from '#tests/support/review-content-fixtures.ts';

function metadata(body = makeCompletedBody()): ReviewMetadata {
  const parsed = parseMetadata({ ...makeMetadata(), body });
  if (isReviewError(parsed)) throw new Error(`${parsed.code}: ${parsed.message}`);
  return parsed;
}

describe('creation draft extraction', () => {
  it('removes the title wrapper and keeps the body bytes', () => {
    const draft = 'Title: feat: thing\n\n---\n\n## Summary\n\nText\n';
    expect(extractBody(draft)).toBe('## Summary\n\nText\n');
  });

  it('rejects a draft without the wrapper', () => {
    const result = extractBody('## Summary\n\nText\n');
    expect(isReviewError(result) ? result.code : '').toBe('DRAFT_INVALID');
  });

  it('rejects a wrapper not followed by the Summary heading', () => {
    const result = extractBody('Title: x\n\n---\n\n## Other\n');
    expect(isReviewError(result) ? result.code : '').toBe('DRAFT_INVALID');
  });
});

describe('section parsing', () => {
  it('splits canonical sections in order', () => {
    const sections = parseSections(makeCompletedBody());
    expect(isReviewError(sections) ? [] : Object.keys(sections)).toEqual([
      'Summary', 'Test plan', 'Findings / blockers', 'Test evidence',
    ]);
  });

  it('rejects a body that does not start with a heading', () => {
    expect(isReviewError(parseSections('text\n## Summary\n\nx\n'))).toBe(true);
  });

  it('rejects an out-of-order section', () => {
    const body = '## Test plan\n\n- [x] a\n\n## Summary\n\nx\n';
    expect(isReviewError(parseSections(body))).toBe(true);
  });

  it('rejects a required section that is absent', () => {
    const body = '## Summary\n\nx\n\n## Test plan\n\n- [x] a\n';
    expect(isReviewError(parseSections(body))).toBe(true);
  });

  it('rejects an empty section', () => {
    const body = '## Summary\n\n\n## Test plan\n\n- [x] a\n\n## Findings / blockers\n\nx\n';
    expect(isReviewError(parseSections(body))).toBe(true);
  });
});

describe('finding table parsing', () => {
  it('accepts an explicit no-findings statement', () => {
    expect(parseFindings('No findings.\n')).toEqual([]);
  });

  it('parses canonical rows', () => {
    const table = [
      '| ID | Severity | Status | Evidence | Owner / resolution |',
      '|---|---|---|---|---|',
      '| F1 | `ADVISORY` | `OPEN` | candidate C1 | Cipher — awaiting decision |',
    ].join('\n');
    expect(parseFindings(table)).toEqual([{
      id: 'F1', severity: 'ADVISORY', status: 'OPEN',
      evidence: 'candidate C1', resolution: 'Cipher — awaiting decision',
    }]);
  });

  it('rejects a non-sequential id', () => {
    const table = [
      '| ID | Severity | Status | Evidence | Owner / resolution |',
      '|---|---|---|---|---|',
      '| F2 | `BLOCK` | `OPEN` | e | r |',
    ].join('\n');
    expect(isReviewError(parseFindings(table))).toBe(true);
  });

  it('rejects an unknown status', () => {
    const table = [
      '| ID | Severity | Status | Evidence | Owner / resolution |',
      '|---|---|---|---|---|',
      '| F1 | `BLOCK` | `PENDING` | e | r |',
    ].join('\n');
    expect(isReviewError(parseFindings(table))).toBe(true);
  });

  it('rejects an empty cell', () => {
    const table = [
      '| ID | Severity | Status | Evidence | Owner / resolution |',
      '|---|---|---|---|---|',
      '| F1 | `BLOCK` | `OPEN` |  | r |',
    ].join('\n');
    expect(isReviewError(parseFindings(table))).toBe(true);
  });
});

describe('completed body validation', () => {
  it('accepts a structurally complete PASS body', () => {
    expect(validateBody(makeCompletedBody(), metadata())).toBeUndefined();
  });

  it('rejects a missing verdict line', () => {
    expect(validateBody(makeCompletedBody({ verdict: 'done' }), metadata())?.code).toBe('BODY_INVALID');
  });

  it('rejects an early verdict line', () => {
    const body = `[PASS] — early\n${makeCompletedBody()}`;
    expect(validateBody(body, metadata(body))?.code).toBe('BODY_INVALID');
  });

  it('rejects an unresolved finding under PASS', () => {
    const findings = [
      '| ID | Severity | Status | Evidence | Owner / resolution |',
      '|---|---|---|---|---|',
      '| F1 | `BLOCK` | `OPEN` | e | r |',
    ].join('\n');
    const body = makeCompletedBody({ findings: `${findings}\n` });
    expect(validateBody(body, metadata(body))?.code).toBe('BODY_INVALID');
  });

  it('rejects a plan whose unchecked item is not an excluded decision', () => {
    const body = makeCompletedBody().replace('- [x] Run the focused suite', '- [ ] Run the focused suite');
    expect(validateBody(body, metadata(body))?.code).toBe('BODY_INVALID');
  });

  it('rejects duplicated plan items', () => {
    const body = makeCompletedBody({ items: ['same', 'same'] });
    expect(validateBody(body, metadata(body))?.code).toBe('BODY_INVALID');
  });

  it('rejects a base that does not end with the metadata base ref', () => {
    const body = makeCompletedBody().replace('origin/main', 'origin/develop');
    expect(validateBody(body, metadata(body))?.code).toBe('BODY_INVALID');
  });

  it('rejects a test-evidence row set that does not match the plan', () => {
    const body = makeCompletedBody().replace('| Confirm the import map resolves | `pnpm vitest run` | passed | Cipher |', '| other | x | y | z |');
    expect(validateBody(body, metadata(body))?.code).toBe('BODY_INVALID');
  });

  it('rejects missing test evidence when plan items remain', () => {
    const body = makeCompletedBody();
    const trimmed = body.slice(0, body.indexOf('## Test evidence')) + '[PASS] — 0 open findings\n';
    expect(validateBody(trimmed, metadata(makeCompletedBody()))?.code).toBe('BODY_INVALID');
  });
});
