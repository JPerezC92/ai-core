// Test data and doubles for the portable System 1 advisory edge: captured messages, the
// outgoing request's user message with its inline image, the contract-valid evaluations the
// block cases read, the injected evidence port doubled as a recorder, the connection the plugin
// builds when no port is supplied doubled as a recording factory, the default connection's
// expected binding, a bounded failure, a rejected channel, a channel that never settles, a leak
// canary, the operational event sink doubled as a recorder with one ordered event fixture and
// one content-bearing input, and a harness that registers the adapter's hook listeners through a
// host session double. Every creator returns fresh values; no module-level mutable state is
// shared, no process is spawned and no network or model endpoint is used.

import plugin, {
  createDefaultConnectionOptions,
  ODD_EVIDENCE_TOOL_NAME,
} from '../../index.ts';
import { createPluginEvent } from '../../domain/plugin-event.ts';

import type {
  AdmittedPart,
  CapturedImage,
  CapturedMessage,
  ContextBuildEvent,
  ContextBuildListener,
  ContextMessage,
  ContextMessagePart,
  EvaluateEvidenceOptions,
  MessageIdentity,
  OddAdviserCleanup,
  OddAdviserHostSession,
  OddEvidenceAdvisory,
  OddEvidenceAnswer,
  OddEvidenceEvaluation,
  OddEvidenceEvaluator,
  OddEvidenceEvaluatorConnection,
  OddEvidenceEvaluatorOptions,
  OddEvidenceInput,
  OddEvidenceOutcome,
  OddEvidenceUnavailableCode,
  PromptAdmissionEvent,
  PromptAdmissionListener,
  PromptDraft,
  StdioMcpClientOptions,
} from '../../index.ts';
import type {
  PluginEvent,
  PluginEventSink,
} from '../../domain/plugin-event.ts';

// The adapter's tool identity, taken from its single owner. The wire request is built inside
// `createStdioMcpClient`, so a port-level double never names a tool; the constant stays the
// one place a test can read that identity from instead of restating it (T15).
export const EVIDENCE_TOOL_NAME = ODD_EVIDENCE_TOOL_NAME;

// What a rejected evaluation channel raises. Exported so a test proves the advisory does not
// repeat it without restating the text (T15).
export const TRANSPORT_FAILURE_MESSAGE = 'mcp channel closed';

// The short bound every case states, so a channel that never settles is observed in
// milliseconds rather than in a runner default.
const EVIDENCE_TIMEOUT_MS = 25;

// A manually triggered deadline: no clock or ambient timer is used by operation tests.
export function createControlledDeadline() {
  let pending: (() => void) | undefined;
  let requestedMs: number | undefined;
  let cancellations = 0;
  return {
    schedule(timeoutMs: number, onElapsed: () => void): () => void {
      requestedMs = timeoutMs;
      pending = onElapsed;
      return () => {
        pending = undefined;
        cancellations += 1;
      };
    },
    trigger(): void {
      const callback = pending;
      pending = undefined;
      callback?.();
    },
    get requestedMs() { return requestedMs; },
    get cancellations() { return cancellations; },
    get isPending() { return pending !== undefined; },
  };
}

const evidenceText = 'The latest user request repeats the accepted implementation scope.';
const expectedModel = 'odd-evidence-test-model';
const evaluatedAdvisoryText = 'The supplied evidence does not justify a scope change.';
const unavailableAdvisoryText = 'The evidence evaluation did not answer in this build.';

// Distinctive markers instead of plausible message content: a leak is then an exact match
// rather than a coincidence, and a prefix of a marker still proves a partial leak (S9).
const leakCanaryText = 'LEAK-CANARY-TEXT-4f7c2a91-do-not-copy-into-an-advisory';
const leakCanaryBase64 = 'TEaKCanaryBase64Payload9d41C7f0A2b35E68qWeRtY';
const leakCanaryPrefixLength = 24;

