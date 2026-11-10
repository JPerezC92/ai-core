// OpenCode host adapter: hook registration, once-per-message reuse, fail-open delivery and
// teardown. Composition supplies the default connection and event sink so path resolution
// stays at the package entry. This module never authorizes, waives a gate, or blocks (S7).
// Host wire types and admission mapping live here: unknown host messages are mapped, media is
// inlined, then domain captureMessage runs on typed AdmittedPart only.

import {
  evaluateEvidence,
  toUnavailableAdvisory,
} from '../application/evaluate-evidence.ts';
import { formatAdvisoryBlock } from '../domain/advisory-block.ts';
import { captureMessage } from '../domain/capture-message.ts';
import type { AdmittedPart, CapturedMessage } from '../domain/capture-message.ts';
import type { Deadline } from '../domain/deadline.ts';
import { createPluginEvent } from '../domain/plugin-event.ts';
import type {
  PluginEventInput,
  PluginEventSink,
  PluginEventStage,
} from '../domain/plugin-event.ts';
import type {
  EvaluateEvidenceOptions,
  MessageIdentity,
  OddEvidenceAdvisory,
  OddEvidenceEvaluatorConnection,
} from '../domain/plugin-contract.ts';
import type { OddEvidenceEvaluator } from '../domain/advisory.ts';
import {
  appendRollingText,
  classifyAssistantCompletion,
  classifyReportedFooter,
  createObservation,
  extractReceivedText,
  extractResponseId,
} from '../domain/observation.ts';
import type {
  ObservationRecord,
  ObservationReportedFooter,
  ObservationSink,
} from '../domain/observation.ts';
import { createDeferredConnection } from './stdio-mcp-client.ts';

export type PromptDraft = {
  readonly text?: string | undefined;
  readonly files?: ReadonlyArray<PromptFile> | undefined;
};

export type PromptFile = {
  readonly uri: string;
  readonly name?: string | undefined;
};

export type PromptAdmissionEvent = {
  readonly sessionID: string;
  readonly messageID: string;
  readonly prompt: PromptDraft;
};

export type ContextSystemPart = {
  readonly type: 'text';
  readonly text: string;
};

export type ContextBuildEvent = {
  readonly sessionID: string;
  readonly agent?: string | undefined;
  readonly system: ContextSystemPart[];
  readonly messages?: unknown;
  readonly tools?: unknown;
  readonly options?: unknown;
};

export type ContextMessage = {
  readonly id: string;
  readonly role: string;
  readonly content?: ReadonlyArray<ContextMessagePart> | undefined;
  readonly parts?: ReadonlyArray<ContextMessagePart> | undefined;
};

export type ContextMessagePart = {
  readonly type: string;
  readonly text?: string | undefined;
  readonly media?: ContextMessageMedia | undefined;
};

export type ContextMessageMedia = {
  readonly inline?: (() => ContextInlinedMedia | undefined) | undefined;
};

export type ContextInlinedMedia = {
  readonly dataUrl?: string | undefined;
};

export type PromptAdmissionListener = (event: PromptAdmissionEvent) => void;
export type ContextBuildListener = (event: ContextBuildEvent) => Promise<void>;

export type HttpResponseEvent = {
  readonly sessionID?: string | undefined;
  readonly response: {
    clone(): { text(): Promise<string> };
  };
};

export type WebSocketReceiveEvent = {
  readonly sessionID?: string | undefined;
  readonly frame: unknown;
};

export type ToolExecuteAfterEvent = {
  readonly sessionID?: string | undefined;
  readonly id?: string | undefined;
  readonly tool?: { readonly id?: string | undefined } | undefined;
  readonly error?: unknown;
};

export type HttpResponseListener = (event: HttpResponseEvent) => Promise<void> | void;
export type WebSocketReceiveListener = (
  event: WebSocketReceiveEvent,
) => Promise<void> | void;
export type ToolExecuteAfterListener = (
  event: ToolExecuteAfterEvent,
) => Promise<void> | void;

export type OddAdviserHostSession = {
  readonly hook: {
    (name: 'prompt', listener: PromptAdmissionListener): Promise<unknown>;
    (name: 'context', listener: ContextBuildListener): Promise<unknown>;
    (name: 'http.response', listener: HttpResponseListener): Promise<unknown>;
    (name: 'experimental.ws.receive', listener: WebSocketReceiveListener): Promise<unknown>;
  };
};

