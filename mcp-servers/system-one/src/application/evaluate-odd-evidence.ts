// Application operation: evaluate supplied text and images against the versioned
// evidence question profile before anything is delivered. It depends on injected
// ports only; no serialization, no IO, and no throws for expected business failures.
//
// Tracing is optional. When the host injects the trace and image-store ports, exactly
// one entry is recorded for every evaluation that reaches the decision gateway: the
// request body the gateway sent — `state` and `questions` are the exact values it
// received, and each image data URL is replaced by a content-addressed descriptor of the
// same bytes — and the parsed response body it returned, or the transport failure that
// replaced the response. The gateway port is unchanged (`decide()` still returns the
// parsed body): the operation forms the exchange around the call, which keeps the domain
// free of IO and needs no gateway change. An evaluation rejected before the gateway call
// sent nothing, so it records no exchange.

import { validateDecisionResponse } from '../domain/decision-response.ts';
import type {
  DecisionChoice,
  ValidatedDecisionAnswer,
  ValidatedEvidenceAnswers,
} from '../domain/decision-response.ts';
import { createEvaluationTraceEntry } from '../domain/evaluation-trace.ts';
import type {
  EvaluationTrace,
  EvaluationTraceContext,
  EvaluationTraceEntryInput,
  EvaluationTraceError,
  EvaluationTraceImageStore,
  EvaluationTraceOutcome,
  EvaluationTraceRequest,
  EvaluationTraceResult,
} from '../domain/evaluation-trace.ts';
import { validateOddEvidenceInput } from '../domain/odd-evidence.ts';
import type {
  OddEvidenceGateway,
  OddEvidenceImage,
  OddEvidenceInput,
  OddEvidenceRejectionCode,
  QuestionProfileSource,
} from '../domain/odd-evidence.ts';
import { derivedQuestionId } from '../domain/question-profile.ts';

export type OddEvidenceEvaluation =
  | {
      readonly ok: true;
      readonly profileId: string;
      readonly profileVersion: number;
      readonly answers: ValidatedEvidenceAnswers;
    }
  | {
      readonly ok: false;
      readonly code: OddEvidenceRejectionCode;
      readonly reason: string;
    };

export type EvaluationTracing = {
  readonly evaluationTrace: EvaluationTrace;
  readonly imageStore: EvaluationTraceImageStore;
  // The model the host configured on the decision gateway. It is what the wire request
  // body carries; the operation cannot read it from a gateway that only returns the
  // parsed response, so the composition that owns both values supplies it. In the
  // composed server it is the same configured model the gateway was built with.
  readonly decisionModel: string;
};

export type EvaluateOddEvidenceDependencies = {
  readonly decisionGateway: OddEvidenceGateway;
  readonly questionProfileSource: QuestionProfileSource;
  // Optional operational trace sink and the image store its request record needs. When
  // absent, no evaluation record is produced.
  readonly tracing?: EvaluationTracing;
};

// One evaluation's trace correlation, fixed when the evaluation starts. The identifier
// and timestamp are correlation metadata, never supplied evidence. The decision model is
// carried here from the injected configuration because the request record needs it, and
// the operation cannot read it back from a gateway that only returns the parsed body.
type ActiveTracing = {
  readonly trace: EvaluationTrace;
  readonly imageStore: EvaluationTraceImageStore;
  readonly decisionModel: string;
  readonly evaluationId: string;
  readonly at: string;
};

type TraceIdentity = {
  readonly profileId: string;
  readonly profileVersion: number;
  readonly model: string;
  readonly sessionId: string | null;
};

// The transport message is the only failure detail this operation can read from an
// unknown thrown value; the bound keeps a pathological message from dominating the line.
const MAX_TRACE_ERROR_DETAIL_LENGTH = 1_000;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function readErrorText(value: unknown, key: 'name' | 'message'): string | undefined {
  if (!isRecord(value)) return undefined;
  const text = value[key];
  return typeof text === 'string' && text.length > 0 ? text : undefined;
}

