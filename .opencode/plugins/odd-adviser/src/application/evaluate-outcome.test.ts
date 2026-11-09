import { describe, expect, test } from 'vitest';
import { evaluateEvidence } from './evaluate-evidence.ts';
import { formatAdvisoryBlock } from '../domain/advisory-block.ts';
import { createCapturedMessage, createControlledDeadline, createEvaluateEvidenceOptions, createExpectedEvaluatedAdvisory, createExpectedUnavailableAdvisory, createEvaluation, createRecordingEvaluator, createThrowingEvaluator, createUnavailableEvaluator, createUnansweredEvaluation, TRANSPORT_FAILURE_MESSAGE } from '../test/helpers/plugin.factory.ts';

describe('evaluateEvidence outcome mapping', () => {
  test('returns the validated evaluation when the port answers with a contract-valid value', async () => {
    const evaluation = createEvaluation();
    const outcome = await evaluateEvidence(createCapturedMessage(), createRecordingEvaluator(evaluation), createEvaluateEvidenceOptions(), createControlledDeadline());
    expect(outcome).toStrictEqual(createExpectedEvaluatedAdvisory(evaluation, expect.any(String)));
  });

  test('maps an evaluation that answers no question to the bounded malformed payload status', async () => {
    const outcome = await evaluateEvidence(createCapturedMessage(), createRecordingEvaluator(createUnansweredEvaluation()), createEvaluateEvidenceOptions(), createControlledDeadline());
    expect(outcome).toStrictEqual(createExpectedUnavailableAdvisory('malformed_payload', expect.any(String)));
    const block = formatAdvisoryBlock(outcome);
    expect(block.split('\n')).toHaveLength(4);
    expect(block).not.toContain('→');
  });

  test('maps a bounded tool error value to the matching unavailable status', async () => {
    const outcome = await evaluateEvidence(createCapturedMessage(), createUnavailableEvaluator(), createEvaluateEvidenceOptions(), createControlledDeadline());
    expect(outcome).toStrictEqual(createExpectedUnavailableAdvisory('tool_error', expect.any(String)));
  });

  test('maps a rejected channel to a bounded status without its message', async () => {
    const outcome = await evaluateEvidence(createCapturedMessage(), createThrowingEvaluator(), createEvaluateEvidenceOptions(), createControlledDeadline());
    expect(outcome).toStrictEqual(createExpectedUnavailableAdvisory('transport_error', expect.any(String)));
    expect(outcome.advisory).not.toContain(TRANSPORT_FAILURE_MESSAGE);
  });
});
