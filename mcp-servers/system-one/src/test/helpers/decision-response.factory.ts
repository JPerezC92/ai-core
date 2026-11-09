// Synthetic profile answers using the observed d1 response envelope; scores are not
// observations. The model answers exactly the two questions the profile asks, and each
// answer carries exactly the two states the profile declares, so a third state is a
// rejection case rather than a fixture value. `visual_evidence` is absent here on purpose:
// the evaluation derives it from the supplied images, so a model answer to it is rejected.
export function createDecisionResponse() {
  return {
    model: 'd1-2b@q8_0',
    answers: {
      scope_changed: createChoiceAnswer('present'),
      user_only_decision: createChoiceAnswer('absent'),
    },
    usage: { input_tokens: 304, output_tokens: 0 },
  };
}

export function createDecisionResponseMissingQuestion() {
  const response = createDecisionResponse();
  const { user_only_decision: _missing, ...answers } = response.answers;
  return { ...response, answers };
}

// A response that also answers the derived question. The derived answer is computed from
// the supplied images, so an answer for it is refused rather than merged.
export function createDecisionResponseWithDerivedAnswer() {
  const response = createDecisionResponse();
  return {
    ...response,
    answers: { ...response.answers, visual_evidence: createChoiceAnswer('present') },
  };
}

// The removed escape state is no longer a choice the contract accepts.
export function createDecisionResponseWithUnknownChoice() {
  const response = createDecisionResponse();
  response.answers.scope_changed.choice = 'unknown';
  return response;
}

// A third probability state alongside the two the profile declares.
export function createDecisionResponseWithThirdProbabilityState() {
  const response = createDecisionResponse();
  Object.assign(response.answers.scope_changed.probabilities, { unknown: 0.1 });
  return response;
}

export function createDecisionResponseWithInvalidProbability() {
  const response = createDecisionResponse();
  response.answers.scope_changed.probabilities.present = 1.5;
  return response;
}

export function createDecisionResponseWithModelMismatch() {
  const response = createDecisionResponse();
  response.model = 'different-model';
  return response;
}

// `String(choice)` widens the property so a case can set a choice outside the contract.
function createChoiceAnswer(choice: 'present' | 'absent') {
  const probabilities: Record<'present' | 'absent', number> = { present: 0.1, absent: 0.1 };
  probabilities[choice] = 0.8;
  return { type: 'choice', choice: String(choice), probabilities, confidence: 0.8 };
}
