// Behaviour tests of the portable System 1 advisory edge's core evaluation path, with its
// injected evidence port doubled: one call per captured message carrying the text, images and
// expected model, the mapping of each bounded port answer to its status, and the advisory that
// follows. No case spawns a process, reaches the network or contacts a model endpoint.

import { describe, expect, test } from 'vitest';

import { evaluateEvidence, formatAdvisoryBlock } from './index.ts';
import {
  createCapturedMessage,
  createEvaluateEvidenceOptions,
  createEvaluation,
  createHangingEvaluator,
  createLeakCanary,
  createRecordingEvaluator,
  createThrowingEvaluator,
  createUnavailableEvaluator,
  createUnansweredEvaluation,
  EVIDENCE_TOOL_NAME,
  TRANSPORT_FAILURE_MESSAGE,
  type LeakCanary,
} from './test/helpers/plugin.factory.ts';

// One check reused by every branch: a delivered advisory is never empty and never repeats any
// part of the supplied evidence, whole or partial (S9).
function expectNoEvidenceLeak(advisory: string, canary: LeakCanary): void {
  expect(advisory.length).toBeGreaterThan(0);
  for (const fragment of canary.forbiddenFragments) {
    expect(advisory).not.toContain(fragment);
  }
}

describe('evaluateEvidence', () => {
  test('calls the injected evidence port once with the captured text, images and expected model', async () => {
    const message = createCapturedMessage();
    const options = createEvaluateEvidenceOptions();
    const evaluator = createRecordingEvaluator();

    await evaluateEvidence(message, evaluator, options);

    expect(evaluator.calls).toHaveLength(1);
    expect(evaluator.calls[0]?.input).toStrictEqual({
      text: message.text,
      images: message.images,
      expectedModel: options.expectedModel,
    });
    expect(evaluator.calls[0]?.options.timeoutMs).toBe(options.timeoutMs);
    // The domain request names no tool: the transport identity stays in the adapter.
    expect(JSON.stringify(evaluator.calls[0]?.input ?? null)).not.toContain(
      EVIDENCE_TOOL_NAME,
    );
  });

  test('returns the validated evaluation when the port answers with a contract-valid value', async () => {
    const evaluation = createEvaluation();

    const outcome = await evaluateEvidence(
      createCapturedMessage(),
      createRecordingEvaluator(evaluation),
      createEvaluateEvidenceOptions(),
    );

    expect(outcome).toStrictEqual({
      status: 'evaluated',
      evaluation,
      advisory: expect.any(String),
    });
  });

  test('maps an evaluation that answers no question to the bounded malformed payload status', async () => {
    const outcome = await evaluateEvidence(
      createCapturedMessage(),
      createRecordingEvaluator(createUnansweredEvaluation()),
      createEvaluateEvidenceOptions(),
    );

    // An empty answers record would otherwise deliver a receipt: a block that reports only that
    // an answer arrived and names no question at all (R2).
    expect(outcome).toStrictEqual({
      status: 'unavailable',
      code: 'malformed_payload',
      advisory: expect.any(String),
    });
    const block = formatAdvisoryBlock(outcome);
    expect(block.split('\n')).toHaveLength(4);
    expect(block).not.toContain('→');
  });

  test('maps a bounded tool error value to the matching unavailable status', async () => {
    const outcome = await evaluateEvidence(
      createCapturedMessage(),
      createUnavailableEvaluator(),
      createEvaluateEvidenceOptions(),
    );

    expect(outcome).toStrictEqual({
      status: 'unavailable',
      code: 'tool_error',
      advisory: expect.any(String),
    });
  });

  test('maps a rejected channel to a bounded status without its message', async () => {
    const outcome = await evaluateEvidence(
      createCapturedMessage(),
      createThrowingEvaluator(),
      createEvaluateEvidenceOptions(),
    );

    expect(outcome).toStrictEqual({
      status: 'unavailable',
      code: 'transport_error',
      advisory: expect.any(String),
    });
    expect(outcome.advisory).not.toContain(TRANSPORT_FAILURE_MESSAGE);
  });

  test('maps a channel that never settles to the timeout status without leaking the message', { timeout: 2000 }, async () => {
    const canary = createLeakCanary();

    const outcome = await evaluateEvidence(
      canary.message,
      createHangingEvaluator(),
      createEvaluateEvidenceOptions(),
    );

    expect(outcome).toStrictEqual({
      status: 'unavailable',
      code: 'timeout',
      advisory: expect.any(String),
    });
    expectNoEvidenceLeak(outcome.advisory, canary);
  });

  // The one delivery-path leak case: it reads a delivered evaluation rather than a fixture that
  // carries no message, and it judges both what the delivery reports and the block the context
  // hook appends from it, so a line the block adds cannot repeat the supplied evidence either
  // (S9). The block carries the advisory beside its question lines, so the second check covers
  // every line that reaches the model.
  test('delivers an evaluated advisory and the block built from it that repeat no supplied text or image bytes', async () => {
    const canary = createLeakCanary();

    const outcome = await evaluateEvidence(
      canary.message,
      createRecordingEvaluator(),
      createEvaluateEvidenceOptions(),
    );

    expect(outcome.status).toBe('evaluated');
    expectNoEvidenceLeak(outcome.advisory, canary);
    expectNoEvidenceLeak(formatAdvisoryBlock(outcome), canary);
  });

  test('delivers an unavailable advisory that repeats no supplied text or image bytes', async () => {
    const canary = createLeakCanary();

    const outcome = await evaluateEvidence(
      canary.message,
      createUnavailableEvaluator(),
      createEvaluateEvidenceOptions(),
    );

    expect(outcome).toStrictEqual({
      status: 'unavailable',
      code: 'tool_error',
      advisory: expect.any(String),
    });
    expectNoEvidenceLeak(outcome.advisory, canary);
  });
});
