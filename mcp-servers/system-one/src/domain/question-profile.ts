// Single owner of the evidence vocabulary: the question ids the evaluation asks the model,
// the one answer id it derives itself, and the two states an answer may take. Every other
// declaration imports these, so the answer contract and the profile contract cannot drift
// apart.
//
// The profile asks the model exactly these two ids. `visual_evidence` is not among them:
// whether an image is attached is envelope metadata the server already holds, so asking a
// model to notice its own attachment only produces a semantic guess about an envelope fact.
// The evaluation derives that answer from the supplied images instead. It stays a closed
// answer id because the delivered payload keeps every id its consumers see today.
export type QuestionId = 'scope_changed' | 'user_only_decision';
export type DerivedQuestionId = 'visual_evidence';
// Every id an answer record carries: the asked questions plus the derived answer.
export type AnswerId = QuestionId | DerivedQuestionId;
// Exactly the two states the evaluation supplies evidence for, so no question can declare
// an answer state its input cannot reach: a profile carrying any third state is rejected.
export type Criterion = 'present' | 'absent';

// The validated profile document. This is the type's single owner: the validator returns it
// and every consumer imports it from here, so no other module declares the profile shape.
export type QuestionProfile = {
  profileId: string;
  version: number;
  notes: string;
  questions: Record<QuestionId, {
    type: 'choice';
    instructions: string;
    criteria: Record<Criterion, string>;
  }>;
};

export const questionIds: readonly QuestionId[] = [
  'scope_changed', 'user_only_decision',
];
export const derivedQuestionId: DerivedQuestionId = 'visual_evidence';
export const answerIds: readonly AnswerId[] = [...questionIds, derivedQuestionId];
export const criteria: readonly Criterion[] = ['present', 'absent'];

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

export function validateQuestionProfile(
  input: unknown,
): { ok: true; profile: QuestionProfile } | { ok: false; reason: string } {
  if (!isRecord(input) || !isNonemptyString(input.profileId) ||
      typeof input.version !== 'number' || !Number.isInteger(input.version) || input.version <= 0 ||
      !isNonemptyString(input.notes) || !isRecord(input.questions) ||
      !hasExactKeys(input.questions, questionIds)) {
    return { ok: false, reason: 'Invalid question profile metadata or question IDs' };
  }

  for (const id of questionIds) {
    const question = input.questions[id];
    if (!isRecord(question) || question.type !== 'choice' ||
        !isNonemptyString(question.instructions)) {
      return { ok: false, reason: `Invalid question: ${id}` };
    }

    // Narrow into a const local: property narrowing does not survive into the callback.
    const questionCriteria = question.criteria;
    if (!isRecord(questionCriteria) || !hasExactKeys(questionCriteria, criteria) ||
        !criteria.every((criterion) => isNonemptyString(questionCriteria[criterion]))) {
      return { ok: false, reason: `Invalid question: ${id}` };
    }
  }

  return { ok: true, profile: input as QuestionProfile };
}
