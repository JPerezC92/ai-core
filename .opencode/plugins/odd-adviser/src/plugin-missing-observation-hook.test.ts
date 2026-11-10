// Missing observation sources stay unobserved: without tool.hook no tool line is written,
// and without a stored evaluationId no observation is written for later frames.

import { describe, expect, test } from 'vitest';

import {
  createAdviserHarness,
  createAppliedFooterLine,
  createEvaluation,
  createEvaluationId,
  createMessageIdentity,
  createOutgoingContext,
  createRecordingEvaluator,
  createToolExecuteAfterEvent,
  createToolId,
  createWebSocketReceiveEvent,
} from './test/helpers/plugin.factory.ts';

describe('missing observation sources', () => {
  test('does not record a tool observation when tool.hook is missing', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.afterTool(createToolExecuteAfterEvent(createToolId()));

    expect(harness.observations).toHaveLength(0);
  });

  test('does not record an observation when evaluationId is unknown', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(),
      includeToolHook: true,
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createAppliedFooterLine()));
    await harness.afterTool(createToolExecuteAfterEvent(createToolId()));

    expect(harness.observations).toHaveLength(0);
  });
});
