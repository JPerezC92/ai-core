/** Pure model-catalog domain: immutable models, parsing, matching, and the source port. */

export const SELECTOR = /^([A-Za-z0-9][A-Za-z0-9_+.-]*)\/(\S+)$/;

export const CODE_NO_MODELS = 'no_models_available';
export const CODE_NO_MATCH = 'no_matching_models';

/** One opencode model entry with its identity and per-1M-token costs. */
export interface Model {
  readonly config: string;
  readonly id: string;
  readonly provider: string;
  readonly name: string;
  readonly costIn: number;
  readonly costOut: number;
}

/** One skipped catalog line, identified by a stable code and a message. */
export interface ParseIssue {
  readonly code: string;
  readonly message: string;
}

/** The parsed models plus the issues recorded while parsing the catalog. */
export interface CatalogParseResult {
  readonly models: readonly Model[];
  readonly issues: readonly ParseIssue[];
}

/** Business outcome: the source produced no usable model records. */
export interface NoModelsAvailable {
  readonly kind: 'no-models';
  readonly code: string;
  readonly message: string;
}

/** Business outcome: the query matched no usable model record. */
export interface NoMatchingModels {
  readonly kind: 'no-match';
  readonly code: string;
  readonly message: string;
  readonly query: string;
}

export type LookupOutcome = readonly Model[] | NoModelsAvailable | NoMatchingModels;

/** A boundary failure raised when the model source transport fails. */
export class ModelSourceFailure extends Error {
  override name = 'ModelSourceFailure';
}

/** Port for fetching the available models as domain values. */
export interface ModelSource {
  fetch(): readonly Model[];
}

export function noModelsAvailable(): NoModelsAvailable {
  return {
    kind: 'no-models',
    code: CODE_NO_MODELS,
    message: 'No models parsed from `opencode models` output.',
  };
}

export function noMatchingModels(query: string): NoMatchingModels {
  return {
    kind: 'no-match',
    code: CODE_NO_MATCH,
    message: `No match for ${query} in \`opencode models\`. `
      + 'Run `node .agents/skills/op-model/scripts/models.ts` '
      + 'to see all available models.',
    query,
  };
}

/**
 * Parse `opencode models` selector lines into models plus per-line issues.
 *
 * Each non-blank line that is a `provider/model` selector becomes a model whose
 * name is its model id and whose in/out costs are 0; every other non-blank line
 * is skipped and recorded as an `unrecognized_line` issue.
 */
export function parseRecords(stdout: string): CatalogParseResult {
  const models: Model[] = [];
  const issues: ParseIssue[] = [];
  for (const rawLine of stdout.split(/\r\n|\n|\r/)) {
    const line = rawLine.trim();
    if (line === '') continue;
    const match = SELECTOR.exec(line);
    if (match === null) {
      issues.push({ code: 'unrecognized_line', message: `${line}: not a provider/model selector` });
      continue;
    }
    models.push({
      config: line,
      id: match[2]!,
      provider: match[1]!,
      name: match[2]!,
      costIn: 0,
      costOut: 0,
    });
  }
  return { models, issues };
}

/** Lowercase `text` and strip every non-alphanumeric character. */
export function normalize(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]/g, '');
}

/** Whether `query` normalizes to a substring of the config or the name. */
export function matches(query: string, record: Model): boolean {
  const needle = normalize(query);
  if (needle === '') return true;
  return normalize(record.config).includes(needle) || normalize(record.name).includes(needle);
}
