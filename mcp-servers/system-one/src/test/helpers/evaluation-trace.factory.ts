// Test data and doubles for the evaluation trace ports: exchange-bearing entry fixtures
// built through the domain factory (a successful evaluation and a failed one), the
// request, response, error and image-descriptor records they carry, a recording trace
// double that keeps every entry, and an image-store double that digests the supplied
// bytes without touching the filesystem. Every creator returns fresh values; no
// module-level mutable state is shared.

import { createHash, randomUUID } from 'node:crypto';

import type {
  DecisionExchange,
  EvaluationTrace,
  EvaluationTraceContext,
  EvaluationTraceEntry,
  EvaluationTraceError,
  EvaluationTraceHandling,
  EvaluationTraceImageDescriptor,
  EvaluationTraceImageStore,
  EvaluationTraceOutcome,
  EvaluationTraceRequest,
} from '../../domain/evaluation-trace.ts';
import {
  createEvaluationTraceEntry as createDomainEvaluationTraceEntry,
  handlingForOutcome,
} from '../../domain/evaluation-trace.ts';
import type { OddEvidenceImage } from '../../domain/odd-evidence.ts';
import {
  createDecisionResponse,
  createEvidence,
  createEvidenceImage,
  createOddEvidenceProfile,
} from './odd-evidence.factory.ts';

const defaultProfileId = 'odd-evidence-v1';
const defaultProfileVersion = 1;
const defaultModel = 'd1-2b@q8_0';
const defaultElapsedMs = 12;
const defaultAt = '2026-11-08T00:00:00.000Z';

// A fresh session identifier shaped like the one the delivery edge reads from the call
// metadata, so a fixture never shares correlation with another.
export function createSessionId(): string {
  return `ses_${randomUUID()}`;
}

// The questions record exactly as the operation derives it from the fixture profile:
// keyed by question id, each with its answer kind, instruction and criteria.
export function createEvaluationTraceQuestions(): EvaluationTraceRequest['questions'] {
  const profile = createOddEvidenceProfile();
  const entries = Object.entries(profile.questions).map(([id, question]) => [
    id,
    {
      type: 'choice',
      instructions: question.instructions,
      criteria: { ...question.criteria },
    },
  ] as const);
  return Object.fromEntries(entries);
}

// A descriptor for one supplied image, computed from its decoded bytes so a fixture and
// the bytes it names agree; the path is a nominal stored location, not a written file.
export function createEvaluationTraceImageDescriptor(
  image: OddEvidenceImage = createEvidenceImage(),
  overrides: Partial<EvaluationTraceImageDescriptor> = {},
): EvaluationTraceImageDescriptor {
  const bytes = Buffer.from(image.base64, 'base64');
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  return {
    mimeType: overrides.mimeType ?? image.mimeType,
    bytes: overrides.bytes ?? bytes.length,
    sha256: overrides.sha256 ?? sha256,
    path: overrides.path === undefined
      ? `output/system1/images/${sha256}.${image.mimeType.split('/')[1] ?? 'bin'}`
      : overrides.path,
  };
}

// An image-store double that performs the same identity computation as the real adapter
// without any filesystem access; the descriptor overrides let a test fix the path.
export function createTraceImageStore(
  overrides: Partial<EvaluationTraceImageDescriptor> = {},
): EvaluationTraceImageStore {
  return {
    store: async (image: OddEvidenceImage) =>
      createEvaluationTraceImageDescriptor(image, overrides),
  };
}

export function createEvaluationTraceRequest(
  overrides: Partial<EvaluationTraceRequest> = {},
): EvaluationTraceRequest {
  return {
    model: overrides.model ?? defaultModel,
    state: overrides.state ?? createEvidence().text,
    questions: overrides.questions ?? createEvaluationTraceQuestions(),
    images: overrides.images ?? [createEvaluationTraceImageDescriptor()],
  };
}

export function createEvaluationTraceError(
  overrides: Partial<EvaluationTraceError> = {},
): EvaluationTraceError {
  return {
    code: overrides.code ?? 'LmStudioGatewayBoundaryError',
    detail: overrides.detail ??
      'LM Studio decision request failed with HTTP 500 Internal Server Error',
    ...(overrides.status === undefined ? {} : { status: overrides.status }),
  };
}

export function createEvaluationTraceHandling(
  overrides: Partial<EvaluationTraceHandling> = {},
): EvaluationTraceHandling {
  return {
    disposition: overrides.disposition ?? 'unknown',
    reportedFooter: overrides.reportedFooter ?? 'not_observed',
    observedActions: overrides.observedActions ?? 'not_observed',
    assessment: overrides.assessment ?? 'not_observed',
  };
}

