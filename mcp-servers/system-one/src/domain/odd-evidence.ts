// Pure domain: the evidence payload a decision gateway evaluates, the ports injected
// into the evidence evaluation, and the typed rejection codes for that evaluation.
// No IO, no infrastructure imports, no throws.

import type { DecisionResponseRejectionCode } from './decision-response.ts';
import type { QuestionProfile } from './question-profile.ts';

export type OddEvidenceImage = {
  readonly mimeType: string;
  readonly base64: string;
};

// One question as the evidence evaluation states it: its answer kind, its instruction and
// its per-criterion descriptions. The question is identified by the key it carries in the
// questions record below, so no separate identity field is repeated inside it.
export type OddEvidenceQuestion = {
  readonly type: 'choice';
  readonly instructions: string;
  readonly criteria: Readonly<Record<string, string>>;
};

// The questions the evaluation asks, keyed by question id; evidence that supplies no
// question has nothing to decide.
export type OddEvidenceInput = {
  readonly questions: Readonly<Record<string, OddEvidenceQuestion>>;
  readonly text: string;
  readonly images: ReadonlyArray<OddEvidenceImage>;
};

export type OddEvidenceGateway = {
  decide(input: OddEvidenceInput): Promise<unknown>;
};

// What the profile port hands to the evaluation: the validated profile, or the validator's
// bounded reason for refusing the document. The raw parsed document never crosses the port,
// so mapping outside data into domain data happens in the adapter that reads it (C4).
export type QuestionProfileValidation =
  | { readonly ok: true; readonly profile: QuestionProfile }
  | { readonly ok: false; readonly reason: string };

export type QuestionProfileSource = {
  load(): Promise<QuestionProfileValidation>;
};

export type OddEvidenceRejectionCode =
  | 'invalid_profile'
  | 'invalid_evidence'
  | DecisionResponseRejectionCode;

export type OddEvidenceInputValidation =
  | { readonly ok: true; readonly input: OddEvidenceInput }
  | { readonly ok: false; readonly code: 'invalid_evidence'; readonly reason: string };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isNonemptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function isOddEvidenceImage(value: unknown): value is OddEvidenceImage {
  return isRecord(value) &&
    isNonemptyString(value.mimeType) && isNonemptyString(value.base64);
}

function isOddEvidenceQuestion(value: unknown): value is OddEvidenceQuestion {
  if (!isRecord(value) || value.type !== 'choice' ||
      !isNonemptyString(value.instructions) || !isRecord(value.criteria)) {
    return false;
  }
  const criteria = Object.values(value.criteria);
  return criteria.length > 0 && criteria.every(isNonemptyString);
}

function readImages(value: unknown): ReadonlyArray<OddEvidenceImage> | undefined {
  if (!Array.isArray(value)) return undefined;
  const images: OddEvidenceImage[] = [];
  for (const item of value as ReadonlyArray<unknown>) {
    if (!isOddEvidenceImage(item)) return undefined;
    images.push({ mimeType: item.mimeType, base64: item.base64 });
  }
  return images;
}

// The record is rebuilt from its own key/value pairs, so only the declared question fields
// survive the copy and neither an empty id nor an empty record can pass as questions.
function readQuestions(
  value: unknown,
): Readonly<Record<string, OddEvidenceQuestion>> | undefined {
  if (!isRecord(value)) return undefined;
  const entries: Array<[string, OddEvidenceQuestion]> = [];
  for (const [id, item] of Object.entries(value)) {
    if (!isNonemptyString(id) || !isOddEvidenceQuestion(item)) return undefined;
    entries.push([
      id,
      {
        type: 'choice',
        instructions: item.instructions,
        criteria: { ...item.criteria },
      },
    ]);
  }
  return entries.length === 0 ? undefined : Object.fromEntries(entries);
}

function reject(reason: string): OddEvidenceInputValidation {
  return { ok: false, code: 'invalid_evidence', reason };
}

export function validateOddEvidenceInput(
  text: unknown,
  images: unknown,
  questions: unknown,
): OddEvidenceInputValidation {
  if (typeof text !== 'string') {
    return reject('Evidence text must be a string');
  }
  const validImages = readImages(images);
  if (validImages === undefined) {
    return reject('Each evidence image must carry a non-empty mimeType and base64 payload');
  }
  const validQuestions = readQuestions(questions);
  if (validQuestions === undefined) {
    return reject(
      'Evidence questions must be a non-empty record keyed by question id, each carrying ' +
        'type, instructions and criteria',
    );
  }
  return { ok: true, input: { questions: validQuestions, text, images: validImages } };
}
