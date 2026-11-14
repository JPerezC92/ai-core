/** Parse and query a schema v1 Markdown text-integrity policy document. */

import {
  CODE_INPUT, CODE_POLICY, MAX_UNICODE_SCALAR, SURROGATE_END, SURROGATE_START,
} from './models.ts';
import type {
  CodepointSpec, Decoding, DomainError, EditorDriftFinding, EditorOverride,
  EditorProjection, InvalidSequence, Policy, RangeSpec, Rule,
} from './models.ts';

const ROOT_KEYS = ['version', 'id', 'default_classification', 'decoding', 'rules', 'editor_projection'];
const DECODING_KEYS = ['encoding', 'invalid_sequence'];
const INVALID_SEQUENCE_KEYS = ['id', 'severity', 'class', 'rationale'];
const RULE_BASE_KEYS = ['id', 'severity', 'class', 'rationale'];
const CODEPOINT_KEYS = ['cp', 'hex'];
const RANGE_KEYS = ['start', 'end', 'start_hex', 'end_hex'];
const EDITOR_KEYS = ['scope', 'setting_key', 'overrides'];
const OVERRIDE_KEYS = ['codepoint', 'hex', 'gremlins_key', 'severity', 'description'];
const RULE_SEVERITIES = ['error', 'warning'];

/** The canonical U+ form: uppercase hex, minimum four digits. */
export function canonicalHex(codepoint: number): string {
  return `U+${codepoint.toString(16).toUpperCase().padStart(4, '0')}`;
}

/** The lowercase hex Gremlins key, minimum four digits, no U+ prefix. */
export function canonicalGremlinsKey(codepoint: number): string {
  return codepoint.toString(16).padStart(4, '0');
}

/** The unique covering rule, or undefined when the scalar is allowed by default. */
export function classifyCodepoint(policy: Policy, codepoint: number): Rule | undefined {
  for (const rule of policy.rules) {
    for (const spec of rule.codepoints) if (spec.cp === codepoint) return rule;
    for (const spec of rule.ranges) if (spec.start <= codepoint && codepoint <= spec.end) return rule;
  }
  return undefined;
}

function isError(value: unknown): value is DomainError {
  return typeof value === 'object' && value !== null && 'code' in value && 'message' in value;
}

/** Validate a decoded JSON document against schema v1 and return a Policy. */
export function parsePolicy(data: unknown): Policy | DomainError {
  const root = requireObject(data, 'policy root');
  if (isError(root)) return root;
  const keysError = requireExactKeys(root, ROOT_KEYS, 'policy root');
  if (keysError !== undefined) return keysError;

  const version = requireInt(root.version, 'version');
  if (isError(version)) return version;
  if (version !== 1) return { code: CODE_POLICY, message: `unsupported policy version: ${version}` };

  const policyId = requireNonemptyString(root.id, 'id');
  if (isError(policyId)) return policyId;

  const defaultClassification = requireNonemptyString(root.default_classification, 'default_classification');
  if (isError(defaultClassification)) return defaultClassification;
  if (defaultClassification !== 'allow') {
    return { code: CODE_POLICY, message: 'default_classification must be allow' };
  }

  const decoding = parseDecoding(root.decoding);
  if (isError(decoding)) return decoding;

  const rules = parseRules(root.rules, decoding.invalidSequence.id);
  if (isError(rules)) return rules;

  const editorProjection = parseEditorProjection(root.editor_projection);
  if (isError(editorProjection)) return editorProjection;

  return {
    version, id: policyId, defaultClassification, decoding, rules, editorProjection,
  };
}

/** Compare only the representable projection; extra cloned defaults are drift. */
export function compareEditorProjection(
  policy: Policy, settings: unknown, path: string,
): EditorDriftFinding | DomainError | undefined {
  if (typeof settings !== 'object' || settings === null || Array.isArray(settings)) {
    return { code: CODE_INPUT, message: 'editor settings must be a JSON object' };
  }
  const root = settings as Record<string, unknown>;
  const scopeValue = root[policy.editorProjection.scope];
  let actual: Record<string, unknown> = {};
  if (scopeValue !== undefined && scopeValue !== null) {
    if (typeof scopeValue !== 'object' || Array.isArray(scopeValue)) {
      return { code: CODE_INPUT, message: 'editor scope must be an object' };
    }
    const characters = (scopeValue as Record<string, unknown>)[policy.editorProjection.settingKey];
    if (characters !== undefined && characters !== null) {
      if (typeof characters !== 'object' || Array.isArray(characters)) {
        return { code: CODE_INPUT, message: 'editor projection must be an object' };
      }
      actual = characters as Record<string, unknown>;
    }
  }

  const expected = new Map(policy.editorProjection.overrides.map(item => [item.gremlinsKey, item]));
  const missing: string[] = [];
  const mismatched: string[] = [];
  const extra: string[] = [];

  for (const [key, override] of expected) {
    if (!Object.hasOwn(actual, key)) {
      missing.push(key);
      continue;
    }
    if (!overrideMatches(actual[key], override)) mismatched.push(key);
  }
  for (const key of Object.keys(actual)) if (!expected.has(key)) extra.push(key);

  if (missing.length === 0 && extra.length === 0 && mismatched.length === 0) return undefined;
  const sort = (values: string[]) => values.sort();
  return {
    kind: 'editor-drift',
    path: path.replaceAll('\\', '/'),
    missing: sort(missing), extra: sort(extra), mismatched: sort(mismatched),
  };
}

