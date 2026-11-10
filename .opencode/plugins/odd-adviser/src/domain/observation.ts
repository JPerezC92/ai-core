// Domain record of one independent observation of a System 1 evaluation: the correlation
// identity, an optional reconstructed footer class, optional tool completions, and a fixed
// independent assessment. This module is framework-free. It declares no storage medium,
// performs no IO, reads no clock and throws nothing. Footer classification is a pure scan
// of complete reconstructed text; it never becomes a handling disposition (S6, S15).
// Completeness is a protocol signal, never the presence of an S1 footer line.

export const OBSERVATION_SCHEMA_VERSION = 4;
export const OBSERVATION_RECORD_TYPE = 'observation';
export const OBSERVATION_TEXT_WINDOW_CHARS = 4096;

export type ObservationReportedFooter =
  | 'applied_line'
  | 'overridden_line'
  | 'mixed'
  | 'none'
  | 'uninspectable';

export type ObservationToolStatus = 'completed' | 'error';

export type ObservationTool = {
  readonly id: string;
  readonly status: ObservationToolStatus;
};

export type ObservationAssessment = 'not_observed';

export type AssistantCompletionKind =
  | 'incomplete'
  | 'text_part'
  | 'tool_step'
  | 'user_facing'
  | 'truncated'
  | 'uninspectable';

export type ObservationInput = {
  readonly evaluationId: string;
  readonly sessionId: string;
  readonly messageId: string;
  readonly at: string;
  readonly reportedFooter?: ObservationReportedFooter;
  readonly tools?: ReadonlyArray<ObservationTool>;
  readonly responseId?: string;
};

export type ObservationRecord = {
  readonly schemaVersion: typeof OBSERVATION_SCHEMA_VERSION;
  readonly recordType: typeof OBSERVATION_RECORD_TYPE;
  readonly evaluationId: string;
  readonly sessionId: string;
  readonly messageId: string;
  readonly at: string;
  readonly reportedFooter?: ObservationReportedFooter;
  readonly tools?: ReadonlyArray<ObservationTool>;
  readonly responseId?: string;
  readonly assessment: ObservationAssessment;
};

export type ObservationSink = {
  record(observation: ObservationRecord): Promise<void>;
};

const APPLIED_FOOTER_PREFIX = 'S1 applied:';
const OVERRIDDEN_FOOTER_PREFIX = 'S1 overridden:';

export function appendRollingText(
  buffer: string,
  chunk: string,
  maxChars: number = OBSERVATION_TEXT_WINDOW_CHARS,
): string {
  const combined = `${buffer}${chunk}`;
  return combined.length <= maxChars ? combined : combined.slice(-maxChars);
}

export function classifyReportedFooter(text: string): ObservationReportedFooter {
  const hasApplied = text.includes(APPLIED_FOOTER_PREFIX);
  const hasOverridden = text.includes(OVERRIDDEN_FOOTER_PREFIX);
  if (hasApplied && hasOverridden) return 'mixed';
  if (hasApplied) return 'applied_line';
  if (hasOverridden) return 'overridden_line';
  return 'none';
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0;
}

function textFromDelta(delta: unknown): string | null {
  if (typeof delta === 'string' && delta.length > 0) return delta;
  if (!isRecord(delta)) return null;
  if (typeof delta.content === 'string' && delta.content.length > 0) return delta.content;
  if (typeof delta.text === 'string' && delta.text.length > 0) return delta.text;
  return null;
}

function extractJsonAssistantText(value: Record<string, unknown>): string | null {
  if (Array.isArray(value.choices)) {
    const parts: string[] = [];
    for (const choice of value.choices) {
      if (!isRecord(choice)) continue;
      const fromDelta = textFromDelta(choice.delta);
      if (fromDelta !== null) parts.push(fromDelta);
      else if (typeof choice.text === 'string' && choice.text.length > 0) {
        parts.push(choice.text);
      }
    }
    if (parts.length > 0) return parts.join('');
  }

  const fromDelta = textFromDelta(value.delta);
  if (fromDelta !== null) return fromDelta;
  if (typeof value.text === 'string' && value.text.length > 0) return value.text;
  if (typeof value.content === 'string' && value.content.length > 0) return value.content;
  return null;
}

