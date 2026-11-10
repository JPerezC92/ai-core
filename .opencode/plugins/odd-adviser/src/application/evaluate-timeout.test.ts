import { describe, expect, test } from 'vitest';
import { evaluateEvidence } from './evaluate-evidence.ts';
import { createControlledDeadline, createEvaluateEvidenceOptions, createExpectedUnavailableAdvisory, createHangingEvaluator, createLeakCanary, type LeakCanary } from '../test/helpers/plugin.factory.ts';

function expectNoEvidenceLeak(advisory: string, canary: LeakCanary): void {
  expect(advisory.length).toBeGreaterThan(0);
  for (const fragment of canary.forbiddenFragments) expect(advisory).not.toContain(fragment);
}

describe('evaluateEvidence timeout', () => {
  test('maps a channel that never settles to the timeout status without leaking the message', { timeout: 2000 }, async () => {
    const canary = createLeakCanary();
    const deadline = createControlledDeadline();
    const options = createEvaluateEvidenceOptions();
    const pending = evaluateEvidence(canary.message, createHangingEvaluator(), options, deadline);
    expect(deadline.requestedMs).toBe(options.timeoutMs);
    expect(deadline.isPending).toBe(true);
    deadline.trigger();
    const outcome = await pending;
    expect(outcome).toStrictEqual(createExpectedUnavailableAdvisory('timeout', expect.any(String)));
    expectNoEvidenceLeak(outcome.advisory, canary);
    expect(deadline.cancellations).toBe(1);
    expect(deadline.isPending).toBe(false);
  });
});
