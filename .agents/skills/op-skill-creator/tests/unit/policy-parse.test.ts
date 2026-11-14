import { describe, expect, it } from 'vitest';

import { isDomainError } from '#scripts/markdown_text_pkg/domain/models.ts';
import type { DomainError, Policy } from '#scripts/markdown_text_pkg/domain/models.ts';
import { canonicalGremlinsKey, canonicalHex, parsePolicy } from '#scripts/markdown_text_pkg/domain/policy.ts';
import { makePolicyDocument } from '#tests/support/markdown-text-fixtures.ts';

function rejected(document: Record<string, unknown>): DomainError {
  const result = parsePolicy(document);
  if (!isDomainError(result)) throw new Error(`expected a policy failure, received ${JSON.stringify(result)}`);
  return result;
}

function accepted(document: Record<string, unknown> = makePolicyDocument()): Policy {
  const result = parsePolicy(document);
  if (isDomainError(result)) throw new Error(`expected a policy, received ${result.code}: ${result.message}`);
  return result;
}

describe('canonical spellings', () => {
  it('formats the U+ form and the Gremlins key', () => {
    expect(canonicalHex(0x200b)).toBe('U+200B');
    expect(canonicalHex(0x1f600)).toBe('U+1F600');
    expect(canonicalGremlinsKey(0x200b)).toBe('200b');
  });
});

describe('policy acceptance', () => {
  it('accepts a schema v1 document', () => {
    const policy = accepted();
    expect(policy.id).toBe('fixture-policy');
    expect(policy.defaultClassification).toBe('allow');
    expect(policy.rules).toHaveLength(1);
    expect(policy.rules[0]?.codepoints[0]).toEqual({ cp: 0x200b, hex: 'U+200B' });
    expect(policy.editorProjection.overrides[0]?.gremlinsKey).toBe('200b');
  });
});

describe('policy rejection', () => {
  it('rejects an unsupported version', () => {
    expect(rejected(makePolicyDocument({ version: 2 })).message).toBe('unsupported policy version: 2');
  });

  it('rejects a non-allow default classification', () => {
    expect(rejected(makePolicyDocument({ default_classification: 'deny' })).message)
      .toBe('default_classification must be allow');
  });

  it('rejects a missing root field', () => {
    const document = makePolicyDocument();
    delete document.decoding;
    expect(rejected(document).message).toContain('policy root: missing decoding');
  });

  it('rejects an unknown root field', () => {
    expect(rejected(makePolicyDocument({ extra: true })).message).toContain('policy root: unknown extra');
  });

  it('rejects an encoding other than utf-8', () => {
    const document = makePolicyDocument();
    (document.decoding as Record<string, unknown>).encoding = 'utf-16';
    expect(rejected(document).message).toBe('decoding.encoding must be utf-8');
  });

  it('rejects a rule carrying both codepoints and ranges', () => {
    const document = makePolicyDocument();
    (document.rules as Array<Record<string, unknown>>)[0]!.ranges = [];
    expect(rejected(document).message).toBe('rules[0] must have exactly one of codepoints or ranges');
  });

  it('rejects a duplicate rule id', () => {
    const document = makePolicyDocument();
    const rule = (document.rules as Array<Record<string, unknown>>)[0]!;
    document.rules = [rule, rule];
    expect(rejected(document).message).toBe('duplicate rule id: no-invisible');
  });

  it('rejects overlapping coverage', () => {
    const document = makePolicyDocument();
    document.rules = [
      { id: 'first', severity: 'error', class: 'c', rationale: 'r', codepoints: [{ cp: 0x200b, hex: 'U+200B' }] },
      { id: 'second', severity: 'error', class: 'c', rationale: 'r', codepoints: [{ cp: 0x200b, hex: 'U+200B' }] },
    ];
    expect(rejected(document).message).toBe('overlapping coverage between first and second');
  });

  it('rejects a non-canonical hex spelling', () => {
    const document = makePolicyDocument();
    (document.rules as Array<Record<string, unknown>>)[0]!['codepoints'] = [{ cp: 0x200b, hex: 'u+200b' }];
    expect(rejected(document).message).toBe('rules[0].codepoints[0].hex must be U+200B');
  });

  it('rejects a surrogate code point', () => {
    const document = makePolicyDocument();
    (document.rules as Array<Record<string, unknown>>)[0]!['codepoints'] = [{ cp: 0xd800, hex: 'U+D800' }];
    expect(rejected(document).message).toBe('rules[0].codepoints[0].cp must not be a surrogate');
  });

  it('rejects a range whose start exceeds its end', () => {
    const document = makePolicyDocument();
    document.rules = [{
      id: 'bad', severity: 'error', class: 'c', rationale: 'r',
      ranges: [{ start: 0x30, end: 0x20, start_hex: 'U+0030', end_hex: 'U+0020' }],
    }];
    expect(rejected(document).message).toBe('rules[0].ranges[0] start must be <= end');
  });

  it('rejects a duplicate editor projection key', () => {
    const document = makePolicyDocument();
    const override = (document.editor_projection as Record<string, unknown>)['overrides'] as Array<Record<string, unknown>>;
    document.editor_projection = { ...document.editor_projection as object, overrides: [override[0], override[0]] };
    expect(rejected(document).message).toBe('duplicate editor_projection codepoint: U+200B');
  });
});
