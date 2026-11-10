// Unit tests of assistant-completion classification: only a user-facing stop is complete;
// tool steps, text-part events, truncation, and generic sentinels are not.

import { describe, expect, test } from 'vitest';

import {
  classifyAssistantCompletion,
  extractReceivedText,
  isAssistantResponseComplete,
} from './observation.ts';
import {
  createAppliedFooterLine,
  createBareDoneObject,
  createBinaryFrame,
  createChoicesDeltaFrame,
  createCompletedTypeFrame,
  createDoneFrame,
  createFinishReasonFrame,
  createLengthFinishFrame,
  createOutputTextDoneFrame,
  createResponseCompletedFunctionCallFrame,
  createResponseCompletedMessageFrame,
  createToolCallsFinishFrame,
  createUnmarkedAssistantText,
} from '../test/helpers/plugin.factory.ts';

describe('assistant completion classification', () => {
  test('treats only a user-facing stop as complete, not intermediate or generic signals', () => {
    expect(isAssistantResponseComplete(createAppliedFooterLine())).toBe(false);
    expect(isAssistantResponseComplete(createChoicesDeltaFrame(createAppliedFooterLine()))).toBe(
      false,
    );
    expect(isAssistantResponseComplete(createFinishReasonFrame())).toBe(true);
    expect(isAssistantResponseComplete(createResponseCompletedMessageFrame())).toBe(true);
    expect(isAssistantResponseComplete(createToolCallsFinishFrame())).toBe(false);
    expect(isAssistantResponseComplete(createOutputTextDoneFrame())).toBe(false);
    expect(isAssistantResponseComplete(createResponseCompletedFunctionCallFrame())).toBe(false);
    expect(isAssistantResponseComplete(createLengthFinishFrame())).toBe(false);
    expect(isAssistantResponseComplete(createDoneFrame())).toBe(false);
    expect(isAssistantResponseComplete(createCompletedTypeFrame())).toBe(false);
    expect(isAssistantResponseComplete(createBareDoneObject())).toBe(false);
    expect(isAssistantResponseComplete(createBinaryFrame())).toBe(false);

    expect(classifyAssistantCompletion(createToolCallsFinishFrame())).toBe('tool_step');
    expect(classifyAssistantCompletion(createOutputTextDoneFrame())).toBe('text_part');
    expect(classifyAssistantCompletion(createResponseCompletedFunctionCallFrame())).toBe(
      'tool_step',
    );
    expect(classifyAssistantCompletion(createLengthFinishFrame())).toBe('truncated');
    expect(classifyAssistantCompletion(createDoneFrame())).toBe('uninspectable');
    expect(classifyAssistantCompletion(createFinishReasonFrame())).toBe('user_facing');
  });

  test('classifies stop-with-content as user_facing and extracts that text', () => {
    const content = createUnmarkedAssistantText();
    const frame = createFinishReasonFrame(content);

    expect(classifyAssistantCompletion(frame)).toBe('user_facing');
    expect(extractReceivedText(frame)).toBe(content);
    expect(isAssistantResponseComplete(frame)).toBe(true);
  });
});
