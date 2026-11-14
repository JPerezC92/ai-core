import { describe, expect, it } from 'vitest';

import { execute } from '#scripts/pr_content/application/validate_final_body.ts';
import { validatePreservation } from '#scripts/pr_content/domain/review_content_preservation.ts';
import { HEAD_SHA, makeCompletedBody, makeMetadata } from '#tests/support/review-content-fixtures.ts';

const BODY = makeCompletedBody();
const METADATA = makeMetadata();

describe('preservation of baseline content', () => {
  it('accepts an unchanged body', () => {
    expect(validatePreservation(BODY, BODY)).toBeUndefined();
  });

  it('rejects a rewritten Summary', () => {
    const changed = BODY.replace('Adds the review preparation commands.', 'Different prose.');
    expect(validatePreservation(BODY, changed)?.code).toBe('BODY_INVALID');
  });

  it('accepts a checkbox change in the test plan', () => {
    const changed = BODY.replace('- [x] Run the focused suite', '- [ ] Run the focused suite');
    expect(validatePreservation(BODY, changed)).toBeUndefined();
  });

  it('rejects an added plan line', () => {
    const changed = BODY.replace(
      '- [x] Confirm the import map resolves',
      '- [x] Confirm the import map resolves\n- [x] extra item',
    );
    expect(validatePreservation(BODY, changed)?.code).toBe('BODY_INVALID');
  });
});

describe('final body validation', () => {
  it('accepts a fresh matching completed body', () => {
    const outcome = execute({ baseline: METADATA, current: METADATA, body: BODY });
    expect('code' in outcome ? outcome.code : outcome.body).toBe(BODY);
  });

  it('rejects a diverged remote metadata record', () => {
    const outcome = execute({
      baseline: METADATA,
      current: { ...METADATA, headRefOid: 'ffffffffffffffffffffffffffffffffffffffff' },
      body: BODY,
    });
    expect('code' in outcome ? outcome.code : '').toBe('REMOTE_DIVERGED');
  });

  it('rejects stale metadata that is not valid at all', () => {
    const outcome = execute({ baseline: METADATA, current: { ...METADATA, state: 'MERGED' }, body: BODY });
    expect('code' in outcome ? outcome.code : '').toBe('METADATA_INVALID');
  });

  it('rejects decisions bound to another head', () => {
    const outcome = execute({
      baseline: METADATA,
      current: METADATA,
      body: BODY,
      decisions: { pr_number: 12, head_sha: 'deadbeef', not_applicable: [], acceptance: [], debt: [] },
    });
    expect('code' in outcome ? outcome.code : '').toBe('DECISIONS_INVALID');
  });

  it('does not treat a matching head as a passing body', () => {
    const broken = BODY.replace('[PASS] — 0 open findings', 'not a verdict');
    const outcome = execute({
      baseline: makeMetadata({ body: broken }), current: makeMetadata({ body: broken }), body: broken,
    });
    expect('code' in outcome ? outcome.code : '').toBe('BODY_INVALID');
  });

  it('rejects a body whose protected prose changed after acceptance', () => {
    const changed = makeCompletedBody({ summary: 'Rewritten after acceptance.\n' });
    const outcome = execute({ baseline: METADATA, current: METADATA, body: changed });
    expect('code' in outcome ? outcome.code : '').toBe('BODY_INVALID');
  });

  it('keeps the immutable head visible in the accepted body', () => {
    const outcome = execute({ baseline: METADATA, current: METADATA, body: BODY });
    expect('code' in outcome ? '' : outcome.body.includes(HEAD_SHA)).toBe(true);
  });
});
