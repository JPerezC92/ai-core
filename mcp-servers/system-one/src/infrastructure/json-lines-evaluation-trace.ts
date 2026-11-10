// Infrastructure adapter for the domain `EvaluationTrace` port: appends one JSON line per
// entry to the configured file. This adapter creates the parent directory, opens the file
// in append mode for each record (no handle or buffer survives a call) and maps the entry
// to exactly its declared fields: the full request body, the full parsed response body or
// the bounded transport error that replaced it, and the outcome. The request's state and
// questions are stored verbatim; each image is stored as its content-addressed descriptor,
// so the line identifies the bytes without containing them.
//
// A tracing failure is operational metadata loss, not an evaluation failure: its own IO
// or serialization errors are swallowed and nothing is written to stdout, which carries
// MCP protocol frames.

import { appendFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

import type {
  EvaluationTrace,
  EvaluationTraceEntry,
  EvaluationTraceHandling,
  EvaluationTraceRequest,
} from '../domain/evaluation-trace.ts';

export type JsonLinesEvaluationTraceOptions = {
  // Absolute path supplied by the host. This adapter applies no path policy: the host
  // configuration owns which file is written.
  readonly tracePath: string;
};

export class JsonLinesEvaluationTrace implements EvaluationTrace {
  readonly #tracePath: string;

  constructor(options: JsonLinesEvaluationTraceOptions) {
    this.#tracePath = options.tracePath;
  }

  async record(entry: EvaluationTraceEntry): Promise<void> {
    try {
      await mkdir(dirname(this.#tracePath), { recursive: true });
      await appendFile(this.#tracePath, `${toTraceLine(entry)}\n`, {
        encoding: 'utf8',
        flag: 'a',
      });
    } catch {
      // Tracing is diagnostic capture; an unwritable path must never fail the evaluation
      // it describes. No diagnostic is emitted here at all.
    }
  }
}

// One mapping step from the domain record to the stored line. The projection is explicit,
// so the stored record contains exactly these fields and exactly one of response/error.
function toTraceLine(entry: EvaluationTraceEntry): string {
  return JSON.stringify({
    schemaVersion: entry.schemaVersion,
    evaluationId: entry.evaluationId,
    at: entry.at,
    sessionId: entry.sessionId,
    profileId: entry.profileId,
    profileVersion: entry.profileVersion,
    model: entry.model,
    request: toRequestLine(entry.request),
    ...toResultLine(entry),
    outcome: entry.outcome,
    handling: toHandlingLine(entry.handling),
    elapsedMs: entry.elapsedMs,
  });
}

function toRequestLine(request: EvaluationTraceRequest) {
  return {
    model: request.model,
    state: request.state,
    questions: request.questions,
    images: request.images.map((image) => ({
      mimeType: image.mimeType,
      bytes: image.bytes,
      sha256: image.sha256,
      path: image.path,
    })),
  };
}

// The response body is stored as received; on a transport failure the line carries the
// bounded error instead, and no `response` key is written.
function toResultLine(entry: EvaluationTraceEntry) {
  return 'response' in entry
    ? { response: entry.response }
    : { error: entry.error };
}

function toHandlingLine(handling: EvaluationTraceHandling) {
  return {
    disposition: handling.disposition,
    reportedFooter: handling.reportedFooter,
    observedActions: handling.observedActions,
    assessment: handling.assessment,
  };
}
