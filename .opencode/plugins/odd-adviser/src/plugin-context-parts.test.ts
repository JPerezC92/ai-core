import { describe, expect, test } from 'vitest';

import { ADVISORY_BLOCK_START } from './index.ts';
import {
  createAdviserHarness,
  createEvidenceText,
  createInlineImage,
  createMessageIdentity,
  createOutgoingContext,
} from './test/helpers/plugin.factory.ts';

describe('context part array shape', () => {
  test('admits a message whose part array arrives under content', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();

    const context = createOutgoingContext(identity, 'content');
    await harness.build(context);

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(harness.evaluator.calls[0]?.input.text).toBe(createEvidenceText());
    expect(harness.evaluator.calls[0]?.input.images).toStrictEqual([createInlineImage()]);
    expect(context.system).toHaveLength(1);
    expect(context.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
  });

  test('admits a message whose part array arrives under parts', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();

    const context = createOutgoingContext(identity, 'parts');
    await harness.build(context);

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(harness.evaluator.calls[0]?.input.text).toBe(createEvidenceText());
    expect(harness.evaluator.calls[0]?.input.images).toStrictEqual([createInlineImage()]);
    expect(context.system).toHaveLength(1);
    expect(context.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
  });
});
