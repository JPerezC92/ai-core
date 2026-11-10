// Domain formatting of one advisory block. Every line comes from the payload or from the
// fixed sentences below, so no supplied message text can reach the block (R12, S9). This
// module performs no IO.

import type { OddEvidenceAnswer, OddEvidenceEvaluation } from './advisory.ts';
import type { OddEvidenceAdvisory } from './plugin-contract.ts';

export const ADVISORY_BLOCK_START = '=== SYSTEM 1 | EXECUTION DIRECTIVES ===';
export const ADVISORY_UNAVAILABLE_BLOCK_START = '=== SYSTEM 1 | UNAVAILABLE ===';
export const ADVISORY_BLOCK_END = '=== END SYSTEM 1 ===';

const EXECUTE_ACCORDINGLY =
  'Execute accordingly. Deviate only when stronger evidence or governing constraints justify it.';
const NO_NEW_PERMISSIONS = 'No new permissions are granted.';

const INTERRUPT_INCLUSION_FIGURE = 0.8;
const GUIDANCE_INCLUSION_FIGURE = 0.6;

const QUESTION_SCOPE_CHANGED = 'scope_changed';
const QUESTION_USER_ONLY_DECISION = 'user_only_decision';
const QUESTION_VISUAL_EVIDENCE = 'visual_evidence';

const CHOICE_PRESENT = 'present';
const CHOICE_ABSENT = 'absent';

const ACTION_SCOPE_CHANGED_PRESENT =
  'Potential new requirement in this message. Check existing context and authorization before expanding. Pause only work that still needs extra authorization.';
const ACTION_SCOPE_CHANGED_ABSENT =
  'No new requirement in this message. Continue the established task without unnecessary renegotiation, respecting actual context and authorization.';
const ACTION_USER_ONLY_DECISION_PRESENT =
  'A reserved decision is in this message. Ask that specific question. Continue independent authorized work; do not freeze the whole turn.';
const ACTION_USER_ONLY_DECISION_ABSENT =
  'No reserved decision in this message. Continue already-authorized work. Do not ask for redundant approval. Not new permission.';
const ACTION_VISUAL_EVIDENCE_PRESENT = 'Image attached. Inspect it before answering.';

const FROZEN_ACTIONS: Readonly<Record<string, Readonly<Record<string, string>>>> = {
  [QUESTION_SCOPE_CHANGED]: {
    [CHOICE_PRESENT]: ACTION_SCOPE_CHANGED_PRESENT,
    [CHOICE_ABSENT]: ACTION_SCOPE_CHANGED_ABSENT,
  },
  [QUESTION_USER_ONLY_DECISION]: {
    [CHOICE_PRESENT]: ACTION_USER_ONLY_DECISION_PRESENT,
    [CHOICE_ABSENT]: ACTION_USER_ONLY_DECISION_ABSENT,
  },
  [QUESTION_VISUAL_EVIDENCE]: {
    [CHOICE_PRESENT]: ACTION_VISUAL_EVIDENCE_PRESENT,
  },
};

function maximumProbability(
  probabilities: Readonly<Record<string, number>>,
): number | null {
  let maximum: number | null = null;
  for (const score of Object.values(probabilities)) {
    if (!Number.isFinite(score)) continue;
    if (maximum === null || score > maximum) maximum = score;
  }
  return maximum;
}

function reportedFigure(answer: OddEvidenceAnswer): number | null {
  if (Number.isFinite(answer.confidence)) return answer.confidence as number;
  return maximumProbability(answer.probabilities);
}

function inclusionThreshold(questionId: string, choice: string): number | null {
  const actions = FROZEN_ACTIONS[questionId];
  if (actions === undefined) return null;
  if (actions[choice] === undefined) return null;
  if (
    choice === CHOICE_PRESENT &&
    (questionId === QUESTION_SCOPE_CHANGED || questionId === QUESTION_USER_ONLY_DECISION)
  ) {
    return INTERRUPT_INCLUSION_FIGURE;
  }
  return GUIDANCE_INCLUSION_FIGURE;
}

function formatFindingLines(
  questionId: string,
  answer: OddEvidenceAnswer,
): ReadonlyArray<string> {
  const action = FROZEN_ACTIONS[questionId]?.[answer.choice];
  const threshold = inclusionThreshold(questionId, answer.choice);
  const figure = reportedFigure(answer);
  if (action === undefined || threshold === null || figure === null) return [];
  if (figure < threshold) return [];
  return [`${questionId} → ${answer.choice} (${figure.toFixed(2)})`, `→ ${action}`];
}

function formatQuestionLines(evaluation: OddEvidenceEvaluation): ReadonlyArray<string> {
  return Object.entries(evaluation.answers).flatMap(([questionId, answer]) =>
    formatFindingLines(questionId, answer),
  );
}

function formatUnavailableBlock(advisory: string): string {
  return [
    ADVISORY_UNAVAILABLE_BLOCK_START,
    advisory,
    NO_NEW_PERMISSIONS,
    ADVISORY_BLOCK_END,
  ].join('\n');
}

function formatExecutionDirectivesBlock(lines: ReadonlyArray<string>): string {
  return [
    ADVISORY_BLOCK_START,
    ...lines,
    EXECUTE_ACCORDINGLY,
    NO_NEW_PERMISSIONS,
    ADVISORY_BLOCK_END,
  ].join('\n');
}

export function formatAdvisoryBlock(advisory: OddEvidenceAdvisory): string {
  if (advisory.status !== 'evaluated') {
    return formatUnavailableBlock(advisory.advisory);
  }

  const lines = formatQuestionLines(advisory.evaluation);
  if (lines.length === 0) return '';
  return formatExecutionDirectivesBlock(lines);
}
