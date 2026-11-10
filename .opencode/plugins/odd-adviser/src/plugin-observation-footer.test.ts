// Plugin footer observation: reconstructed assistant text classifies the S1 line, never
// sets a handling disposition from that line, and leaves host frames and HTTP bodies intact.

import { describe, expect, test } from 'vitest';

import {
  createAdviserHarness,
  createAppliedFooterLine,
  createFinishReasonFrame,
  createEvaluation,
  createEvaluationId,
  createHttpResponseEvent,
  createMessageIdentity,
  createOutgoingContext,
  createOverriddenFooterLine,
  createRecordingEvaluator,
  createSplitFooterPrefix,
  createSplitFooterSuffix,
  createWebSocketReceiveEvent,
} from './test/helpers/plugin.factory.ts';

describe('plugin observation footer', () => {
  test('records one applied_line after a split footer completes and does not set applied', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });
    const first = createWebSocketReceiveEvent(createSplitFooterPrefix());
    const second = createWebSocketReceiveEvent(createSplitFooterSuffix());
    const done = createWebSocketReceiveEvent(createFinishReasonFrame());

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(first);
    await harness.receiveWs(second);
    expect(harness.observations).toHaveLength(0);

    await harness.receiveWs(done);

    expect(first.event.frame).toBe(first.frame);
    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]).toMatchObject({
      evaluationId: createEvaluationId(),
      sessionId: identity.sessionID,
      messageId: identity.messageID,
      reportedFooter: 'applied_line',
      assessment: 'not_observed',
    });
    expect(harness.observations[0]).not.toHaveProperty('handling');
    expect(harness.observations[0]?.assessment).not.toBe('applied');
  });

  test('clones an HTTP body and classifies mixed footer markers once', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });
    const { event, response } = createHttpResponseEvent(
      `${createAppliedFooterLine()}\n${createOverriddenFooterLine()}`,
    );

    await harness.build(createOutgoingContext(identity));
    await harness.receiveHttp(event);

    expect(event.response).toBe(response);
    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('mixed');
    expect(harness.observations[0]?.assessment).toBe('not_observed');
  });
});
