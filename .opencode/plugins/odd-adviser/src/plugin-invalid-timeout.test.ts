import { expect, test } from 'vitest';

import { ADVISORY_BLOCK_START } from './index.ts';
import {
  createAdviserHarness,
  createEvaluateEvidenceOptions,
  createMessageIdentity,
  createOutgoingContext,
} from './test/helpers/plugin.factory.ts';

test('reports an unavailable caller for an invalid time limit without evaluating', async () => {
  const timeoutMs = -createEvaluateEvidenceOptions().timeoutMs;
  const harness = await createAdviserHarness({ timeoutMs });
  const context = createOutgoingContext(createMessageIdentity());

  await harness.build(context);

  expect(harness.evaluator.calls).toHaveLength(0);
  expect(harness.connections).toHaveLength(0);
  expect(harness.events.filter((event) => event.stage === 'evaluate_finished').map((event) => event.code))
    .toStrictEqual(['caller_unavailable']);
  expect(context.system).toHaveLength(1);
  expect(context.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
  expect(context.system[0]?.text).toContain('No System 1 evidence evaluation channel is configured for this session.');
});
