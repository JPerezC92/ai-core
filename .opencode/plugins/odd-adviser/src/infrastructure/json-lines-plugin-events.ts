// Infrastructure adapter for the domain `PluginEventSink` port: appends one JSON line per
// lifecycle event to the configured file. It creates the parent directory, opens the file in
// append mode for each event (no handle or buffer survives a call) and maps the event to
// exactly its declared fields, so a stored line can carry no field the domain record does not
// declare.
//
// A trace failure is operational evidence loss, not a delivery failure: this adapter swallows
// its own IO and serialization errors and writes nothing to stdout or stderr, which the host
// may reserve for its own channels. The caller decides whether to await an event; this adapter
// performs one append per call and no work on its own.

import { appendFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

import type { PluginEvent, PluginEventSink } from '../domain/plugin-event.ts';

export type JsonLinesPluginEventsOptions = {
  // The path supplied by composition. This adapter applies no path policy of its own: the
  // composition root owns which file receives the trace.
  readonly eventPath: string;
};

export class JsonLinesPluginEvents implements PluginEventSink {
  readonly #eventPath: string;

  constructor(options: JsonLinesPluginEventsOptions) {
    this.#eventPath = options.eventPath;
  }

  async record(event: PluginEvent): Promise<void> {
    try {
      await mkdir(dirname(this.#eventPath), { recursive: true });
      await appendFile(this.#eventPath, `${toEventLine(event)}\n`, {
        encoding: 'utf8',
        flag: 'a',
      });
    } catch {
      // An unwritable path must never change the advisory path this line describes. No
      // diagnostic is emitted here at all.
    }
  }
}

// One mapping step from the domain record to the stored line. The projection is explicit, so a
// caller that hands a wider object to the sink still stores exactly these fields.
function toEventLine(event: PluginEvent): string {
  return JSON.stringify({
    schemaVersion: event.schemaVersion,
    stage: event.stage,
    at: event.at,
    ...(event.sessionId === undefined ? {} : { sessionId: event.sessionId }),
    ...(event.messageId === undefined ? {} : { messageId: event.messageId }),
    ...(event.imageCount === undefined ? {} : { imageCount: event.imageCount }),
    ...(event.textChars === undefined ? {} : { textChars: event.textChars }),
    ...(event.code === undefined ? {} : { code: event.code }),
    ...(event.parts === undefined ? {} : { parts: event.parts }),
  });
}
