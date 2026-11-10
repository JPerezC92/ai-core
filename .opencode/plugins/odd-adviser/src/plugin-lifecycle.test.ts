// Lifecycle stages recorded by the advisory edge through an in-memory event sink.
import { describe, expect, test } from 'vitest';

import {
  createAllBelowBarEvaluation,
  createAdviserHarness,
  createContextWithoutUserMessage,
  createMessageIdentity,
  createOutgoingContext,
  createRecordingEvaluator,
} from './test/helpers/plugin.factory.ts';

describe('plugin lifecycle stages', () => {
  test('records each stage of a found candidate in the order the adapter reached it', async () => {
    const harness = await createAdviserHarness();

    await harness.build(createOutgoingContext(createMessageIdentity()));

    expect(harness.events.map ( (event) => event.stage)).toStrictEqual([
      'hook_registered',
      'candidate_found',
      'evaluate_started',
      'evaluate_finished',
      'advisory_injected',
    ]);
    const finished = harness.events.find((event) => event.stage === 'evaluate_finished');
    expect(finished?.code).toBe('evaluated');
    const injected = harness.events.find((event) => event.stage === 'advisory_injected');
    expect(injected?.parts).toBe(1);
  });

  test('records a context build whose conversation carries no user message', async () => {
    const harness = await createAdviserHarness();

    await harness.build(createContextWithoutUserMessage(createMessageIdentity()));

    expect(harness.events.map((event) => event.stage)).toStrictEqual([
      'hook_registered',
      'candidate_none',
    ]);
  });

  test('does not push an empty advisory or record advisory_injected when nothing qualifies', async () => {
    const harness = await createAdviserHarness({
      evaluator: createRecordingEvaluator(createAllBelowBarEvaluation()),
    });
    const context = createOutgoingContext(createMessageIdentity());

    await harness.build(context);

    expect(context.system).toHaveLength(0);
    expect(harness.events.map((event) => event.stage)).toStrictEqual([
      'hook_registered',
      'candidate_found',
      'evaluate_started',
      'evaluate_finished',
    ]);
  });
});
