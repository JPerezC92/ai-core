/** Validate explicit supplied decision binding and provenance without authenticating it. */

import type {
  DecisionEvidence, ReviewDecisions, ReviewPreparationError,
} from '#scripts/pr_content/domain/records.ts';
import { parseMetadata, reviewError } from '#scripts/pr_content/domain/records.ts';

const ENTRY_FIELDS = ['target', 'actor', 'date', 'statement', 'evidence', 'destination'] as const;

/** An ISO calendar date; the reference accepts the extended `YYYY-MM-DD` form. */
function isIsoDate(value: string): boolean {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (match === null) return false;
  const [year, month, day] = match.slice(1).map(Number) as [number, number, number];
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

function parseEntries(value: unknown, debt: boolean): DecisionEvidence[] | ReviewPreparationError {
  const error = reviewError('DECISIONS_INVALID', 'complete unique decision provenance required');
  if (!Array.isArray(value)) return error;

  const entries: DecisionEvidence[] = [];
  for (const entry of value) {
    if (typeof entry !== 'object' || entry === null || Array.isArray(entry)) return error;
    const record = entry as Record<string, unknown>;
    const keys = Object.keys(record);
    if (keys.length !== ENTRY_FIELDS.length || ENTRY_FIELDS.some(field => !Object.hasOwn(record, field))) return error;
    if (ENTRY_FIELDS.some(field => typeof record[field] !== 'string')) return error;
    if (ENTRY_FIELDS.some(field => field !== 'destination' && (record[field] as string).trim() === '')) return error;
    if (!isIsoDate(record.date as string)) return error;
    if (debt && (record.destination as string).trim() === '') return error;
    entries.push({
      target: record.target as string,
      actor: record.actor as string,
      date: record.date as string,
      statement: record.statement as string,
      evidence: record.evidence as string,
      destination: record.destination as string,
    });
  }
  if (new Set(entries.map(entry => entry.target)).size !== entries.length) return error;
  return entries;
}

/** Check supplied records match the PR/head; owners verify actual authority. */
export function parseDecisions(value: unknown, metadata: unknown): ReviewDecisions | ReviewPreparationError {
  const context = parseMetadata(metadata);
  if ('code' in context) return reviewError('DECISIONS_INVALID', context.message);
  if (value === null || value === undefined) {
    return { notApplicable: [], acceptance: [], debt: [] };
  }
  const error = reviewError('DECISIONS_INVALID', 'decision PR/head binding required');
  if (typeof value !== 'object' || Array.isArray(value)) return error;

  const record = value as Record<string, unknown>;
  const expected = ['pr_number', 'head_sha', 'not_applicable', 'acceptance', 'debt'];
  const keys = Object.keys(record);
  if (keys.length !== expected.length || expected.some(field => !Object.hasOwn(record, field))) return error;
  if (typeof record.pr_number !== 'number' || !Number.isInteger(record.pr_number)) return error;
  if (record.pr_number !== context.number || record.head_sha !== context.headRefOid) return error;

  const notApplicable = parseEntries(record.not_applicable, false);
  if ('code' in notApplicable) return notApplicable;
  const acceptance = parseEntries(record.acceptance, false);
  if ('code' in acceptance) return acceptance;
  const debt = parseEntries(record.debt, true);
  if ('code' in debt) return debt;
  return { notApplicable, acceptance, debt };
}
