// OpenCode adapter for the portable System 1 MCP surface. It captures the text and the
// inline images of an admitted chat message, evaluates them through the injected advisory
// capability, and injects one delimited advisory block into the outgoing context. It owns
// no question profile, no inference, no record and no authorization: delivered advice never
// authorizes, waives a gate, or blocks an action (S7).
//
// The capability contract lives in `domain/advisory.ts`: the typed evidence input, the
// bounded outcome union and the `OddEvidenceEvaluator` port. This module is the edge that
// composes it. `createStdioMcpClient` is the concrete adapter and owns the tool name, the
// wire arguments, the payload parsing and the time bound; `evaluateEvidence` is the core
// function and depends on the port alone. The exported plugin object below is the thin
// wiring that supplies the capture, the once-per-message reuse and the context injection.
//
// Composition: a supplied evaluator always wins, so an embedded caller keeps its own
// capability. The pinned host passes the plugin context alone and composes no evaluator
// (observed), so the edge otherwise builds this repository's own System 1 MCP connection —
// deferred to the first evaluation, one connection per setup, closed by the returned cleanup —
// instead of reporting that no channel exists.
//
// Host binding: `setup` awaits the pinned host's `ctx.session.hook` registrations for the
// outgoing context and, secondarily, for prompt submission. Admission is derived from the
// context event's own conversation messages, because the pinned host fires the prompt hook
// for no ordinary user message (observed); the prompt hook only fills an empty admission
// slot when it does fire. The adapter appends one advisory part to the model request through
// the documented seam. Whether an appended part reaches the main model remains unverified
// (feature Log L24, L25, L41).
//
// Observability: every stage this edge reaches is recorded as one bounded, content-free event,
// so an operator can tell a hook that never fired from a candidate that was never found and
// from an evaluation that failed (S6, S9). The sink is injected at composition; when the host
// composes none, the plugin writes its own JSON Lines trace at a path resolved from this
// module. Recording is best effort and never changes the advisory path.

import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/client';
import { getDefaultEnvironment, StdioClientTransport } from '@modelcontextprotocol/client/stdio';

import { createPluginEvent } from './domain/plugin-event.ts';
import { JsonLinesPluginEvents } from './infrastructure/json-lines-plugin-events.ts';

import type {
  OddEvidenceAnswer,
  OddEvidenceEvaluation,
  OddEvidenceEvaluator,
  OddEvidenceEvaluatorOptions,
  OddEvidenceInput,
  OddEvidenceOutcome,
  OddEvidenceUnavailableCode,
} from './domain/advisory.ts';
import type {
  PluginEventInput,
  PluginEventSink,
  PluginEventStage,
} from './domain/plugin-event.ts';

// The domain vocabulary is re-exported here so this package keeps one import point for its
// callers without owning a second copy of the contract.
export type {
  OddEvidenceAnswer,
  OddEvidenceEvaluation,
  OddEvidenceEvaluator,
  OddEvidenceEvaluatorOptions,
  OddEvidenceImage,
  OddEvidenceInput,
  OddEvidenceOutcome,
  OddEvidenceUnavailableCode,
} from './domain/advisory.ts';

// The operational event vocabulary is re-exported for the same reason: a caller that composes a
// sink names it through this entry, not through a second copy of the contract.
export type {
  PluginEvent,
  PluginEventCode,
  PluginEventInput,
  PluginEventSink,
  PluginEventStage,
} from './domain/plugin-event.ts';

// The teardown a skipped or failed setup returns, so the host always receives a callable
// cleanup rather than no cleanup at all.
const NOOP_CLEANUP: OddAdviserCleanup = async () => undefined;

// The bound one evaluation is given, beside the per-evaluation domain data. The plugin edge
// states the documented default when the host states no bound; `expectedModel` travels with the
// request, not with the transport configuration the adapter is built from.
export type EvaluateEvidenceOptions = OddEvidenceEvaluatorOptions & {
  readonly expectedModel?: string;
};

export type OddEvidenceAdvisory =
  | {
      readonly status: 'evaluated';
      readonly evaluation: OddEvidenceEvaluation;
      readonly advisory: string;
    }
  | {
      readonly status: 'unavailable';
      readonly code: OddEvidenceUnavailableCode;
      readonly advisory: string;
    };

// Fixed sentence per code. No supplied text, image bytes, caller error message or payload
// value can reach these strings (S9).
const unavailableAdvisories: Readonly<Record<OddEvidenceUnavailableCode, string>> = {
  not_implemented: 'The System 1 evidence evaluation is not implemented in this build.',
  caller_unavailable: 'No System 1 evidence evaluation channel is configured for this session.',
  timeout: 'The System 1 evidence evaluation did not answer within its configured time limit.',
  transport_error: 'The System 1 evidence evaluation channel failed before an answer arrived.',
  tool_error: 'The System 1 evidence evaluation reported an error for this request.',
  malformed_payload: 'The System 1 evidence evaluation answered outside its advertised contract.',
  rejected: 'The System 1 evidence evaluation rejected the supplied evidence.',
};

function toUnavailableAdvisory(code: OddEvidenceUnavailableCode): OddEvidenceAdvisory {
  return { status: 'unavailable', code, advisory: unavailableAdvisories[code] };
}

// The one sentence an evaluated advisory record carries beside its evaluation. It reports only
// that a contract-valid evaluation arrived: it repeats no supplied value and claims no accuracy,
// citation or authority (S3, S9). The choices themselves travel in the block's own question
// lines, which are derived from the payload rather than from this sentence.
const evaluatedAdvisory =
  'The System 1 evidence evaluation returned a contract-valid answer for this message.';