function parseJsonRecord(text: string): Record<string, unknown> | null {
  try {
    const parsed: unknown = JSON.parse(text);
    return isRecord(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

const INTERMEDIATE_FINISH_REASONS = new Set([
  'tool_calls',
  'function_call',
  'tool_use',
]);
const USER_FACING_FINISH_REASONS = new Set(['stop', 'end_turn']);
const TRUNCATED_FINISH_REASONS = new Set([
  'length',
  'max_tokens',
  'max_output_tokens',
]);
const INTERMEDIATE_FRAME_TYPES = new Set([
  'response.output_text.done',
  'content_block_stop',
  'response.function_call_arguments.done',
]);
const FUNCTION_CALL_OUTPUT_TYPES = new Set([
  'function_call',
  'tool_call',
  'tool_use',
]);

function isDoneSentinel(frame: string): boolean {
  const trimmed = frame.trim();
  return trimmed === '[DONE]' || trimmed === 'data: [DONE]';
}

function collectFinishReasons(value: Record<string, unknown>): string[] {
  const reasons: string[] = [];
  if (isNonEmptyString(value.finish_reason)) reasons.push(value.finish_reason);
  if (isNonEmptyString(value.stop_reason)) reasons.push(value.stop_reason);
  if (!Array.isArray(value.choices)) return reasons;
  for (const choice of value.choices) {
    if (!isRecord(choice)) continue;
    if (isNonEmptyString(choice.finish_reason)) reasons.push(choice.finish_reason);
    if (isNonEmptyString(choice.stop_reason)) reasons.push(choice.stop_reason);
  }
  return reasons;
}

function classifyFinishReason(reason: string): AssistantCompletionKind | null {
  if (INTERMEDIATE_FINISH_REASONS.has(reason)) return 'tool_step';
  if (TRUNCATED_FINISH_REASONS.has(reason)) return 'truncated';
  if (USER_FACING_FINISH_REASONS.has(reason)) return 'user_facing';
  return null;
}

function outputHasFunctionCall(output: unknown): boolean {
  if (!Array.isArray(output)) return false;
  for (const item of output) {
    if (!isRecord(item) || !isNonEmptyString(item.type)) continue;
    if (FUNCTION_CALL_OUTPUT_TYPES.has(item.type)) return true;
  }
  return false;
}

function outputHasAssistantMessage(output: unknown): boolean {
  if (!Array.isArray(output)) return false;
  for (const item of output) {
    if (!isRecord(item) || !isNonEmptyString(item.type)) continue;
    if (item.type === 'message' || item.type === 'output_text') return true;
  }
  return false;
}

function classifyResponseCompleted(value: Record<string, unknown>): AssistantCompletionKind {
  const response = isRecord(value.response) ? value.response : value;
  if (isRecord(response.incomplete_details) || response.status === 'incomplete') {
    return 'truncated';
  }
  if (outputHasFunctionCall(response.output)) return 'tool_step';
  if (outputHasAssistantMessage(response.output)) return 'user_facing';
  return 'uninspectable';
}

function classifyProtocolRecord(value: Record<string, unknown>): AssistantCompletionKind {
  if (isNonEmptyString(value.type)) {
    if (INTERMEDIATE_FRAME_TYPES.has(value.type)) return 'text_part';
    if (value.type === 'response.incomplete') return 'truncated';
    if (value.type === 'response.completed' || value.type === 'response.done') {
      return classifyResponseCompleted(value);
    }
    if (value.type === 'message_stop') {
      const reasons = collectFinishReasons(value);
      if (reasons.length === 0) return 'uninspectable';
    }
  }

  const reasons = collectFinishReasons(value);
  for (const reason of reasons) {
    const kind = classifyFinishReason(reason);
    if (kind === 'tool_step') return 'tool_step';
  }
  for (const reason of reasons) {
    const kind = classifyFinishReason(reason);
    if (kind === 'truncated') return 'truncated';
  }
  for (const reason of reasons) {
    const kind = classifyFinishReason(reason);
    if (kind === 'user_facing') return 'user_facing';
  }
  if (reasons.length > 0) return 'uninspectable';
  if (value.done === true) return 'uninspectable';
  return 'incomplete';
}

export function classifyAssistantCompletion(frame: unknown): AssistantCompletionKind {
  if (typeof frame === 'string') {
    if (isDoneSentinel(frame)) return 'uninspectable';
    const parsed = parseJsonRecord(frame);
    return parsed === null ? 'incomplete' : classifyProtocolRecord(parsed);
  }
  if (!isRecord(frame)) return 'incomplete';
  return classifyProtocolRecord(frame);
}

export function extractResponseId(frame: unknown): string | undefined {
  const record =
    typeof frame === 'string'
      ? parseJsonRecord(frame)
      : isRecord(frame)
        ? frame
        : null;
  if (record === null) return undefined;
  if (isRecord(record.response) && isNonEmptyString(record.response.id)) {
    return record.response.id;
  }
  return undefined;
}

export function extractReceivedText(frame: unknown): string | null {
  if (typeof ArrayBuffer !== 'undefined' && frame instanceof ArrayBuffer) return null;
  if (typeof Uint8Array !== 'undefined' && frame instanceof Uint8Array) return null;

  if (typeof frame === 'string') {
    const parsed = parseJsonRecord(frame);
    if (parsed !== null) return extractJsonAssistantText(parsed);
    return frame;
  }

  if (!isRecord(frame)) return null;
  return extractJsonAssistantText(frame);
}

export function isAssistantResponseComplete(frame: unknown): boolean {
  return classifyAssistantCompletion(frame) === 'user_facing';
}

export function createObservation(input: ObservationInput): ObservationRecord {
  return {
    schemaVersion: OBSERVATION_SCHEMA_VERSION,
    recordType: OBSERVATION_RECORD_TYPE,
    evaluationId: input.evaluationId,
    sessionId: input.sessionId,
    messageId: input.messageId,
    at: input.at,
    ...(input.reportedFooter === undefined ? {} : { reportedFooter: input.reportedFooter }),
    ...(input.tools === undefined
      ? {}
      : {
          tools: input.tools.map((tool) => ({ id: tool.id, status: tool.status })),
        }),
    ...(input.responseId === undefined ? {} : { responseId: input.responseId }),
    assessment: 'not_observed',
  };
}
