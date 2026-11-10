import { expect, test } from 'vitest';

import { validateQuestionProfile } from './question-profile.ts';
import {
  createQuestionProfile,
  createQuestionProfileWithDerivedQuestion,
  createQuestionProfileWithMalformedQuestion,
  createQuestionProfileWithNonChoiceQuestion,
  createQuestionProfileWithoutProfileId,
  createQuestionProfileWithThirdCriterionState,
} from '../test/helpers/question-profile.factory.ts';

test('accepts a profile declaring exactly present and absent for both questions', () => {
  const profile = createQuestionProfile();
  const result = validateQuestionProfile(profile);

  expect(result.ok).toBe(true);
  if (!result.ok) return;
  expect(result.profile).toStrictEqual(profile);
  // The accepted profile declares exactly the two reachable states and no third one.
  for (const question of Object.values(result.profile.questions)) {
    expect(Object.keys(question.criteria).sort()).toStrictEqual(['absent', 'present']);
  }
});

test('rejects a profile that asks the derived visual evidence question', () => {
  const input = createQuestionProfileWithDerivedQuestion();

  // The model is asked exactly two questions; the visual_evidence answer is derived from
  // the supplied images. The rejection is for the extra question itself, not for an
  // unrelated defect: the same profile without it is accepted by the case above.
  expect(validateQuestionProfile(input)).toStrictEqual({
    ok: false,
    reason: 'Invalid question profile metadata or question IDs',
  });
});

test('rejects a profile declaring a third criterion state', () => {
  const input = createQuestionProfileWithThirdCriterionState();

  // The rejection is for the extra state itself, not for an unrelated defect: the same
  // profile without it is accepted by the case above.
  expect(validateQuestionProfile(input)).toStrictEqual({
    ok: false,
    reason: 'Invalid question: scope_changed',
  });
});

test('rejects a non-choice question', () => {
  const profile = createQuestionProfileWithNonChoiceQuestion();

  expect(validateQuestionProfile(profile).ok).toBe(false);
});

test('rejects a profile without an identifier', () => {
  const profile = createQuestionProfileWithoutProfileId();

  expect(validateQuestionProfile(profile).ok).toBe(false);
});

test('rejects an additional malformed question', () => {
  const input = createQuestionProfileWithMalformedQuestion();

  expect(validateQuestionProfile(input).ok).toBe(false);
});