function overrideMatches(value: unknown, override: EditorOverride): boolean {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false;
  const entry = value as Record<string, unknown>;
  return entry.level === override.severity && entry.description === override.description;
}

function parseDecoding(value: unknown): Decoding | DomainError {
  const payload = requireObject(value, 'decoding');
  if (isError(payload)) return payload;
  const keysError = requireExactKeys(payload, DECODING_KEYS, 'decoding');
  if (keysError !== undefined) return keysError;

  const encoding = requireNonemptyString(payload.encoding, 'decoding.encoding');
  if (isError(encoding)) return encoding;
  if (encoding !== 'utf-8') return { code: CODE_POLICY, message: 'decoding.encoding must be utf-8' };

  const invalidSequence = parseInvalidSequence(payload.invalid_sequence);
  if (isError(invalidSequence)) return invalidSequence;
  return { encoding, invalidSequence };
}

function parseInvalidSequence(value: unknown): InvalidSequence | DomainError {
  const payload = requireObject(value, 'decoding.invalid_sequence');
  if (isError(payload)) return payload;
  const keysError = requireExactKeys(payload, INVALID_SEQUENCE_KEYS, 'decoding.invalid_sequence');
  if (keysError !== undefined) return keysError;

  const id = requireNonemptyString(payload.id, 'decoding.invalid_sequence.id');
  if (isError(id)) return id;
  const severity = requireNonemptyString(payload.severity, 'decoding.invalid_sequence.severity');
  if (isError(severity)) return severity;
  if (severity !== 'error') {
    return { code: CODE_POLICY, message: 'decoding.invalid_sequence.severity must be error' };
  }
  const className = requireNonemptyString(payload.class, 'decoding.invalid_sequence.class');
  if (isError(className)) return className;
  const rationale = requireNonemptyString(payload.rationale, 'decoding.invalid_sequence.rationale');
  if (isError(rationale)) return rationale;
  return { id, severity, className, rationale };
}

function parseRules(value: unknown, invalidSequenceId: string): Rule[] | DomainError {
  if (!Array.isArray(value)) return { code: CODE_POLICY, message: 'rules must be an array' };

  const rules: Rule[] = [];
  const seenIds = new Set([invalidSequenceId]);
  const intervals: Array<[number, number, string]> = [];
  for (const [index, item] of value.entries()) {
    const rule = parseRule(item, index);
    if (isError(rule)) return rule;
    if (seenIds.has(rule.id)) return { code: CODE_POLICY, message: `duplicate rule id: ${rule.id}` };
    seenIds.add(rule.id);
    for (const spec of rule.codepoints) intervals.push([spec.cp, spec.cp, rule.id]);
    for (const spec of rule.ranges) intervals.push([spec.start, spec.end, rule.id]);
    rules.push(rule);
  }
  return firstOverlap(intervals) ?? rules;
}

function parseRule(value: unknown, index: number): Rule | DomainError {
  const label = `rules[${index}]`;
  const payload = requireObject(value, label);
  if (isError(payload)) return payload;

  const hasCodepoints = Object.hasOwn(payload, 'codepoints');
  const hasRanges = Object.hasOwn(payload, 'ranges');
  if (hasCodepoints === hasRanges) {
    return { code: CODE_POLICY, message: `${label} must have exactly one of codepoints or ranges` };
  }
  const expected = hasCodepoints ? [...RULE_BASE_KEYS, 'codepoints'] : [...RULE_BASE_KEYS, 'ranges'];
  const keysError = requireExactKeys(payload, expected, label);
  if (keysError !== undefined) return keysError;

  const id = requireNonemptyString(payload.id, `${label}.id`);
  if (isError(id)) return id;
  const severity = requireNonemptyString(payload.severity, `${label}.severity`);
  if (isError(severity)) return severity;
  if (!RULE_SEVERITIES.includes(severity)) {
    return { code: CODE_POLICY, message: `${label}.severity must be error or warning` };
  }
  const className = requireNonemptyString(payload.class, `${label}.class`);
  if (isError(className)) return className;
  const rationale = requireNonemptyString(payload.rationale, `${label}.rationale`);
  if (isError(rationale)) return rationale;

  if (hasCodepoints) {
    const codepoints = parseCodepoints(payload.codepoints, `${label}.codepoints`);
    if (isError(codepoints)) return codepoints;
    return { id, severity, className, rationale, codepoints, ranges: [] };
  }
  const ranges = parseRanges(payload.ranges, `${label}.ranges`);
  if (isError(ranges)) return ranges;
  return { id, severity, className, rationale, codepoints: [], ranges };
}