// Fixed event times, so an ordered trace is asserted without reading the clock (T18).
const firstEventAt = '2026-11-08T10:00:00.000Z';
const secondEventAt = '2026-11-08T10:00:01.000Z';
const contentBearingEventAt = '2026-11-08T10:00:02.000Z';

export type RecordedEvaluation = {
  readonly input: OddEvidenceInput;
  readonly options: OddEvidenceEvaluatorOptions;
};

export type RecordingEvaluator = OddEvidenceEvaluator & {
  readonly calls: ReadonlyArray<RecordedEvaluation>;
};

// One inline PNG, already base64 encoded: the shape the adapter captures from a data URL.
export function createInlineImage(): CapturedImage {
  return {
    mimeType: 'image/png',
    base64: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  };
}

export function createInlineImageDataUrl(): string {
  const image = createInlineImage();
  return `data:${image.mimeType};base64,${image.base64}`;
}

// A host-supplied location that carries no inline bytes: a path, a remote URL and a data URL
// whose payload is not base64. None of them may become a captured image (S2).
export function createFileImagePath(): string {
  return '.opencode/plugins/odd-adviser/src/test/helpers/capture-fixture.png';
}

export function createRemoteImageUrl(): string {
  return 'https://example.invalid/capture-fixture.png';
}

export function createNonBase64DataUrl(): string {
  return 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"/>';
}

export function createEvidenceText(): string {
  return evidenceText;
}

// The capture parts of one admitted message: the chat text, one inline base64 image, and
// three locations that must be ignored rather than read.
export function createAdmittedParts(): ReadonlyArray<AdmittedPart> {
  return [
    { text: evidenceText },
    { url: createInlineImageDataUrl() },
    { url: createFileImagePath() },
    { url: createRemoteImageUrl() },
    { url: createNonBase64DataUrl() },
  ];
}

// The host draft the adapter actually receives: one text field and one attachment per file
// location. It is derived from the same parts, so the draft and the capture fixture can never
// disagree about which attachment carries inline bytes (S2).
export function createPromptDraft(): PromptDraft {
  const files: { uri: string }[] = [];
  const texts: string[] = [];
  for (const part of createAdmittedParts()) {
    if (part.text !== undefined) texts.push(part.text);
    if (part.url !== undefined) files.push({ uri: part.url });
  }
  return { text: texts.join('\n'), files };
}

export function createCapturedMessage(
  image: CapturedImage = createInlineImage(),
): CapturedMessage {
  return { text: evidenceText, images: [image] };
}

export function createNonMaximumChoiceAnswer(): OddEvidenceAnswer {
  return createAnswerWithoutConfidence('absent', { present: 0.56, absent: 0.44 });
}

export function createNonMaximumChoiceEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({ user_only_decision: createNonMaximumChoiceAnswer() });
}

export function createExpectedEvidenceInput(
  message: CapturedMessage,
  options: EvaluateEvidenceOptions,
): OddEvidenceInput {
  return { text: message.text, images: message.images, expectedModel: options.expectedModel } as OddEvidenceInput;
}

export function createExpectedEvaluatedAdvisory(
  evaluation: OddEvidenceEvaluation,
  advisory: string,
): OddEvidenceAdvisory {
  return { status: 'evaluated', evaluation, advisory };
}

export function createExpectedUnavailableAdvisory(
  code: OddEvidenceUnavailableCode,
  advisory: string,
): OddEvidenceAdvisory {
  return { status: 'unavailable', code, advisory };
}

// A value the advisory port may report as its evaluated outcome: the profile identity plus
// one validated choice answer per question. The wire payload's own acceptance flag is judged
// where the outside record is mapped, so this domain record carries none (C2, C4).
export function createEvaluation(): OddEvidenceEvaluation {
  return {
    profileId: 'odd-evidence-v1',
    profileVersion: 1,
    answers: {
      scope_changed: createAnswer('present'),
      user_only_decision: createAnswer('absent'),
      visual_evidence: createAnswerWithConfidence('absent', 0.8, { present: 0.2, absent: 0.8 }),
    },
  };
}