// The successful exchange: the request the gateway received and the parsed body it
// returned. A response override preserves an explicit null rather than replacing it.
export function createEvaluationTraceExchange(
  overrides: {
    readonly request?: EvaluationTraceRequest;
    readonly response?: unknown;
  } = {},
): DecisionExchange {
  return {
    request: overrides.request ?? createEvaluationTraceRequest(),
    response: overrides.response === undefined ? createDecisionResponse() : overrides.response,
  };
}

// The failed exchange: the request was sent, and no response replaced it.
export function createFailedEvaluationTraceExchange(
  overrides: {
    readonly request?: EvaluationTraceRequest;
    readonly error?: EvaluationTraceError;
  } = {},
): DecisionExchange {
  return {
    request: overrides.request ?? createEvaluationTraceRequest(),
    error: overrides.error ?? createEvaluationTraceError(),
  };
}

export type EvaluationTraceEntryOverrides = Partial<EvaluationTraceContext> & {
  readonly exchange?: DecisionExchange;
};

export function createEvaluationTraceEntry(
  overrides: EvaluationTraceEntryOverrides = {},
): EvaluationTraceEntry {
  const exchange = overrides.exchange ?? createEvaluationTraceExchange();
  return buildEvaluationTraceEntry(exchange, defaultOutcomeFor(exchange), overrides);
}

export function createFailedEvaluationTraceEntry(
  overrides: EvaluationTraceEntryOverrides = {},
): EvaluationTraceEntry {
  const exchange = overrides.exchange ?? createFailedEvaluationTraceExchange();
  return buildEvaluationTraceEntry(exchange, defaultOutcomeFor(exchange), overrides);
}

// The outcome follows the exchange: a recorded response means the endpoint answered; a
// recorded error means no response replaced it.
function defaultOutcomeFor(exchange: DecisionExchange): EvaluationTraceOutcome {
  return 'response' in exchange
    ? { status: 'evaluated' }
    : { status: 'unavailable', code: 'gateway_error' };
}

// Explicit per-field defaults, so an override of null (no validated profile identity, no
// session correlation) or zero (no images) is preserved rather than treated as absent.
function buildEvaluationTraceEntry(
  exchange: DecisionExchange,
  defaultOutcome: EvaluationTraceOutcome,
  overrides: EvaluationTraceEntryOverrides,
): EvaluationTraceEntry {
  const context: EvaluationTraceContext = {
    evaluationId: overrides.evaluationId ?? randomUUID(),
    at: overrides.at ?? defaultAt,
    sessionId: overrides.sessionId === undefined ? createSessionId() : overrides.sessionId,
    profileId: overrides.profileId === undefined ? defaultProfileId : overrides.profileId,
    profileVersion: overrides.profileVersion === undefined
      ? defaultProfileVersion
      : overrides.profileVersion,
    model: overrides.model ?? defaultModel,
    outcome: overrides.outcome ?? defaultOutcome,
    handling: toRecordedHandling(
      overrides.handling ?? handlingForOutcome(overrides.outcome ?? defaultOutcome),
    ),
    elapsedMs: overrides.elapsedMs ?? defaultElapsedMs,
  };
  return 'response' in exchange
    ? createDomainEvaluationTraceEntry({
        ...context,
        request: exchange.request,
        response: exchange.response,
      })
    : createDomainEvaluationTraceEntry({
        ...context,
        request: exchange.request,
        error: exchange.error,
      });
}

function toRecordedHandling(handling: EvaluationTraceHandling): EvaluationTraceHandling {
  return {
    disposition: handling.disposition,
    reportedFooter: handling.reportedFooter,
    observedActions: handling.observedActions,
    assessment: handling.assessment,
  };
}

// The recording double keeps every entry it receives; the `entries` getter returns a
// snapshot copy, so a test can assert exactly what one evaluation recorded.
export type RecordingEvaluationTrace = EvaluationTrace & {
  readonly entries: ReadonlyArray<EvaluationTraceEntry>;
};

export function createEvaluationTraceRecorder(): RecordingEvaluationTrace {
  const entries: EvaluationTraceEntry[] = [];
  return {
    record: async (entry: EvaluationTraceEntry) => {
      entries.push(entry);
    },
    get entries() {
      return entries.slice();
    },
  };
}