export type OddAdviserHostTool = {
  readonly hook: {
    (name: 'execute.after', listener: ToolExecuteAfterListener): Promise<unknown>;
  };
};

export type OddAdviserCleanup = () => Promise<void>;

export type OddAdviserSetupContext = {
  readonly session: OddAdviserHostSession;
  readonly evaluator?: OddEvidenceEvaluator;
  readonly timeoutMs?: number;
  readonly expectedModel?: string;
  readonly createConnection?: () => OddEvidenceEvaluatorConnection;
  readonly events?: PluginEventSink;
  readonly observations?: ObservationSink;
  readonly tool?: OddAdviserHostTool;
};

export type OddAdviserPlugin = {
  readonly id: string;
  setup(context: OddAdviserSetupContext): Promise<OddAdviserCleanup>;
};

type AdmittedMessage = {
  readonly identity: MessageIdentity;
  readonly message: CapturedMessage;
};

function identityKey(identity: MessageIdentity): string {
  return `${identity.sessionID}\u0000${identity.messageID}`;
}

function toAdmittedParts(draft: PromptDraft): ReadonlyArray<AdmittedPart> {
  const parts: AdmittedPart[] = [];
  if (draft.text !== undefined) parts.push({ text: draft.text });
  for (const file of draft.files ?? []) parts.push({ url: file.uri });
  return parts;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

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

function selectContextParts(message: Record<string, unknown>): unknown {
  const content = message.content;
  if (Array.isArray(content)) return content;

  const parts = message.parts;
  if (Array.isArray(parts)) return parts;

  return [];
}

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

const NOOP_CLEANUP: OddAdviserCleanup = async () => undefined;

const DEFAULT_EVIDENCE_TIMEOUT_MS = 15_000;

type AdviserConfiguration = {
  readonly evaluator: OddEvidenceEvaluator;
  readonly options: EvaluateEvidenceOptions;
};

type AdmissionSource = 'prompt' | 'context';

export type OddAdviserDefaults = {
  readonly createDefaultConnection: () => OddEvidenceEvaluatorConnection;
  readonly createDefaultEventSink: () => PluginEventSink;
  readonly createDefaultObservationSink: () => ObservationSink;
};

type ObservationIdentity = {
  readonly evaluationId: string;
  readonly sessionID: string;
  readonly messageID: string;
};

function observationKey(identity: ObservationIdentity): string {
  return `${identity.evaluationId}\u0000${identity.sessionID}\u0000${identity.messageID}`;
}

function toolIdFromEvent(event: ToolExecuteAfterEvent): string | undefined {
  if (typeof event.id === 'string' && event.id.length > 0) return event.id;
  const nested = event.tool?.id;
  return typeof nested === 'string' && nested.length > 0 ? nested : undefined;
}

function createTimerDeadline(): Deadline {
  return {
    schedule(timeoutMs, onElapsed) {
      const timer = setTimeout(onElapsed, timeoutMs);
      return () => {
        clearTimeout(timer);
      };
    },
  };
}

function resolveConfiguration(
  context: OddAdviserSetupContext,
  defaults: OddAdviserDefaults,
): AdviserConfiguration | null {
  const timeoutMs = context.timeoutMs ?? DEFAULT_EVIDENCE_TIMEOUT_MS;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) return null;

  const evaluator =
    context.evaluator ??
    createDeferredConnection(context.createConnection ?? defaults.createDefaultConnection);

  return {
    evaluator,
    options: {
      timeoutMs,
      ...(context.expectedModel === undefined ? {} : { expectedModel: context.expectedModel }),
    },
  };
}

function isCloseableEvaluator(
  evaluator: OddEvidenceEvaluator | undefined,
): evaluator is OddEvidenceEvaluatorConnection {
  if (evaluator === undefined) return false;
  const candidate = evaluator as Partial<OddEvidenceEvaluatorConnection>;
  return typeof candidate.close === 'function';
}

function evaluateOnce(
  identity: AdmittedMessage['identity'],
  message: AdmittedMessage['message'],
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
    createTimerDeadline(),
  );
  evaluations.set(key, pending);
  return pending;
}

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

type PluginEventDetails = Omit<PluginEventInput, 'stage' | 'at'>;

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

