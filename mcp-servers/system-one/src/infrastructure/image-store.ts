// Infrastructure adapter for the domain `EvaluationTraceImageStore` port: decodes one
// supplied image, names the file by its sha256 digest and writes the bytes only when that
// name is missing, so repeated payloads share one file. The descriptor it returns is what
// the recorded request carries instead of the wire data URL, so an operator can find the
// exact bytes behind a request without the trace line containing them.
//
// The write is best-effort by contract: an unusable directory or a refused write still
// returns the descriptor with the computed mime type, byte count and digest but
// `path: null`, because tracing must never fail the evaluation it describes. The
// directory is supplied by the host; this adapter applies no path policy.

import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

import type {
  EvaluationTraceImageDescriptor,
  EvaluationTraceImageStore,
} from '../domain/evaluation-trace.ts';
import type { OddEvidenceImage } from '../domain/odd-evidence.ts';

export type ImageStoreOptions = {
  // Absolute path supplied by the host. This adapter applies no path policy: the host
  // configuration owns which directory is written.
  readonly directory: string;
};

// The media types this adapter knows by name; any other subtype is sanitized into a safe
// suffix instead of being trusted as a path fragment.
const extensionByMimeType: Readonly<Record<string, string>> = {
  'image/png': 'png',
  'image/jpeg': 'jpg',
  'image/gif': 'gif',
  'image/webp': 'webp',
  'image/avif': 'avif',
  'image/bmp': 'bmp',
  'image/svg+xml': 'svg',
};

function extensionFor(mimeType: string): string {
  const known = extensionByMimeType[mimeType.toLowerCase()];
  if (known !== undefined) return known;
  const subtype = mimeType.split('/')[1] ?? '';
  const sanitized = subtype.toLowerCase().replace(/[^a-z0-9]/g, '');
  return sanitized.length === 0 ? 'bin' : sanitized;
}

// Content-addressed deduplication: an existing file with the digest name is the stored
// payload, so a concurrent or repeated write reports the path rather than failing.
function isAlreadyExists(error: unknown): boolean {
  return typeof error === 'object' &&
    error !== null &&
    (error as { readonly code?: unknown }).code === 'EEXIST';
}

export class ImageStore implements EvaluationTraceImageStore {
  readonly #directory: string;

  constructor(options: ImageStoreOptions) {
    this.#directory = options.directory;
  }

  async store(image: OddEvidenceImage): Promise<EvaluationTraceImageDescriptor> {
    const bytes = Buffer.from(image.base64, 'base64');
    const sha256 = createHash('sha256').update(bytes).digest('hex');
    const path = join(this.#directory, `${sha256}.${extensionFor(image.mimeType)}`);
    const descriptor = (storedPath: string | null): EvaluationTraceImageDescriptor => ({
      mimeType: image.mimeType,
      bytes: bytes.length,
      sha256,
      path: storedPath,
    });

    try {
      await mkdir(this.#directory, { recursive: true });
    } catch {
      return descriptor(null);
    }

    try {
      await writeFile(path, bytes, { flag: 'wx' });
    } catch (error) {
      return isAlreadyExists(error) ? descriptor(path) : descriptor(null);
    }
    return descriptor(path);
  }
}
