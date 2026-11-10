// Domain contract of the advisory capability: the evidence one evaluation is given, the
// bounded outcome union, and the capability port the delivery edge depends on. This module
// is framework-free. It declares no transport shape, names no tool, performs no IO and
// throws nothing: the adapter that implements the port owns the tool name, the wire
// arguments and the mapping from the external answer to the outcome below (C2, C4).

// One inline image as the domain states it: the media type and the base64 payload, never a
// path or a remote URL (S2).
export type OddEvidenceImage = {
  readonly mimeType: string;
  readonly base64: string;
};

// Everything one evaluation is given: the captured text, its inline images and, only when
// the caller states one, the model identity it expects the evaluation to report. This is
// the closed input contract; a caller cannot add a transport field to it.
export type OddEvidenceInput = {
  readonly text: string;
  readonly images: ReadonlyArray<OddEvidenceImage>;
  readonly expectedModel?: string;
};

// The answer vocabulary stays owned here, so the adapter validates the external record
// against it instead of restating the choices.
export type OddEvidenceAnswer = {
  readonly type: 'choice';
  readonly choice: string;
  readonly probabilities: Readonly<Record<string, number>>;
  readonly confidence?: number;
};

// A contract-valid evaluation is exactly the profile identity plus one validated answer per
// question. The external answer's own acceptance flag is judged once where the outside record
// is mapped (C4); carrying a duplicate flag here would mirror the transport payload (C2).
export type OddEvidenceEvaluation = {
  readonly profileId: string;
  readonly profileVersion: number;
  readonly answers: Readonly<Record<string, OddEvidenceAnswer>>;
};

// Every way an evaluation can fail to produce advice. Each code is bounded vocabulary, so a
// failure class can be recorded or shown without any supplied value.
export type OddEvidenceUnavailableCode =
  | 'not_implemented'
  | 'caller_unavailable'
  | 'timeout'
  | 'transport_error'
  | 'tool_error'
  | 'malformed_payload'
  | 'rejected';

// Every way one evaluation can end: a contract-valid evaluation, or the bounded code that
// names the failure class. An expected failure is a returned value, never a throw (C5).
export type OddEvidenceOutcome =
  | {
      readonly status: 'evaluated';
      readonly evaluation: OddEvidenceEvaluation;
      readonly evaluationId?: string;
    }
  | {
      readonly status: 'unavailable';
      readonly code: OddEvidenceUnavailableCode;
      readonly evaluationId?: string;
    };

// Bound supplied by the caller per evaluation; no silent default, so composition states the
// time limit.
export type OddEvidenceEvaluatorOptions = {
  readonly timeoutMs: number;
};

// The capability port the delivery edge depends on. An adapter owns the executable, the
// tool name, the request encoding, the time bound and the parsing of the external answer;
// callers see only domain types and never a transport record. Every expected failure is
// reported as an `unavailable` outcome with its bounded code; an unexpected defect may
// still throw, and remains an exception for the caller to handle (C2, C5).
export type OddEvidenceEvaluator = {
  evaluate(
    input: OddEvidenceInput,
    options: OddEvidenceEvaluatorOptions,
  ): Promise<OddEvidenceOutcome>;
};
