// Integration test of the content-addressed image store across its filesystem boundary:
// the same payload stored twice resolves to one file whose bytes hash to the recorded
// descriptor, a different payload gets its own file, and an unusable directory still
// returns the descriptor with the computed identity and `path: null` instead of failing
// the trace. The test owns its temporary directory and removes it afterwards.

import { createHash } from 'node:crypto';
import { mkdtemp, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { expect, test } from 'vitest';

import { createEvidenceImage } from '../test/helpers/odd-evidence.factory.ts';
import { ImageStore } from './image-store.ts';

function sha256Of(base64: string): string {
  return createHash('sha256').update(Buffer.from(base64, 'base64')).digest('hex');
}

test('stores one file per sha256 and deduplicates a repeated payload', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'system-one-image-store-'));
  try {
    const imageDirectory = join(directory, 'images');
    const store = new ImageStore({ directory: imageDirectory });
    const image = createEvidenceImage();

    const first = await store.store(image);
    const second = await store.store(image);

    // The same bytes are content-addressed to the same path and written only once.
    expect(second).toStrictEqual(first);
    const firstPath = first.path;
    expect(firstPath).not.toBeNull();
    if (firstPath === null) throw new Error('the store must report the path it wrote');
    expect(first.sha256).toBe(sha256Of(image.base64));
    expect(await readdir(imageDirectory)).toStrictEqual([`${first.sha256}.png`]);

    const storedBytes = await readFile(firstPath);
    expect(createHash('sha256').update(storedBytes).digest('hex')).toBe(first.sha256);
    expect(storedBytes.length).toBe(first.bytes);

    // A different payload is a different digest and therefore its own file.
    const other = await store.store({ ...image, base64: 'AAECAw==' });
    expect(other.sha256).not.toBe(first.sha256);
    expect((await readdir(imageDirectory)).sort()).toStrictEqual(
      [`${first.sha256}.png`, `${other.sha256}.png`].sort(),
    );
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test('returns the descriptor without a path when the directory cannot be used', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'system-one-image-store-'));
  try {
    // A regular file occupies the configured directory path, so creating the directory
    // and writing beside it both fail on every supported platform.
    const blockedDirectory = join(directory, 'blocked');
    await writeFile(blockedDirectory, 'not a directory');
    const store = new ImageStore({ directory: blockedDirectory });
    const image = createEvidenceImage();

    const descriptor = await store.store(image);

    // The bytes are still identified, and the failure is reported as an absent path so
    // the trace records what it could not persist instead of losing the evaluation.
    expect(descriptor).toStrictEqual({
      mimeType: image.mimeType,
      bytes: Buffer.from(image.base64, 'base64').length,
      sha256: sha256Of(image.base64),
      path: null,
    });
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
