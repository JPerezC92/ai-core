// Integration test of the LM Studio decision gateway across its HTTP boundary:
// `fetch` is stubbed at the transport and the adapter is exercised directly, so the
// assertions cover the request it forms and how each transport outcome surfaces.
// No real network, filesystem path or environment value participates.

import { afterEach, expect, test, vi } from 'vitest';

import {
  LmStudioDecisionGateway,
  LmStudioGatewayBoundaryError,
} from './lm-studio-decision-gateway.ts';
import {
  createAbortFailureNames,
  createDecisionBody,
  createDecisionRequestUrl,
  createEvidenceInput,
  createGatewayOptions,
  createInlineImageDataUrl,
  createNonSuccessFetchDouble,
  createNonSuccessScenario,
  createNonTimeoutFailures,
  createSuccessFetchDouble,
  createTimeoutFetchDouble,
  createTimeoutScenario,
} from '../test/helpers/lm-studio.factory.ts';

// The transport is stubbed on the global for each case; restoring it after every case
// keeps the suite independent of run order and of the real `fetch`.
afterEach(() => {
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

// The timeout outcome is an abort, so the surfaced error must name the abort cause
// itself or carry it in its cause chain. The HTTP boundary error reports a status and
// cannot represent a timeout; a generic error and the `TypeError` that `fetch` raises
// for a transport failure name no abort cause. Both helpers are arrow functions so the
// `toSatisfy` matcher receives a predicate rather than a class to construct.
const abortFailureNames = new Set(createAbortFailureNames());
// Bound retained because a cause chain is caller-controlled.
const maxCauseDepth = 4;

const namesAbortCause = (error: Error, depth: number): boolean =>
  abortFailureNames.has(error.name) ||
  (depth < maxCauseDepth &&
    error.cause instanceof Error &&
    namesAbortCause(error.cause, depth + 1));

const isTimeoutAbortFailure = (error: unknown): boolean =>
  error instanceof Error &&
  !(error instanceof LmStudioGatewayBoundaryError) &&
  namesAbortCause(error, 0);

// Vitest's `expect` reports a missing value but does not narrow it for TypeScript the
// way the previous `assert.ok` call did, so the recorded item is also narrowed here; a
// missing item still fails the case with the message below.
function recorded<T>(value: T | undefined, message: string): T {
  expect(value, message).toBeDefined();
  if (value === undefined) throw new Error(message);
  return value;
}

// A parsed JSON body is `unknown`/`any`; this narrows it to the keyed object the wire
// contract requires, failing the case rather than silently skipping the shape check.
function readRecord(value: unknown, message: string): Record<string, unknown> {
  const isKeyedObject = typeof value === 'object' && value !== null && !Array.isArray(value);
  expect(isKeyedObject, message).toBe(true);
  if (!isKeyedObject) throw new Error(message);
  return value as Record<string, unknown>;
}

test('posts the evidence to the system-1 endpoint with inline image data URLs', async () => {
  const options = createGatewayOptions();
  const input = createEvidenceInput();
  const transport = createSuccessFetchDouble();
  vi.stubGlobal('fetch', transport.fetch);

  const gateway = new LmStudioDecisionGateway(options);
  await gateway.decide(input);

  expect(transport.calls.length).toBe(1);
  const request = recorded(transport.calls[0], 'the transport recorded the request it sent');
  expect(request.url).toBe(createDecisionRequestUrl(options));
  expect(request.init.method).toBe('POST');
  expect(new Headers(request.init.headers).get('content-type') ?? '').toMatch(/^application\/json/);

  const body = readRecord(
    JSON.parse(String(request.init.body)),
    'the request body is a JSON object',
  );

  // The observed body carries exactly these four fields; an invented field is a defect, so
  // the whole key set is asserted rather than only the fields this adapter sends.
  expect(Object.keys(body).sort()).toStrictEqual(['images', 'model', 'questions', 'state']);
  expect(body.model).toBe(options.model);
  expect(body.state).toBe(input.text);

  // The observed question container is an object keyed by question id, never an array, and
  // its ids are asserted literally here rather than taken from the input under test, so the
  // assertion covers the wire shape the endpoint accepts instead of restating the fixture.
  const expectedQuestionIds = ['scope_changed', 'user_only_decision'] as const;
  expect(Array.isArray(body.questions)).toBe(false);
  const questions = readRecord(
    body.questions,
    'the questions container is an object keyed by question id',
  );
  expect(Object.keys(questions).sort()).toStrictEqual([...expectedQuestionIds].sort());
  for (const id of expectedQuestionIds) {
    // Each question carries exactly the answer kind, instruction and criteria the endpoint
    // accepts; the omitted `type` was the second observed defect.
    const question = readRecord(questions[id], `the ${id} question is a JSON object`);
    expect(Object.keys(question).sort()).toStrictEqual(['criteria', 'instructions', 'type']);
    expect(question.type).toBe('choice');
    expect(typeof question.instructions).toBe('string');
    const criteria = readRecord(question.criteria, `the ${id} criteria are a JSON object`);
    expect(Object.keys(criteria).sort()).toStrictEqual(['absent', 'present']);

    // The supplied question still reaches the endpoint unchanged, so the shape assertions
    // above prove the container and this one proves nothing was silently dropped or edited.
    const supplied = input.questions[id];
    expect(supplied, `the fixture supplies the ${id} question`).toBeDefined();
    expect(question).toStrictEqual(supplied);
  }

  // The exact-image assertion is the no-path guarantee: every image is represented only by
  // a data URL derived from its mimeType and base64 payload.
  expect(body.images).toStrictEqual(
    input.images.map((image) => createInlineImageDataUrl(image)),
  );
});

test('returns the parsed decision envelope for a 2xx response', async () => {
  const body = createDecisionBody();
  const transport = createSuccessFetchDouble(body);
  vi.stubGlobal('fetch', transport.fetch);

  const gateway = new LmStudioDecisionGateway(createGatewayOptions());

  const result = await gateway.decide(createEvidenceInput());

  expect(result).toStrictEqual(body);
  expect(transport.calls.length).toBe(1);
});

test('throws a boundary error for a non-2xx response', async () => {
  const scenario = createNonSuccessScenario();
  const transport = createNonSuccessFetchDouble(scenario);
  vi.stubGlobal('fetch', transport.fetch);

  const gateway = new LmStudioDecisionGateway(createGatewayOptions());

  await expect(gateway.decide(createEvidenceInput())).rejects.toSatisfy(
    (error: unknown) =>
      error instanceof LmStudioGatewayBoundaryError && error.status === scenario.status,
    `the gateway rejection reports the ${scenario.status} response status`,
  );
  expect(transport.calls.length).toBe(1);
});

test('aborts each configured timeout and surfaces the abort cause', async () => {
  const scenario = createTimeoutScenario();
  let previousCase: { readonly timeoutMs: number; readonly elapsedMs: number } | undefined;

  for (const timeoutCase of scenario.cases) {
    const transport = createTimeoutFetchDouble(timeoutCase);
    vi.stubGlobal('fetch', transport.fetch);
    const gateway = new LmStudioDecisionGateway(
      createGatewayOptions({ timeoutMs: timeoutCase.timeoutMs }),
    );

    // A timeout is not an HTTP boundary response: it surfaces as the abort cause, never
    // as a returned value and never as a status-carrying boundary error.
    await expect(gateway.decide(createEvidenceInput())).rejects.toSatisfy(
      isTimeoutAbortFailure,
      `the ${timeoutCase.timeoutMs} ms timeout surfaces the abort cause`,
    );

    expect(transport.calls.length).toBe(1);
    const request = recorded(
      transport.calls[0],
      'the transport recorded the request it aborted',
    );
    expect(request.init.signal).toBeInstanceOf(AbortSignal);
    expect(request.init.signal?.aborted).toBe(true);

    // The double records the abort, so the injected timeout itself is verified: the
    // elapsed time sits inside this case's factory-derived window rather than "some
    // rejection happened". The windows of the two cases do not overlap, so an adapter
    // that aborts immediately or applies one fixed delay cannot satisfy both.
    const abort = recorded(
      transport.aborts[0],
      'the timeout transport recorded the abort it settled on',
    );
    expect(
      abort.elapsedMs >= timeoutCase.minAbortElapsedMs &&
        abort.elapsedMs <= timeoutCase.maxAbortElapsedMs,
      `expected an abort after ${timeoutCase.timeoutMs} ms within ` +
        `[${timeoutCase.minAbortElapsedMs}, ${timeoutCase.maxAbortElapsedMs}] ms, ` +
        `observed ${abort.elapsedMs} ms`,
    ).toBe(true);

    // Each case tracks its own injected timeout: the longer timeout aborts later, which
    // a fixed delay cannot produce.
    if (previousCase !== undefined) {
      expect(
        abort.elapsedMs > previousCase.elapsedMs,
        `expected the ${timeoutCase.timeoutMs} ms case to abort after the ` +
          `${previousCase.timeoutMs} ms case, observed ${abort.elapsedMs} ms and ` +
          `${previousCase.elapsedMs} ms`,
      ).toBe(true);
    }
    previousCase = { timeoutMs: timeoutCase.timeoutMs, elapsedMs: abort.elapsedMs };
  }

  // The predicate discriminates the cause instead of accepting any rejection.
  for (const failure of createNonTimeoutFailures()) {
    expect(
      isTimeoutAbortFailure(failure.error),
      `the timeout predicate must reject the ${failure.label}`,
    ).toBe(false);
  }
});