// A thrown boundary exception is not a domain rejection (C5), so it is recorded as the
// trace's own `gateway_error` outcome and its stable name, HTTP status when present and
// bounded transport message become the error record. The exception itself is rethrown.
function toTraceError(error: unknown): EvaluationTraceError {
  const code = readErrorText(error, 'name') ?? 'unknown_error';
  const message = readErrorText(error, 'message') ??
    'The decision gateway failed without a message';
  const detail = message.length > MAX_TRACE_ERROR_DETAIL_LENGTH
    ? message.slice(0, MAX_TRACE_ERROR_DETAIL_LENGTH)
    : message;
  const status = isRecord(error) ? error['status'] : undefined;
  return typeof status === 'number' && Number.isFinite(status)
    ? { status, code, detail }
    : { code, detail };
}

// The answer for the one question the model is not asked. Whether an image is attached is
// envelope metadata this server already holds, so the evaluation computes the answer from
// the supplied image count rather than asking a model to judge its own attachment: one or
// more images is `present` with certainty, none is `absent` with certainty. Nothing here
// reads model output, so a model answer can never change it.
function deriveVisualEvidenceAnswer(
  images: ReadonlyArray<OddEvidenceImage>,
): ValidatedDecisionAnswer {
  const attached = images.length > 0;
  const probabilities: Record<DecisionChoice, number> = attached
    ? { present: 1, absent: 0 }
    : { present: 0, absent: 1 };
  return { type: 'choice', choice: attached ? 'present' : 'absent', probabilities };
}

export class EvaluateOddEvidence {
  #decisionGateway: OddEvidenceGateway;
  #questionProfileSource: QuestionProfileSource;
  #tracing: EvaluationTracing | undefined;

  constructor(dependencies: EvaluateOddEvidenceDependencies) {
    this.#decisionGateway = dependencies.decisionGateway;
    this.#questionProfileSource = dependencies.questionProfileSource;
    this.#tracing = dependencies.tracing;
  }

  async execute(
    text: string,
    images: ReadonlyArray<OddEvidenceImage>,
    expectedModel: string,
    // The invoking session the delivery edge read from the call metadata, when the host
    // supplied one. It is correlation metadata, never supplied evidence.
    sessionId?: string,
  ): Promise<OddEvidenceEvaluation> {
    const trace = this.#startTracing();
    const traceSessionId = sessionId ?? null;

    // The port already mapped the outside document to domain data, so this is a typed
    // result rather than a document to validate: a rejection carries the validator's reason
    // unchanged, which is the same bounded code and text a caller saw before.
    const loadedProfile = await this.#questionProfileSource.load();
    if (!loadedProfile.ok) {
      return { ok: false, code: 'invalid_profile', reason: loadedProfile.reason };
    }
    const profile = loadedProfile.profile;

    // The profile's questions become the record the evaluation asks, keyed by their own
    // ids; each keeps the answer kind the profile declares beside its instruction and
    // criteria, so the keyed record is the whole question set rather than a list to index.
    const questions = Object.fromEntries(
      Object.entries(profile.questions).map(([id, question]) => [
        id,
        {
          type: question.type,
          instructions: question.instructions,
          criteria: { ...question.criteria },
        },
      ] as const),
    );

    const validatedInput = validateOddEvidenceInput(text, images, questions);
    if (!validatedInput.ok) {
      return { ok: false, code: validatedInput.code, reason: validatedInput.reason };
    }
    const identity: TraceIdentity = {
      profileId: profile.profileId,
      profileVersion: profile.version,
      model: expectedModel,
      sessionId: traceSessionId,
    };

    // Build the recorded request before the call: the request carries the model the
    // gateway was configured with and the image descriptors that identify the exact bytes
    // it is about to forward as data URLs. Storage failures are reported as `path: null`
    // by the store port and never abort the evaluation.
    const request = trace === undefined
      ? undefined
      : await this.#createTraceRequest(
          trace.decisionModel,
          validatedInput.input,
          trace.imageStore,
        );