export const ADVISORY_BLOCK_START = '=== SYSTEM 1 ADVISER - ADVISORY ONLY ===';
export const ADVISORY_BLOCK_END = '=== END SYSTEM 1 ADVISER ===';

// The figure below which a line is marked. A low figure marks the same line; it never replaces
// the choice with a non-answer and never adds a third state (R11).
const WEAK_SIGNAL_CONFIDENCE = 0.6;

// The mark a line below that bound carries. It repeats no supplied value and states no verdict
// of its own, so a reader still sees which option the evaluation chose (R11, R12).
const WEAK_SIGNAL_MARKER = ' ⚠ weak signal';

// The largest probability an answer states, or `null` when it states none. The reduction starts
// from nothing rather than from zero, so an empty probability record is not read as a
// confidence of zero (R11).
function maximumProbability(
  probabilities: Readonly<Record<string, number>>,
): number | null {
  let maximum: number | null = null;
  for (const score of Object.values(probabilities)) {
    if (maximum === null || score > maximum) maximum = score;
  }
  return maximum;
}

// The figure one answered question's line reports: the confidence the answer states, otherwise
// the largest probability it states. `null` means the payload carries neither, and the line then
// prints `n/a` rather than an invented number (R11, R12).
function reportedConfidence(answer: OddEvidenceAnswer): number | null {
  return answer.confidence ?? maximumProbability(answer.probabilities);
}

// One question's line: the question it answers, the option the payload chose and the figure that
// choice carries, so a reader sees what was chosen rather than only that an answer arrived
// (R1, R2). A figure below the weak-signal bound is marked on the same line (R11).
function formatQuestionLine(questionId: string, answer: OddEvidenceAnswer): string {
  const confidence = reportedConfidence(answer);
  const figure = confidence === null ? 'n/a' : confidence.toFixed(2);
  const marker =
    confidence !== null && confidence < WEAK_SIGNAL_CONFIDENCE ? WEAK_SIGNAL_MARKER : '';
  return `${questionId} → ${answer.choice} (${figure})${marker}`;
}

// Every line a block adds for an evaluation: one per answered question, in the order the payload
// states them, so the block carries the choices rather than a summary of them (R2).
function formatQuestionLines(evaluation: OddEvidenceEvaluation): ReadonlyArray<string> {
  return Object.entries(evaluation.answers).map(([questionId, answer]) =>
    formatQuestionLine(questionId, answer),
  );
}

// The one block the context hook appends. The authority boundary travels with every block, so a
// reader of the outgoing context cannot mistake the advice for an authorization. An evaluated
// block names each answered question with the option the payload chose and the figure that
// choice carries (R1, R2, R11); an unavailable block keeps its single fixed sentence and gains
// no question line, because no answer exists to report. Every line comes from the payload or
// from the fixed sentences above, so no supplied message text can reach the block (R12, S9).
export function formatAdvisoryBlock(advisory: OddEvidenceAdvisory): string {
  return [
    ADVISORY_BLOCK_START,
    advisory.advisory,
    ...(advisory.status === 'evaluated' ? formatQuestionLines(advisory.evaluation) : []),
    'Advisory only: it never authorizes, waives a gate, or blocks an action.',
    ADVISORY_BLOCK_END,
  ].join('\n');
}

// One capture part, narrowed to the two fields `captureMessage` reads. The host draft and the
// context event's message parts are both mapped to these parts once, at the edge, so capture
// stays free of the host wire shape (C4). A part carrying neither field is ignored rather than
// modelled.
export type AdmittedPart = {
  readonly text?: string;
  readonly url?: string;
};

export type CapturedImage = {
  readonly mimeType: string;
  readonly base64: string;
};

export type CapturedMessage = {
  readonly text: string;
  readonly images: ReadonlyArray<CapturedImage>;
};

// Only an inline base64 data URL is captured. A path, a remote URL or a non-base64 data URL
// is ignored, so no project file is created or read to evaluate an attached image (S2).
const INLINE_BASE64_DATA_URL = /^data:([^;,]+);base64,([A-Za-z0-9+/=]+)$/;

export function captureMessage(parts: ReadonlyArray<AdmittedPart>): CapturedMessage {
  const text = parts
    .map((part) => (part.text === undefined ? '' : part.text.trim()))
    .filter((part) => part.length > 0)
    .join('\n');

  const images: CapturedImage[] = [];
  for (const part of parts) {
    const match = part.url === undefined ? null : INLINE_BASE64_DATA_URL.exec(part.url);
    if (match === null) continue;
    const [, mimeType, base64] = match;
    if (mimeType === undefined || base64 === undefined) continue;
    images.push({ mimeType, base64 });
  }

  return { text, images };
}

// The tool this adapter calls. The name is mirrored from the MCP edge's single owner so the
// adapter carries no copy of the question profile or the evaluation rules, and no other part
// of this package names a tool.
export const ODD_EVIDENCE_TOOL_NAME = 'evaluate_odd_evidence';

// The subset of the tool result the adapter reads. `isError` is the protocol's tool-level
// failure flag; `structuredContent` is the payload the tool advertised. Both stay inside
// this module: nothing else in the package receives a transport record.
type McpToolResult = {
  readonly isError?: boolean | undefined;
  readonly structuredContent?: unknown;
};

