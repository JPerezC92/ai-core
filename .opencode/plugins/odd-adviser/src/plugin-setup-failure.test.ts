import { expect, test } from 'vitest';

import { createFailedSetup } from './test/helpers/plugin.factory.ts';

test('records a failed hook registration and returns a callable cleanup', async () => {
  const failed = await createFailedSetup();

  expect(failed.registrations).toStrictEqual(['prompt']);
  expect(failed.events.map((event) => event.stage)).toStrictEqual(['setup_failed']);
  await expect(failed.cleanup()).resolves.toBeUndefined();
});