    // Elapsed time measures the decision gateway call only; with no trace sink there is
    // nothing to measure.
    const gatewayStartedAt = trace === undefined ? undefined : globalThis.performance.now();
    let rawResponse: unknown;
    try {
      rawResponse = await this.#decisionGateway.decide(validatedInput.input);
    } catch (error) {
      await this.#record(
        trace,
        request,
        identity,
        { error: toTraceError(error) },
        { status: 'unavailable', code: 'gateway_error' },
        this.#elapsed(gatewayStartedAt),
      );
      // The boundary exception keeps its own classification and propagation (C5).
      throw error;
    }
    const elapsedMs = this.#elapsed(gatewayStartedAt);

    const validatedResponse = validateDecisionResponse(rawResponse, expectedModel);
    if (!validatedResponse.ok) {
      await this.#record(
        trace,
        request,
        identity,
        { response: rawResponse },
        { status: 'unavailable', code: validatedResponse.code },
        elapsedMs,
      );
      return { ok: false, code: validatedResponse.code, reason: validatedResponse.reason };
    }

    await this.#record(
      trace,
      request,
      identity,
      { response: rawResponse },
      { status: 'evaluated' },
      elapsedMs,
    );

    // Only a validated model answer reaches here, so the derived answer is appended to an
    // answer record that already passed the contract; the failure paths above return their
    // bounded code and no answers at all, so a failed call cannot fabricate this one.
    const answers: ValidatedEvidenceAnswers = {
      ...validatedResponse.response.answers,
      [derivedQuestionId]: deriveVisualEvidenceAnswer(validatedInput.input.images),
    };

    return {
      ok: true,
      profileId: profile.profileId,
      profileVersion: profile.version,
      answers,
    };
  }

  #startTracing(): ActiveTracing | undefined {
    const tracing = this.#tracing;
    if (tracing === undefined) return undefined;
    return {
      trace: tracing.evaluationTrace,
      imageStore: tracing.imageStore,
      decisionModel: tracing.decisionModel,
      evaluationId: globalThis.crypto.randomUUID(),
      at: new Date().toISOString(),
    };
  }

  // One request record: the model the endpoint was addressed with, the supplied state and
  // questions exactly as the gateway receives them, and one stored descriptor per image.
  async #createTraceRequest(
    model: string,
    input: OddEvidenceInput,
    imageStore: EvaluationTraceImageStore,
  ): Promise<EvaluationTraceRequest> {
    const images = await Promise.all(input.images.map((image) => imageStore.store(image)));
    return {
      model,
      state: input.text,
      questions: input.questions,
      images,
    };
  }

  #elapsed(startedAt: number | undefined): number {
    return startedAt === undefined ? 0 : globalThis.performance.now() - startedAt;
  }

  // One trace write per evaluation outcome that reached the gateway. With no injected
  // ports the call is a no-op; when present, the adapter owns the write and its own IO
  // failure handling.
  async #record(
    trace: ActiveTracing | undefined,
    request: EvaluationTraceRequest | undefined,
    identity: TraceIdentity,
    result: EvaluationTraceResult,
    outcome: EvaluationTraceOutcome,
    elapsedMs: number,
  ): Promise<void> {
    if (trace === undefined || request === undefined) return;
    const context: EvaluationTraceContext = {
      evaluationId: trace.evaluationId,
      at: trace.at,
      sessionId: identity.sessionId,
      profileId: identity.profileId,
      profileVersion: identity.profileVersion,
      model: identity.model,
      outcome,
      elapsedMs,
    };
    const input: EvaluationTraceEntryInput = 'response' in result
      ? { ...context, request, response: result.response }
      : { ...context, request, error: result.error };
    await trace.trace.record(createEvaluationTraceEntry(input));
  }
}
