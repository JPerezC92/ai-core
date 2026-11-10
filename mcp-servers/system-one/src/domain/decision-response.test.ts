import { expect, test } from 'vitest';

import { validateDecisionResponse } from './decision-response.ts';
import {
  createDecisionResponse,
  createDecisionResponseMissingQuestion,
  createDecisionResponseWithDerivedAnswer,
  createDecisionResponseWithInvalidProbability,
  createDecisionResponseWithModelMismatch,
  createDecisionResponseWithThirdProbabilityState,
  createDecisionResponseWithUnknownChoice,
} from '../test/helpers/decision-response.factory.ts';

test('accepts a response answering exactly present and absent', () => {
  const response = createDecisionResponse();
  const expectedModel = createDecisionResponse().model;
  const result = validateDecisionResponse(response, expectedModel);

  expect(result.ok).toBe(true);
  if (!result.ok) return;
  expect(result.response).toStrictEqual(response);
  // The accepted answer carries exactly the two declared states and no third one.
  for (const answer of Object.values(result.response.answers)) {
    expect(Object.keys(answer.probabilities).sort()).toStrictEqual(['absent', 'present']);
  }
});

test('rejects a response missing a question', () => {
  const response = createDecisionResponseMissingQuestion();
  const expectedModel = createDecisionResponse().model;

  expect(validateDecisionResponse(response, expectedModel).ok).toBe(false);
});

test('rejects a response that also answers the derived question', () => {
  const response = createDecisionResponseWithDerivedAnswer();
  const expectedModel = createDecisionResponse().model;

  const result = validateDecisionResponse(response, expectedModel);
  expect(result.ok).toBe(false);
  if (result.ok) return;
  // The derived answer is computed from the supplied images, so an answer for it is an
  // extra key: a response answers exactly the two questions the profile asked.
  expect(result.code).toBe('invalid_answers');
});

test('rejects a response choosing the removed third state', () => {
  const response = createDecisionResponseWithUnknownChoice();
  const expectedModel = createDecisionResponse().model;

  const result = validateDecisionResponse(response, expectedModel);
  expect(result.ok).toBe(false);
  if (result.ok) return;
  // The rejection is the choice rule itself, not a probability defect in the fixture.
  expect(result.code).toBe('invalid_answer');
});

test('rejects an answer carrying a third probability state', () => {
  const response = createDecisionResponseWithThirdProbabilityState();
  const expectedModel = createDecisionResponse().model;

  const result = validateDecisionResponse(response, expectedModel);
  expect(result.ok).toBe(false);
  if (result.ok) return;
  // The extra state is rejected by the probability rule, so a profile's two declared
  // states are also the only states a response may score.
  expect(result.code).toBe('invalid_probabilities');
});

test('rejects a response with an invalid probability', () => {
  const response = createDecisionResponseWithInvalidProbability();
  const expectedModel = createDecisionResponse().model;

  expect(validateDecisionResponse(response, expectedModel).ok).toBe(false);
});

test('rejects a response from the wrong model', () => {
  const response = createDecisionResponseWithModelMismatch();
  const expectedModel = createDecisionResponse().model;

  expect(validateDecisionResponse(response, expectedModel).ok).toBe(false);
});
