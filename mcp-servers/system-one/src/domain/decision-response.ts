// Pure domain rule: decide whether a model decision response satisfies the versioned
// answer contract before anything is delivered. No IO, no infrastructure imports, no throws.

import { criteria, questionIds } from './question-profile.ts';
import type { AnswerId, Criterion, QuestionId } from './question-profile.ts';

// The answer vocabulary is the profile document's own: these names preserve the module's
// existing exports while declaring no second copy of the ids or states. A decision response
// answers exactly the questions the profile asked, so its ids are the asked question ids.
export type DecisionQuestionId = QuestionId;
// The answer states are exactly the two the question profile declares, so a response can
// only answer a state the supplied input reaches: a third state is not a valid choice.
export type DecisionChoice = Criterion;

export type ValidatedDecisionAnswer = {
  readonly type: 'choice';
  readonly choice: DecisionChoice;
  readonly probabilities: Readonly<Record<DecisionChoice, number>>;
  readonly confidence?: number;
};

export type ValidatedDecisionResponse = {
  readonly model: string;
  readonly answers: Readonly<Record<DecisionQuestionId, ValidatedDecisionAnswer>>;
  // Envelope field preserved from the API response; this contract does not validate it.
  readonly usage?: unknown;
};

// The complete answer record an evaluation delivers: one validated model answer per asked
// question plus the answer the evaluation derives itself. Every entry carries the same
// answer shape, so a consumer reads one record without knowing which entries the model
// produced.
export type ValidatedEvidenceAnswers = Readonly<Record<AnswerId, ValidatedDecisionAnswer>>;

export type DecisionResponseRejectionCode =
  | 'invalid_response'
  | 'invalid_expected_model'
  | 'invalid_model'
  | 'model_mismatch'
  | 'invalid_answers'
  | 'invalid_answer'
  | 'invalid_probabilities'
  | 'invalid_confidence';

export type DecisionResponseValidation =
  | { readonly ok: true; readonly response: ValidatedDecisionResponse }
  | { readonly ok: false; readonly code: DecisionResponseRejectionCode; readonly reason: string };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isNonemptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function hasExactKeys(record: Record<string, unknown>, keys: readonly string[]): boolean {
  return Object.keys(record).length === keys.length &&
    keys.every((key) => Object.prototype.hasOwnProperty.call(record, key));
}

function isProbability(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1;
}

function isChoice(value: unknown): value is DecisionChoice {
  return criteria.some((criterion) => criterion === value);
}

function readProbabilities(
  value: unknown,
): Readonly<Record<DecisionChoice, number>> | undefined {
  if (!isRecord(value) || !hasExactKeys(value, criteria)) return undefined;
  const present = value['present'];
  const absent = value['absent'];
  if (!isProbability(present) || !isProbability(absent)) {
    return undefined;
  }
  return { present, absent };
}

export function validateDecisionResponse(
  input: unknown,
  expectedModel: string,
): DecisionResponseValidation {
  if (!isNonemptyString(expectedModel)) {
    return reject('invalid_expected_model', 'Expected model must be a non-empty string');
  }
  if (!isRecord(input)) {
    return reject('invalid_response', 'Decision response must be a non-array object');
  }
  if (!isNonemptyString(input.model)) {
    return reject('invalid_model', 'Decision response model must be a non-empty string');
  }
  if (input.model !== expectedModel) {
    return reject('model_mismatch', `Expected model "${expectedModel}" but response used "${input.model}"`);
  }
  if (!isRecord(input.answers) || !hasExactKeys(input.answers, questionIds)) {
    return reject(
      'invalid_answers',
      `Decision response must answer exactly: ${questionIds.join(', ')}`,
    );
  }

  const answers = {} as Record<DecisionQuestionId, ValidatedDecisionAnswer>;
  for (const id of questionIds) {
    const answer = input.answers[id];
    if (!isRecord(answer) || answer.type !== 'choice' || !isChoice(answer.choice)) {
      return reject('invalid_answer', `Invalid choice answer for question: ${id}`);
    }
    const probabilities = readProbabilities(answer.probabilities);
    if (probabilities === undefined) {
      return reject('invalid_probabilities', `Invalid probabilities for question: ${id}`);
    }
    const confidence = answer.confidence;
    if (confidence !== undefined && !isProbability(confidence)) {
      return reject('invalid_confidence', `Invalid confidence for question: ${id}`);
    }
    answers[id] = {
      type: 'choice',
      choice: answer.choice,
      probabilities,
      ...(confidence === undefined ? {} : { confidence }),
    };
  }

  return {
    ok: true,
    response: {
      model: input.model,
      answers,
      ...(Object.prototype.hasOwnProperty.call(input, 'usage') ? { usage: input.usage } : {}),
    },
  };
}

function reject(
  code: DecisionResponseRejectionCode,
  reason: string,
): DecisionResponseValidation {
  return { ok: false, code, reason };
}
