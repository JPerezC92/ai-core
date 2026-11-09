// Domain contract of the advisory plugin: evaluation options, advisory records, message
// identity, and the evaluator connection port. This module is framework-free. It declares no
// host wire types, performs no IO and throws nothing.

import type {
  OddEvidenceEvaluation,
  OddEvidenceEvaluator,
  OddEvidenceEvaluatorOptions,
  OddEvidenceUnavailableCode,
} from './advisory.ts';

export type EvaluateEvidenceOptions = OddEvidenceEvaluatorOptions & {
  readonly expectedModel?: string;
};

export type OddEvidenceAdvisory =
  | {
      readonly status: 'evaluated';
      readonly evaluation: OddEvidenceEvaluation;
      readonly advisory: string;
    }
  | {
      readonly status: 'unavailable';
      readonly code: OddEvidenceUnavailableCode;
      readonly advisory: string;
    };

export type MessageIdentity = {
  readonly sessionID: string;
  readonly messageID: string;
};

export type OddEvidenceEvaluatorConnection = OddEvidenceEvaluator & {
  readonly close: () => Promise<void>;
};