function parseCodepoints(value: unknown, label: string): CodepointSpec[] | DomainError {
  if (!Array.isArray(value)) return { code: CODE_POLICY, message: `${label} must be an array` };
  if (value.length === 0) return { code: CODE_POLICY, message: `${label} must not be empty` };
  const items: CodepointSpec[] = [];
  for (const [index, item] of value.entries()) {
    const parsed = parseCodepointItem(item, `${label}[${index}]`);
    if (isError(parsed)) return parsed;
    items.push(parsed);
  }
  return items;
}

function parseCodepointItem(value: unknown, label: string): CodepointSpec | DomainError {
  const payload = requireObject(value, label);
  if (isError(payload)) return payload;
  const keysError = requireExactKeys(payload, CODEPOINT_KEYS, label);
  if (keysError !== undefined) return keysError;

  const cp = requireScalarInt(payload.cp, `${label}.cp`);
  if (isError(cp)) return cp;
  const hex = requireNonemptyString(payload.hex, `${label}.hex`);
  if (isError(hex)) return hex;
  const expected = canonicalHex(cp);
  if (hex !== expected) return { code: CODE_POLICY, message: `${label}.hex must be ${expected}` };
  return { cp, hex };
}

function parseRanges(value: unknown, label: string): RangeSpec[] | DomainError {
  if (!Array.isArray(value)) return { code: CODE_POLICY, message: `${label} must be an array` };
  if (value.length === 0) return { code: CODE_POLICY, message: `${label} must not be empty` };
  const items: RangeSpec[] = [];
  for (const [index, item] of value.entries()) {
    const parsed = parseRangeItem(item, `${label}[${index}]`);
    if (isError(parsed)) return parsed;
    items.push(parsed);
  }
  return items;
}

function parseRangeItem(value: unknown, label: string): RangeSpec | DomainError {
  const payload = requireObject(value, label);
  if (isError(payload)) return payload;
  const keysError = requireExactKeys(payload, RANGE_KEYS, label);
  if (keysError !== undefined) return keysError;

  const start = requireScalarInt(payload.start, `${label}.start`);
  if (isError(start)) return start;
  const end = requireScalarInt(payload.end, `${label}.end`);
  if (isError(end)) return end;
  if (start > end) return { code: CODE_POLICY, message: `${label} start must be <= end` };

  const startHex = requireNonemptyString(payload.start_hex, `${label}.start_hex`);
  if (isError(startHex)) return startHex;
  const endHex = requireNonemptyString(payload.end_hex, `${label}.end_hex`);
  if (isError(endHex)) return endHex;
  const expectedStart = canonicalHex(start);
  const expectedEnd = canonicalHex(end);
  if (startHex !== expectedStart) {
    return { code: CODE_POLICY, message: `${label}.start_hex must be ${expectedStart}` };
  }
  if (endHex !== expectedEnd) {
    return { code: CODE_POLICY, message: `${label}.end_hex must be ${expectedEnd}` };
  }
  return { start, end, startHex, endHex };
}

function parseEditorProjection(value: unknown): EditorProjection | DomainError {
  const payload = requireObject(value, 'editor_projection');
  if (isError(payload)) return payload;
  const keysError = requireExactKeys(payload, EDITOR_KEYS, 'editor_projection');
  if (keysError !== undefined) return keysError;

  const scope = requireNonemptyString(payload.scope, 'editor_projection.scope');
  if (isError(scope)) return scope;
  const settingKey = requireNonemptyString(payload.setting_key, 'editor_projection.setting_key');
  if (isError(settingKey)) return settingKey;
  if (!Array.isArray(payload.overrides)) {
    return { code: CODE_POLICY, message: 'editor_projection.overrides must be an array' };
  }

  const overrides: EditorOverride[] = [];
  const seenCodepoints = new Set<number>();
  const seenKeys = new Set<string>();
  for (const [index, item] of payload.overrides.entries()) {
    const parsed = parseOverride(item, index);
    if (isError(parsed)) return parsed;
    if (seenCodepoints.has(parsed.codepoint)) {
      return { code: CODE_POLICY, message: `duplicate editor_projection codepoint: ${canonicalHex(parsed.codepoint)}` };
    }
    if (seenKeys.has(parsed.gremlinsKey)) {
      return { code: CODE_POLICY, message: `duplicate editor_projection gremlins_key: ${parsed.gremlinsKey}` };
    }
    seenCodepoints.add(parsed.codepoint);
    seenKeys.add(parsed.gremlinsKey);
    overrides.push(parsed);
  }
  return { scope, settingKey, overrides };
}

