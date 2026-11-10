// Unit test of the evidence evaluation application operation: it constructs the
// operation directly with injected doubles and asserts its orchestration result for
// supplied evidence, including whether a decision was requested, the input derived from
// the loaded profile, and the decision exchange handed to the trace ports. Returned
// business failures stay values; only a gateway boundary exception propagates.

import { expect, test } from 'vitest';

import { EvaluateOddEvidence } from './evaluate-odd-evidence.ts';
import { answerIds } from '../domain/question-profile.ts';
import {
  createEvaluationTraceHandling,
  createEvaluationTraceRecorder,
  createSessionId,
  createTraceImageStore,
} from '../test/helpers/evaluation-trace.factory.ts';
import {
  createDecisionGateway,
  createDecisionGatewayRejecting,
  createDecisionGatewayWithInvalidResponse,
  createDecisionResponse,
  createDecisionResponseMissingQuestion,
  createDecisionResponseWithDerivedAnswer,
  createDerivedVisualEvidenceAnswer,
  createEvidence,
  createEvidenceWithInvalidImage,
  createEvidenceWithoutImages,
  createExpectedModel,
  createGatewayBoundaryError,
  createOddEvidenceProfile,
  createQuestionProfileSource,
  createQuestionProfileSourceWithInvalidProfile,
} from '../test/helpers/odd-evidence.factory.ts';

const EVALUATION_ID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

test('returns the validated answers plus the derived visual evidence answer', async () => {
  const profile = createOddEvidenceProfile();
  const response = createDecisionResponse();
  const evidence = createEvidence();
  const gateway = createDecisionGateway(response);
  const operation = new EvaluateOddEvidence({
    decisionGateway: gateway,
    questionProfileSource: createQuestionProfileSource(profile),
  });

  const result = await operation.execute(evidence.text, evidence.images, createExpectedModel());

  // The model's two validated answers are delivered unchanged, and the answer the model is
  // not asked is appended from the supplied image count: one image is `present`.
  expect(result.evaluationId).toMatch(EVALUATION_ID_PATTERN);
  expect(result).toStrictEqual({
    ok: true,
    evaluationId: result.evaluationId,
    profileId: profile.profileId,
    profileVersion: profile.version,
    answers: {
      ...response.answers,
      visual_evidence: createDerivedVisualEvidenceAnswer('present'),
    },
  });
  expect(gateway.calls.length).toBe(1);
  const [call] = gateway.calls;
  expect(call).toBeDefined();
  // The operation asks the profile's questions as a record keyed by their own ids, and each
  // question keeps the answer kind the profile declares beside its instruction and criteria.
  // The derived question is not asked of the model.
  expect(call).toStrictEqual({
    questions: {
      scope_changed: {
        type: 'choice',
        instructions: profile.questions.scope_changed.instructions,
        criteria: profile.questions.scope_changed.criteria,
      },
      user_only_decision: {
        type: 'choice',
        instructions: profile.questions.user_only_decision.instructions,
        criteria: profile.questions.user_only_decision.criteria,
      },
    },
    text: evidence.text,
    images: evidence.images,
  });
});

test('derives visual evidence absent when the evidence carries no image', async () => {
  const evidence = createEvidenceWithoutImages();
  const response = createDecisionResponse();
  const operation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGateway(response),
    questionProfileSource: createQuestionProfileSource(),
  });

  const result = await operation.execute(evidence.text, evidence.images, createExpectedModel());

  expect(result.ok).toBe(true);
  if (!result.ok) return;
  // The delivered record keeps every id in the closed answer vocabulary, and each entry
  // carries the same answer shape whatever produced it.
  expect(Object.keys(result.answers).sort()).toStrictEqual([...answerIds].sort());
  expect(result.answers.visual_evidence).toStrictEqual(
    createDerivedVisualEvidenceAnswer('absent'),
  );
  // The text-only evidence still reaches the model unchanged, so the derivation is not a
  // substitute for the call.
  expect(result.answers.scope_changed).toStrictEqual(response.answers.scope_changed);
});

test('returns no derived answer when the model answers the derived question', async () => {
  const evidence = createEvidence();
  const operation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGateway(createDecisionResponseWithDerivedAnswer()),
    questionProfileSource: createQuestionProfileSource(),
  });

  const result = await operation.execute(evidence.text, evidence.images, createExpectedModel());

  // A response answering the derived question is refused as an answer-set defect, and the
  // rejected evaluation carries no answers at all, so nothing fabricates visual_evidence.
  expect(result.ok).toBe(false);
  if (result.ok) return;
  expect(result.evaluationId).toMatch(EVALUATION_ID_PATTERN);
  expect(result.code).toBe('invalid_answers');
  expect(result).not.toHaveProperty('answers');
});

