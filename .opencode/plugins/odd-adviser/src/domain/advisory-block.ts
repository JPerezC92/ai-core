// Domain formatting of one advisory block. Every line comes from the payload or from the
// fixed sentences below, so no supplied message text can reach the block (R12, S9). This
// module performs no IO.

import type { OddEvidenceAnswer, OddEvidenceEvaluation } from './advisory.ts';
import type { OddEvidenceAdvisory } from './plugin-contract.ts';

export const ADVISORY_BLOCK_START = '=== SYSTEM 1 ADVISER - ADVISORY ONLY ===';
export const ADVISORY_BLOCK_END = '=== END SYSTEM 1 ADVISER ===';

const WEAK_SIGNAL_CONFIDENCE = 0.6;
const WEAK_SIGNAL_MARKER = ' ⚠ weak signal';

function maximumProbability(
  probabilities: Readonly<Record<string, number>>,
): number | null {
  let maximum: number | null = null;
  for (const score of Object.values(probabilities)) {
    if (maximum === null || score > maximum) maximum = score;
  }
  return maximum;
}

function reportedConfidence(answer: OddEvidenceAnswer): number | null {
  return answer.confidence ?? maximumProbability(answer.probabilities);
}

function formatQuestionLine(questionId: string, answer: OddEvidenceAnswer): string {
  const confidence = reportedConfidence(answer);
  const figure = confidence === null ? 'n/a' : confidence.toFixed(2);
  const marker =
    confidence !== null && confidence < WEAK_SIGNAL_CONFIDENCE ? WEAK_SIGNAL_MARKER : '';
  return `${questionId} → ${answer.choice} (${figure})${marker}`;
}

function formatQuestionLines(evaluation: OddEvidenceEvaluation): ReadonlyArray<string> {
  return Object.entries(evaluation.answers).map(([questionId, answer]) =>
    formatQuestionLine(questionId, answer),
  );
}

export function formatAdvisoryBlock(advisory: OddEvidenceAdvisory): string {
  return [
    ADVISORY_BLOCK_START,
    advisory.advisory,
    ...(advisory.status === 'evaluated' ? formatQuestionLines(advisory.evaluation) : []),
    'Advisory only: it never authorizes, waives a gate, or blocks an action.',
    ADVISORY_BLOCK_END,
  ].join('\n');
}
