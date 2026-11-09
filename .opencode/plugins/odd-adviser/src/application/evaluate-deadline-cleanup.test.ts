import { describe, expect, test } from 'vitest';
import { evaluateEvidence } from './evaluate-evidence.ts';
import { createCapturedMessage, createControlledDeadline, createEvaluateEvidenceOptions, createEvaluation, createExpectedEvaluatedAdvisory, createExpectedUnavailableAdvisory, createRecordingEvaluator, createThrowingEvaluator } from '../test/helpers/plugin.factory.ts';

describe('evaluateEvidence deadline cleanup', () => {
  test('cancels the pending deadline when evaluation succeeds first', async () => {
    const deadline = createControlledDeadline();
    const evaluation = createEvaluation();
    const outcome = await evaluateEvidence(createCapturedMessage(), createRecordingEvaluator(evaluation), createEvaluateEvidenceOptions(), deadline);

    expect(outcome).toStrictEqual(createExpectedEvaluatedAdvisory(evaluation, expect.any(String)));
    expect(deadline.cancellations).toBe(1);
    expect(deadline.isPending).toBe(false);
  });

  test('cancels the pending deadline when evaluation rejects first', async () => {
    const deadline = createControlledDeadline();
    const outcome = await evaluateEvidence(createCapturedMessage(), createThrowingEvaluator(), createEvaluateEvidenceOptions(), deadline);

    expect(outcome).toStrictEqual(createExpectedUnavailableAdvisory('transport_error', expect.any(String)));
    expect(deadline.cancellations).toBe(1);
    expect(deadline.isPending).toBe(false);
  });
});
