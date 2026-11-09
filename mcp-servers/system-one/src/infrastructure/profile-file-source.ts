// Infrastructure adapter for the domain `QuestionProfileSource` port: reads one JSON
// profile document from the path the host supplies, parses it and validates it in one
// mapping step, returning the domain validator's typed result. Profile policy stays with
// the domain validator; the adapter decides nothing itself. It reads once per call (a
// changed profile file is therefore observed without a restart) and never logs, echoes or
// copies the document's contents.

import { readFile } from 'node:fs/promises';

import { validateQuestionProfile } from '../domain/question-profile.ts';
import type { QuestionProfileSource, QuestionProfileValidation } from '../domain/odd-evidence.ts';

export type ProfileFileSourceOptions = {
  // Absolute path supplied by the host. This adapter applies no path policy: the host
  // configuration owns which document is read.
  readonly profilePath: string;
};

// The two boundary steps this adapter performs, exposed so a host can tell an unreadable
// path from unparsable contents.
export type ProfileFileSourceStep = 'read' | 'parse';

// Boundary exception, never a domain result (C5): the file could not be read or its
// contents were not JSON. The message names the failed step only — neither the path nor
// the document contents appear in it, and no parser cause is attached because a parse
// error can quote the document.
export class ProfileFileSourceBoundaryError extends Error {
  readonly step: ProfileFileSourceStep;

  constructor(step: ProfileFileSourceStep) {
    super(
      step === 'read'
        ? 'The question profile file could not be read'
        : 'The question profile file did not contain valid JSON',
    );
    this.name = 'ProfileFileSourceBoundaryError';
    this.step = step;
  }
}

export class ProfileFileSource implements QuestionProfileSource {
  readonly #profilePath: string;

  constructor(options: ProfileFileSourceOptions) {
    this.#profilePath = options.profilePath;
  }

  // One read, one parse and one validation per call: the adapter owns the only mapping from
  // the outside document to domain data, so callers receive the validated profile or the
  // validator's reason and never the raw parsed value.
  async load(): Promise<QuestionProfileValidation> {
    const contents = await this.#readProfileText();
    return validateQuestionProfile(this.#parseProfileText(contents));
  }

  async #readProfileText(): Promise<string> {
    try {
      return await readFile(this.#profilePath, 'utf8');
    } catch {
      throw new ProfileFileSourceBoundaryError('read');
    }
  }

  #parseProfileText(contents: string): unknown {
    try {
      return JSON.parse(contents) as unknown;
    } catch {
      throw new ProfileFileSourceBoundaryError('parse');
    }
  }
}
