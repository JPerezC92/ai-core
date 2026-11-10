// Completion-boundary footer observation: user-facing stop emits one footer row; intermediate
// tool/text-part signals do not; truncated or generic completes stay uninspectable, not none.

import { describe, expect, test } from 'vitest';

import {
  createAdviserHarness,
  createAppliedFooterLine,
  createChoicesDeltaFrame,
  createContinuationTextChunk,
  createDoneFrame,
  createIncompleteTextChunks,
  createEvaluation,
  createEvaluationId,
  createFinishReasonFrame,
  createLengthFinishFrame,
  createMessageIdentity,
  createOutgoingContext,
  createOutputTextDoneFrame,
  createOverriddenFooterLine,
  createRecordingEvaluator,
  createResponseCompletedFunctionCallFrame,
  createResponseCompletedMessageFrame,
  createResponseCompletedMessageId,
  createToolCallsFinishFrame,
  createUnmarkedAssistantText,
  createWebSocketReceiveEvent,
} from './test/helpers/plugin.factory.ts';

describe('plugin observation completion boundary', () => {
  test('does not record footer observations for many incomplete frames', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    for (const chunk of [...createIncompleteTextChunks(), createAppliedFooterLine()]) {
      await harness.receiveWs(createWebSocketReceiveEvent(createChoicesDeltaFrame(chunk)));
    }

    expect(harness.observations).toHaveLength(0);
  });

  test('records none for a user-facing stop with unmarked text', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createUnmarkedAssistantText()));
    await harness.receiveWs(createWebSocketReceiveEvent(createFinishReasonFrame()));

    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('none');
    expect(harness.observations[0]?.assessment).toBe('not_observed');
  });

  test('records one none for stop-with-content and no extra per-frame row', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });
    const content = createUnmarkedAssistantText();

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createFinishReasonFrame(content)));

    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('none');
    expect(harness.observations[0]?.evaluationId).toBe(createEvaluationId());
    expect(harness.observations[0]?.assessment).not.toBe('applied');
  });

  test('does not record none for a tool-call step before a final stop', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createUnmarkedAssistantText()));
    await harness.receiveWs(createWebSocketReceiveEvent(createToolCallsFinishFrame()));
    expect(harness.observations).toHaveLength(0);

    await harness.receiveWs(createWebSocketReceiveEvent(createAppliedFooterLine()));
    await harness.receiveWs(createWebSocketReceiveEvent(createFinishReasonFrame()));

    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('applied_line');
    expect(harness.observations[0]?.evaluationId).toBe(createEvaluationId());
    expect(harness.observations[0]?.assessment).toBe('not_observed');
  });

  test('does not record a footer for response.completed with a function call', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createUnmarkedAssistantText()));
    await harness.receiveWs(
      createWebSocketReceiveEvent(createResponseCompletedFunctionCallFrame()),
    );

    expect(harness.observations).toHaveLength(0);
  });

  test('does not record a footer for output_text.done before later user-facing stop', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createAppliedFooterLine()));
    await harness.receiveWs(createWebSocketReceiveEvent(createOutputTextDoneFrame()));
    expect(harness.observations).toHaveLength(0);

    await harness.receiveWs(
      createWebSocketReceiveEvent(createChoicesDeltaFrame(createContinuationTextChunk())),
    );
    await harness.receiveWs(
      createWebSocketReceiveEvent(createResponseCompletedMessageFrame()),
    );

    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('applied_line');
    expect(harness.observations[0]?.responseId).toBe(createResponseCompletedMessageId());
  });

  test('records uninspectable for length truncation, not none', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createUnmarkedAssistantText()));
    await harness.receiveWs(createWebSocketReceiveEvent(createLengthFinishFrame()));

    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('uninspectable');
  });

  test('records uninspectable for a generic [DONE] sentinel, not none', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createUnmarkedAssistantText()));
    await harness.receiveWs(createWebSocketReceiveEvent(createDoneFrame()));

    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('uninspectable');
  });

  test('records one observation per genuine user-facing continuation', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createAppliedFooterLine()));
    await harness.receiveWs(createWebSocketReceiveEvent(createFinishReasonFrame()));
    await harness.receiveWs(createWebSocketReceiveEvent(createOverriddenFooterLine()));
    await harness.receiveWs(createWebSocketReceiveEvent(createFinishReasonFrame()));

    expect(harness.observations).toHaveLength(2);
    expect(harness.observations[0]?.reportedFooter).toBe('applied_line');
    expect(harness.observations[1]?.reportedFooter).toBe('overridden_line');
    expect(harness.observations[0]?.evaluationId).toBe(createEvaluationId());
    expect(harness.observations[1]?.evaluationId).toBe(createEvaluationId());
  });

  test('records uninspectable on cleanup of an incomplete buffer, not none', async () => {
    const identity = createMessageIdentity();
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(identity));
    await harness.receiveWs(createWebSocketReceiveEvent(createUnmarkedAssistantText()));
    await harness.cleanup();

    expect(harness.observations).toHaveLength(1);
    expect(harness.observations[0]?.reportedFooter).toBe('uninspectable');
    expect(harness.observations[0]?.assessment).toBe('not_observed');
  });

  test('does not cross-associate concurrent message identities', async () => {
    const first = createMessageIdentity(1);
    const second = createMessageIdentity(2);
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createEvaluation(), createEvaluationId()),
    });

    await harness.build(createOutgoingContext(first));
    await harness.receiveWs(createWebSocketReceiveEvent(createAppliedFooterLine()));
    await harness.build(createOutgoingContext(second));
    await harness.receiveWs(createWebSocketReceiveEvent(createUnmarkedAssistantText()));
    await harness.receiveWs(createWebSocketReceiveEvent(createFinishReasonFrame()));

    expect(harness.observations).toHaveLength(2);
    expect(harness.observations[0]).toMatchObject({
      messageId: first.messageID,
      reportedFooter: 'uninspectable',
    });
    expect(harness.observations[1]).toMatchObject({
      messageId: second.messageID,
      reportedFooter: 'none',
    });
  });
});
