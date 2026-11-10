// Integration test of the JSON Lines plugin event adapter across its filesystem boundary: two
// lifecycle events are appended into a fresh temporary directory and read back as JSON lines in
// the order they were recorded, and an event built from a caller object that carries supplied
// text and image bytes stores only the declared content-free fields. The test owns its
// temporary directory and removes it afterwards; it reads no clock and writes no repository
// path (T18).

import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { expect, test } from 'vitest';

import { JsonLinesPluginEvents } from './json-lines-plugin-events.ts';
import {
  createContentBearingPluginEvent,
  createPluginEvents,
} from '../test/helpers/plugin.factory.ts';

// A parsed line is `any`; this narrows it to the keyed object the stored contract requires, so
// each assertion reads a real field rather than skipping the shape check.
function readEventLine(lines: ReadonlyArray<string>, index: number): Record<string, unknown> {
  const line = lines[index];
  expect(line, `the adapter wrote line ${index + 1}`).toBeDefined();
  if (line === undefined) throw new Error(`the adapter wrote line ${index + 1}`);
  const parsed: unknown = JSON.parse(line);
  const isKeyedObject = typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed);
  expect(isKeyedObject, 'a stored event is a JSON object').toBe(true);
  if (!isKeyedObject) throw new Error('a stored event is a JSON object');
  return parsed as Record<string, unknown>;
}

test('appends each event as one JSON line in the order it was recorded', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'odd-adviser-plugin-events-'));
  try {
    const [first, second] = createPluginEvents();
    // A nested path exercises the adapter's parent-directory creation.
    const eventPath = join(directory, 'system1', 'plugin.jsonl');
    const events = new JsonLinesPluginEvents({ eventPath });

    await events.record(first);
    await events.record(second);

    const contents = await readFile(eventPath, 'utf8');
    const lines = contents.split('\n').filter((line) => line.length > 0);
    expect(lines).toHaveLength(2);

    // The order the stages were reached in is the order the file carries, and each line is
    // exactly its event: no field is added, dropped or renamed.
    const storedFirst = readEventLine(lines, 0);
    const storedSecond = readEventLine(lines, 1);
    expect(storedFirst).toStrictEqual(first);
    expect(storedSecond).toStrictEqual(second);
    expect(storedFirst['stage']).toBe('candidate_found');
    expect(storedFirst['textChars']).toBe(first.textChars);
    expect(storedSecond['stage']).toBe('evaluate_finished');
    expect(storedSecond['code']).toBe(second.code);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('stores none of the supplied text or image bytes a caller attaches to an event', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'odd-adviser-plugin-events-'));
  try {
    const { event, forbiddenFragments } = createContentBearingPluginEvent();
    const eventPath = join(directory, 'system1', 'plugin.jsonl');

    await new JsonLinesPluginEvents({ eventPath }).record(event);

    const contents = await readFile(eventPath, 'utf8');
    const lines = contents.split('\n').filter((line) => line.length > 0);
    expect(lines).toHaveLength(1);

    // The line carries exactly the declared fields the caller stated; the two content fields
    // the caller attached have no field to travel in (S9).
    expect(readEventLine(lines, 0)).toStrictEqual(event);
    for (const fragment of forbiddenFragments) {
      expect(contents).not.toContain(fragment);
    }
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