async function registerAdviserHooks(
  context: OddAdviserSetupContext,
  session: OddAdviserHostSession,
  events: PluginEventSink,
  observations: ObservationSink,
  defaults: OddAdviserDefaults,
): Promise<OddAdviserCleanup> {
  const configuration = resolveConfiguration(context, defaults);

  let admission: AdmittedMessage | null = null;
  let admissionSource: AdmissionSource | null = null;
  let evaluations = new Map<string, Promise<OddEvidenceAdvisory>>();
  let observationIdentities = new Map<string, ObservationIdentity>();
  let rollingText = new Map<string, string>();
  let disposed = false;

  async function flushIncompleteObservations(): Promise<void> {
    const pending: ObservationIdentity[] = [];
    for (const identity of observationIdentities.values()) {
      const buffer = rollingText.get(observationKey(identity)) ?? '';
      if (buffer.length > 0) pending.push(identity);
    }
    observationIdentities = new Map();
    rollingText = new Map();
    for (const identity of pending) {
      await recordObservation(identity, { reportedFooter: 'uninspectable' });
    }
  }

  function appendObservedText(identity: ObservationIdentity, chunk: string): void {
    const key = observationKey(identity);
    rollingText.set(key, appendRollingText(rollingText.get(key) ?? '', chunk));
  }

  function takeObservedText(identity: ObservationIdentity): string {
    const key = observationKey(identity);
    const reconstructed = rollingText.get(key) ?? '';
    rollingText.delete(key);
    return reconstructed;
  }

  function rememberEvaluation(
    identity: MessageIdentity,
    evaluationId: string | undefined,
  ): void {
    if (evaluationId === undefined || evaluationId.length === 0) return;
    observationIdentities.set(identityKey(identity), {
      evaluationId,
      sessionID: identity.sessionID,
      messageID: identity.messageID,
    });
  }

  function lookupObservationIdentity(sessionID?: string): ObservationIdentity | undefined {
    const current = admission;
    if (current === null) return undefined;
    if (sessionID !== undefined && current.identity.sessionID !== sessionID) {
      return undefined;
    }
    return observationIdentities.get(identityKey(current.identity));
  }

  async function recordObservation(
    identity: ObservationIdentity,
    details: Pick<ObservationRecord, 'reportedFooter' | 'tools' | 'responseId'>,
  ): Promise<void> {
    try {
      await observations.record(
        createObservation({
          evaluationId: identity.evaluationId,
          sessionId: identity.sessionID,
          messageId: identity.messageID,
          at: new Date().toISOString(),
          ...details,
        }),
      );
    } catch {
      // Observation is operational evidence, never a delivery step (S7).
    }
  }

  await session.hook('prompt', (event) => {
    if (disposed) return;

    const identity = { sessionID: event.sessionID, messageID: event.messageID };
    const current = admission;
    if (current !== null && identityKey(current.identity) === identityKey(identity)) {
      return;
    }
    if (current !== null && admissionSource === 'context') {
      return;
    }

    admission = {
      identity,
      message: captureMessage(toAdmittedParts(event.prompt)),
    };
    admissionSource = 'prompt';
    evaluations = new Map();
    void flushIncompleteObservations();
  });

  await session.hook('context', async (event) => {
    try {
      if (disposed) return;

      const candidate = toContextAdmission(event);
      if (candidate === null) {
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
          admission = candidate;
          admissionSource = 'context';
        } else {
          admission = candidate;
          admissionSource = 'context';
          evaluations = new Map();
          await flushIncompleteObservations();
        }
      }

      const current = admission;
      if (current === null) return;
      if (event.sessionID !== current.identity.sessionID) return;

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
      rememberEvaluation(current.identity, advisory.evaluationId);

      if (started) {
        await emitPluginEvent(events, 'evaluate_finished', {
          sessionId: current.identity.sessionID,
          messageId: current.identity.messageID,
          code: advisory.status === 'evaluated' ? 'evaluated' : advisory.code,
        });
      }

      if (disposed) return;
      const block = formatAdvisoryBlock(advisory);
      if (block === '') return;
      event.system.push({ type: 'text', text: block });
      await emitPluginEvent(events, 'advisory_injected', {
        sessionId: current.identity.sessionID,
        messageId: current.identity.messageID,
        parts: event.system.length,
      });
    } catch {
      // Delivering advice is best effort. An unexpected defect in this edge must neither
      // fail nor block the host request (S7).
    }
  });

  const registerOptionalHook = async (
    register: () => Promise<unknown>,
  ): Promise<void> => {
    try {
      await register();
    } catch {
      // Unsupported host hooks stay unobserved; they must not fail setup (S7).
    }
  };

  await registerOptionalHook(() =>
    session.hook('http.response', async (event) => {
      try {
        if (disposed) return;
        const identity = lookupObservationIdentity(event.sessionID);
        if (identity === undefined) return;

        let reportedFooter: ObservationReportedFooter = 'uninspectable';
        try {
          const cloned = event.response.clone();
          const text = await cloned.text();
          reportedFooter = classifyReportedFooter(text);
        } catch {
          reportedFooter = 'uninspectable';
        }
        await recordObservation(identity, { reportedFooter });
      } catch {
        // Observation hooks fail open (S7).
      }
    }),
  );

  await registerOptionalHook(() =>
    session.hook('experimental.ws.receive', async (event) => {
      try {
        if (disposed) return;
        const identity = lookupObservationIdentity(event.sessionID);
        if (identity === undefined) return;
        const kind = classifyAssistantCompletion(event.frame);
        const text = extractReceivedText(event.frame);
        if (text !== null && kind === 'incomplete') {
          appendObservedText(identity, text);
          return;
        }
        if (text !== null) {
          const trimmed = text.trim();
          if (trimmed !== '[DONE]' && trimmed !== 'data: [DONE]') {
            appendObservedText(identity, text);
          }
        }
        if (kind === 'incomplete' || kind === 'text_part') return;
        if (kind === 'tool_step') {
          takeObservedText(identity);
          return;
        }
        const reconstructed = takeObservedText(identity);
        if (reconstructed.length === 0) return;
        const responseId = extractResponseId(event.frame);
        if (kind === 'user_facing') {
          await recordObservation(identity, {
            reportedFooter: classifyReportedFooter(reconstructed),
            ...(responseId === undefined ? {} : { responseId }),
          });
          return;
        }
        await recordObservation(identity, {
          reportedFooter: 'uninspectable',
          ...(responseId === undefined ? {} : { responseId }),
        });
      } catch {
        // Observation hooks fail open (S7).
      }
    }),
  );

  await registerOptionalHook(async () => {
    const toolHook = context.tool?.hook;
    if (typeof toolHook !== 'function') return;
    await toolHook('execute.after', async (event) => {
      try {
        if (disposed) return;
        const identity = lookupObservationIdentity(event.sessionID);
        if (identity === undefined) return;
        const id = toolIdFromEvent(event);
        if (id === undefined) return;
        await recordObservation(identity, {
          tools: [{ id, status: event.error === undefined ? 'completed' : 'error' }],
        });
      } catch {
        // Observation hooks fail open (S7).
      }
    });
  });

  await emitPluginEvent(events, 'hook_registered');

  return async () => {
    if (disposed) return;
    disposed = true;
    admission = null;
    admissionSource = null;
    evaluations.clear();
    await flushIncompleteObservations();

    const evaluator = configuration?.evaluator ?? context.evaluator;
    if (!isCloseableEvaluator(evaluator)) return;
    await evaluator.close().catch(() => undefined);
  };
}

export function createOddAdviserPlugin(defaults: OddAdviserDefaults): OddAdviserPlugin {
  return {
    id: 'odd-adviser',
    async setup(context) {
      let events: PluginEventSink | null = null;
      try {
        events = context.events ?? defaults.createDefaultEventSink();

        const session = context.session as OddAdviserHostSession | null | undefined;
        if (session === null || session === undefined) {
          await emitPluginEvent(events, 'setup_failed');
          return NOOP_CLEANUP;
        }
        if (typeof session.hook !== 'function') {
          await emitPluginEvent(events, 'setup_failed');
          return NOOP_CLEANUP;
        }

        const observations = context.observations ?? defaults.createDefaultObservationSink();
        return await registerAdviserHooks(context, session, events, observations, defaults);
      } catch {
        if (events !== null) await emitPluginEvent(events, 'setup_failed');
        return NOOP_CLEANUP;
      }
    },
  };
}