// One contract-valid evaluation over exactly the answers a case states, so a block assertion
// reads the payload it was given rather than the shared three-answer fixture (T15).
export function createEvaluationWithAnswers(
  answers: Readonly<Record<string, OddEvidenceAnswer>>,
): OddEvidenceEvaluation {
  return { profileId: 'odd-evidence-v1', profileVersion: 1, answers };
}

// One validated choice answer stating the confidence and the probabilities a case reads, so a
// case about the figure a line reports states that figure instead of inheriting a default.
export function createAnswerWithConfidence(
  choice: string,
  confidence: number,
  probabilities: Readonly<Record<string, number>>,
): OddEvidenceAnswer {
  return { type: 'choice', choice, probabilities, confidence };
}

// One validated choice answer stating probabilities and no confidence, so the figure a line
// reports has to be derived from the largest probability the payload states (R11).
export function createAnswerWithoutConfidence(
  choice: string,
  probabilities: Readonly<Record<string, number>>,
): OddEvidenceAnswer {
  return { type: 'choice', choice, probabilities };
}

// One validated choice answer stating neither a confidence nor a probability, so its line has
// no figure to report and prints the absence rather than an invented number (R11, R12).
export function createAnswerWithoutFigure(choice: string): OddEvidenceAnswer {
  return { type: 'choice', choice, probabilities: {} };
}

// An evaluation whose stated confidences sit on both sides of the weak-signal bound: the weaker
// line carries the mark and the stronger one does not (R11). Each map states exactly the profile's
// two criteria, so the chosen option carries the stated confidence and the other carries its
// complement: the figure the line reports is a probability of the choice, not of a third state.
export function createWeakSignalEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('present', 0.82, {
      present: 0.82,
      absent: 0.18,
    }),
    user_only_decision: createAnswerWithConfidence('absent', 0.41, {
      present: 0.59,
      absent: 0.41,
    }),
  });
}

// An evaluation whose confidences sit exactly on and just below the bound, so a mark at the
// bound itself would be observed rather than assumed away (R11). The maps follow the same
// two-criteria rule: the chosen option takes the stated confidence, the other its complement.
export function createWeakSignalThresholdEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('present', 0.6, {
      present: 0.6,
      absent: 0.4,
    }),
    user_only_decision: createAnswerWithConfidence('absent', 0.59, {
      present: 0.41,
      absent: 0.59,
    }),
  });
}

// An evaluation stating probabilities and no confidence, so each figure has to be derived from
// the largest probability its answer states rather than read from a stated confidence (R11).
// The last answer states a probability larger than the option it chose, so a figure read from the
// chosen option instead of from the largest stated probability is observed rather than assumed
// away. With the retired third state gone, both maps that carried it still state the only source of
// these figures, now as a pair a softmax payload could actually return: `scope_changed` gives the
// retired mass to `absent`, and `user_only_decision` spreads it across both criteria, which keeps
// `absent` the largest at 0.58 and below the weak bound.
export function createDerivedConfidenceEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithoutConfidence('present', {
      present: 0.74,
      absent: 0.26,
    }),
    user_only_decision: createAnswerWithoutConfidence('absent', {
      present: 0.42,
      absent: 0.58,
    }),
    visual_evidence: createAnswerWithoutConfidence('present', {
      present: 0.45,
      absent: 0.55,
    }),
  });
}

// An evaluation stating neither a confidence nor a probability, so the block has one line with
// no figure to report (R11, R12). The option is one the profile emits, so the line is printed from
// a payload the system can still produce.
export function createFigurelessEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    visual_evidence: createAnswerWithoutFigure('absent'),
  });
}

