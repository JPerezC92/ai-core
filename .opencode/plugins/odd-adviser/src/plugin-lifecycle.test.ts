// Behaviour tests of the portable System 1 advisory edge's hook lifecycle: the once-per-message
// reuse of one evaluation across repeated context builds, the two part-array spellings a context
// message can arrive under, and the lifecycle stages the adapter records as it reaches them. No
// case spawns a process, reaches the network or contacts a model endpoint: the listeners are
// driven through a host session double and the recorded stages come from an event sink double.

import { describe, expect, test } from 'vitest';

import { ADVISORY_BLOCK_START } from './index.ts';
import {
  createAdmittedMessage,
  createAdviserHarness,
  createContextWithoutUserMessage,
  createEvidenceText,
  createInlineImage,
  createMessageIdentity,
  createOutgoingContext,
} from './test/helpers/plugin.factory.ts';

describe('one evaluation per admitted message', () => {
  test('reuses one evaluation for repeated context builds of the same message', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();
    harness.admit(createAdmittedMessage(identity));

    const first = createOutgoingContext(identity);
    const continuation = createOutgoingContext(identity);
    await harness.build(first);
    await harness.build(continuation);

    expect(harness.evaluator.calls).toHaveLength(1);
    // Each build of the same message receives exactly one advisory part, and the supplied
    // text is not pushed beside it.
    expect(first.system).toHaveLength(1);
    expect(first.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
    expect(first.system[0]?.text).not.toContain(createEvidenceText());
    expect(continuation.system).toHaveLength(1);
  });

  test('starts a new evaluation when a newer message is admitted', async () => {
    const harness = await createAdviserHarness();
    const first = createMessageIdentity(1);
    const second = createMessageIdentity(2);

    harness.admit(createAdmittedMessage(first));
    await harness.build(createOutgoingContext(first));
    await harness.build(createOutgoingContext(first));

    harness.admit(createAdmittedMessage(second));
    await harness.build(createOutgoingContext(second));
    await harness.build(createOutgoingContext(second));

    expect(harness.evaluator.calls).toHaveLength(2);
  });

  test('evaluates a message admitted only by the outgoing context and reuses it', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();

    // The prompt hook never fires for this message, so the context event's own conversation
    // is the only admission source.
    const first = createOutgoingContext(identity);
    const continuation = createOutgoingContext(identity);
    await harness.build(first);
    await harness.build(continuation);

    expect(harness.evaluator.calls).toHaveLength(1);
    // The message is captured from the context parts, text and inline image included.
    expect(harness.evaluator.calls[0]?.input.text).toBe(createEvidenceText());
    expect(harness.evaluator.calls[0]?.input.images).toStrictEqual([createInlineImage()]);
    // Each build receives exactly one advisory part, and the repeated build reuses it.
    expect(first.system).toHaveLength(1);
    expect(first.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
    expect(continuation.system).toHaveLength(1);
  });
});

describe('context part array shape', () => {
  test('admits a message whose part array arrives under content', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();

    // The researched host shape behind the observed `candidate none`: the array under
    // `content` with no `parts` field beside it, so only the newly accepted spelling can admit
    // this message.
    const context = createOutgoingContext(identity, 'content');
    await harness.build(context);

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(harness.evaluator.calls[0]?.input.text).toBe(createEvidenceText());
    expect(harness.evaluator.calls[0]?.input.images).toStrictEqual([createInlineImage()]);
    expect(context.system).toHaveLength(1);
    expect(context.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
  });

  test('admits a message whose part array arrives under parts', async () => {
    const harness = await createAdviserHarness();
    const identity = createMessageIdentity();

    // The spelling this adapter previously assumed, kept covered so accepting `content` did
    // not become the only shape the edge can read.
    const context = createOutgoingContext(identity, 'parts');
    await harness.build(context);

    expect(harness.evaluator.calls).toHaveLength(1);
    expect(harness.evaluator.calls[0]?.input.text).toBe(createEvidenceText());
    expect(harness.evaluator.calls[0]?.input.images).toStrictEqual([createInlineImage()]);
    expect(context.system).toHaveLength(1);
    expect(context.system[0]?.text.startsWith(ADVISORY_BLOCK_START)).toBe(true);
  });
});

describe('plugin lifecycle stages', () => {
  test('records each stage of a found candidate in the order the adapter reached it', async () => {
    const harness = await createAdviserHarness();

    await harness.build(createOutgoingContext(createMessageIdentity()));

    expect(harness.events.map((event) => event.stage)).toStrictEqual([
      'hook_registered',
      'candidate_found',
      'evaluate_started',
      'evaluate_finished',
      'advisory_injected',
    ]);
    // The finished stage names the bounded outcome, and the injected stage counts the parts the
    // host request received rather than repeating their text (S6, S9).
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
});