function parseOverride(value: unknown, index: number): EditorOverride | DomainError {
  const label = `editor_projection.overrides[${index}]`;
  const payload = requireObject(value, label);
  if (isError(payload)) return payload;
  const keysError = requireExactKeys(payload, OVERRIDE_KEYS, label);
  if (keysError !== undefined) return keysError;

  const codepoint = requireScalarInt(payload.codepoint, `${label}.codepoint`);
  if (isError(codepoint)) return codepoint;
  const hex = requireNonemptyString(payload.hex, `${label}.hex`);
  if (isError(hex)) return hex;
  const expectedHex = canonicalHex(codepoint);
  if (hex !== expectedHex) return { code: CODE_POLICY, message: `${label}.hex must be ${expectedHex}` };

  const gremlinsKey = requireNonemptyString(payload.gremlins_key, `${label}.gremlins_key`);
  if (isError(gremlinsKey)) return gremlinsKey;
  const expectedKey = canonicalGremlinsKey(codepoint);
  if (gremlinsKey !== expectedKey) {
    return { code: CODE_POLICY, message: `${label}.gremlins_key must be ${expectedKey}` };
  }

  const severity = requireNonemptyString(payload.severity, `${label}.severity`);
  if (isError(severity)) return severity;
  if (severity !== 'none') return { code: CODE_POLICY, message: `${label}.severity must be none` };

  const description = requireNonemptyString(payload.description, `${label}.description`);
  if (isError(description)) return description;
  return { codepoint, hex, gremlinsKey, severity, description };
}

function firstOverlap(intervals: Array<[number, number, string]>): DomainError | undefined {
  const ordered = [...intervals].sort((a, b) => a[0] - b[0] || a[1] - b[1] || (a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0));
  for (let index = 0; index < ordered.length - 1; index++) {
    const [startA, endA, idA] = ordered[index]!;
    const [startB, , idB] = ordered[index + 1]!;
    if (endA >= startB) {
      return { code: CODE_POLICY, message: `overlapping coverage between ${idA} and ${idB}` };
    }
  }
  return undefined;
}

function requireObject(value: unknown, label: string): Record<string, unknown> | DomainError {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return { code: CODE_POLICY, message: `${label} must be an object` };
  }
  return value as Record<string, unknown>;
}

function requireExactKeys(
  payload: Record<string, unknown>, expected: readonly string[], label: string,
): DomainError | undefined {
  const keys = new Set(Object.keys(payload));
  const missing = expected.filter(key => !keys.has(key)).sort();
  const extra = [...keys].filter(key => !expected.includes(key)).sort();
  if (missing.length === 0 && extra.length === 0) return undefined;
  const parts: string[] = [];
  if (missing.length) parts.push(`missing ${missing.join(', ')}`);
  if (extra.length) parts.push(`unknown ${extra.join(', ')}`);
  return { code: CODE_POLICY, message: `${label}: ${parts.join('; ')}` };
}

function requireInt(value: unknown, label: string): number | DomainError {
  if (typeof value !== 'number' || !Number.isInteger(value)) {
    return { code: CODE_POLICY, message: `${label} must be an integer` };
  }
  return value;
}

function requireScalarInt(value: unknown, label: string): number | DomainError {
  const number = requireInt(value, label);
  if (isError(number)) return number;
  if (number < 0 || number > MAX_UNICODE_SCALAR) {
    return { code: CODE_POLICY, message: `${label} must be a Unicode scalar 0..${MAX_UNICODE_SCALAR}` };
  }
  if (number >= SURROGATE_START && number <= SURROGATE_END) {
    return { code: CODE_POLICY, message: `${label} must not be a surrogate` };
  }
  return number;
}

function requireNonemptyString(value: unknown, label: string): string | DomainError {
  if (typeof value !== 'string') return { code: CODE_POLICY, message: `${label} must be a string` };
  if (value === '') return { code: CODE_POLICY, message: `${label} must be non-empty` };
  return value;
}
