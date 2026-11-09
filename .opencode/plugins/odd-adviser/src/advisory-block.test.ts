// Behaviour tests of the portable System 1 advisory edge's block: the markers that frame every
// delivered advisory, the one fixed authority sentence a block carries, and the question lines
// that report each answered choice with the figure it was made with. The delivery-path check that
// a block built from a real evaluation repeats no supplied text lives in `evaluate-evidence.test.ts`,
// where that evaluation is made. No case spawns a process or reaches a model endpoint.

import { describe, expect, test } from 'vitest';

import {
  ADVISORY_BLOCK_END,
  ADVISORY_BLOCK_START,
  formatAdvisoryBlock,
} from './index.ts';
import {
  createAnswerWithoutConfidence,
  createDerivedConfidenceEvaluation,
  createEvaluatedAdvisory,
  createEvaluation,
  createEvaluationWithAnswers,
  createFigurelessEvaluation,
  createStatedZeroConfidenceEvaluation,
  createUnavailableAdvisory,
  createWeakSignalEvaluation,
  createWeakSignalThresholdEvaluation,
} from './test/helpers/plugin.factory.ts';

// The one authority sentence every block carries, read from a block the adapter itself emits, so
// a case pins its position and its constancy without a second copy of production text (S7).
function authoritySentence(): string {
  const lines = formatAdvisoryBlock(createUnavailableAdvisory()).split('\n');
  const sentence = lines[lines.length - 2];
  if (sentence === undefined) {
    throw new Error('the unavailable block carries no authority sentence');
  }
  return sentence;
}

describe('formatAdvisoryBlock', () => {
  test('wraps every advisory in the block markers around one fixed authority sentence', () => {
    const evaluated = createEvaluatedAdvisory();
    const unavailable = createUnavailableAdvisory();

    const evaluatedLines = formatAdvisoryBlock(evaluated).split('\n');
    const unavailableLines = formatAdvisoryBlock(unavailable).split('\n');

    // The frame is the same for both branches: the markers enclose the block, the advisory's own
    // sentence follows the start marker and the one authority sentence sits before the end one.
    expect(unavailableLines[0]).toBe(ADVISORY_BLOCK_START);
    expect(unavailableLines[1]).toBe(unavailable.advisory);
    expect(unavailableLines[2]?.length).toBeGreaterThan(0);
    expect(unavailableLines[3]).toBe(ADVISORY_BLOCK_END);

    expect(evaluatedLines[0]).toBe(ADVISORY_BLOCK_START);
    expect(evaluatedLines[1]).toBe(evaluated.advisory);
    expect(evaluatedLines[evaluatedLines.length - 2]).toBe(unavailableLines[2]);
    expect(evaluatedLines[evaluatedLines.length - 1]).toBe(ADVISORY_BLOCK_END);

    // An evaluated block adds exactly one line per answered question between its own sentence and
    // the authority line, and nothing else.
    const answerCount = Object.keys(createEvaluation().answers).length;
    expect(evaluatedLines).toHaveLength(unavailableLines.length + answerCount);

    // The authority sentence is identical for every advisory: it is never derived from the
    // delivered text and never varies with it (S7).
    expect(unavailableLines[2]).not.toBe(evaluated.advisory);
    expect(evaluatedLines[evaluatedLines.length - 2]).not.toBe(evaluated.advisory);
  });
});

