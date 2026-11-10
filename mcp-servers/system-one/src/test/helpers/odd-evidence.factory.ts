// Test data and doubles for the evidence evaluation application operation:
// a contract-valid question profile, text-and-image evidence inputs including a
// contract-invalid one, and gateway/profile-source doubles covering the valid
// path and each rejection. The decision gateway doubles record every call they
// receive. Every creator returns fresh values; no module-level mutable state is
// shared.

import type {
  OddEvidenceGateway,
  OddEvidenceImage,
  OddEvidenceInput,
  QuestionProfileSource,
} from '../../domain/odd-evidence.ts';
import { validateQuestionProfile } from '../../domain/question-profile.ts';

const decisionModel = 'd1-2b@q8_0';

// The two question identifiers the profile asks the model; the decision response below is
// keyed to exactly these IDs. `visual_evidence` is deliberately not one of them: the
// evaluation derives that answer from the supplied images.
const questionIds = ['scope_changed', 'user_only_decision'] as const;
export type ProfileQuestionId = (typeof questionIds)[number];

const criterionIds = ['present', 'absent'] as const;
type CriterionId = (typeof criterionIds)[number];

type ProfileQuestion = {
  readonly type: 'choice';
  readonly instructions: string;
  readonly criteria: Readonly<Record<CriterionId, string>>;
};

type ChoiceAnswer = {
  readonly type: 'choice';
  readonly choice: CriterionId;
  readonly probabilities: Readonly<Record<CriterionId, number>>;
  readonly confidence: number;
};

type DecisionResponse = {
  readonly model: string;
  readonly answers: Readonly<Record<ProfileQuestionId, ChoiceAnswer>>;
  readonly usage: { readonly input_tokens: number; readonly output_tokens: number };
};

export function createOddEvidenceProfile() {
  return {
    profileId: 'odd-evidence-fixture',
    version: 1,
    questions: {
      scope_changed: createQuestion(
        'Decide whether the request changes the accepted implementation scope.',
      ),
      user_only_decision: createQuestion(
        'Decide whether an unresolved user-only decision remains.',
      ),
    },
    notes: 'Advisory only: no answer in this profile authorizes action.',
  };
}

export function createInvalidOddEvidenceProfile() {
  return {
    ...createOddEvidenceProfile(),
    version: 0,
  };
}

export type OddEvidencePayload = {
  readonly text: string;
  readonly images: OddEvidenceImage[];
};

export function createEvidenceImage(): OddEvidenceImage {
  return {
    mimeType: 'image/png',
    base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  };
}

export function createEvidence(): OddEvidencePayload {
  return {
    text: 'The latest user request repeats the accepted implementation scope.',
    images: [createEvidenceImage()],
  };
}

// Contract-invalid variant: the factory text with an image whose base64 payload
// is empty, which the evidence rule rejects before any decision is requested.
export function createEvidenceWithInvalidImage(): OddEvidencePayload {
  const evidence = createEvidence();
  return {
    text: evidence.text,
    images: [{ ...createEvidenceImage(), base64: '' }],
  };
}

// Text-only evidence: no image is attached, so the derived visual_evidence answer is absent.
export function createEvidenceWithoutImages(): OddEvidencePayload {
  const evidence = createEvidence();
  return { text: evidence.text, images: [] };
}

export function createExpectedModel(): string {
  return decisionModel;
}

// Deterministic response keyed to the profile's two question IDs.
export function createDecisionResponse(): DecisionResponse {
  return {
    model: createExpectedModel(),
    answers: {
      scope_changed: createChoiceAnswer('present'),
      user_only_decision: createChoiceAnswer('absent'),
    },
    usage: { input_tokens: 0, output_tokens: 0 },
  };
}

export function createDecisionResponseMissingQuestion() {
  const response = createDecisionResponse();
  const { user_only_decision: _missing, ...answers } = response.answers;
  return { ...response, answers };
}

// A response that also answers the derived visual_evidence question. The evaluation computes
// that answer from the supplied images, so a model answer for it is refused, not merged.
export function createDecisionResponseWithDerivedAnswer() {
  const response = createDecisionResponse();
  return {
    ...response,
    answers: {
      ...response.answers,
      visual_evidence: createChoiceAnswer('present'),
    },
  };
}

// The port double answers through the same domain validator the adapter uses, so a fixture
// reaches the operation in the typed form the port declares: a valid fixture is returned as
// the validated profile, and an invalid one as the validator's own bounded reason rather
// than being asserted valid by a cast.
export function createQuestionProfileSource(
  profile: unknown = createOddEvidenceProfile(),
): QuestionProfileSource {
  return {
    load: async () => validateQuestionProfile(profile),
  };
}

export function createQuestionProfileSourceWithInvalidProfile(): QuestionProfileSource {
  return createQuestionProfileSource(createInvalidOddEvidenceProfile());
}

// Decision gateway doubles record every call they receive, so a test can assert
// whether a decision was requested and what input the operation forwarded. Each
// creator returns a fresh instance with its own call log; the `calls` getter
// returns a snapshot copy of that log.
export type RecordingDecisionGateway = OddEvidenceGateway & {
  readonly calls: ReadonlyArray<OddEvidenceInput>;
};

export function createDecisionGateway(
  response: unknown = createDecisionResponse(),
): RecordingDecisionGateway {
  return createRecordingGateway(async () => response);
}

export function createDecisionGatewayWithInvalidResponse(): RecordingDecisionGateway {
  return createDecisionGateway(createDecisionResponseMissingQuestion());
}

export function createGatewayBoundaryError(): Error {
  return new Error('Decision gateway transport unavailable');
}

export function createDecisionGatewayRejecting(
  error: Error = createGatewayBoundaryError(),
): RecordingDecisionGateway {
  return createRecordingGateway(async () => {
    throw error;
  });
}

function createRecordingGateway(
  respond: (input: OddEvidenceInput) => Promise<unknown>,
): RecordingDecisionGateway {
  const calls: OddEvidenceInput[] = [];
  return {
    decide: async (input: OddEvidenceInput) => {
      calls.push(input);
      return respond(input);
    },
    get calls() {
      return calls.slice();
    },
  };
}

function createQuestion(instructions: string): ProfileQuestion {
  return {
    type: 'choice',
    instructions,
    criteria: {
      present: 'The supplied evidence establishes the condition.',
      absent: 'The supplied evidence establishes the condition is absent.',
    },
  };
}

function createChoiceAnswer(choice: CriterionId): ChoiceAnswer {
  const probabilities: Record<CriterionId, number> = {
    present: 0.1,
    absent: 0.1,
  };
  probabilities[choice] = 0.8;
  return { type: 'choice', choice, probabilities, confidence: 0.8 };
}

// The answer the evaluation derives for visual_evidence: the image count decides it with
// certainty, so the chosen state scores 1 and the other 0. Stated as a factory value so a
// test never reconstructs the derived shape inline.
export function createDerivedVisualEvidenceAnswer(
  choice: CriterionId,
): { readonly type: 'choice'; readonly choice: CriterionId; readonly probabilities: Readonly<Record<CriterionId, number>> } {
  const probabilities: Record<CriterionId, number> = { present: 0, absent: 0 };
  probabilities[choice] = 1;
  return { type: 'choice', choice, probabilities };
}
