// Domain record of the plugin's own lifecycle: the bounded stage the delivery edge reached,
// the message identity it concerns, the input's coverage as counts, and the bounded code that
// names an evaluation's outcome. This module is framework-free: it declares no storage medium,
// names no file, performs no IO, reads no clock and throws nothing. The JSON Lines adapter owns
// the file and the line format.
//
// An event is content-free by construction. The record has no field for supplied text, image
// bytes, a path or a payload value, and the factory below copies only the declared fields, so
// an object that carries content cannot become an event (S9). Coverage is stated as counts
// (`textChars`, `imageCount`), which report how much input an evaluation saw without repeating
// it.

import type { OddEvidenceUnavailableCode } from './advisory.ts';

// Version of the stored line's field set. A reader that meets an unknown version can stop
// instead of guessing what a field means.
export const PLUGIN_EVENT_SCHEMA_VERSION = 1;

// Every stage this edge can report, in the order an ordinary context build reaches them. The
// union is closed, so a new stage is an explicit decision rather than a free-form string.
export type PluginEventStage =
  | 'hook_registered'
  | 'candidate_found'
  | 'candidate_none'
  | 'evaluate_started'
  | 'evaluate_finished'
  | 'advisory_injected'
  | 'setup_failed';

// The bounded outcome of `evaluate_finished`: an evaluation arrived, or the fixed code naming
// why none did. A code names a failure class and never carries a supplied value.
export type PluginEventCode = OddEvidenceUnavailableCode | 'evaluated';

// Everything a caller may state about one event. `at` is required so no clock read happens
// inside the domain: the edge that owns time stamps the event it records.
export type PluginEventInput = {
  readonly stage: PluginEventStage;
  readonly at: string;
  readonly sessionId?: string;
  readonly messageId?: string;
  readonly imageCount?: number;
  readonly textChars?: number;
  readonly code?: PluginEventCode;
  readonly parts?: number;
};

// One event as it is recorded: the schema version plus exactly the declared fields. Fields a
// caller did not state stay absent rather than becoming `undefined`, so a stored line states
// only what the edge observed.
export type PluginEvent = {
  readonly schemaVersion: typeof PLUGIN_EVENT_SCHEMA_VERSION;
  readonly stage: PluginEventStage;
  readonly at: string;
  readonly sessionId?: string;
  readonly messageId?: string;
  readonly imageCount?: number;
  readonly textChars?: number;
  readonly code?: PluginEventCode;
  readonly parts?: number;
};

// One explicit copy, so a caller passing extra runtime properties cannot smuggle them into the
// record: an event contains exactly the declared fields, and each is copied by name.
export function createPluginEvent(input: PluginEventInput): PluginEvent {
  return {
    schemaVersion: PLUGIN_EVENT_SCHEMA_VERSION,
    stage: input.stage,
    at: input.at,
    ...(input.sessionId === undefined ? {} : { sessionId: input.sessionId }),
    ...(input.messageId === undefined ? {} : { messageId: input.messageId }),
    ...(input.imageCount === undefined ? {} : { imageCount: input.imageCount }),
    ...(input.textChars === undefined ? {} : { textChars: input.textChars }),
    ...(input.code === undefined ? {} : { code: input.code }),
    ...(input.parts === undefined ? {} : { parts: input.parts }),
  };
}

// The capability the delivery edge records into. The method returns a promise so an
// implementation may await its own IO; the domain knows neither the medium nor the
// serialization, and recording failure is an implementation concern that never reaches here.
export type PluginEventSink = {
  record(event: PluginEvent): Promise<void>;
};