// An evaluation whose only answer states a confidence of `0` beside an empty probability record,
// so the figure its line reports is a stated zero rather than an absence. A falsy test would print
// `n/a` instead, which is what this fixture makes observable (R11, R12). Its option differs from
// the figureless one, so a constant label cannot satisfy both lines.
export function createStatedZeroConfidenceEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    visual_evidence: createAnswerWithConfidence('present', 0, {}),
  });
}

export function createScopeChangedPresentEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('present', 0.82, {
      present: 0.82,
      absent: 0.18,
    }),
  });
}

export function createScopeChangedAbsentEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('absent', 0.98, {
      present: 0.02,
      absent: 0.98,
    }),
  });
}

export function createUserOnlyPresentEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    user_only_decision: createAnswerWithConfidence('present', 0.94, {
      present: 0.94,
      absent: 0.06,
    }),
  });
}

export function createUserOnlyAbsentEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    user_only_decision: createAnswerWithConfidence('absent', 0.94, {
      present: 0.06,
      absent: 0.94,
    }),
  });
}

export function createVisualPresentEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    visual_evidence: createAnswerWithConfidence('present', 0.6, {
      present: 0.6,
      absent: 0.4,
    }),
  });
}

export function createGuidanceWithSubBarVisualEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('absent', 0.98, {
      present: 0.02,
      absent: 0.98,
    }),
    user_only_decision: createAnswerWithConfidence('absent', 0.94, {
      present: 0.06,
      absent: 0.94,
    }),
    visual_evidence: createAnswerWithConfidence('present', 0.48, {
      present: 0.48,
      absent: 0.52,
    }),
  });
}

export function createAbsentScopeWithPresentUserOnlyEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('absent', 0.98, {
      present: 0.02,
      absent: 0.98,
    }),
    user_only_decision: createAnswerWithConfidence('present', 0.8, {
      present: 0.8,
      absent: 0.2,
    }),
  });
}

export function createInterruptPresentBelowBarEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('present', 0.79, {
      present: 0.79,
      absent: 0.21,
    }),
  });
}

export function createGuidanceAbsentBelowBarEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    user_only_decision: createAnswerWithConfidence('absent', 0.59, {
      present: 0.41,
      absent: 0.59,
    }),
  });
}

export function createInterruptPresentAtBarEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('present', 0.8, {
      present: 0.8,
      absent: 0.2,
    }),
  });
}

export function createGuidanceAbsentAtBarEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    user_only_decision: createAnswerWithConfidence('absent', 0.6, {
      present: 0.4,
      absent: 0.6,
    }),
  });
}

export function createVisualEvidenceAbsentAtCertaintyEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    visual_evidence: createAnswerWithConfidence('absent', 1, {
      present: 0,
      absent: 1,
    }),
  });
}

export function createAllBelowBarEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({
    scope_changed: createAnswerWithConfidence('present', 0.79, {
      present: 0.79,
      absent: 0.21,
    }),
    user_only_decision: createAnswerWithConfidence('absent', 0.59, {
      present: 0.41,
      absent: 0.59,
    }),
    visual_evidence: createAnswerWithConfidence('present', 0.48, {
      present: 0.48,
      absent: 0.52,
    }),
  });
}

// An evaluation that answers no question at all: the payload the edge must not deliver, because
// its block would carry no question line and would only report that an answer arrived (R2).
export function createUnansweredEvaluation(): OddEvidenceEvaluation {
  return createEvaluationWithAnswers({});
}

// The caller-supplied bound and expected model one evaluation is given. The model is domain
// data and travels with the request, so the recorded port input carries it.
export function createEvaluateEvidenceOptions(): EvaluateEvidenceOptions {
  return { timeoutMs: EVIDENCE_TIMEOUT_MS, expectedModel };
}

