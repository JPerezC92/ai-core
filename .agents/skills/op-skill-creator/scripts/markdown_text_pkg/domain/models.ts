/** Typed policy, finding, failure and discovery values for Markdown text integrity. */

export const CODE_POLICY = 'policy';
export const CODE_INPUT = 'input';
export const CODE_IO = 'io';
export const EDITOR_DRIFT_ID = 'EDITOR-DRIFT';
export const MAX_UNICODE_SCALAR = 0x10ffff;
export const SURROGATE_START = 0xd800;
export const SURROGATE_END = 0xdfff;

/** A typed policy, input or IO failure returned as a value. */
export interface DomainError {
  readonly code: string;
  readonly message: string;
}

/** Narrow a value to a returned domain failure. */
export function isDomainError(value: unknown): value is DomainError {
  return typeof value === 'object' && value !== null
    && typeof (value as DomainError).code === 'string'
    && typeof (value as DomainError).message === 'string';
}

export interface CodepointSpec {
  readonly cp: number;
  readonly hex: string;
}

export interface RangeSpec {
  readonly start: number;
  readonly end: number;
  readonly startHex: string;
  readonly endHex: string;
}

export interface Rule {
  readonly id: string;
  readonly severity: string;
  readonly className: string;
  readonly rationale: string;
  readonly codepoints: readonly CodepointSpec[];
  readonly ranges: readonly RangeSpec[];
}

export interface InvalidSequence {
  readonly id: string;
  readonly severity: string;
  readonly className: string;
  readonly rationale: string;
}

export interface Decoding {
  readonly encoding: string;
  readonly invalidSequence: InvalidSequence;
}

export interface EditorOverride {
  readonly codepoint: number;
  readonly hex: string;
  readonly gremlinsKey: string;
  readonly severity: string;
  readonly description: string;
}

export interface EditorProjection {
  readonly scope: string;
  readonly settingKey: string;
  readonly overrides: readonly EditorOverride[];
}

export interface Policy {
  readonly version: number;
  readonly id: string;
  readonly defaultClassification: string;
  readonly decoding: Decoding;
  readonly rules: readonly Rule[];
  readonly editorProjection: EditorProjection;
}

export interface ScalarFinding {
  readonly kind: 'scalar';
  readonly path: string;
  readonly line: number;
  readonly column: number;
  readonly severity: string;
  readonly ruleId: string;
  readonly codepoint: number;
  readonly excerpt: string;
}

export interface Utf8Finding {
  readonly kind: 'utf8';
  readonly path: string;
  readonly line: number;
  readonly column: number;
  readonly severity: string;
  readonly ruleId: string;
  readonly byteOffset: number;
}

export interface EditorDriftFinding {
  readonly kind: 'editor-drift';
  readonly path: string;
  readonly missing: readonly string[];
  readonly extra: readonly string[];
  readonly mismatched: readonly string[];
}

export type Finding = ScalarFinding | Utf8Finding | EditorDriftFinding;

export interface FileTarget {
  readonly displayPath: string;
  readonly absNorm: string;
}

export interface DiscoverResult {
  readonly targets: readonly FileTarget[];
  readonly failures: readonly DomainError[];
}

export interface CheckOutcome {
  readonly findings: readonly Finding[];
  readonly failures: readonly DomainError[];
}

/** The deterministic stdout sort key for a finding. */
export function findingSortKey(finding: Finding): [string, number, number, string] {
  const path = finding.path.replaceAll('\\', '/');
  if (finding.kind === 'editor-drift') return [path, 0, 0, EDITOR_DRIFT_ID];
  return [path, finding.line, finding.column, finding.ruleId];
}
