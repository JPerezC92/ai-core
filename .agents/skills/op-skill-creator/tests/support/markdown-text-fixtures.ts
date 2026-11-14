import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

/** A schema v1 policy document with one prohibited invisible scalar. */
export function makePolicyDocument(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    version: 1,
    id: 'fixture-policy',
    default_classification: 'allow',
    decoding: {
      encoding: 'utf-8',
      invalid_sequence: {
        id: 'INVALID-UTF8', severity: 'error', class: 'decoding', rationale: 'fixture',
      },
    },
    rules: [
      {
        id: 'no-invisible', severity: 'error', class: 'invisible', rationale: 'fixture',
        codepoints: [{ cp: 0x200b, hex: 'U+200B' }],
      },
    ],
    editor_projection: {
      scope: 'editor',
      setting_key: 'unicodeHighlight.ambiguousCharacters',
      overrides: [
        {
          codepoint: 0x200b, hex: 'U+200B', gremlins_key: '200b', severity: 'none',
          description: 'zero width space',
        },
      ],
    },
    ...overrides,
  };
}

/** A policy document reworded to cover an astral range instead of one scalar. */
export function makeRangePolicyDocument(): Record<string, unknown> {
  const base = makePolicyDocument();
  return {
    ...base,
    rules: [
      {
        id: 'no-emoji', severity: 'warning', class: 'symbol', rationale: 'fixture',
        ranges: [{ start: 0x1f600, end: 0x1f64f, start_hex: 'U+1F600', end_hex: 'U+1F64F' }],
      },
    ],
    editor_projection: { ...base.editor_projection as object, overrides: [] },
  };
}

export function writePolicy(root: string, document: Record<string, unknown> = makePolicyDocument()): string {
  const path = join(root, 'policy.json');
  writeFileSync(path, JSON.stringify(document, null, 2));
  return path;
}

export function writeMarkdown(root: string, name: string, content: string): string {
  const path = join(root, name);
  writeFileSync(path, content);
  return path;
}

export function writeDirectory(root: string, ...names: string[]): string {
  const path = join(root, ...names);
  mkdirSync(path, { recursive: true });
  return path;
}