test('returns invalid_profile when the question profile is rejected', async () => {
  const evidence = createEvidence();
  const gateway = createDecisionGateway();
  const operation = new EvaluateOddEvidence({
    decisionGateway: gateway,
    questionProfileSource: createQuestionProfileSourceWithInvalidProfile(),
  });

  const result = await operation.execute(evidence.text, evidence.images, createExpectedModel());

  // The port's rejection is returned unchanged: the code and the reason text a caller sees do
  // not depend on which layer performed the validation. This replaces the previous
  // `ok === false` plus `code === 'invalid_profile'` pair with one exact-shape assertion that
  // also pins the reason text and refuses any extra field.
  expect(result.evaluationId).toMatch(EVALUATION_ID_PATTERN);
  expect(result).toStrictEqual({
    ok: false,
    evaluationId: result.evaluationId,
    code: 'invalid_profile',
    reason: 'Invalid question profile metadata or question IDs',
  });
  expect(gateway.calls.length).toBe(0);
});

test('returns invalid_evidence when the evidence payload is rejected', async () => {
  const evidence = createEvidenceWithInvalidImage();
  const gateway = createDecisionGateway();
  const operation = new EvaluateOddEvidence({
    decisionGateway: gateway,
    questionProfileSource: createQuestionProfileSource(),
  });

  const result = await operation.execute(evidence.text, evidence.images, createExpectedModel());

  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(result.evaluationId).toMatch(EVALUATION_ID_PATTERN);
    expect(result.code).toBe('invalid_evidence');
  }
  expect(gateway.calls.length).toBe(0);
});

test('returns invalid_answers when the decision response is rejected', async () => {
  const evidence = createEvidence();
  const operation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGatewayWithInvalidResponse(),
    questionProfileSource: createQuestionProfileSource(),
  });

  const result = await operation.execute(evidence.text, evidence.images, createExpectedModel());

  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(result.evaluationId).toMatch(EVALUATION_ID_PATTERN);
    expect(result.code).toBe('invalid_answers');
  }
});

test('propagates a decision gateway rejection as a boundary exception', async () => {
  const boundaryError = createGatewayBoundaryError();
  const evidence = createEvidence();
  const operation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGatewayRejecting(boundaryError),
    questionProfileSource: createQuestionProfileSource(),
  });

  await expect(
    operation.execute(evidence.text, evidence.images, createExpectedModel()),
  ).rejects.toBe(boundaryError);
});

test('records the exact request and response bodies for a validated evaluation', async () => {
  const profile = createOddEvidenceProfile();
  const evidence = createEvidence();
  const response = createDecisionResponse();
  const sessionId = createSessionId();
  const gateway = createDecisionGateway(response);
  const recorder = createEvaluationTraceRecorder();
  const imageStore = createTraceImageStore();
  const operation = new EvaluateOddEvidence({
    decisionGateway: gateway,
    questionProfileSource: createQuestionProfileSource(profile),
    tracing: {
      evaluationTrace: recorder,
      imageStore,
      decisionModel: createExpectedModel(),
    },
  });

  const result = await operation.execute(
    evidence.text,
    evidence.images,
    createExpectedModel(),
    sessionId,
  );

  expect(result.ok).toBe(true);
  expect(recorder.entries).toHaveLength(1);
  const [entry] = recorder.entries;
  if (entry === undefined) throw new Error('a traced evaluation must record one entry');
  expect(result.evaluationId).toBe(entry.evaluationId);
  const [call] = gateway.calls;
  if (call === undefined) throw new Error('a traced evaluation must call the gateway once');

  // The recorded request is the body the gateway received, not a summary: the state is the
  // supplied text verbatim and the questions are the exact object handed to the gateway.
  expect(entry.request.model).toBe(createExpectedModel());
  expect(entry.request.state).toBe(evidence.text);
  expect(entry.request.questions).toBe(call.questions);
  expect(entry.request.questions).toStrictEqual(call.questions);
  const suppliedImage = evidence.images[0];
  if (suppliedImage === undefined) throw new Error('the evidence factory supplies one image');
  expect(entry.request.images).toStrictEqual([await imageStore.store(suppliedImage)]);

  // The parsed response body is stored unmodified, and the successful line carries no
  // error: the exchange is exactly one of response or error.
  expect('response' in entry).toBe(true);
  expect(entry).not.toHaveProperty('error');
  if (!('response' in entry)) {
    throw new Error('a validated evaluation must record the response it received');
  }
  expect(entry.response).toBe(response);

  expect(entry.schemaVersion).toBe(4);
  expect(entry.at).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  expect(entry.sessionId).toBe(sessionId);
  expect(entry.profileId).toBe(profile.profileId);
  expect(entry.profileVersion).toBe(profile.version);
  expect(entry.outcome).toStrictEqual({ status: 'evaluated' });
  expect(entry.handling).toStrictEqual(
    createEvaluationTraceHandling({ disposition: 'unknown' }),
  );
  expect(entry.elapsedMs).toBeGreaterThanOrEqual(0);
});

