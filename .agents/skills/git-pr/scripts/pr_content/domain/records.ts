/** Typed review inputs, successful bodies, and returned business failures. */

export interface ReviewMetadata {
  readonly number: number;
  readonly headRefOid: string;
  readonly baseRefName: string;
  readonly headRefName: string;
  readonly state: string;
  readonly title: string;
  readonly body: string;
}

export const METADATA_FIELDS = [
  'number', 'headRefOid', 'baseRefName', 'headRefName', 'state', 'title', 'body',
] as const;

/** A stable rejection code and explanation returned as a value. */
export interface ReviewPreparationError {
  readonly code: string;
  readonly message: string;
}

export interface Finding {
  readonly id: string;
  readonly severity: string;
  readonly status: string;
  readonly evidence: string;
  readonly resolution: string;
}

/** Supplied provenance, never independently authenticated authority. */
export interface DecisionEvidence {
  readonly target: string;
  readonly actor: string;
  readonly date: string;
  readonly statement: string;
  readonly evidence: string;
  readonly destination: string;
}

/** Parsed decision records bound to supplied review metadata. */
export interface ReviewDecisions {
  readonly notApplicable: readonly DecisionEvidence[];
  readonly acceptance: readonly DecisionEvidence[];
  readonly debt: readonly DecisionEvidence[];
}

/** A structurally checked body; no claim about evidence truth. */
export interface PreparedBody {
  readonly body: string;
}

export function reviewError(code: string, message: string): ReviewPreparationError {
  return { code, message };
}

/** Narrow a value to a returned business failure. */
export function isReviewError(value: unknown): value is ReviewPreparationError {
  return typeof value === 'object' && value !== null
    && typeof (value as ReviewPreparationError).code === 'string'
    && typeof (value as ReviewPreparationError).message === 'string';
}

function keysAre(record: Record<string, unknown>, expected: readonly string[]): boolean {
  const keys = Object.keys(record);
  return keys.length === expected.length && expected.every(field => Object.hasOwn(record, field));
}

/** Validate decoded metadata without authenticating its external provenance. */
export function parseMetadata(value: unknown): ReviewMetadata | ReviewPreparationError {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return reviewError('METADATA_INVALID', 'metadata must be an object');
  }
  const record = value as Record<string, unknown>;
  if (!keysAre(record, METADATA_FIELDS)) {
    return reviewError(
      'METADATA_INVALID',
      `metadata must contain exactly the documented fields: ${METADATA_FIELDS.join(', ')}`,
    );
  }
  if (typeof record.number !== 'number' || !Number.isInteger(record.number) || record.number < 1) {
    return reviewError('METADATA_INVALID', 'positive PR number required');
  }
  for (const field of ['headRefOid', 'baseRefName', 'headRefName', 'state', 'title', 'body']) {
    if (typeof record[field] !== 'string') {
      return reviewError('METADATA_INVALID', 'metadata string fields required');
    }
  }
  if (!/^[0-9a-fA-F]{7,64}$/.test(record.headRefOid as string)) {
    return reviewError('METADATA_INVALID', 'immutable head required');
  }
  const identity = ['baseRefName', 'headRefName', 'title'] as const;
  if (record.state !== 'OPEN' || identity.some(field => (record[field] as string).trim() === '')) {
    return reviewError('METADATA_INVALID', 'open PR and nonempty identity required');
  }
  return {
    number: record.number,
    headRefOid: record.headRefOid as string,
    baseRefName: record.baseRefName as string,
    headRefName: record.headRefName as string,
    state: record.state as string,
    title: record.title as string,
    body: record.body as string,
  };
}

/** Compare two metadata records by the documented field set. */
export function metadataMatches(left: ReviewMetadata, right: ReviewMetadata): boolean {
  return METADATA_FIELDS.every(field => left[field] === right[field]);
}
