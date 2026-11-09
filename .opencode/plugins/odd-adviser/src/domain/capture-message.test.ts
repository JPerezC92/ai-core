// Behaviour tests of the portable System 1 advisory edge's capture step: the host's admitted parts
// narrowed to the chat text and the inline base64 images they carry, with every other location
// ignored rather than read. No case spawns a process or reaches a model endpoint.

import { describe, expect, test } from 'vitest';

import { captureMessage } from './capture-message.ts';
import {
  createAdmittedParts,
  createCapturedMessage,
} from '../test/helpers/plugin.factory.ts';

describe('captureMessage', () => {
  test('captures the text and only the inline base64 image of the admitted parts', () => {
    const captured = captureMessage(createAdmittedParts());

    expect(captured).toStrictEqual(createCapturedMessage());
  });
});
