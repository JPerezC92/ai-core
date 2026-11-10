// Test data and transport doubles for the LM Studio decision gateway integration
// boundary: the injected gateway options, a text-and-inline-image evidence payload,
// the observed decision envelope keyed to the profile's two question ids, the
// non-2xx and bounded-timeout scenarios, the failures that must never pass as a
// timeout, and a recording `fetch` double for each transport outcome. The timeout
// double records the elapsed time between the call and the abort signal firing, so the
// injected timeout is observable rather than assumed. Every creator returns fresh
// values; each double owns its own request and abort logs.

import { performance } from 'node:perf_hooks';

import {
  LmStudioGatewayBoundaryError,
  type LmStudioDecisionGatewayOptions,
} from '../../infrastructure/lm-studio-decision-gateway.ts';
import type { OddEvidenceImage, OddEvidenceInput } from '../../domain/odd-evidence.ts';

const endpointPath = '/v1/systemone';
const questionIds = ['scope_changed', 'user_only_decision'] as const;
type QuestionId = (typeof questionIds)[number];
type CriterionId = 'present' | 'absent';

export type GatewayOptions = LmStudioDecisionGatewayOptions;

export function createGatewayOptions(
  overrides: { readonly timeoutMs?: number } = {},
): GatewayOptions {
  return {
    endpoint: 'http://127.0.0.1:1234',
    model: 'd1-2b@q8_0',
    timeoutMs: overrides.timeoutMs ?? 500,
  };
}

// The request URL the adapter must use for the injected endpoint.
export function createDecisionRequestUrl(options: GatewayOptions): string {
  return `${options.endpoint}${endpointPath}`;
}

export function createEvidenceImage(): OddEvidenceImage {
  return {
    mimeType: 'image/png',
    base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  };
}

// The only permitted image representation on the wire: a data URL derived from the
// supplied mimeType and base64 payload, never a filesystem path or remote URL.
export function createInlineImageDataUrl(image: OddEvidenceImage): string {
  return `data:${image.mimeType};base64,${image.base64}`;
}

// The request's question as the observed wire shape states it: keyed by its id in the
// record below, each carrying its answer kind, instruction and per-criterion text.
type EvidenceQuestion = OddEvidenceInput['questions'][string];

export function createEvidenceInput(): OddEvidenceInput {
  return {
    questions: Object.fromEntries(
      questionIds.map((id) => [id, createQuestion(id)] as const),
    ),
    text: 'The latest user request repeats the accepted implementation scope.',
    images: [createEvidenceImage()],
  };
}

// Synthetic decision envelope using the observed response fields; scores are not observations.
// The model answers exactly the two questions the profile asks.
export function createDecisionBody() {
  return {
    model: 'd1-2b@q8_0',
    answers: {
      scope_changed: createChoiceAnswer('present'),
      user_only_decision: createChoiceAnswer('absent'),
    },
    usage: { input_tokens: 412, output_tokens: 0 },
  };
}

export type NonSuccessScenario = {
  readonly status: number;
  readonly statusText: string;
  readonly body: string;
};

export function createNonSuccessScenario(): NonSuccessScenario {
  return {
    status: 503,
    statusText: 'Service Unavailable',
    body: '{"error":"model_not_loaded"}',
  };
}

export type TimeoutCase = {
  // The bounded timeout injected into the adapter for this case.
  readonly timeoutMs: number;
  // Guard so an adapter that never aborts fails fast instead of hanging the suite.
  readonly settlementMs: number;
  // The accepted abort window around the injected timeout: the lower bound allows the
  // signal to have been created slightly before the call, the upper bound is the
  // overshoot tolerance. The windows of the two cases do not overlap, so neither an
  // immediate abort nor a single fixed delay can satisfy both.
  readonly minAbortElapsedMs: number;
  readonly maxAbortElapsedMs: number;
};

export type TimeoutScenario = {
  readonly cases: readonly [TimeoutCase, TimeoutCase];
};

// Two distinct, short injected timeouts plus the tolerance constants that derive each
// abort window and the settlement guard's extra allowance. Windows: [20, 100] and
// [140, 220] ms.
const timeoutCaseTimeoutsMs = [40, 160] as const;
const abortSchedulingSlackMs = 20;
const abortOvershootToleranceMs = 60;
const settlementAllowanceMs = 900;

export function createTimeoutScenario(): TimeoutScenario {
  const [firstTimeoutMs, secondTimeoutMs] = timeoutCaseTimeoutsMs;
  return {
    cases: [createTimeoutCase(firstTimeoutMs), createTimeoutCase(secondTimeoutMs)],
  };
}

function createTimeoutCase(timeoutMs: number): TimeoutCase {
  return {
    timeoutMs,
    settlementMs: timeoutMs + abortOvershootToleranceMs + settlementAllowanceMs,
    minAbortElapsedMs: timeoutMs - abortSchedulingSlackMs,
    maxAbortElapsedMs: timeoutMs + abortOvershootToleranceMs,
  };
}

export type NonTimeoutFailure = {
  readonly label: string;
  readonly error: Error;
};

