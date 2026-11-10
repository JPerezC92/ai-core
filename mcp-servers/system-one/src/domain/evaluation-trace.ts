// Pure domain: the record of one evidence evaluation and the ports that receive it. A
// trace line records the decision exchange itself — the request body the decision
// endpoint received and the parsed response body it returned, or the transport failure
// that replaced the response — so an operator can read what System 1 was asked and what
// it answered. Supplied state and questions are recorded verbatim and never truncated;
// each image data URL is replaced by a descriptor (mime type, byte count, sha256 and
// stored path) produced by the trace image store, so the line identifies the exact bytes
// without carrying them. No IO, no infrastructure imports, no throws.
//
// The parsed response is deliberately `unknown`: it is diagnostic capture data that must
// stay exactly as received, never a remapped domain model, and no domain behavior reads
// it. The request's questions are the domain's own question record.

import type {
  OddEvidenceImage,
  OddEvidenceInput,
  OddEvidenceRejectionCode,
} from './odd-evidence.ts';

// Version 4 replaces the metadata-only projection with the decision exchange: the full
// request body, the full parsed response body (or the error that replaced it), and the
// content-addressed image descriptors that stand in for the wire data URLs.
export const EVALUATION_TRACE_SCHEMA_VERSION = 4;

// The two lifecycle states this record distinguishes: the decision endpoint answered, or
// it did not. `gateway_error` is the trace's own code for a boundary exception — a thrown
// transport failure is not a business rejection, so it never borrows a rejection code.
export type EvaluationTraceOutcomeCode = OddEvidenceRejectionCode | 'gateway_error';

export type EvaluationTraceOutcome =
  | { readonly status: 'evaluated' }
  | { readonly status: 'unavailable'; readonly code: EvaluationTraceOutcomeCode };

// Handling is recorded separately from the decision exchange. This slice cannot observe
// an S1 footer, tool actions or an independent evaluator, so those three fields stay
// `not_observed`. Disposition follows the outcome only: an unavailable evaluation is
// recorded as `unavailable`; an evaluated one is `unknown` because applied/overridden
// cannot be established here. `applied` and `overridden` are not representable.
export type EvaluationTraceHandlingDisposition = 'unavailable' | 'unknown';

export type EvaluationTraceObservation = 'not_observed';

export type EvaluationTraceHandling = {
  readonly disposition: EvaluationTraceHandlingDisposition;
  readonly reportedFooter: EvaluationTraceObservation;
  readonly observedActions: EvaluationTraceObservation;
  readonly assessment: EvaluationTraceObservation;
};

export function handlingForOutcome(
  outcome: EvaluationTraceOutcome,
): EvaluationTraceHandling {
  return {
    disposition: outcome.status === 'unavailable' ? 'unavailable' : 'unknown',
    reportedFooter: 'not_observed',
    observedActions: 'not_observed',
    assessment: 'not_observed',
  };
}

// One image as the recorded request identifies it. The bytes are content addressed, so
// equal payloads share one stored file; `path` is null when the store could not write
// them, and the descriptor still identifies the bytes by digest and byte count.
export type EvaluationTraceImageDescriptor = {
  readonly mimeType: string;
  readonly bytes: number;
  readonly sha256: string;
  readonly path: string | null;
};

// The outbound decision request: the model the endpoint was addressed with, the supplied
// state verbatim, the exact questions object the gateway forwarded, and one descriptor
// per image that stood in for the wire data URL of the same bytes.
export type EvaluationTraceRequest = {
  readonly model: string;
  readonly state: string;
  readonly questions: OddEvidenceInput['questions'];
  readonly images: ReadonlyArray<EvaluationTraceImageDescriptor>;
};

// A decision attempt that produced no parsed response. `code` is the failure's stable
// name (the gateway boundary error, a timeout, or `unknown_error`), `status` is the HTTP
// status when the failure carried one, and `detail` is the bounded transport message.
export type EvaluationTraceError = {
  readonly status?: number;
  readonly code: string;
  readonly detail: string;
};

// Exactly one side follows the request: the parsed response body, unmodified, or the
// failure that replaced it. An absent response is represented by the error branch, so a
// stored line never carries both fields.
export type EvaluationTraceResult =
  | { readonly response: unknown }
  | { readonly error: EvaluationTraceError };

// The exchange record itself: the request and exactly one of the response or the error.
// Written as an explicit union so callers narrow it by `in`.
export type DecisionExchange =
  | { readonly request: EvaluationTraceRequest; readonly response: unknown }
  | { readonly request: EvaluationTraceRequest; readonly error: EvaluationTraceError };