// A port double that records every request it receives and answers with a contract-valid
// evaluation. The `calls` getter returns a snapshot copy, so a later request never mutates an
// earlier assertion's input.
export function createRecordingEvaluator(
  evaluation: OddEvidenceEvaluation = createEvaluation(),
): RecordingEvaluator {
  const calls: RecordedEvaluation[] = [];
  return {
    evaluate: async (
      input: OddEvidenceInput,
      options: OddEvidenceEvaluatorOptions,
    ): Promise<OddEvidenceOutcome> => {
      calls.push({ input, options });
      return { status: 'evaluated', evaluation };
    },
    get calls() {
      return calls.slice();
    },
  };
}

export type RecordedConnection = {
  // The connection double itself, handed to the plugin's own deferred wrapper.
  readonly connection: OddEvidenceEvaluatorConnection;
  // Every evaluation this connection received, in the order it received them.
  readonly evaluations: ReadonlyArray<RecordedEvaluation>;
  // How many times the plugin closed it.
  readonly closes: number;
};

// One connection double: it answers with a contract-valid evaluation, records each request and
// records its own close. Nothing here starts a process, so a case observes the plugin's own
// laziness and teardown without spawning anything (T15, T18).
export function createRecordingConnection(
  evaluation: OddEvidenceEvaluation = createEvaluation(),
): RecordedConnection {
  const evaluations: RecordedEvaluation[] = [];
  let closes = 0;

  return {
    connection: {
      evaluate: async (
        input: OddEvidenceInput,
        options: OddEvidenceEvaluatorOptions,
      ): Promise<OddEvidenceOutcome> => {
        evaluations.push({ input, options });
        return { status: 'evaluated', evaluation };
      },
      close: async (): Promise<void> => {
        closes += 1;
      },
    },
    get evaluations() {
      return evaluations.slice();
    },
    get closes() {
      return closes;
    },
  };
}

export type RecordingConnectionFactory = {
  // The factory the plugin edge composes in place of its own default.
  readonly createConnection: () => OddEvidenceEvaluatorConnection;
  // One entry per connection the plugin created, in creation order.
  readonly connections: ReadonlyArray<RecordedConnection>;
};

// The factory double for the connection the plugin builds when composition supplies no
// evaluator. A connection exists only when the plugin asks for one, so a plugin that was
// composed but never evaluated leaves `connections` empty and a single setup never creates a
// second connection.
export function createRecordingConnectionFactory(): RecordingConnectionFactory {
  const connections: RecordedConnection[] = [];
  return {
    createConnection: () => {
      const created = createRecordingConnection();
      connections.push(created);
      return created.connection;
    },
    get connections() {
      return connections.slice();
    },
  };
}

// The binding the plugin's own default connection must state, stated as test data rather than as
// a second copy of the plugin's own constant: `expectedCommand` is the literal the observed
// `transport_error` session did not use, and `forbiddenCommand` is the host executable the
// session spawned in its place (`process.execPath`), which cannot run this `.ts` entry. `options`
// is the binding the plugin builds, produced by its pure builder, so the expectation observes the
// real default without starting a process (T18).
export type DefaultConnectionExpectation = {
  readonly expectedCommand: string;
  readonly forbiddenCommand: string;
  readonly requiredEnvironmentName: string;
  readonly options: StdioMcpClientOptions;
};

export function createDefaultConnectionExpectation(): DefaultConnectionExpectation {
  return {
    expectedCommand: 'node',
    forbiddenCommand: process.execPath,
    requiredEnvironmentName: 'PATH',
    options: createDefaultConnectionOptions(),
  };
}

// A port double that reports one bounded failure code as a returned value (T3). The outcome
// union admits no payload beside a failure, so the reported code is the only cause a caller
// can observe: no second cause can justify the mapped status, unlike the former transport
// record whose tool-level flag could be read together with a missing payload.
export function createUnavailableEvaluator(
  code: OddEvidenceUnavailableCode = 'tool_error',
): OddEvidenceEvaluator {
  return {
    evaluate: async (): Promise<OddEvidenceOutcome> => ({ status: 'unavailable', code }),
  };
}

