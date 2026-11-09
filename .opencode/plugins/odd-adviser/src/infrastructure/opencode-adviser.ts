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

export type OddAdviserHostSession = {
  readonly hook: {
    (name: 'prompt', listener: PromptAdmissionListener): Promise<unknown>;
    (name: 'context', listener: ContextBuildListener): Promise<unknown>;
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
};

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
  defaults: OddAdviserDefaults,
): Promise<OddAdviserCleanup> {
  const configuration = resolveConfiguration(context, defaults);

  let admission: AdmittedMessage | null = null;
  let admissionSource: AdmissionSource | null = null;
  let evaluations = new Map<string, Promise<OddEvidenceAdvisory>>();
  let disposed = false;

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

  await emitPluginEvent(events, 'hook_registered');

  return async () => {
    if (disposed) return;
    disposed = true;
    admission = null;
    admissionSource = null;
    evaluations.clear();

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

        return await registerAdviserHooks(context, session, events, defaults);
      } catch {
        if (events !== null) await emitPluginEvent(events, 'setup_failed');
        return NOOP_CLEANUP;
      }
    },
  };
}
