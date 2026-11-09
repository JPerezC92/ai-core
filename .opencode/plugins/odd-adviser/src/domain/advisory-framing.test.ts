import { describe, expect, test } from 'vitest';

import {
  ADVISORY_BLOCK_END,
  ADVISORY_BLOCK_START,
  ADVISORY_UNAVAILABLE_BLOCK_START,
  formatAdvisoryBlock,
} from './advisory-block.ts';
import {
  createAllBelowBarEvaluation,
  createEvaluatedAdvisory,
  createFigurelessEvaluation,
  createStatedZeroConfidenceEvaluation,
  createUnavailableAdvisory,
} from '../test/helpers/plugin.factory.ts';

describe('formatAdvisoryBlock framing', () => {
  test('wraps qualifying findings in the execution-directives markers without a receipt sentence', () => {
    const evaluated = createEvaluatedAdvisory();
    const lines = formatAdvisoryBlock(evaluated).split('\n');
    expect(lines[0]).toBe(ADVISORY_BLOCK_START);
    expect(ADVISORY_BLOCK_START).toBe('=== SYSTEM 1 | EXECUTION DIRECTIVES ===');
    expect(lines).not.toContain(evaluated.advisory);
    expect(lines[lines.length - 3]).toBe(
      'Execute accordingly. Deviate only when stronger evidence or governing constraints justify it.',
    );
    expect(lines[lines.length - 2]).toBe('No new permissions are granted.');
    expect(lines[lines.length - 1]).toBe(ADVISORY_BLOCK_END);
  });

  test('wraps an unavailable advisory in the unavailable markers without directive arrows', () => {
    const unavailable = createUnavailableAdvisory();
    const block = formatAdvisoryBlock(unavailable);
    expect(block.split('\n')).toStrictEqual([
      ADVISORY_UNAVAILABLE_BLOCK_START,
      unavailable.advisory,
      'No new permissions are granted.',
      ADVISORY_BLOCK_END,
    ]);
    expect(block).not.toContain('→');
    expect(block).not.toContain('EXECUTION DIRECTIVES');
  });

  test('returns an empty string when no finding qualifies', () => {
    expect(formatAdvisoryBlock(createEvaluatedAdvisory(createAllBelowBarEvaluation()))).toBe(
      '',
    );
    expect(formatAdvisoryBlock(createEvaluatedAdvisory(createFigurelessEvaluation()))).toBe('');
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createStatedZeroConfidenceEvaluation())),
    ).toBe('');
  });
});