// Everything a trace line carries besides the exchange. `evaluationId` and `at` locate
// one evaluation; `sessionId` correlates it with the invoking session the delivery edge
// read from the call metadata; `model` is the model the evaluation expected and validated
// against (the request record carries the model the gateway addressed); a profile that
// failed validation has no validated identity, so its identifier and version are null
// rather than copied. `handling` is the S6 disposition record, never inferred from an
// S1 footer.
export type EvaluationTraceContext = {
  readonly evaluationId: string;
  readonly at: string;
  readonly sessionId: string | null;
  readonly profileId: string | null;
  readonly profileVersion: number | null;
  readonly model: string;
  readonly outcome: EvaluationTraceOutcome;
  readonly handling: EvaluationTraceHandling;
  readonly elapsedMs: number;
};

// The exchange side of an entry. The input and the branded entry are explicit unions
// rather than an intersection with a union, so the response/error distinction narrows
// everywhere it is consumed.
type EvaluationTraceExchangeContext = EvaluationTraceContext & {
  readonly request: EvaluationTraceRequest;
};

export type EvaluationTraceEntryInput =
  | (EvaluationTraceExchangeContext & { readonly response: unknown })
  | (EvaluationTraceExchangeContext & { readonly error: EvaluationTraceError });

// Module-private brand: an adapter or caller cannot construct an entry-shaped object that
// carries an extra content field; only `createEvaluationTraceEntry` produces this type. The
// marker is a real symbol so the factory can build a branded value directly instead of
// asserting one into the type; `unique symbol` keeps it nominal and this module never
// exports it.
const evaluationTraceEntryBrand: unique symbol = Symbol('evaluationTraceEntryBrand');

type EvaluationTraceEntryBrand = {
  readonly schemaVersion: typeof EVALUATION_TRACE_SCHEMA_VERSION;
  readonly [evaluationTraceEntryBrand]: true;
};

export type EvaluationTraceEntry =
  | (EvaluationTraceExchangeContext & { readonly response: unknown } & EvaluationTraceEntryBrand)
  | (EvaluationTraceExchangeContext & { readonly error: EvaluationTraceError } &
      EvaluationTraceEntryBrand);

// One explicit copy, so a caller passing extra runtime properties cannot smuggle them
// into the record: the entry contains exactly the declared fields, each image descriptor
// is rebuilt field by field, and the error keeps only its declared fields. The request's
// questions object is kept by reference because it is the exact object the gateway
// forwarded — copying it would weaken that claim without improving the stored line.
export function createEvaluationTraceEntry(
  input: EvaluationTraceEntryInput,
): EvaluationTraceEntry {
  const context: EvaluationTraceContext & {
    readonly schemaVersion: typeof EVALUATION_TRACE_SCHEMA_VERSION;
    readonly request: EvaluationTraceRequest;
  } = {
    schemaVersion: EVALUATION_TRACE_SCHEMA_VERSION,
    evaluationId: input.evaluationId,
    at: input.at,
    sessionId: input.sessionId,
    profileId: input.profileId,
    profileVersion: input.profileVersion,
    model: input.model,
    request: toRecordedRequest(input.request),
    outcome: input.outcome,
    handling: toRecordedHandling(input.handling),
    elapsedMs: input.elapsedMs,
  };
  const entry: EvaluationTraceEntry = 'response' in input
    ? { ...context, response: input.response, [evaluationTraceEntryBrand]: true }
    : { ...context, error: toRecordedError(input.error), [evaluationTraceEntryBrand]: true };
  // The brand records provenance, not content: keeping it out of the entry's enumerable
  // own properties leaves the record's observable shape exactly its declared fields.
  Object.defineProperty(entry, evaluationTraceEntryBrand, { enumerable: false });
  return entry;
}

function toRecordedRequest(request: EvaluationTraceRequest): EvaluationTraceRequest {
  return {
    model: request.model,
    state: request.state,
    questions: request.questions,
    images: request.images.map((image) => ({
      mimeType: image.mimeType,
      bytes: image.bytes,
      sha256: image.sha256,
      path: image.path,
    })),
  };
}

function toRecordedError(error: EvaluationTraceError): EvaluationTraceError {
  return error.status === undefined
    ? { code: error.code, detail: error.detail }
    : { status: error.status, code: error.code, detail: error.detail };
}

function toRecordedHandling(handling: EvaluationTraceHandling): EvaluationTraceHandling {
  return {
    disposition: handling.disposition,
    reportedFooter: handling.reportedFooter,
    observedActions: handling.observedActions,
    assessment: handling.assessment,
  };
}

// The storage capability the application operation records into. The method returns a
// promise so an adapter may await its own IO; the domain knows neither the medium nor the
// serialization.
export type EvaluationTrace = {
  record(entry: EvaluationTraceEntry): Promise<void>;
};

// The capability that turns one supplied image into the descriptor the recorded request
// carries. An implementation persists the decoded bytes under a content-addressed name
// and reports the path it used; storage that is unavailable must still return the
// descriptor with `path: null` rather than throw, because tracing may never fail the
// evaluation it describes.
export type EvaluationTraceImageStore = {
  store(image: OddEvidenceImage): Promise<EvaluationTraceImageDescriptor>;
};
