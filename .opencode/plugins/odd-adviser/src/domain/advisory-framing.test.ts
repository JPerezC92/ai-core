import { describe, expect, test } from 'vitest';
import { ADVISORY_BLOCK_END, ADVISORY_BLOCK_START, formatAdvisoryBlock } from './advisory-block.ts';
import { createEvaluatedAdvisory, createEvaluation, createUnavailableAdvisory } from '../test/helpers/plugin.factory.ts';

describe('formatAdvisoryBlock framing', () => {
  test('wraps every advisory in the block markers around one fixed authority sentence', () => {
    const evaluated = createEvaluatedAdvisory();
    const unavailable = createUnavailableAdvisory();
    const evaluatedLines = formatAdvisoryBlock(evaluated).split('\n');
    const unavailableLines = formatAdvisoryBlock(unavailable).split('\n');
    expect(unavailableLines[0]).toBe(ADVISORY_BLOCK_START);
    expect(unavailableLines[1]).toBe(unavailable.advisory);
    expect(unavailableLines[2]?.length).toBeGreaterThan(0);
    expect(unavailableLines[3]).toBe(ADVISORY_BLOCK_END);
    expect(evaluatedLines[0]).toBe(ADVISORY_BLOCK_START);
    expect(evaluatedLines[1]).toBe(evaluated.advisory);
    expect(evaluatedLines[evaluatedLines.length - 2]).toBe(unavailableLines[2]);
    expect(evaluatedLines[evaluatedLines.length - 1]).toBe(ADVISORY_BLOCK_END);
    const answerCount = Object.keys(createEvaluation().answers).length;
    expect(evaluatedLines).toHaveLength(unavailableLines.length + answerCount);
    expect(unavailableLines[2]).not.toBe(evaluated.advisory);
    expect(evaluatedLines[evaluatedLines.length - 2]).not.toBe(evaluated.advisory);
  });
});