// A channel that rejects instead of answering: the rejection carries a distinctive message
// the delivered advisory must not repeat.
export function createThrowingEvaluator(): OddEvidenceEvaluator {
  return {
    evaluate: async (): Promise<OddEvidenceOutcome> => {
      throw new Error(TRANSPORT_FAILURE_MESSAGE);
    },
  };
}

// A channel that never settles, so only the adapter's own bound can finish the attempt.
export function createHangingEvaluator(): OddEvidenceEvaluator {
  return {
    evaluate: () => new Promise<OddEvidenceOutcome>(() => undefined),
  };
}

export type LeakCanary = {
  readonly message: CapturedMessage;
  readonly forbiddenFragments: ReadonlyArray<string>;
};

// Evidence whose every part is identifiable, so an advisory can be checked for a full leak
// and for a partial one. The fragments cover the whole text marker, the whole image payload,
// the first characters of each, and the data-URL scheme an adapter might rebuild from the
// bytes (S9).
export function createLeakCanary(): LeakCanary {
  return {
    message: {
      text: leakCanaryText,
      images: [{ mimeType: 'image/png', base64: leakCanaryBase64 }],
    },
    forbiddenFragments: [
      leakCanaryText,
      leakCanaryText.slice(0, leakCanaryPrefixLength),
      leakCanaryBase64,
      leakCanaryBase64.slice(0, leakCanaryPrefixLength),
      'data:',
    ],
  };
}

export function createEvaluatedAdvisory(
  evaluation: OddEvidenceEvaluation = createEvaluation(),
): OddEvidenceAdvisory {
  return {
    status: 'evaluated',
    evaluation,
    advisory: evaluatedAdvisoryText,
  };
}

export function createUnavailableAdvisory(
  code: OddEvidenceUnavailableCode = 'tool_error',
): OddEvidenceAdvisory {
  return { status: 'unavailable', code, advisory: unavailableAdvisoryText };
}

export function createMessageIdentity(sequence = 1): MessageIdentity {
  return { sessionID: 'ses_odd_adviser_unit', messageID: `msg_${sequence}` };
}

export function createAdmittedMessage(
  identity: MessageIdentity = createMessageIdentity(),
  prompt: PromptDraft = createPromptDraft(),
): PromptAdmissionEvent {
  return { sessionID: identity.sessionID, messageID: identity.messageID, prompt };
}

// The parts of the conversation message the outgoing request carries: the chat text and one
// inline image. The media part exposes the host's lazy `inline()` accessor, whose data URL is
// the only thing an attachment contributes to capture (S2).
export function createContextMessageParts(): ReadonlyArray<ContextMessagePart> {
  return [
    { type: 'text', text: evidenceText },
    {
      type: 'media',
      media: { inline: () => ({ dataUrl: createInlineImageDataUrl() }) },
    },
  ];
}

// The two field names a context message's part array can arrive under: `content`, the
// researched host spelling, and `parts`, the spelling this adapter previously assumed. The
// adapter accepts either, so a test states which one it drives instead of the fixture deciding
// it silently.
export type ContextMessageShape = 'content' | 'parts';

// The user message the outgoing request carries for one host message identity. Its id is the
// same message id the prompt event would carry, so both admission sources describe one
// message rather than two. The array is placed under the requested field and nowhere else, so
// a test proves the adapter reads that spelling rather than one field masking the other.
export function createContextMessage(
  identity: MessageIdentity = createMessageIdentity(),
  parts: ReadonlyArray<ContextMessagePart> = createContextMessageParts(),
  shape: ContextMessageShape = 'parts',
): ContextMessage {
  return shape === 'content'
    ? { id: identity.messageID, role: 'user', content: parts }
    : { id: identity.messageID, role: 'user', parts };
}

