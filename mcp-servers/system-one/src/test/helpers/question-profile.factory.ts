// A synthetic contract fixture, not a copy of the shipped document: the validator unit test
// needs a well-formed profile, and `profile-file-source.test.ts` is the test that reads the
// document this package actually ships.
export function createQuestionProfile() {
  return {
    profileId: 'odd-evidence-fixture',
    version: 1,
    questions: {
      scope_changed: createQuestion(),
      user_only_decision: createQuestion(),
    },
    notes: 'Advice does not authorize action.',
  };
}

// A profile that also declares the derived answer id as a question. The model is asked
// exactly the two question ids, so a profile asking for the derived one is rejected: the
// derived answer is computed from the supplied images, never requested from the model.
export function createQuestionProfileWithDerivedQuestion() {
  const profile = createQuestionProfile();
  return {
    ...profile,
    questions: {
      ...profile.questions,
      visual_evidence: createQuestion(),
    },
  };
}

export function createQuestionProfileWithNonChoiceQuestion() {
  const profile = createQuestionProfile();
  profile.questions.scope_changed.type = 'text';
  return profile;
}

// The inverse of the shipped rule: a profile may declare only the two states its input
// reaches, so any third state is a rejection case rather than a required criterion.
export function createQuestionProfileWithThirdCriterionState() {
  const profile = createQuestionProfile();
  return {
    ...profile,
    questions: {
      ...profile.questions,
      scope_changed: {
        ...profile.questions.scope_changed,
        criteria: {
          ...profile.questions.scope_changed.criteria,
          unknown: 'The supplied evidence does not establish either condition.',
        },
      },
    },
  };
}

export function createQuestionProfileWithoutProfileId() {
  const { profileId: _profileId, ...profile } = createQuestionProfile();
  return profile;
}

export function createQuestionProfileWithMalformedQuestion() {
  const profile = createQuestionProfile();
  return {
    ...profile,
    questions: { ...profile.questions, malformed: null },
  };
}

function createQuestion() {
  return {
    type: 'choice',
    instructions: 'Classify the supplied evidence.',
    criteria: {
      present: 'The evidence establishes the condition.',
      absent: 'The evidence establishes the condition is absent.',
    },
  };
}
