import { describe, expect, it } from 'vitest';

import { isDomainError } from '#scripts/markdown_text_pkg/domain/models.ts';
import type { Policy } from '#scripts/markdown_text_pkg/domain/models.ts';
import { parsePolicy } from '#scripts/markdown_text_pkg/domain/policy.ts';
import { escapeForDiagnostic, scanMarkdownBytes } from '#scripts/markdown_text_pkg/domain/scan.ts';
import { makePolicyDocument, makeRangePolicyDocument } from '#tests/support/markdown-text-fixtures.ts';

function policy(document: Record<string, unknown> = makePolicyDocument()): Policy {
  const parsed = parsePolicy(document);
  if (isDomainError(parsed)) throw new Error(`${parsed.code}: ${parsed.message}`);
  return parsed;
}

function bytes(text: string): Uint8Array {
  return new TextEncoder().encode(text);
}

describe('diagnostic escaping', () => {
  it('spells non-printable characters as U+ forms', () => {
    expect(escapeForDiagnostic('ok\u0007bad')).toBe('okU+0007bad');
  });

  it('keeps ordinary text and spaces', () => {
    expect(escapeForDiagnostic('plain text')).toBe('plain text');
  });
});

describe('markdown scanning', () => {
  it('reports a prohibited scalar with its position and code point', () => {
    const findings = scanMarkdownBytes(bytes('abc\u200bdef\n'), policy(), 'docs/a.md');
    expect(findings).toEqual([{
      kind: 'scalar', path: 'docs/a.md', line: 1, column: 4, severity: 'error',
      ruleId: 'no-invisible', codepoint: 0x200b, excerpt: 'abcU+200Bdef',
    }]);
  });

  it('reports every occurrence on every line', () => {
    const findings = scanMarkdownBytes(bytes('\u200b\nx\u200by\n'), policy(), 'a.md');
    expect(findings.map(finding => [finding.kind === 'scalar' ? finding.line : 0, finding.kind === 'scalar' ? finding.column : 0]))
      .toEqual([[1, 1], [2, 2]]);
  });

  it('reports a scalar inside a range rule as a warning', () => {
    const findings = scanMarkdownBytes(bytes('ok \u{1f600}\n'), policy(makeRangePolicyDocument()), 'a.md');
    expect(findings[0]?.kind === 'scalar' ? findings[0].severity : '').toBe('warning');
  });

  it('normalizes Windows separators in the reported path', () => {
    const findings = scanMarkdownBytes(bytes('\u200b'), policy(), 'docs\\a.md');
    expect(findings[0]?.path).toBe('docs/a.md');
  });

  it('returns nothing for clean content', () => {
    expect(scanMarkdownBytes(bytes('plain\n'), policy(), 'a.md')).toEqual([]);
  });

  it('stops at the first ill-formed UTF-8 sequence', () => {
    const invalid = new Uint8Array([0x61, 0x0a, 0x62, 0xff, 0x63]);
    const findings = scanMarkdownBytes(invalid, policy(), 'a.md');
    expect(findings).toEqual([{
      kind: 'utf8', path: 'a.md', line: 2, column: 2, severity: 'error',
      ruleId: 'INVALID-UTF8', byteOffset: 4,
    }]);
  });

  it('treats a truncated multi-byte sequence as invalid at its first byte', () => {
    const findings = scanMarkdownBytes(new Uint8Array([0x61, 0xe2, 0x82]), policy(), 'a.md');
    expect(findings[0]?.kind === 'utf8' ? findings[0].byteOffset : 0).toBe(2);
  });

  it('keeps a leading byte order mark in the scanned text', () => {
    const findings = scanMarkdownBytes(bytes('\uFEFFx'), policy(), 'a.md');
    expect(findings).toEqual([]);
  });
});
