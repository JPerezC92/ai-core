// Mapping tests of the stdio MCP adapter: a contract-valid payload and a rejected payload
// both carry evaluationId, extra keys are ignored, and a non-string evaluationId is omitted.

import { describe, expect, test } from 'vitest';

import { mapMcpToolResultToOutcome } from './stdio-mcp-client.ts';
import {
  createEvaluatedMcpPayload,
  createEvaluation,
  createEvaluationId,
  createNumericEvaluationIdPayload,
  createRejectedMcpPayload,
} from '../test/helpers/plugin.factory.ts';

describe('stdio MCP result mapping', () => {
  test('maps an evaluated payload evaluationId and ignores extra keys', () => {
    const evaluation = createEvaluation();
    const outcome = mapMcpToolResultToOutcome({
      structuredContent: createEvaluatedMcpPayload(),
    });

    expect(outcome).toStrictEqual({
      status: 'evaluated',
      evaluationId: createEvaluationId(),
      evaluation,
    });
  });

  test('maps a rejected payload evaluationId and ignores extra keys', () => {
    const outcome = mapMcpToolResultToOutcome({
      structuredContent: createRejectedMcpPayload(),
    });

    expect(outcome).toStrictEqual({
      status: 'unavailable',
      code: 'rejected',
      evaluationId: createEvaluationId(),
    });
  });

  test('omits a non-string evaluationId from an otherwise valid evaluation', () => {
    const evaluation = createEvaluation();
    const outcome = mapMcpToolResultToOutcome({
      structuredContent: createNumericEvaluationIdPayload(),
    });

    expect(outcome).toStrictEqual({ status: 'evaluated', evaluation });
  });
});