// The one mapping step from the domain input to the tool's advertised arguments (C4). The
// fields are copied one by one, so the transport never shares a captured object and no path
// or URL can appear in the request. The open record is the transport's shape, not the
// domain's: the closed input contract stays in `domain/advisory.ts`.
function toToolArguments(input: OddEvidenceInput): Record<string, unknown> {
  return {
    text: input.text,
    images: input.images.map((image) => ({
      mimeType: image.mimeType,
      base64: image.base64,
    })),
    ...(input.expectedModel === undefined ? {} : { expectedModel: input.expectedModel }),
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function toProbabilities(value: unknown): Record<string, number> | null {
  if (!isRecord(value)) return null;
  const probabilities: Record<string, number> = {};
  for (const [state, score] of Object.entries(value)) {
    if (typeof score !== 'number' || !Number.isFinite(score)) return null;
    probabilities[state] = score;
  }
  return probabilities;
}

function toAnswer(value: unknown): OddEvidenceAnswer | null {
  if (!isRecord(value)) return null;
  if (value.type !== 'choice') return null;
  if (typeof value.choice !== 'string' || value.choice.length === 0) return null;
  const probabilities = toProbabilities(value.probabilities);
  if (probabilities === null) return null;
  const confidence = value.confidence;
  if (confidence === undefined) {
    return { type: 'choice', choice: value.choice, probabilities };
  }
  if (typeof confidence !== 'number' || !Number.isFinite(confidence)) return null;
  return { type: 'choice', choice: value.choice, probabilities, confidence };
}

function toAnswers(value: unknown): Record<string, OddEvidenceAnswer> | null {
  if (!isRecord(value)) return null;
  const answers: Record<string, OddEvidenceAnswer> = {};
  for (const [questionId, candidate] of Object.entries(value)) {
    const answer = toAnswer(candidate);
    if (answer === null) return null;
    answers[questionId] = answer;
  }
  return answers;
}

// An answered-question record that states no question is not a contract-valid evaluation: the
// block built from it would carry no question line and would only report that an answer arrived,
// which is the receipt R2 rejects. The domain type admits an empty record, so both places that
// form an evaluated outcome judge it through this one predicate (R2).
function answersNoQuestion(
  answers: Readonly<Record<string, OddEvidenceAnswer>>,
): boolean {
  return Object.keys(answers).length === 0;
}

function toEvaluation(
  profileId: unknown,
  profileVersion: unknown,
  answers: unknown,
): OddEvidenceEvaluation | null {
  if (typeof profileId !== 'string' || profileId.length === 0) return null;
  if (
    typeof profileVersion !== 'number' ||
    !Number.isInteger(profileVersion) ||
    profileVersion <= 0
  ) {
    return null;
  }
  const validAnswers = toAnswers(answers);
  return validAnswers === null || answersNoQuestion(validAnswers)
    ? null
    : { profileId, profileVersion, answers: validAnswers };
}

function toUnavailableOutcome(code: OddEvidenceUnavailableCode): OddEvidenceOutcome {
  return { status: 'unavailable', code };
}

// The single mapping step from the external answer to the domain outcome (C4). A tool-level
// failure, a payload outside the advertised union and the tool's own rejection branch all
// become bounded codes; no supplied text, image bytes or rejection reason is carried over
// (S9). The payload's own `ok` flag is judged here, once: the domain evaluation carries no
// duplicate acceptance flag (C2, C4). Validation below covers every answer the client
// returns; a failure the client raises before returning an answer is a boundary exception
// and is reported as `transport_error`.
function toOutcome(result: McpToolResult): OddEvidenceOutcome {
  if (result.isError === true) return toUnavailableOutcome('tool_error');
  const payload = result.structuredContent;
  if (!isRecord(payload)) return toUnavailableOutcome('malformed_payload');
  if (payload.ok === false) return toUnavailableOutcome('rejected');
  if (payload.ok !== true) return toUnavailableOutcome('malformed_payload');
  const evaluation = toEvaluation(payload.profileId, payload.profileVersion, payload.answers);
  return evaluation === null
    ? toUnavailableOutcome('malformed_payload')
    : { status: 'evaluated', evaluation };
}

// The outcome of one bounded attempt: an answer, a rejection, or the caller's stated time
// limit elapsing. The rejection value is never retained, so no transport message can reach a
// caller or an advisory (S9). A timeout does not prove the request was cancelled; the
// attempt simply stops being awaited.
type BoundedAttempt<T> =
  | { readonly kind: 'answered'; readonly result: T }
  | { readonly kind: 'failed' }
  | { readonly kind: 'elapsed' };

async function boundedAttempt<T>(
  work: () => Promise<T>,
  timeoutMs: number,
): Promise<BoundedAttempt<T>> {
  const attempt: Promise<BoundedAttempt<T>> = work().then(
    (result) => ({ kind: 'answered' as const, result }),
    () => ({ kind: 'failed' as const }),
  );

  let timer: ReturnType<typeof setTimeout> | undefined;
  const elapsed = new Promise<BoundedAttempt<T>>((resolve) => {
    timer = setTimeout(() => resolve({ kind: 'elapsed' }), timeoutMs);
  });

  try {
    return await Promise.race([attempt, elapsed]);
  } finally {
    if (timer !== undefined) clearTimeout(timer);
  }
}

export type StdioMcpClientOptions = {
  readonly command: string;
  readonly args: ReadonlyArray<string>;
  readonly cwd: string;
  readonly env?: Readonly<Record<string, string>>;
  // The tool this adapter calls. It defaults to the name mirrored from the MCP edge, so an
  // override is stated at composition rather than assumed here.
  readonly toolName?: string;
};

export type OddEvidenceEvaluatorConnection = OddEvidenceEvaluator & {
  readonly close: () => Promise<void>;
};

// Concrete binding of the advisory port to the official stdio client: one child process,
// connected on first use. Composition supplies the exact executable, arguments, working
// directory and environment, so no path, interpreter or process default is guessed here.
// `close()` closes the client, which closes its transport and terminates the child.
export function createStdioMcpClient(
  options: StdioMcpClientOptions,
): OddEvidenceEvaluatorConnection {
  const toolName = options.toolName ?? ODD_EVIDENCE_TOOL_NAME;
  let connection: Promise<Client> | undefined;

  async function connect(): Promise<Client> {
    const client = new Client({ name: 'odd-adviser', version: '0.1.0' });
    const transport = new StdioClientTransport({
      command: options.command,
      args: [...options.args],
      cwd: options.cwd,
      ...(options.env === undefined ? {} : { env: { ...options.env } }),
    });
    await client.connect(transport);
    return client;
  }

  return {
    // One bounded attempt covers the connection and the single tool call, so the stated
    // limit bounds the whole evaluation rather than only the wire request. A rejected
    // connection stays cached, so later attempts report the same bounded failure until the
    // adapter is closed and composed again.
    evaluate: async (input, evaluationOptions) => {
      const attempt = await boundedAttempt<McpToolResult>(async () => {
        connection ??= connect();
        const client = await connection;
        return client.callTool(
          { name: toolName, arguments: toToolArguments(input) },
          { timeout: evaluationOptions.timeoutMs },
        );
      }, evaluationOptions.timeoutMs);

      if (attempt.kind === 'answered') return toOutcome(attempt.result);
      if (attempt.kind === 'failed') return toUnavailableOutcome('transport_error');
      // The remaining attempt kind is the elapsed bound.
      return toUnavailableOutcome('timeout');
    },
    close: async () => {
      const pending = connection;
      connection = undefined;
      if (pending === undefined) return;
      // A failed connection has nothing to close; the call that opened it reports the
      // failure, so the rejection is not re-raised here.
      await pending.then(
        (client) => client.close(),
        () => undefined,
      );
    },
  };
}

// A connection that must not start a process until it is first used. The wrapper creates the
// concrete client on the first evaluation and keeps it, so one setup owns exactly one
// connection however many messages it evaluates; a plugin that was composed but never evaluated
// therefore reaches no process. `close()` releases whatever connection exists and never creates
// one, so teardown of an unused plugin spawns nothing.
function createDeferredConnection(
  createConnection: () => OddEvidenceEvaluatorConnection,
): OddEvidenceEvaluatorConnection {
  let connection: OddEvidenceEvaluatorConnection | undefined;

  return {
    evaluate: async (input, evaluationOptions) => {
      if (connection === undefined) connection = createConnection();
      return connection.evaluate(input, evaluationOptions);
    },
    close: async () => {
      const current = connection;
      connection = undefined;
      if (current === undefined) return;
      await current.close().catch(() => undefined);
    },
  };
}

// One evaluation attempt: exactly one request to the injected capability carrying the
// captured text, the inline images and the caller's expected model. The request is mapped
// once and the port is bounded by the caller's stated time limit, so a returned failure code,
// a rejection and an elapsed bound each become a fixed advisory sentence; an evaluation that
// answers no question becomes the bounded malformed class rather than a receipt. No supplied
// text, image bytes, transport message or payload value can reach the returned advisory (S9).
export async function evaluateEvidence(
  message: CapturedMessage,
  evaluator: OddEvidenceEvaluator,
  options: EvaluateEvidenceOptions,
): Promise<OddEvidenceAdvisory> {
  const input: OddEvidenceInput = {
    text: message.text,
    images: message.images,
    ...(options.expectedModel === undefined
      ? {}
      : { expectedModel: options.expectedModel }),
  };

  const attempt = await boundedAttempt(
    () => evaluator.evaluate(input, { timeoutMs: options.timeoutMs }),
    options.timeoutMs,
  );

  if (attempt.kind === 'answered') {
    const outcome = attempt.result;
    if (outcome.status !== 'evaluated') return toUnavailableAdvisory(outcome.code);
    // An evaluated outcome whose answers record is empty would deliver a receipt with no question
    // line, so it is reported as the bounded malformed class instead of being delivered (R2).
    if (answersNoQuestion(outcome.evaluation.answers)) {
      return toUnavailableAdvisory('malformed_payload');
    }
    return {
      status: 'evaluated',
      evaluation: outcome.evaluation,
      advisory: evaluatedAdvisory,
    };
  }

  // A rejection at the port and the elapsed bound each map to their bounded code; the
  // rejection value itself is discarded, so no transport message is retained (S9).
  return toUnavailableAdvisory(attempt.kind === 'failed' ? 'transport_error' : 'timeout');
}

export type MessageIdentity = {
  readonly sessionID: string;
  readonly messageID: string;
};

// The one cache key for a message identity. The pair is joined with a separator that neither
// half can contain, so two identities never collide onto one evaluation.
function identityKey(identity: MessageIdentity): string {
  return `${identity.sessionID}\u0000${identity.messageID}`;
}

// One evaluation per admitted message, reused by every later context build: the cache key
// is the message identity, so a tool continuation reuses the earlier attempt instead of
// asking the capability again (S5). Exactly-once behaviour across a reload is not claimed.
function evaluateOnce(
  identity: MessageIdentity,
  message: CapturedMessage,
  configuration: AdviserConfiguration,
  evaluations: Map<string, Promise<OddEvidenceAdvisory>>,
): Promise<OddEvidenceAdvisory> {
  const key = identityKey(identity);
  const cached = evaluations.get(key);
  if (cached !== undefined) return cached;

  const pending = evaluateEvidence(
    message,
    configuration.evaluator,
    configuration.options,
  );
  evaluations.set(key, pending);
  return pending;
}

// The host events this adapter consumes, narrowed to the fields it reads. The names are the
// pinned host API's: identity on the admission event, the mutable draft under `prompt`, and
// the outgoing request's `system` parts plus its conversation `messages`. No field is invented
// here to stand in for a hook the host does not expose.
export type PromptDraft = {
  readonly text?: string | undefined;
  readonly files?: ReadonlyArray<PromptFile> | undefined;
};

// One entry of the draft's `files`. Only an inline base64 data URL in `uri` is captured; a
// file path or a remote URL is ignored rather than opened (S2).
export type PromptFile = {
  readonly uri: string;
  readonly name?: string | undefined;
};

export type PromptAdmissionEvent = {
  readonly sessionID: string;
  readonly messageID: string;
  readonly prompt: PromptDraft;
};

// One system part of the outgoing model request. The adapter appends a single text part,
// reads the conversation beside it only to admit the user's message, and never rewrites
// either the system parts it did not add or the conversation itself.
export type ContextSystemPart = {
  readonly type: 'text';
  readonly text: string;
};

// The outgoing request. The host builds it for every model call, including tool
// continuations, so the same admitted message is seen repeatedly within one turn (S5). The
// conversation it carries is `unknown` on purpose: the adapter narrows it defensively, so an
// unexpected host shape yields no admission rather than an exception.
export type ContextBuildEvent = {
  readonly sessionID: string;
  readonly agent?: string | undefined;
  readonly system: ContextSystemPart[];
  readonly messages?: unknown;
  readonly tools?: unknown;
  readonly options?: unknown;
};

// One conversation message as the context event carries it: the host message identity the
// admission is cached by, the role that decides whether it is a user message, and its part
// array. The researched host shape carries that array under `content` while this adapter read
// `parts`, so both spellings are named and exactly one is read. Only the fields the adapter
// reads are named; nothing here restates the host's full model.
export type ContextMessage = {
  readonly id: string;
  readonly role: string;
  readonly content?: ReadonlyArray<ContextMessagePart> | undefined;
  readonly parts?: ReadonlyArray<ContextMessagePart> | undefined;
};

// One part of a context message. A text part contributes its text and a media part its inline
// data URL; every other part is ignored rather than modelled (S2).
export type ContextMessagePart = {
  readonly type: string;
  readonly text?: string | undefined;
  readonly media?: ContextMessageMedia | undefined;
};

// A media part's lazy inline accessor. The host resolves a path or a remote URL to no data
// URL, and only an inline base64 data URL becomes a captured image (S2).
export type ContextMessageMedia = {
  readonly inline?: (() => ContextInlinedMedia | undefined) | undefined;
};

export type ContextInlinedMedia = {
  readonly dataUrl?: string | undefined;
};

export type PromptAdmissionListener = (event: PromptAdmissionEvent) => void;
export type ContextBuildListener = (event: ContextBuildEvent) => Promise<void>;

// The two hook registrations this adapter uses. `session.hook` is overloaded per hook name, so
// a listener receives the event belonging to the hook it was registered for.
export type OddAdviserHostSession = {
  readonly hook: {
    (name: 'prompt', listener: PromptAdmissionListener): Promise<unknown>;
    (name: 'context', listener: ContextBuildListener): Promise<unknown>;
  };
};

export type OddAdviserCleanup = () => Promise<void>;

export type OddAdviserSetupContext = {
  readonly session: OddAdviserHostSession;
  // The advisory capability. A supplied evaluator always wins; when composition supplies none,
  // the edge builds its own stdio connection on the first evaluation.
  readonly evaluator?: OddEvidenceEvaluator;
  // The evaluation bound. When composition states none, the documented default stands.
  readonly timeoutMs?: number;
  readonly expectedModel?: string;
  // The connection the edge builds when it has to supply its own evaluator. Composition may
  // supply its own factory; a test supplies a recording factory instead of spawning a process.
  // It is called once, on the first evaluation, and the created connection is closed by the
  // returned cleanup.
  readonly createConnection?: () => OddEvidenceEvaluatorConnection;
  // The operational trace this edge records into. Composition may supply its own sink; when it
  // does not, the plugin writes the JSON Lines trace composed below.
  readonly events?: PluginEventSink;
};

export type OddAdviserPlugin = {
  readonly id: string;
  setup(context: OddAdviserSetupContext): Promise<OddAdviserCleanup>;
};

type AdviserConfiguration = {
  readonly evaluator: OddEvidenceEvaluator;
  readonly options: EvaluateEvidenceOptions;
};

type AdmittedMessage = {
  readonly identity: MessageIdentity;
  readonly message: CapturedMessage;
};

// Which hook admitted the message currently in the slot. The context event carries the live
// conversation and is the only source the host fires for an ordinary message; the prompt
// event is a secondary source that never replaces a context-admitted identity.
type AdmissionSource = 'prompt' | 'context';

// The MCP entry this edge starts when composition supplies no evaluator, resolved from this
// module's location rather than from the working directory: `src/index.ts` is four directories
// below the repository root, which owns `mcp-servers/system-one/`.
const DEFAULT_CONNECTION_ENTRY_PATH =
  '../../../../mcp-servers/system-one/src/mcp/stdio.ts';

// The child process's working directory: that same repository root, so a relative path the
// server resolves lands where the repository expects it rather than wherever the host started.
const DEFAULT_CONNECTION_WORKING_DIRECTORY = '../../../../';

// The documented evaluation bound, used when composition states none. It matches the bound the
// MCP server documents for itself, so the outer and inner limits do not disagree.
const DEFAULT_EVIDENCE_TIMEOUT_MS = 15_000;

// The environment namespace this repository's MCP server reads its own configuration from
// (`SYSTEM_ONE_ENDPOINT`, `SYSTEM_ONE_MODEL`, ...). The transport otherwise spawns the child
// with a filtered safe environment, so a host-level setting in this namespace would be dropped
// and the child would silently fall back to its own defaults.
const SYSTEM_ONE_ENVIRONMENT_PREFIX = 'SYSTEM_ONE_';

function readSystemOneEnvironment(): Readonly<Record<string, string>> {
  const environment: Record<string, string> = {};
  for (const [name, value] of Object.entries(process.env)) {
    if (!name.startsWith(SYSTEM_ONE_ENVIRONMENT_PREFIX) || value === undefined) continue;
    environment[name] = value;
  }
  return environment;
}

// The inherited variable that makes a bare executable name resolvable. The transport spawns the
// child with its own filtered safe environment rather than the host's, so the inherited `PATH`
// has to be carried over explicitly; without it a child named by a bare command cannot be found
// and never starts.
const EXECUTABLE_RESOLUTION_ENVIRONMENT_NAME = 'PATH';

// The inherited resolution environment, copied under its canonical name. An environment variable
// name is case-insensitive on Windows, where the inherited spelling is usually `Path`, so
// publishing the canonical `PATH` name keeps one entry in the child environment instead of two
// spellings of the same variable.
function readExecutableResolutionEnvironment(): Readonly<Record<string, string>> {
  const value = process.env[EXECUTABLE_RESOLUTION_ENVIRONMENT_NAME];
  return value === undefined ? {} : { [EXECUTABLE_RESOLUTION_ENVIRONMENT_NAME]: value };
}

// The interpreter the default connection names. The host runs its own JavaScript runtime —
// OpenCode's server traces report `B:/~BUN/root/chunk-*.js` — so `process.execPath` there is the
// host's own executable, not an interpreter started for this `.ts` entry, and a real session
// recorded `evaluate_finished` with `transport_error` before any answer arrived. The literal
// `node` names the interpreter explicitly and is resolved from the inherited PATH.
const DEFAULT_CONNECTION_COMMAND = 'node';

// The binding this edge composes for itself: the interpreter, the entry module, the working
// directory and the environment the child needs. The entry and working directory are resolved
// from this module's location, so no installed copy and no host working directory is assumed. It
// is a pure builder, exported so a test can pin the binding without starting a process.
export function createDefaultConnectionOptions(): StdioMcpClientOptions {
  return {
    command: DEFAULT_CONNECTION_COMMAND,
    args: [fileURLToPath(new URL(DEFAULT_CONNECTION_ENTRY_PATH, import.meta.url))],
    cwd: fileURLToPath(
      new URL(DEFAULT_CONNECTION_WORKING_DIRECTORY, import.meta.url),
    ),
    env: {
      ...getDefaultEnvironment(),
      ...readExecutableResolutionEnvironment(),
      ...readSystemOneEnvironment(),
    },
  };
}

// The connection this edge composes when the host supplies no evaluator: this repository's own
// System 1 MCP server over stdio, started by the `node` executable the binding above names.
// Nothing is spawned here: the caller wraps this factory in `createDeferredConnection`, so the
// process starts on the first evaluation.
function createDefaultConnection(): OddEvidenceEvaluatorConnection {
  return createStdioMcpClient(createDefaultConnectionOptions());
}

// Composition resolution. A supplied evaluator always wins, so an embedded caller keeps its own
// capability, and an unusable stated time limit still degrades to the bounded status rather than
// being silently replaced. A missing evaluator is not a reason to report that no channel exists:
// the host composes the plugin context alone (observed), so the edge builds its own deferred
// connection instead. The connection is created on the first evaluation, once per setup, and the
// teardown closes it.
function resolveConfiguration(
  context: OddAdviserSetupContext,
): AdviserConfiguration | null {
  const timeoutMs = context.timeoutMs ?? DEFAULT_EVIDENCE_TIMEOUT_MS;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) return null;

  const evaluator =
    context.evaluator ??
    createDeferredConnection(context.createConnection ?? createDefaultConnection);

  return {
    evaluator,
    options: {
      timeoutMs,
      ...(context.expectedModel === undefined
        ? {}
        : { expectedModel: context.expectedModel }),
    },
  };
}

// The single mapping step from the host draft to the parts `captureMessage` reads (C4). The
// draft's text contributes one text part and each attachment contributes its `uri` as a
// location, so capture decides what the attachment is and no path is ever opened (S2).
function toAdmittedParts(draft: PromptDraft): ReadonlyArray<AdmittedPart> {
  const parts: AdmittedPart[] = [];
  if (draft.text !== undefined) parts.push({ text: draft.text });
  for (const file of draft.files ?? []) parts.push({ url: file.uri });
  return parts;
}

// The mapping step from one context message's parts to the parts `captureMessage` reads (C4).
// A text part contributes its text and a media part contributes only the data URL its inline
// accessor returns; a part whose accessor throws, a non-inline location and every other part
// contribute nothing, so no path or remote URL is ever opened (S2).
function toContextParts(parts: unknown): ReadonlyArray<AdmittedPart> {
  if (!Array.isArray(parts)) return [];

  const admitted: AdmittedPart[] = [];
  for (const part of parts) {
    if (!isRecord(part)) continue;
    if (part.type === 'text' && typeof part.text === 'string') {
      admitted.push({ text: part.text });
      continue;
    }
    if (part.type !== 'media') continue;

    const media = part.media;
    if (!isRecord(media)) continue;
    const inline = media.inline;
    if (typeof inline !== 'function') continue;

    try {
      const inlined: unknown = (inline as () => unknown).call(media);
      if (!isRecord(inlined)) continue;
      const dataUrl = inlined.dataUrl;
      if (typeof dataUrl === 'string') admitted.push({ url: dataUrl });
    } catch {
      // An attachment that cannot be inlined contributes nothing; no file is read (S2).
    }
  }
  return admitted;
}

// The single selection step for one context message's part array (C4). The researched host
// shape carries the array under `content` while this adapter read `parts`; both spellings are
// accepted and `content` wins when both are arrays, so the choice is stated once instead of
// being left to property order or to the host's version.
function selectContextParts(message: Record<string, unknown>): unknown {
  const content = message.content;
  if (Array.isArray(content)) return content;

  const parts = message.parts;
  if (Array.isArray(parts)) return parts;

  return [];
}

// The newest user message of the outgoing request, mapped to one admission. The context event
// is the admission source the host actually fires for an ordinary message, so a message the
// prompt hook never saw is still captured and evaluated. Every access is guarded: an
// unexpected entry, a missing identity, a message carrying its part array under neither
// accepted field, or a message carrying neither text nor an inline image yields no candidate
// rather than an exception.
function toContextAdmission(event: ContextBuildEvent): AdmittedMessage | null {
  const entries = event.messages;
  if (!Array.isArray(entries)) return null;

  let newest: Record<string, unknown> | null = null;
  for (const entry of entries) {
    if (!isRecord(entry)) continue;
    if (entry.role !== 'user') continue;
    newest = entry;
  }
  if (newest === null) return null;

  const messageID = newest.id;
  if (typeof messageID !== 'string' || messageID.length === 0) return null;

  const message = captureMessage(toContextParts(selectContextParts(newest)));
  if (message.text.length === 0 && message.images.length === 0) return null;

  return { identity: { sessionID: event.sessionID, messageID }, message };
}

// A capability may own a child process — a supplied evaluator or the edge's own default
// connection. Only one that exposes `close` is closed at teardown; a plain port double has
// nothing to release.
function isCloseableEvaluator(
  evaluator: OddEvidenceEvaluator | undefined,
): evaluator is OddEvidenceEvaluatorConnection {
  if (evaluator === undefined) return false;
  const candidate = evaluator as Partial<OddEvidenceEvaluatorConnection>;
  return typeof candidate.close === 'function';
}

// Fail open: a failure inside the capability or inside this edge becomes the bounded
// unavailable advisory instead of an exception, so advice never blocks a message (S7). The
// port contract already maps expected failures to values; a programming or boundary exception
// is reported as the transport class, carrying none of its message (S9).
async function evaluateWithoutThrowing(
  admission: AdmittedMessage,
  configuration: AdviserConfiguration | null,
  evaluations: Map<string, Promise<OddEvidenceAdvisory>>,
): Promise<OddEvidenceAdvisory> {
  if (configuration === null) return toUnavailableAdvisory('caller_unavailable');
  try {
    return await evaluateOnce(
      admission.identity,
      admission.message,
      configuration,
      evaluations,
    );
  } catch {
    return toUnavailableAdvisory('transport_error');
  }
}

// The environment variable that overrides where the plugin's own lifecycle trace is written. A
// composition that injects its own sink ignores it.
const PLUGIN_EVENT_PATH_VARIABLE = 'ODD_ADVISER_EVENT_PATH';

// The documented default, resolved from this module's location rather than from the working
// directory: `src/index.ts` is four directories below the repository root, whose gitignored
// `output/` directory already holds the MCP's own `events.jsonl`. The plugin's stage trace is a
// separate file because it answers a different question — whether a stage ran at all.
const DEFAULT_PLUGIN_EVENT_RELATIVE_PATH = '../../../../output/system1/plugin.jsonl';

// An unset or blank override is not a usable configuration, so the documented default stands.
function resolvePluginEventPath(): string {
  const configured = process.env[PLUGIN_EVENT_PATH_VARIABLE]?.trim();
  return configured === undefined || configured.length === 0
    ? fileURLToPath(new URL(DEFAULT_PLUGIN_EVENT_RELATIVE_PATH, import.meta.url))
    : configured;
}

// The sink the host receives when it composes none of its own. Construction performs no IO: the
// file is created by the first event, so a plugin that reaches no stage writes nothing.
function createDefaultPluginEventSink(): PluginEventSink {
  return new JsonLinesPluginEvents({ eventPath: resolvePluginEventPath() });
}

// Everything an emission states besides its stage: the message identity it concerns, the
// input's coverage as counts, and the bounded code of a finished evaluation.
type PluginEventDetails = Omit<PluginEventInput, 'stage' | 'at'>;

// Diagnostics are best effort: a sink that throws can neither delay delivery nor change the
// advisory, and the JSON Lines adapter already contains its own IO failures. Every call site
// awaits the emission, so the recorded order is the order the stages were reached in.
async function emitPluginEvent(
  sink: PluginEventSink,
  stage: PluginEventStage,
  details: PluginEventDetails = {},
): Promise<void> {
  try {
    await sink.record(
      createPluginEvent({ ...details, stage, at: new Date().toISOString() }),
    );
  } catch {
    // A trace line is operational evidence, never a delivery step (S7).
  }
}

// The registration body: both hook registrations and the teardown they share. `setup` calls it
// inside its guard, so a registration that throws still yields a callable cleanup instead of
// breaking the host.
async function registerAdviserHooks(
  context: OddAdviserSetupContext,
  session: OddAdviserHostSession,
  events: PluginEventSink,
): Promise<OddAdviserCleanup> {
  const configuration = resolveConfiguration(context);

  // The newest admitted message, its identity and which hook admitted it. The context event
  // carries the conversation itself, so it is the admission source the host actually fires for
  // an ordinary message; the prompt event remains a secondary source that fills an empty slot.
  // A build for another session is left untouched rather than given this session's advice.
  let admission: AdmittedMessage | null = null;
  let admissionSource: AdmissionSource | null = null;

  // One promise per message identity. Replacing the map when a newer message is admitted
  // keeps it bounded to the current message, while a tool continuation of the same message
  // reuses the earlier attempt instead of asking the capability again (S5).
  let evaluations = new Map<string, Promise<OddEvidenceAdvisory>>();

  // Set by the returned cleanup. After teardown no attempt is awaited for delivery.
  let disposed = false;

  await session.hook('prompt', (event) => {
    if (disposed) return;

    const identity = { sessionID: event.sessionID, messageID: event.messageID };
    const current = admission;
    // Same message: the earlier capture and its cached evaluation stand, so a repeated
    // delivery of one prompt never starts a second evaluation (S5).
    if (current !== null && identityKey(current.identity) === identityKey(identity)) {
      return;
    }
    // A message the context build already admitted reflects the live conversation, so a
    // prompt event never replaces it; the secondary source only fills the slot.
    if (current !== null && admissionSource === 'context') {
      return;
    }

    admission = {
      identity,
      message: captureMessage(toAdmittedParts(event.prompt)),
    };
    admissionSource = 'prompt';
    evaluations = new Map();
  });

  await session.hook('context', async (event) => {
    try {
      if (disposed) return;

      const candidate = toContextAdmission(event);
      if (candidate === null) {
        // The outgoing request carried no usable user message. Recording the miss is what
        // separates "the hook ran and found nothing" from "the hook never ran" (L24).
        await emitPluginEvent(events, 'candidate_none', {
          sessionId: event.sessionID,
        });
      } else {
        await emitPluginEvent(events, 'candidate_found', {
          sessionId: event.sessionID,
          messageId: candidate.identity.messageID,
          imageCount: candidate.message.images.length,
          textChars: candidate.message.text.length,
        });

        const admitted = admission;
        if (
          admitted !== null &&
          identityKey(admitted.identity) === identityKey(candidate.identity)
        ) {
          // The same message seen again: the cached evaluation is reused and only the stored
          // capture is refreshed from the conversation's own parts.
          admission = candidate;
          admissionSource = 'context';
        } else {
          admission = candidate;
          admissionSource = 'context';
          evaluations = new Map();
        }
      }

      const current = admission;
      if (current === null) return;
      if (event.sessionID !== current.identity.sessionID) return;

      // One attempt per message identity: a build that reuses the cached attempt is not a
      // second inference, so the started/finished pair is recorded only when this build starts
      // one (S5, S6).
      const started = !evaluations.has(identityKey(current.identity));
      if (started) {
        await emitPluginEvent(events, 'evaluate_started', {
          sessionId: current.identity.sessionID,
          messageId: current.identity.messageID,
          imageCount: current.message.images.length,
          textChars: current.message.text.length,
        });
      }

      const advisory = await evaluateWithoutThrowing(
        current,
        configuration,
        evaluations,
      );

      if (started) {
        await emitPluginEvent(events, 'evaluate_finished', {
          sessionId: current.identity.sessionID,
          messageId: current.identity.messageID,
          // The bounded outcome: an evaluation arrived, or the fixed code naming why none did.
          code: advisory.status === 'evaluated' ? 'evaluated' : advisory.code,
        });
      }

      // Teardown may have happened while the attempt was in flight: its result is dropped
      // rather than pushed into a request the host no longer owns.
      if (disposed) return;
      event.system.push({ type: 'text', text: formatAdvisoryBlock(advisory) });
      // The request's system-part count after this push: a count proves the part was appended
      // without repeating any of its text.
      await emitPluginEvent(events, 'advisory_injected', {
        sessionId: current.identity.sessionID,
        messageId: current.identity.messageID,
        parts: event.system.length,
      });
    } catch {
      // Delivering advice is best effort. An unexpected defect in this edge must neither
      // fail nor block the host request; the evaluation path above already delivers its
      // bounded unavailable advisory (S7).
    }
  });

  // Both registrations resolved. This is the stage that proves the host reached this plugin at
  // all, and the absence of every later stage is read against it (L24).
  await emitPluginEvent(events, 'hook_registered');

  // Teardown: stop awaiting attempts for delivery, drop the cached attempt, and close the
  // capability connection if it owns one. Closing the connection is what ends a request
  // already on the wire; a bounded timeout alone proves no cancellation (L25).
  return async () => {
    if (disposed) return;
    disposed = true;
    admission = null;
    admissionSource = null;
    evaluations.clear();

    // The capability this setup actually used: the supplied port when composition supplied one,
    // otherwise the edge's own deferred connection. Closing a deferred connection that was never
    // evaluated releases nothing and starts no process.
    const evaluator = configuration?.evaluator ?? context.evaluator;
    if (!isCloseableEvaluator(evaluator)) return;
    await evaluator.close().catch(() => undefined);
  };
}

const plugin: OddAdviserPlugin = {
  id: 'odd-adviser',
  async setup(context) {
    // The trace this edge records into: the host's own sink when it composes one, otherwise the
    // JSON Lines file at the documented location. Construction does no IO.
    let events: PluginEventSink | null = null;
    try {
      events = context.events ?? createDefaultPluginEventSink();

      // A host session without the hook registrations is skipped, rather than left to throw
      // inside the plugin loader. The skip is recorded as the bounded failure stage, so an
      // unusable host context is not indistinguishable from a plugin that never loaded.
      const session = context.session as OddAdviserHostSession | null | undefined;
      if (session === null || session === undefined) {
        await emitPluginEvent(events, 'setup_failed');
        return NOOP_CLEANUP;
      }
      if (typeof session.hook !== 'function') {
        await emitPluginEvent(events, 'setup_failed');
        return NOOP_CLEANUP;
      }

      return await registerAdviserHooks(context, session, events);
    } catch {
      // A throwing setup yields a no-op cleanup instead of an exception inside the plugin
      // loader, so this edge can never break the host request. Only the bounded stage is
      // recorded: the exception's own message may carry a path or supplied text (S9).
      if (events !== null) await emitPluginEvent(events, 'setup_failed');
      return NOOP_CLEANUP;
    }
  },
};

export default plugin;