// R1, R2, R11: a block that only reports that an answer arrived is a receipt. These cases pin the
// lines that carry the question, the option the payload chose, the figure that choice was made
// with and the mark of a weak signal, so the model reading the block sees what was chosen.
describe('advisory question lines', () => {
  test('reports one line per answered question with the option and its two-decimal confidence', () => {
    const advisory = createEvaluatedAdvisory(createWeakSignalEvaluation());

    const block = formatAdvisoryBlock(advisory);

    expect(block.split('\n')).toStrictEqual([
      ADVISORY_BLOCK_START,
      advisory.advisory,
      'scope_changed → present (0.82)',
      'user_only_decision → absent (0.41) ⚠ weak signal',
      authoritySentence(),
      ADVISORY_BLOCK_END,
    ]);
  });

  test('marks a figure below the weak-signal bound and leaves the bound itself unmarked', () => {
    const advisory = createEvaluatedAdvisory(createWeakSignalThresholdEvaluation());

    expect(formatAdvisoryBlock(advisory).split('\n')).toStrictEqual([
      ADVISORY_BLOCK_START,
      advisory.advisory,
      'scope_changed → present (0.60)',
      'user_only_decision → absent (0.59) ⚠ weak signal',
      authoritySentence(),
      ADVISORY_BLOCK_END,
    ]);
  });

  test('derives the figure from the largest stated probability when no confidence is stated', () => {
    const advisory = createEvaluatedAdvisory(createDerivedConfidenceEvaluation());

    expect(formatAdvisoryBlock(advisory).split('\n')).toStrictEqual([
      ADVISORY_BLOCK_START,
      advisory.advisory,
      'scope_changed → present (0.74)',
      'user_only_decision → absent (0.58) ⚠ weak signal',
      // The chosen option here is not the most probable one, so this line reports the largest
      // stated probability rather than the probability of the option the payload chose (R11).
      'visual_evidence → present (0.55) ⚠ weak signal',
      authoritySentence(),
      ADVISORY_BLOCK_END,
    ]);
  });

  // `visual_evidence` above is not a question profile v4 asks the model, so the same derivation is
  // demonstrated once on a question the model actually answers: the chosen option is again not the
  // most probable one, and its own probability would print `0.44` instead of the stated `0.56`.
  test('reports the largest stated probability on an answered question whose chosen option is not the most probable', () => {
    const advisory = createEvaluatedAdvisory(
      createEvaluationWithAnswers({
        user_only_decision: createAnswerWithoutConfidence('absent', {
          present: 0.56,
          absent: 0.44,
        }),
      }),
    );

    expect(formatAdvisoryBlock(advisory).split('\n')).toStrictEqual([
      ADVISORY_BLOCK_START,
      advisory.advisory,
      'user_only_decision → absent (0.56) ⚠ weak signal',
      authoritySentence(),
      ADVISORY_BLOCK_END,
    ]);
  });

  test('prints the choice without a figure when the answer states neither', () => {
    const advisory = createEvaluatedAdvisory(createFigurelessEvaluation());

    expect(formatAdvisoryBlock(advisory).split('\n')).toStrictEqual([
      ADVISORY_BLOCK_START,
      advisory.advisory,
      'visual_evidence → absent (n/a)',
      authoritySentence(),
      ADVISORY_BLOCK_END,
    ]);
  });

  test('prints a stated zero confidence as its own figure rather than as an absence', () => {
    const advisory = createEvaluatedAdvisory(createStatedZeroConfidenceEvaluation());

    // A stated `0` is a figure the payload gave, not a missing one: a falsy test would print the
    // same `n/a` the absent case prints and hide the difference (R11, R12).
    expect(formatAdvisoryBlock(advisory).split('\n')).toStrictEqual([
      ADVISORY_BLOCK_START,
      advisory.advisory,
      'visual_evidence → present (0.00) ⚠ weak signal',
      authoritySentence(),
      ADVISORY_BLOCK_END,
    ]);
  });

  test('emits no question line for an unavailable evaluation', () => {
    const advisory = createUnavailableAdvisory();

    expect(advisory.status).toBe('unavailable');
    expect(formatAdvisoryBlock(advisory).split('\n')).toStrictEqual([
      ADVISORY_BLOCK_START,
      advisory.advisory,
      authoritySentence(),
      ADVISORY_BLOCK_END,
    ]);
    // Nothing in an unavailable block can be mistaken for an answered question.
    expect(formatAdvisoryBlock(advisory)).not.toContain('→');
  });
});