test('records the request and the transport failure when the gateway rejects', async () => {
  const profile = createOddEvidenceProfile();
  const evidence = createEvidence();
  const boundaryError = createGatewayBoundaryError();
  const recorder = createEvaluationTraceRecorder();
  const operation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGatewayRejecting(boundaryError),
    questionProfileSource: createQuestionProfileSource(profile),
    tracing: {
      evaluationTrace: recorder,
      imageStore: createTraceImageStore(),
      decisionModel: createExpectedModel(),
    },
  });

  await expect(
    operation.execute(evidence.text, evidence.images, createExpectedModel()),
  ).rejects.toBe(boundaryError);

  // The evaluation still records what it sent, and no response replaced the failure.
  expect(recorder.entries).toHaveLength(1);
  const [entry] = recorder.entries;
  if (entry === undefined) throw new Error('a failed evaluation must record one entry');
  expect(entry.request.state).toBe(evidence.text);
  expect(entry).not.toHaveProperty('response');
  if (!('error' in entry)) throw new Error('a failed evaluation must record its error');
  expect(entry.error).toStrictEqual({
    code: boundaryError.name,
    detail: boundaryError.message,
  });
  expect(entry.outcome).toStrictEqual({ status: 'unavailable', code: 'gateway_error' });
  expect(entry.handling).toStrictEqual(
    createEvaluationTraceHandling({ disposition: 'unavailable' }),
  );
});

test('records the exact response body when the decision response is rejected', async () => {
  const profile = createOddEvidenceProfile();
  const evidence = createEvidence();
  const recorder = createEvaluationTraceRecorder();
  const invalidResponse = createDecisionResponseMissingQuestion();
  const operation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGateway(invalidResponse),
    questionProfileSource: createQuestionProfileSource(profile),
    tracing: {
      evaluationTrace: recorder,
      imageStore: createTraceImageStore(),
      decisionModel: createExpectedModel(),
    },
  });

  const result = await operation.execute(evidence.text, evidence.images, createExpectedModel());

  expect(result.ok).toBe(false);
  if (!result.ok) expect(result.code).toBe('invalid_answers');
  expect(recorder.entries).toHaveLength(1);
  const [entry] = recorder.entries;
  if (entry === undefined || !('response' in entry)) {
    throw new Error('a rejected decision response must record the body it received');
  }
  expect(result.evaluationId).toBe(entry.evaluationId);
  // The endpoint answered, so the line shows exactly what it answered even though the
  // operation refused to deliver it.
  expect(entry.response).toBe(invalidResponse);
  expect(entry.outcome).toStrictEqual({ status: 'unavailable', code: 'invalid_answers' });
  expect(entry.handling).toStrictEqual(
    createEvaluationTraceHandling({ disposition: 'unavailable' }),
  );
});

test('leaves the result unchanged and records nothing when the trace ports are omitted', async () => {
  const profile = createOddEvidenceProfile();
  const evidence = createEvidence();
  const recorder = createEvaluationTraceRecorder();
  const tracedOperation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGateway(),
    questionProfileSource: createQuestionProfileSource(profile),
    tracing: {
      evaluationTrace: recorder,
      imageStore: createTraceImageStore(),
      decisionModel: createExpectedModel(),
    },
  });
  const untracedOperation = new EvaluateOddEvidence({
    decisionGateway: createDecisionGateway(),
    questionProfileSource: createQuestionProfileSource(profile),
  });

  const tracedResult = await tracedOperation.execute(
    evidence.text,
    evidence.images,
    createExpectedModel(),
  );
  expect(recorder.entries).toHaveLength(1);

  const untracedResult = await untracedOperation.execute(
    evidence.text,
    evidence.images,
    createExpectedModel(),
  );

  // Omitting the ports leaves the delivered answers unchanged and records no additional
  // entry: each call still mints its own evaluationId, and the log still holds only the
  // traced evaluation.
  expect(untracedResult.evaluationId).toMatch(EVALUATION_ID_PATTERN);
  expect(tracedResult.evaluationId).toBe(recorder.entries[0]?.evaluationId);
  expect({ ...untracedResult, evaluationId: tracedResult.evaluationId }).toStrictEqual(
    tracedResult,
  );
  expect(recorder.entries).toHaveLength(1);
});
