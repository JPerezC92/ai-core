import { describe, expect, test } from 'vitest';

import { ADVISORY_BLOCK_START } from './index.ts';
import {
  createAdmittedMessage,
  createAdviserHarness,
  createEvidenceText,
  createInlineImage,
  createMessageIdentity,
  createOutgoingContext,
} from './test/helpers/plugin.factory.ts';

describe('one evaluation per admitted message', () => {
  test('reuses one evaluation for repeated context builds of the same message', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();
    harness.admit(createAdmittedMessage(identity));

    const first = createOutgoingContext(identity);
    const continuation = createOutgoingContext(identity);
    await harness.build(first);
    await harness.build(continuation);

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(first.system).toHaveLength(1);
    expect(first.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
    expect(first.system[0]?.text).not.toContain(createEvidenceText());
    expect(continuation.system).toHaveLength(1);
  });

  test('starts a new evaluation when a newer message is admitted', async () => {
    const harness = await createAdviserHarness();
    const first = createMessageIdentity(1);
    const second = createMessageIdentity(2);

    harness.admit(createAdmittedMessage(first));
    await harness.build(createOutgoingContext(first));
    await harness.build(createOutgoingContext(first));

    harness.admit(createAdmittedMessage(second));
    await harness.build(createOutgoingContext(second));
    await harness.build(createOutgoingContext(second));

    expect(harness.evaluator.calls).toHaveLength(2);
  });

  test('evaluates a message admitted only by the outgoing context and reuses it', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();

    const first = createOutgoingContext(identity);
    const continuation = createOutgoingContext(identity);
    await harness.build(first);
    await harness.build(continuation);

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(harness.evaluator.calls[0]?.input.text).toBe(createEvidenceText());
    expect(harness.evaluator.calls[0]?.input.images).toStrictEqual([createInlineImage()]);
    expect(first.system).toHaveLength(1);
    expect(first.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
    expect(continuation.system).toHaveLength(1);
  });
});
