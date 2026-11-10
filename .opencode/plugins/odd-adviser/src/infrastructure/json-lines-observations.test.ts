// Integration test of the JSON Lines observation adapter: two observations are appended
// into a fresh temporary directory and read back in order, and a caller object that
// carries request state, tool arguments and a provider body stores only the declared
// observation fields. The test owns its temporary directory (T18).

import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { expect, test } from 'vitest';

import { JsonLinesObservations } from './json-lines-observations.ts';
import {
  createContentBearingObservation,
  createObservationRecord,
  createToolId,
} from '../test/helpers/plugin.factory.ts';

function readObservationLine(
  lines: ReadonlyArray<string>,
  index: number,
): Record<string, unknown> {
  const line = lines[index];
  expect(line, `the adapter wrote line ${index + 1}`).toBeDefined();
  if (line === undefined) throw new Error(`the adapter wrote line ${index + 1}`);
  const parsed: unknown = JSON.parse(line);
  const isKeyedObject = typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed);
  expect(isKeyedObject, 'a stored observation is a JSON object').toBe(true);
  if (!isKeyedObject) throw new Error('a stored observation is a JSON object');
  return parsed as Record<string, unknown>;
}

test('appends each observation as one JSON line in the order it was recorded', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'odd-adviser-observations-'));
  try {
    const first = createObservationRecord({ reportedFooter: 'none' });
    const second = createObservationRecord({
      reportedFooter: 'applied_line',
      tools: [{ id: createToolId(), status: 'completed' }],
    });
    const eventPath = join(directory, 'system1', 'events.jsonl');
    const observations = new JsonLinesObservations({ eventPath });

    await observations.record(first);
    await observations.record(second);

    const contents = await readFile(eventPath, 'utf8');
    const lines = contents.split('\n').filter((line) => line.length > 0);
    expect(lines).toHaveLength(2);
    expect(readObservationLine(lines, 0)).toStrictEqual(first);
    expect(readObservationLine(lines, 1)).toStrictEqual(second);
    expect(readObservationLine(lines, 0)['recordType']).toBe('observation');
    expect(readObservationLine(lines, 0)['assessment']).toBe('not_observed');
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('stores none of the request state, tool arguments or provider body a caller attaches', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'odd-adviser-observations-'));
  try {
    const { observation, forbiddenFragments } = createContentBearingObservation();
    const eventPath = join(directory, 'system1', 'events.jsonl');

    await new JsonLinesObservations({ eventPath }).record(observation);

    const contents = await readFile(eventPath, 'utf8');
    const stored = readObservationLine(
      contents.split('\n').filter((line) => line.length > 0),
      0,
    );
    expect(stored).toStrictEqual(observation);
    expect(stored).not.toHaveProperty('request');
    expect(stored).not.toHaveProperty('args');
    expect(stored).not.toHaveProperty('providerBody');
    expect(stored).not.toHaveProperty('handling');
    for (const fragment of forbiddenFragments) {
      expect(contents).not.toContain(fragment);
    }
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
