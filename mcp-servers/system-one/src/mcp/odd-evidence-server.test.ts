// Unit test of the portable MCP surface. A built `McpServer` exposes no public handle
// for invoking a registered tool handler directly (its registration state is private),
// so each case connects a real SDK client to a freshly built server over the SDK's
// in-memory linked transport pair and calls the registered `evaluate_odd_evidence` tool
// through the protocol. The evaluation operation is doubled, so no network and no model
// endpoint are involved.

import { Client } from '@modelcontextprotocol/client';
import { InMemoryTransport } from '@modelcontextprotocol/server';
import { expect, test } from 'vitest';

import { createOddEvidenceServer } from './odd-evidence-server.ts';
import type { OddEvidenceEvaluator } from './odd-evidence-server.ts';
import {
  createEvaluateToolImage,
  createEvaluateToolInput,
  createEvaluationResult,
  createOverLengthBase64ToolInput,
  createOverLimitImagesToolInput,
  createRecordingEvaluateOddEvidence,
  createServerOptions,
} from '../test/helpers/mcp.factory.ts';
import type { EvaluateToolInput } from '../test/helpers/mcp.factory.ts';

// Hermetic per-call harness: one server, one linked transport pair, one client. Closing
// both ends in `finally` keeps each case independent of every other case.
async function callEvaluateTool(
  evaluateOddEvidence: OddEvidenceEvaluator,
  input: EvaluateToolInput,
) {
  const server = createOddEvidenceServer({ evaluateOddEvidence }, createServerOptions());
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: 'odd-evidence-test', version: '0.0.0' });

  await server.connect(serverTransport);
  await client.connect(clientTransport);
  try {
    return await client.callTool({
      name: 'evaluate_odd_evidence',
      arguments: { text: input.text, images: input.images },
    });
  } finally {
    await client.close();
    await server.close();
  }
}

test('delegates the supplied evidence to the evaluation once and returns its result', async () => {
  const evaluate = createRecordingEvaluateOddEvidence();
  const input = createEvaluateToolInput();

  const result = await callEvaluateTool(evaluate, input);

  expect(result.isError).toBeFalsy();
  expect(result.structuredContent).toStrictEqual(createEvaluationResult());
  expect(evaluate.calls).toStrictEqual([
    {
      text: input.text,
      images: input.images,
      expectedModel: createServerOptions().expectedModel,
    },
  ]);
});

test('rejects an image array over the advertised limit without evaluating', async () => {
  const evaluate = createRecordingEvaluateOddEvidence();

  const result = await callEvaluateTool(evaluate, createOverLimitImagesToolInput());

  expect(result.isError).toBe(true);
  expect(evaluate.calls).toStrictEqual([]);
});

test('rejects a base64 payload over the advertised length without evaluating', async () => {
  const evaluate = createRecordingEvaluateOddEvidence();

  const result = await callEvaluateTool(evaluate, createOverLengthBase64ToolInput());

  expect(result.isError).toBe(true);
  expect(evaluate.calls).toStrictEqual([]);
});

test('returns no supplied text or image bytes in the tool payload', async () => {
  const evaluate = createRecordingEvaluateOddEvidence();
  const image = createEvaluateToolImage();
  const input = createEvaluateToolInput(image);

  const result = await callEvaluateTool(evaluate, input);

  expect(result.structuredContent).toStrictEqual(createEvaluationResult());
  const payload = JSON.stringify(result);
  expect(payload).not.toContain(input.text);
  expect(payload).not.toContain(image.base64);
});
