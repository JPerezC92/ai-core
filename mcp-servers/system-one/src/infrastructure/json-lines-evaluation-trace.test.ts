// Integration test of the JSON Lines evaluation trace adapter across its filesystem
// boundary: one successful exchange and one transport-failure exchange are recorded into
// a fresh temporary directory and read back as JSON lines. The stored request carries the
// supplied state and questions verbatim, the stored response is the exact parsed body
// received, the failure line carries the bounded error instead of a response, and the
// stored image descriptor resolves to a file whose bytes hash to its recorded sha256. The
// test owns its temporary directory and removes it afterwards.

import { createHash } from 'node:crypto';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { expect, test } from 'vitest';

import { ImageStore } from './image-store.ts';
import { JsonLinesEvaluationTrace } from './json-lines-evaluation-trace.ts';
import {
  createEvaluationTraceEntry,
  createEvaluationTraceError,
  createEvaluationTraceExchange,
  createEvaluationTraceQuestions,
  createEvaluationTraceRequest,
  createFailedEvaluationTraceEntry,
  createFailedEvaluationTraceExchange,
} from '../test/helpers/evaluation-trace.factory.ts';
import { createDecisionResponse, createEvidence } from '../test/helpers/odd-evidence.factory.ts';

// Vitest reports a missing value but does not narrow it for TypeScript, so the stored item
// is also narrowed here; a missing item still fails the case with the message below.
function recorded<T>(value: T | undefined, message: string): T {
  expect(value, message).toBeDefined();
  if (value === undefined) throw new Error(message);
  return value;
}

// A parsed JSON line is `any`; this narrows it to the keyed object the stored contract
// requires so each assertion reads a real field rather than skipping the shape check.
function readRecord(value: unknown, message: string): Record<string, unknown> {
  const isKeyedObject = typeof value === 'object' && value !== null && !Array.isArray(value);
  expect(isKeyedObject, message).toBe(true);
  if (!isKeyedObject) throw new Error(message);
  return value as Record<string, unknown>;
}

test('stores the exact request and response exchange with a resolvable image reference', async () => {
  const traceDirectory = await mkdtemp(join(tmpdir(), 'system-one-evaluation-trace-'));
  try {
    const evidence = createEvidence();
    const suppliedImage = recorded(
      evidence.images[0],
      'the evidence factory supplies one image',
    );
    const questions = createEvaluationTraceQuestions();
    const response = createDecisionResponse();

    // The image store is real here: the descriptor under test must name a file that
    // actually exists and whose bytes reproduce the recorded digest.
    const imageStore = new ImageStore({ directory: join(traceDirectory, 'images') });
    const image = await imageStore.store(suppliedImage);
    const request = createEvaluationTraceRequest({
      state: evidence.text,
      questions,
      images: [image],
    });
    // A nested path exercises the adapter's parent-directory creation.
    const tracePath = join(traceDirectory, 'system1', 'events.jsonl');
    const trace = new JsonLinesEvaluationTrace({ tracePath });

    const evaluatedEntry = createEvaluationTraceEntry({
      evaluationId: 'evaluation-1',
      at: '2026-11-08T10:00:00.000Z',
      sessionId: 'ses_trace_test',
      exchange: createEvaluationTraceExchange({ request, response }),
    });
    const failedEntry = createFailedEvaluationTraceEntry({
      evaluationId: 'evaluation-2',
      exchange: createFailedEvaluationTraceExchange({
        request,
        error: createEvaluationTraceError({
          status: 503,
          code: 'LmStudioGatewayBoundaryError',
          detail: 'LM Studio decision request failed with HTTP 503 Service Unavailable',
        }),
      }),
    });

    await trace.record(evaluatedEntry);
    await trace.record(failedEntry);

    const contents = await readFile(tracePath, 'utf8');
    const lines = contents.split('\n').filter((line) => line.length > 0);
    expect(lines).toHaveLength(2);

    // The successful line carries the request and response bodies themselves, not a
    // summary: the supplied state and questions are preserved verbatim.
    const storedEvaluated = readRecord(
      JSON.parse(recorded(lines[0], 'the evaluated entry produced one line')),
      'the evaluated entry is a JSON object',
    );
    expect(storedEvaluated['schemaVersion']).toBe(4);
    expect(storedEvaluated['evaluationId']).toBe('evaluation-1');
    expect(storedEvaluated['at']).toBe('2026-11-08T10:00:00.000Z');
    expect(storedEvaluated['sessionId']).toBe('ses_trace_test');
    expect(storedEvaluated['outcome']).toStrictEqual({ status: 'evaluated' });

    const storedRequest = readRecord(
      storedEvaluated['request'],
      'the evaluated entry stores its request body',
    );
    expect(storedRequest['model']).toBe(request.model);
    expect(storedRequest['state']).toBe(evidence.text);
    expect(storedRequest['questions']).toStrictEqual(questions);
    expect(storedEvaluated).not.toHaveProperty('error');
    expect(storedEvaluated['response']).toStrictEqual(response);

    // The image data URL is replaced by a descriptor that resolves to the stored bytes,
    // and those bytes hash to the recorded digest.
    const storedImages = storedRequest['images'];
    expect(Array.isArray(storedImages)).toBe(true);
    const storedImage = readRecord(
      recorded(
        Array.isArray(storedImages) ? storedImages[0] : undefined,
        'the request stores one image descriptor',
      ),
      'the stored image descriptor is a JSON object',
    );
    expect(storedImage['mimeType']).toBe(suppliedImage.mimeType);
    expect(storedImage['sha256']).toBe(image.sha256);
    expect(storedImage['bytes']).toBe(image.bytes);
    const storedPath = recorded(
      typeof storedImage['path'] === 'string' ? storedImage['path'] : undefined,
      'the stored image descriptor names the file it wrote',
    );
    const storedBytes = await readFile(storedPath);
    expect(createHash('sha256').update(storedBytes).digest('hex')).toBe(image.sha256);
    expect(storedBytes.length).toBe(image.bytes);

    // The failure line records why no response exists instead of inventing one.
    const storedFailed = readRecord(
      JSON.parse(recorded(lines[1], 'the failed entry produced one line')),
      'the failed entry is a JSON object',
    );
    expect(storedFailed['evaluationId']).toBe('evaluation-2');
    expect(storedFailed).not.toHaveProperty('response');
    expect(storedFailed['error']).toStrictEqual({
      status: 503,
      code: 'LmStudioGatewayBoundaryError',
      detail: 'LM Studio decision request failed with HTTP 503 Service Unavailable',
    });
    expect(storedFailed['outcome']).toStrictEqual({
      status: 'unavailable',
      code: 'gateway_error',
    });

    // The exact content is recorded; the inline payload itself is not, because the bytes
    // live in their content-addressed file.
    expect(contents).toContain(evidence.text);
    expect(contents).not.toContain(suppliedImage.base64);
  } finally {
    await rm(traceDirectory, { recursive: true, force: true });
  }
});
