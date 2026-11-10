// Tool-after observation: a completed or failed tool is recorded by id and status only,
// assessment stays not_observed, and continuations reuse the stored evaluationId.

import { describe, expect, test } from 'vitest';

import {
  createAdviserHarness,
  createEvaluation,
  createEvaluationId,
  createMessageIdentity,
  createOutgoingContext,
  createRecordingEvaluator,
  createToolExecuteAfterEvent,
  createToolId,
  TRANSPORT_FAILURE_MESSAGE,
} from './test/helpers/plugin.factory.ts';

describe('tool execute after observation', () => {
  test('records tool id and status without treating the footer as applied', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
      includeToolHook: true,
    });

    await harness.build(createOutgoingContext(identity));
    await harness.afterTool(createToolExecuteAfterEvent(createToolId()));
    await harness.afterTool(
      createToolExecuteAfterEvent(createToolId(), { message: TRANSPORT_FAILURE_MESSAGE }),
    );

    expect(harness.observations).toHaveLength(2);
    expect(harness.observations[0]).toMatchObject({
      schemaVersion: 4,
      recordType: 'observation',
      evaluationId: createEvaluationId(),
      sessionId: identity.sessionID,
      messageId: identity.messageID,
      tools: [{ id: createToolId(), status: 'completed' }],
      assessment: 'not_observed',
    });
    expect(harness.observations[1]?.tools).toStrictEqual([
      { id: createToolId(), status: 'error' },
    ]);
    expect(harness.observations[0]).not.toHaveProperty('handling');
    expect(JSON.stringify(harness.observations)).not.toContain(TRANSPORT_FAILURE_MESSAGE);
  });

  test('reuses the stored evaluationId on a continuation tool call', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
      includeToolHook: true,
    });

    await harness.build(createOutgoingContext(identity));
    await harness.build(createOutgoingContext(identity));
    await harness.afterTool(createToolExecuteAfterEvent(createToolId()));

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.evaluationId).toBe(createEvaluationId());
  });
});
