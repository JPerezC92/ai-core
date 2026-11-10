// Application operation: one evaluation attempt against the injected advisory capability.
// It races the port against an injected deadline, maps every outcome to a fixed advisory
// sentence, and never imports infrastructure. Empty answers are the bounded malformed
// class rather than a receipt (R2). No supplied text, image bytes, transport message or
// payload value can reach the returned advisory (S9).

import type {
  OddEvidenceAnswer,
  OddEvidenceEvaluator,
  OddEvidenceInput,
  OddEvidenceUnavailableCode,
} from '../domain/advisory.ts';
import type { CapturedMessage } from '../domain/capture-message.ts';
import type { Deadline } from '../domain/deadline.ts';
import type {
  EvaluateEvidenceOptions,
  OddEvidenceAdvisory,
} from '../domain/plugin-contract.ts';

const unavailableAdvisories: Readonly<Record<OddEvidenceUnavailableCode, string>> = {
  not_implemented: 'The System 1 evidence evaluation is not implemented in this build.',
  caller_unavailable: 'No System 1 evidence evaluation channel is configured for this session.',
  timeout: 'The System 1 evidence evaluation did not answer within its configured time limit.',
  transport_error: 'The System 1 evidence evaluation channel failed before an answer arrived.',
  tool_error: 'The System 1 evidence evaluation reported an error for this request.',
  malformed_payload: 'The System 1 evidence evaluation answered outside its advertised contract.',
  rejected: 'The System 1 evidence evaluation rejected the supplied evidence.',
};

const evaluatedAdvisory =
  'The System 1 evidence evaluation returned a contract-valid answer for this message.';

export function toUnavailableAdvisory(
  code: OddEvidenceUnavailableCode,
  evaluationId?: string,
): OddEvidenceAdvisory {
  return {
    status: 'unavailable',
    code,
    advisory: unavailableAdvisories[code],
    ...(evaluationId === undefined || evaluationId.length === 0 ? {} : { evaluationId }),
  };
}

export function answersNoQuestion(
  answers: Readonly<Record<string, OddEvidenceAnswer>>,
): boolean {
  return Object.keys(answers).length === 0;
}

type EvaluationAttempt =
  | { readonly kind: 'answered'; readonly result: Awaited<ReturnType<OddEvidenceEvaluator['evaluate']>> }
  | { readonly kind: 'failed' }
  | { readonly kind: 'elapsed' };

export async function evaluateEvidence(
  message: CapturedMessage,
  evaluator: OddEvidenceEvaluator,
  options: EvaluateEvidenceOptions,
  deadline: Deadline,
): Promise<OddEvidenceAdvisory> {
  const input: OddEvidenceInput = {
    text: message.text,
    images: message.images,
    ...(options.expectedModel === undefined ? {} : { expectedModel: options.expectedModel }),
  };

  const evaluation: Promise<EvaluationAttempt> = evaluator
    .evaluate(input, { timeoutMs: options.timeoutMs })
    .then(
      (result) => ({ kind: 'answered' as const, result }),
      () => ({ kind: 'failed' as const }),
    );

  let cancelDeadline = (): void => undefined;
  const elapsed = new Promise<EvaluationAttempt>((resolve) => {
    cancelDeadline = deadline.schedule(options.timeoutMs, () => {
      resolve({ kind: 'elapsed' });
    });
  });

  try {
    const attempt = await Promise.race([evaluation, elapsed]);

    if (attempt.kind === 'answered') {
      const outcome = attempt.result;
      if (outcome.status !== 'evaluated') {
        return toUnavailableAdvisory(outcome.code, outcome.evaluationId);
      }
      if (answersNoQuestion(outcome.evaluation.answers)) {
        return toUnavailableAdvisory('malformed_payload', outcome.evaluationId);
      }
      return {
        status: 'evaluated',
        evaluation: outcome.evaluation,
        advisory: evaluatedAdvisory,
        ...(outcome.evaluationId === undefined || outcome.evaluationId.length === 0
          ? {}
          : { evaluationId: outcome.evaluationId }),
      };
    }

    return toUnavailableAdvisory(attempt.kind === 'failed' ? 'transport_error' : 'timeout');
  } finally {
    cancelDeadline();
  }
}
