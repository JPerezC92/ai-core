// Unit tests of reconstructed-footer classification: a marker split across frames is
// recovered from the rolling window, mixed markers are distinct from a single line, and
// binary frames contribute no text.

import { describe, expect, test } from 'vitest';

import {
  OBSERVATION_TEXT_WINDOW_CHARS,
  appendRollingText,
  classifyReportedFooter,
  extractReceivedText,
} from './observation.ts';
import {
  createAppliedFooterLine,
  createBinaryFrame,
  createOverflowWindowBuffer,
  createOverflowWindowChunk,
  createChoicesDeltaFrame,
  createCompletedTypeFrame,
  createDeltaFrame,
  createFinishReasonFrame,
  createOverriddenFooterLine,
  createSplitFooterPrefix,
  createSplitFooterSuffix,
  createTextFrame,
  createUnmarkedAssistantText,
} from '../test/helpers/plugin.factory.ts';

describe('reconstructed footer classification', () => {
  test('classifies a footer marker that is split across frames', () => {
    const reconstructed = appendRollingText(
      createSplitFooterPrefix(),
      createSplitFooterSuffix(),
    );

    expect(classifyReportedFooter(reconstructed)).toBe('applied_line');
  });

  test('classifies mixed applied and overridden markers', () => {
    const reconstructed = `${createAppliedFooterLine()}\n${createOverriddenFooterLine()}`;

    expect(classifyReportedFooter(reconstructed)).toBe('mixed');
    expect(classifyReportedFooter(createAppliedFooterLine())).toBe('applied_line');
    expect(classifyReportedFooter(createOverriddenFooterLine())).toBe('overridden_line');
    expect(classifyReportedFooter(createUnmarkedAssistantText())).toBe('none');
  });

  test('keeps only the trailing window and extracts text frames', () => {
    const overflow = appendRollingText(
      createOverflowWindowBuffer(),
      createOverflowWindowChunk(),
    );
    expect(overflow).toHaveLength(OBSERVATION_TEXT_WINDOW_CHARS);
    expect(overflow.endsWith(createOverflowWindowChunk())).toBe(true);

    expect(extractReceivedText(createAppliedFooterLine())).toBe(createAppliedFooterLine());
    expect(extractReceivedText(createChoicesDeltaFrame(createAppliedFooterLine()))).toBe(
      createAppliedFooterLine(),
    );
    expect(extractReceivedText(createDeltaFrame(createOverriddenFooterLine()))).toBe(
      createOverriddenFooterLine(),
    );
    expect(extractReceivedText(createTextFrame(createAppliedFooterLine()))).toBe(
      createAppliedFooterLine(),
    );
    expect(extractReceivedText(createBinaryFrame())).toBeNull();
    expect(extractReceivedText(createCompletedTypeFrame())).toBeNull();
    expect(extractReceivedText(createFinishReasonFrame())).toBeNull();
  });
});
