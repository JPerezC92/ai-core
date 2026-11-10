// Infrastructure adapter for the domain `ObservationSink` port: appends one JSON line per
// observation to the same file MCP evaluation traces use. It creates the parent directory,
// opens the file in append mode for each record (no handle or buffer survives a call) and
// maps the record to exactly its declared fields, so a stored line cannot carry request
// state, tool arguments, a provider body or a handling disposition.
//
// A trace failure is operational evidence loss, not a delivery failure: this adapter
// swallows its own IO and serialization errors. It never rewrites an evaluation line.

import { appendFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

import type { ObservationRecord, ObservationSink } from '../domain/observation.ts';

export type JsonLinesObservationsOptions = {
  readonly eventPath: string;
};

export class JsonLinesObservations implements ObservationSink {
  readonly #eventPath: string;

  constructor(options: JsonLinesObservationsOptions) {
    this.#eventPath = options.eventPath;
  }

  async record(observation: ObservationRecord): Promise<void> {
    try {
      await mkdir(dirname(this.#eventPath), { recursive: true });
      await appendFile(this.#eventPath, `${toObservationLine(observation)}\n`, {
        encoding: 'utf8',
        flag: 'a',
      });
    } catch {
      // An unwritable path must never change the advisory path this line describes.
    }
  }
}

function toObservationLine(observation: ObservationRecord): string {
  return JSON.stringify({
    schemaVersion: observation.schemaVersion,
    recordType: observation.recordType,
    evaluationId: observation.evaluationId,
    sessionId: observation.sessionId,
    messageId: observation.messageId,
    at: observation.at,
    ...(observation.reportedFooter === undefined
      ? {}
      : { reportedFooter: observation.reportedFooter }),
    ...(observation.tools === undefined
      ? {}
      : {
          tools: observation.tools.map((tool) => ({
            id: tool.id,
            status: tool.status,
          })),
        }),
    assessment: observation.assessment,
  });
}