// The outgoing request the host builds for one admitted message, with an empty `system` list
// so a build can be observed for exactly what the adapter pushed, and the conversation the
// adapter admits from under the requested part-array spelling. Each call returns a fresh
// object, so two builds of the same message never share what an earlier build appended to.
export function createOutgoingContext(
  identity: MessageIdentity,
  shape: ContextMessageShape = 'parts',
): ContextBuildEvent {
  return {
    sessionID: identity.sessionID,
    agent: 'odd-adviser-test-agent',
    system: [],
    messages: [createContextMessage(identity, createContextMessageParts(), shape)],
    tools: [],
    options: {},
  };
}

// An outgoing request whose conversation carries no user message: the continuation the host
// builds after a tool call looks like this, and the adapter must record that this build found
// no candidate rather than finding none silently.
export function createContextWithoutUserMessage(
  identity: MessageIdentity,
): ContextBuildEvent {
  return {
    sessionID: identity.sessionID,
    agent: 'odd-adviser-test-agent',
    system: [],
    messages: [
      {
        id: identity.messageID,
        role: 'assistant',
        parts: [{ type: 'text', text: 'The previous answer.' }],
      },
    ],
    tools: [],
    options: {},
  };
}

// The two lifecycle events the adapter test appends in order: the context admission that
// reports the input's coverage as counts, then the bounded outcome of the evaluation that
// followed. Neither has a field a supplied value could travel in (S6, S9).
export function createPluginEvents(): readonly [PluginEvent, PluginEvent] {
  const identity = createMessageIdentity();
  return [
    createPluginEvent({
      stage: 'candidate_found',
      at: firstEventAt,
      sessionId: identity.sessionID,
      messageId: identity.messageID,
      imageCount: 1,
      textChars: evidenceText.length,
    }),
    createPluginEvent({
      stage: 'evaluate_finished',
      at: secondEventAt,
      sessionId: identity.sessionID,
      messageId: identity.messageID,
      code: 'timeout',
    }),
  ];
}

export type ContentBearingPluginEvent = {
  readonly event: PluginEvent;
  readonly forbiddenFragments: ReadonlyArray<string>;
};

// An event built the way a careless caller would build one: the supplied chat text and the
// image's base64 payload are attached beside the declared fields. The record keeps only the
// declared fields, so the stored line can repeat none of the fragments (S9).
export function createContentBearingPluginEvent(): ContentBearingPluginEvent {
  const canary = createLeakCanary();
  const image = canary.message.images[0];
  if (image === undefined) throw new Error('the leak canary supplies one image');
  const identity = createMessageIdentity();
  const contentBearing = {
    stage: 'advisory_injected' as const,
    at: contentBearingEventAt,
    sessionId: identity.sessionID,
    messageId: identity.messageID,
    parts: 1,
    text: canary.message.text,
    base64: image.base64,
  };
  return {
    event: createPluginEvent(contentBearing),
    forbiddenFragments: canary.forbiddenFragments,
  };
}

export type RecordingEventSink = PluginEventSink & {
  readonly events: ReadonlyArray<PluginEvent>;
};

// An event sink double that records every lifecycle event in the order the adapter reached it
// and writes nothing: a test observes the stages without touching a developer's file system
// (T18). The `events` getter returns a snapshot copy, so a later event never mutates an earlier
// assertion's sequence.
export function createRecordingEventSink(): RecordingEventSink {
  const events: PluginEvent[] = [];
  return {
    record: async (event: PluginEvent): Promise<void> => {
      events.push(event);
    },
    get events() {
      return events.slice();
    },
  };
}

