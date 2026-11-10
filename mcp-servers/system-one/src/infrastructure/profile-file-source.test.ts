// Integration test of the profile file source across its filesystem boundary: the package's
// own profile document is read through the adapter and the returned value is the validated
// profile, so the assertions cover the outside-document to domain handoff the adapter owns
// and how an unreadable path or unparsable contents surfaces. No network, environment value,
// temporary file or developer path participates.

import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { expect, test } from 'vitest';

import { ProfileFileSource, ProfileFileSourceBoundaryError } from './profile-file-source.ts';

type ProfileFilePaths = {
  readonly profilePath: string;
  readonly missingProfilePath: string;
  // A shipped document that is valid JSON but is not a question profile, so the adapter's
  // validation step can be observed without writing a fixture file.
  readonly nonProfileJsonPath: string;
  // A shipped document whose contents are not JSON at all: the read succeeds and the parse
  // step is the only one left to fail, so the parse boundary outcome is observable through
  // the same shipped-document route rather than a fixture file.
  readonly malformedJsonPath: string;
  readonly expectedProfileId: string;
  readonly expectedProfileVersion: number;
};

// Paths are derived from this module's location, so the suite reads the package's own
// profile document rather than a developer's machine state. The missing case names a
// document the package never ships, and the malformed case reads the package's own YAML
// lockfile, which is readable text that cannot parse as JSON.
function createProfileFilePaths(): ProfileFilePaths {
  const profilesDirectory = fileURLToPath(new URL('../../profiles/', import.meta.url));
  const profileId = 'odd-evidence-v4';
  return {
    profilePath: join(profilesDirectory, `${profileId}.json`),
    missingProfilePath: join(profilesDirectory, `${profileId}.missing.json`),
    nonProfileJsonPath: fileURLToPath(new URL('../../package.json', import.meta.url)),
    malformedJsonPath: fileURLToPath(new URL('../../pnpm-lock.yaml', import.meta.url)),
    expectedProfileId: profileId,
    expectedProfileVersion: 4,
  };
}

test('loads the package profile as the validated profile, not the raw document', async () => {
  const paths = createProfileFilePaths();
  const source = new ProfileFileSource({ profilePath: paths.profilePath });

  const loaded = await source.load();

  // The adapter performs the outside-document mapping, so the port hands back a validated
  // profile. The assertion narrows explicitly, so a shipped document that stops validating
  // reports the domain validator's own reason instead of a bare `false`.
  if (!loaded.ok) {
    throw new Error(`the package profile must validate: ${loaded.reason}`);
  }
  expect(loaded.profile.profileId).toBe(paths.expectedProfileId);
  expect(loaded.profile.version).toBe(paths.expectedProfileVersion);
  // The shipped document itself declares exactly the two states its input reaches, so no
  // question in the loaded profile carries a third one.
  for (const question of Object.values(loaded.profile.questions)) {
    expect(Object.keys(question.criteria).sort()).toStrictEqual(['absent', 'present']);
  }
});

test('returns the domain rejection for valid JSON that is not a question profile', async () => {
  const paths = createProfileFilePaths();
  const source = new ProfileFileSource({ profilePath: paths.nonProfileJsonPath });

  const loaded = await source.load();

  // Validation belongs to the adapter's single mapping step, so a document that cannot be a
  // profile is a typed rejection at this boundary rather than a raw value the caller must
  // validate. The reason is the domain validator's own text, unchanged.
  expect(loaded).toStrictEqual({
    ok: false,
    reason: 'Invalid question profile metadata or question IDs',
  });
});

test('throws the read boundary error when the configured file is missing', async () => {
  const paths = createProfileFilePaths();
  const source = new ProfileFileSource({ profilePath: paths.missingProfilePath });

  await expect(source.load()).rejects.toSatisfy(
    (error: unknown) => error instanceof ProfileFileSourceBoundaryError && error.step === 'read',
    'a missing profile file surfaces the read boundary exception, never a domain result',
  );
});

test('throws the parse boundary error when the configured file is not JSON', async () => {
  const paths = createProfileFilePaths();
  const source = new ProfileFileSource({ profilePath: paths.malformedJsonPath });

  // The read step succeeds on this document, so the only boundary step that can fail is the
  // parse. Both halves matter: a raw `SyntaxError` escaping the adapter is not this type,
  // and the adapter's other boundary outcome reports `step === 'read'`.
  await expect(source.load()).rejects.toSatisfy(
    (error: unknown) => error instanceof ProfileFileSourceBoundaryError && error.step === 'parse',
    'unparsable contents surface the parse boundary exception, never the read one',
  );
});
