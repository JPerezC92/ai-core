// Behaviour tests of the portable System 1 advisory edge's frozen execution-directive lines:
// each injectable present/absent cell, the inclusion bars, and combinations that must not
// drop a continuation or print a below-bar visual line. Framing of the block markers lives
// in `advisory-framing.test.ts`. No case spawns a process or reaches a model endpoint.

import { describe, expect, test } from 'vitest';

import {
  ADVISORY_BLOCK_END,
  ADVISORY_BLOCK_START,
  formatAdvisoryBlock,
} from './advisory-block.ts';
import {
  createAbsentScopeWithPresentUserOnlyEvaluation,
  createEvaluatedAdvisory,
  createGuidanceAbsentAtBarEvaluation,
  createGuidanceAbsentBelowBarEvaluation,
  createGuidanceWithSubBarVisualEvaluation,
  createInterruptPresentAtBarEvaluation,
  createInterruptPresentBelowBarEvaluation,
  createScopeChangedAbsentEvaluation,
  createScopeChangedPresentEvaluation,
  createUserOnlyAbsentEvaluation,
  createUserOnlyPresentEvaluation,
  createVisualEvidenceAbsentAtCertaintyEvaluation,
  createVisualPresentEvaluation,
} from '../test/helpers/plugin.factory.ts';

const EXECUTE_ACCORDINGLY =
  'Execute accordingly. Deviate only when stronger evidence or governing constraints justify it.';
const NO_NEW_PERMISSIONS = 'No new permissions are granted.';
const ACTION_SCOPE_CHANGED_PRESENT =
  'Potential new requirement in this message. Check existing context and authorization before expanding. Pause only work that still needs extra authorization.';
const ACTION_SCOPE_CHANGED_ABSENT =
  'No new requirement in this message. Continue the established task without unnecessary renegotiation, respecting actual context and authorization.';
const ACTION_USER_ONLY_DECISION_PRESENT =
  'A reserved decision is in this message. Ask that specific question. Continue independent authorized work; do not freeze the whole turn.';
const ACTION_USER_ONLY_DECISION_ABSENT =
  'No reserved decision in this message. Continue already-authorized work. Do not ask for redundant approval. Not new permission.';
const ACTION_VISUAL_EVIDENCE_PRESENT = 'Image attached. Inspect it before answering.';

function expectedDirectives(lines: ReadonlyArray<string>): ReadonlyArray<string> {
  return [
    ADVISORY_BLOCK_START,
    ...lines,
    EXECUTE_ACCORDINGLY,
    NO_NEW_PERMISSIONS,
    ADVISORY_BLOCK_END,
  ];
}

describe('advisory question lines', () => {
  test('emits the frozen action for scope_changed present', () => {
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createScopeChangedPresentEvaluation())).split(
        '\n',
      ),
    ).toStrictEqual(
      expectedDirectives([
        'scope_changed → present (0.82)',
        `→ ${ACTION_SCOPE_CHANGED_PRESENT}`,
      ]),
    );
  });

  test('emits the frozen action for scope_changed absent', () => {
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createScopeChangedAbsentEvaluation())).split(
        '\n',
      ),
    ).toStrictEqual(
      expectedDirectives([
        'scope_changed → absent (0.98)',
        `→ ${ACTION_SCOPE_CHANGED_ABSENT}`,
      ]),
    );
  });

  test('emits the frozen action for user_only_decision present', () => {
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createUserOnlyPresentEvaluation())).split('\n'),
    ).toStrictEqual(
      expectedDirectives([
        'user_only_decision → present (0.94)',
        `→ ${ACTION_USER_ONLY_DECISION_PRESENT}`,
      ]),
    );
  });

  test('emits the frozen action for user_only_decision absent', () => {
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createUserOnlyAbsentEvaluation())).split('\n'),
    ).toStrictEqual(
      expectedDirectives([
        'user_only_decision → absent (0.94)',
        `→ ${ACTION_USER_ONLY_DECISION_ABSENT}`,
      ]),
    );
  });

  test('emits the frozen action for visual_evidence present', () => {
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createVisualPresentEvaluation())).split('\n'),
    ).toStrictEqual(
      expectedDirectives([
        'visual_evidence → present (0.60)',
        `→ ${ACTION_VISUAL_EVIDENCE_PRESENT}`,
      ]),
    );
  });

  test('omits a below-bar visual present while keeping the two guidance absents', () => {
    const block = formatAdvisoryBlock(
      createEvaluatedAdvisory(createGuidanceWithSubBarVisualEvaluation()),
    );

    expect(block.split('\n')).toStrictEqual(
      expectedDirectives([
        'scope_changed → absent (0.98)',
        `→ ${ACTION_SCOPE_CHANGED_ABSENT}`,
        'user_only_decision → absent (0.94)',
        `→ ${ACTION_USER_ONLY_DECISION_ABSENT}`,
      ]),
    );
    expect(block).not.toContain('visual_evidence');
  });

  test('emits both a guidance absent and an interrupt present rather than cancelling the ask', () => {
    expect(
      formatAdvisoryBlock(
        createEvaluatedAdvisory(createAbsentScopeWithPresentUserOnlyEvaluation()),
      ).split('\n'),
    ).toStrictEqual(
      expectedDirectives([
        'scope_changed → absent (0.98)',
        `→ ${ACTION_SCOPE_CHANGED_ABSENT}`,
        'user_only_decision → present (0.80)',
        `→ ${ACTION_USER_ONLY_DECISION_PRESENT}`,
      ]),
    );
  });

  test('omits interrupt present and guidance absent below their bars and includes them on the bars', () => {
    expect(
      formatAdvisoryBlock(
        createEvaluatedAdvisory(createInterruptPresentBelowBarEvaluation()),
      ),
    ).toBe('');
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createGuidanceAbsentBelowBarEvaluation())),
    ).toBe('');
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createInterruptPresentAtBarEvaluation())).split(
        '\n',
      ),
    ).toStrictEqual(
      expectedDirectives([
        'scope_changed → present (0.80)',
        `→ ${ACTION_SCOPE_CHANGED_PRESENT}`,
      ]),
    );
    expect(
      formatAdvisoryBlock(createEvaluatedAdvisory(createGuidanceAbsentAtBarEvaluation())).split(
        '\n',
      ),
    ).toStrictEqual(
      expectedDirectives([
        'user_only_decision → absent (0.60)',
        `→ ${ACTION_USER_ONLY_DECISION_ABSENT}`,
      ]),
    );
  });

  test('omits visual_evidence absent even at certainty', () => {
    expect(
      formatAdvisoryBlock(
        createEvaluatedAdvisory(createVisualEvidenceAbsentAtCertaintyEvaluation()),
      ),
    ).toBe('');
  });
});
