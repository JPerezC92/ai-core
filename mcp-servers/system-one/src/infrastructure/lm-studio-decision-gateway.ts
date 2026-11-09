// Infrastructure adapter for the injected LM Studio system-1 decision endpoint: one
// HTTP POST per call, images forwarded only as inline data URLs derived from the
// supplied mimeType and base64 payloads, a bounded timeout, no retries, and no logging
// of text, images, prompts or headers. The endpoint, model and timeout are injected;
// this module hardcodes no LM Studio URL and applies no domain policy: the response
// envelope is returned as `unknown` for the application layer to validate.

import type { OddEvidenceGateway, OddEvidenceInput } from '../domain/odd-evidence.ts';

const decisionPath = '/v1/systemone';

export type LmStudioDecisionGatewayOptions = {
  readonly endpoint: string;
  readonly model: string;
  readonly timeoutMs: number;
};

// Boundary exception, never a domain result: the endpoint answered outside 2xx.
export class LmStudioGatewayBoundaryError extends Error {
  readonly status: number;

  constructor(status: number, statusText: string) {
    super(`LM Studio decision request failed with HTTP ${status} ${statusText}`.trim());
    this.name = 'LmStudioGatewayBoundaryError';
    this.status = status;
  }
}

// Boundary exception, never a domain result: a 2xx response whose body is not JSON.
export class LmStudioGatewayResponseError extends Error {
  constructor() {
    super('LM Studio decision response body was not valid JSON');
    this.name = 'LmStudioGatewayResponseError';
  }
}

// The request the endpoint receives: the domain questions unchanged and, only when at
// least one image is supplied, its inline data URLs. No field carries a path or URL.
type DecisionRequestBody = {
  readonly model: string;
  readonly state: string;
  readonly questions: OddEvidenceInput['questions'];
  readonly images?: ReadonlyArray<string>;
};

function createDecisionUrl(endpoint: string): string {
  return `${endpoint.replace(/\/+$/, '')}${decisionPath}`;
}

// The only permitted image representation on the wire: a data URL built from the
// supplied mimeType and base64 payload, never a filesystem path or remote URL.
function toInlineImageDataUrl(image: OddEvidenceInput['images'][number]): string {
  return `data:${image.mimeType};base64,${image.base64}`;
}

function createDecisionRequestBody(
  model: string,
  input: OddEvidenceInput,
): DecisionRequestBody {
  const body = { model, state: input.text, questions: input.questions };
  return input.images.length === 0
    ? body
    : { ...body, images: input.images.map(toInlineImageDataUrl) };
}

// The configured timeout aborts the request, so an aborted call surfaces a timeout that
// retains the transport's abort cause. The HTTP boundary error reports a status and
// must never stand in for a timeout.
function createTimeoutError(cause: unknown): Error {
  const timeoutError = new Error(
    'The LM Studio decision request exceeded its configured timeout',
    { cause },
  );
  timeoutError.name = 'TimeoutError';
  return timeoutError;
}

export class LmStudioDecisionGateway implements OddEvidenceGateway {
  readonly #requestUrl: string;
  readonly #model: string;
  readonly #timeoutMs: number;

  constructor(options: LmStudioDecisionGatewayOptions) {
    this.#requestUrl = createDecisionUrl(options.endpoint);
    this.#model = options.model;
    this.#timeoutMs = options.timeoutMs;
  }

  async decide(input: OddEvidenceInput): Promise<unknown> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.#timeoutMs);
    try {
      const response = await this.#postDecisionRequest(input, controller.signal);
      if (!response.ok) {
        throw new LmStudioGatewayBoundaryError(response.status, response.statusText);
      }
      try {
        return (await response.json()) as unknown;
      } catch (error) {
        throw controller.signal.aborted
          ? createTimeoutError(error)
          : new LmStudioGatewayResponseError();
      }
    } finally {
      clearTimeout(timer);
    }
  }

  // Exactly one POST, never retried; the request carries the abort signal so the
  // configured timeout bounds the transport call itself.
  async #postDecisionRequest(
    input: OddEvidenceInput,
    signal: AbortSignal,
  ): Promise<Response> {
    try {
      return await fetch(this.#requestUrl, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(createDecisionRequestBody(this.#model, input)),
        signal,
      });
    } catch (error) {
      throw signal.aborted ? createTimeoutError(error) : error;
    }
  }
}