// Failures that must never satisfy the timeout outcome: a generic error carries no
// cause, the `TypeError` is what `fetch` raises for a transport failure, and the
// boundary error reports an HTTP status, which cannot represent a timeout.
export function createNonTimeoutFailures(): ReadonlyArray<NonTimeoutFailure> {
  const scenario = createNonSuccessScenario();
  return [
    { label: 'plain error', error: new Error('the decision request failed') },
    { label: 'transport TypeError', error: new TypeError('fetch failed') },
    {
      label: 'HTTP boundary error',
      error: new LmStudioGatewayBoundaryError(scenario.status, scenario.statusText),
    },
  ];
}

// The names that report the abort/timeout cause themselves: the abort the transport
// double raises, and the native timeout name. The timeout outcome may surface either.
export function createAbortFailureNames(): ReadonlyArray<string> {
  return ['AbortError', 'TimeoutError'];
}

export type RecordedRequest = {
  readonly url: string;
  readonly init: RequestInit;
};

export type RecordingFetch = {
  readonly fetch: typeof globalThis.fetch;
  readonly calls: ReadonlyArray<RecordedRequest>;
};

export type RecordedAbort = {
  // Milliseconds between the recorded fetch call and the abort signal firing.
  readonly elapsedMs: number;
};

export type RecordingTimeoutFetch = {
  readonly fetch: typeof globalThis.fetch;
  readonly calls: ReadonlyArray<RecordedRequest>;
  readonly aborts: ReadonlyArray<RecordedAbort>;
};

export function createSuccessFetchDouble(
  body: unknown = createDecisionBody(),
): RecordingFetch {
  return createRecordingFetch(async () => createJsonResponse(body));
}

export function createNonSuccessFetchDouble(
  scenario: NonSuccessScenario = createNonSuccessScenario(),
): RecordingFetch {
  return createRecordingFetch(async () =>
    new Response(scenario.body, {
      status: scenario.status,
      statusText: scenario.statusText,
      headers: { 'content-type': 'application/json' },
    })
  );
}

// Transport double for the bounded-timeout case: the request settles only when the
// adapter aborts the supplied signal, so an adapter that applies no timeout is
// reported by the settlement guard instead of leaving the test pending. Every abort is
// recorded with the elapsed time between the call and the abort, so the caller can
// assert the injected timeout was honored rather than that some rejection occurred.
export function createTimeoutFetchDouble(
  timeoutCase: TimeoutCase,
): RecordingTimeoutFetch {
  const aborts: RecordedAbort[] = [];
  const transport = createRecordingFetch((_url, init) =>
    settleOnAbort(init, timeoutCase, aborts)
  );
  return {
    fetch: transport.fetch,
    get calls() {
      return transport.calls;
    },
    get aborts() {
      return aborts.slice();
    },
  };
}

function settleOnAbort(
  init: RequestInit,
  timeoutCase: TimeoutCase,
  aborts: RecordedAbort[],
): Promise<Response> {
  const dispatchedAt = performance.now();
  return new Promise<Response>((_resolve, reject) => {
    const signal = init.signal;
    if (!(signal instanceof AbortSignal)) {
      reject(createMissingAbortSignalError());
      return;
    }
    let settled = false;
    const settle = (error: Error) => {
      if (settled) return;
      settled = true;
      clearTimeout(guard);
      reject(error);
    };
    const recordAbort = () => {
      aborts.push({ elapsedMs: performance.now() - dispatchedAt });
      settle(createTransportAbortError());
    };
    const guard = setTimeout(
      () => settle(createUnsettledTimeoutError()),
      timeoutCase.settlementMs,
    );
    signal.addEventListener('abort', recordAbort, { once: true });
    if (signal.aborted) recordAbort();
  });
}

function createRecordingFetch(
  respond: (url: string, init: RequestInit) => Promise<Response>,
): RecordingFetch {
  const calls: RecordedRequest[] = [];
  const fetchImpl = async (
    input: string | URL | Request,
    init?: RequestInit,
  ): Promise<Response> => {
    const url = readRequestUrl(input);
    const request = init ?? {};
    calls.push({ url, init: request });
    return respond(url, request);
  };
  return {
    fetch: fetchImpl as typeof globalThis.fetch,
    get calls() {
      return calls.slice();
    },
  };
}

function readRequestUrl(input: string | URL | Request): string {
  if (typeof input === 'string') return input;
  if (input instanceof URL) return input.href;
  return input.url;
}

function createJsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'content-type': 'application/json' },
  });
}

function createTransportAbortError(): Error {
  const error = new Error('The decision request was aborted at the transport');
  error.name = 'AbortError';
  return error;
}

function createMissingAbortSignalError(): Error {
  const error = new Error('The decision request supplied no abort signal');
  error.name = 'MissingAbortSignalError';
  return error;
}

function createUnsettledTimeoutError(): Error {
  const error = new Error('The decision request was never aborted within the injected timeout');
  error.name = 'TimeoutNotObservedError';
  return error;
}

function createQuestion(id: QuestionId): EvidenceQuestion {
  return {
    type: 'choice',
    instructions: `Decide the ${id} evidence state from the supplied message.`,
    criteria: {
      present: 'The supplied evidence establishes the condition.',
      absent: 'The supplied evidence establishes the condition is absent.',
    },
  };
}

function createChoiceAnswer(choice: CriterionId) {
  const probabilities: Record<CriterionId, number> = {
    present: 0.1,
    absent: 0.1,
  };
  probabilities[choice] = 0.8;
  return { type: 'choice', choice, probabilities, confidence: 0.8 };
}
