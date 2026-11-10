import { describe, expect, test } from 'vitest';
import { evaluateEvidence } from './evaluate-evidence.ts';
import { createCapturedMessage, createControlledDeadline, createEvaluateEvidenceOptions, createExpectedEvidenceInput, createRecordingEvaluator, EVIDENCE_TOOL_NAME } from '../test/helpers/plugin.factory.ts';

describe('evaluateEvidence invocation', () => {
  test('calls the injected evidence port once with the captured text, images and expected model', async () => {
    const message = createCapturedMessage();
    const options = createEvaluateEvidenceOptions();
    const evaluator = createRecordingEvaluator();
    await evaluateEvidence(message, evaluator, options, createControlledDeadline());
    expect(evaluator.calls).toHaveLength(1);
    expect(evaluator.calls[0]?.input).toStrictEqual(createExpectedEvidenceInput(message, options));
    expect(evaluator.calls[0]?.options.timeoutMs).toBe(options.timeoutMs);
    expect(JSON.stringify(evaluator.calls[0]?.input ?? null)).not.toContain(EVIDENCE_TOOL_NAME);
  });
});