// A host that rejects hook registration, with a content-free sink and no external effects.
export async function createFailedSetup(): Promise<{
  readonly cleanup: OddAdviserCleanup;
  readonly events: ReadonlyArray<PluginEvent>;
  readonly registrations: ReadonlyArray<string>;
}> {
  const events = createRecordingEventSink();
  const registrations: string[] = [];
  const session: OddAdviserHostSession = {
    hook: async (name: string): Promise<never> => {
      registrations.push(name);
      throw new Error(TRANSPORT_FAILURE_MESSAGE);
    },
  };
  const cleanup = await plugin.setup({ session, events });
  return { cleanup, events: events.events, registrations };
}

export type AdviserHarnessOptions = {
  // The port composition supplies. `null` states that composition supplies none, which is the
  // host's own arrangement: the plugin must then build its default connection through the
  // factory double below. Omitted composes the recording port double every other case uses.
  readonly evaluator?: RecordingEvaluator | null;
  // The stated time limit. `null` states that composition states none, so the documented default
  // must stand. Omitted keeps the short bound the timer-sensitive cases rely on.
  readonly timeoutMs?: number | null;
};

export type AdviserHarness = {
  // The harness's own port double. It is composed unless a case states that composition supplies
  // no evaluator, so `calls` observes exactly the requests the plugin sent to a supplied port.
  readonly evaluator: RecordingEvaluator;
  // The connections the plugin created through the factory double, in creation order: empty when
  // a supplied port was used, one entry per setup otherwise.
  readonly connections: ReadonlyArray<RecordedConnection>;
  readonly events: ReadonlyArray<PluginEvent>;
  readonly cleanup: OddAdviserCleanup;
  admit(message: PromptAdmissionEvent): void;
  build(context: ContextBuildEvent): Promise<void>;
};

// Registers the adapter's hook listeners through a host session double and drives them the way
// the host would, so a test observes the once-per-message reuse without inventing a host or
// reaching into the plugin's private state. The event sink double is injected at composition,
// so the recorded stages are observed and no file is written. The connection factory is always
// the recording double, so the plugin's own default path never reaches a real process (T18).
// Registration is awaited because `session.hook` is promise-based; the returned cleanup is the
// adapter's own.
export async function createAdviserHarness(
  options: AdviserHarnessOptions = {},
): Promise<AdviserHarness> {
  let promptListener: PromptAdmissionListener | undefined;
  let contextListener: ContextBuildListener | undefined;

  // The host-session double: it records the listeners the adapter registers and nothing more.
  // Registration is promise-based, so the harness awaits setup before driving either hook.
  const session: OddAdviserHostSession = {
    hook: async (name: string, listener: unknown): Promise<unknown> => {
      if (name === 'prompt') promptListener = listener as PromptAdmissionListener;
      else if (name === 'context') contextListener = listener as ContextBuildListener;
      return undefined;
    },
  };

  const evaluator = options.evaluator ?? createRecordingEvaluator();
  const timeoutMs =
    options.timeoutMs === undefined ? EVIDENCE_TIMEOUT_MS : options.timeoutMs;
  const connectionFactory = createRecordingConnectionFactory();
  const eventSink = createRecordingEventSink();

  const cleanup = await plugin.setup({
    session,
    ...(options.evaluator === null ? {} : { evaluator }),
    ...(timeoutMs === null ? {} : { timeoutMs }),
    expectedModel,
    createConnection: connectionFactory.createConnection,
    events: eventSink,
  });

  return {
    evaluator,
    get connections() {
      return connectionFactory.connections;
    },
    get events() {
      return eventSink.events;
    },
    cleanup,
    admit(message) {
      promptListener?.(message);
    },
    async build(context) {
      await contextListener?.(context);
    },
  };
}

// One answer over exactly the two criteria the profile states, the chosen option carrying the
// stated confidence and the other the remainder, so the map agrees with the confidence it states.
function createAnswer(choice: string): OddEvidenceAnswer {
  const probabilities: Record<string, number> = {
    present: 0.2,
    absent: 0.2,
  };
  probabilities[choice] = 0.8;
  return { type: 'choice', choice, probabilities, confidence: 0.8 };
}
