import { describe, expect, it } from 'vitest';

import { isDomainError } from '#scripts/markdown_text_pkg/domain/models.ts';
import type { Policy } from '#scripts/markdown_text_pkg/domain/models.ts';
import { compareEditorProjection, parsePolicy } from '#scripts/markdown_text_pkg/domain/policy.ts';
import { makePolicyDocument } from '#tests/support/markdown-text-fixtures.ts';

const SETTING = 'unicodeHighlight.ambiguousCharacters';

function policy(): Policy {
  const parsed = parsePolicy(makePolicyDocument());
  if (isDomainError(parsed)) throw new Error(`${parsed.code}: ${parsed.message}`);
  return parsed;
}

function settings(entries: Record<string, unknown> | undefined, scope = 'editor'): Record<string, unknown> {
  if (entries === undefined) return { [scope]: {} };
  return { [scope]: { [SETTING]: entries } };
}

const MATCHING = { '200b': { level: 'none', description: 'zero width space' } };

describe('editor projection comparison', () => {
  it('accepts a matching projection', () => {
    expect(compareEditorProjection(policy(), settings(MATCHING), '.vscode/settings.json')).toBeUndefined();
  });

  it('reports a missing key', () => {
    const drift = compareEditorProjection(policy(), settings({}), 'a.json');
    expect(drift).toEqual({ kind: 'editor-drift', path: 'a.json', missing: ['200b'], extra: [], mismatched: [] });
  });

  it('reports an extra cloned key', () => {
    const drift = compareEditorProjection(policy(), settings({ ...MATCHING, '00a0': { level: 'none' } }), 'a.json');
    expect(drift).toEqual({ kind: 'editor-drift', path: 'a.json', missing: [], extra: ['00a0'], mismatched: [] });
  });

  it('reports a mismatched entry', () => {
    const drift = compareEditorProjection(policy(), settings({ '200b': { level: 'warning', description: 'zero width space' } }), 'a.json');
    expect(drift).toEqual({ kind: 'editor-drift', path: 'a.json', missing: [], extra: [], mismatched: ['200b'] });
  });

  it('treats an absent scope as fully missing', () => {
    const drift = compareEditorProjection(policy(), {}, 'a.json');
    expect(drift).toEqual({ kind: 'editor-drift', path: 'a.json', missing: ['200b'], extra: [], mismatched: [] });
  });

  it('rejects a non-object settings document', () => {
    const drift = compareEditorProjection(policy(), [], 'a.json');
    expect(isDomainError(drift) ? drift.message : '').toBe('editor settings must be a JSON object');
  });

  it('rejects a non-object scope', () => {
    const drift = compareEditorProjection(policy(), { editor: [] }, 'a.json');
    expect(isDomainError(drift) ? drift.message : '').toBe('editor scope must be an object');
  });

  it('normalizes Windows separators in the reported path', () => {
    const drift = compareEditorProjection(policy(), settings({}), '.vscode\\settings.json');
    expect(drift !== undefined && !isDomainError(drift) ? drift.path : '').toBe('.vscode/settings.json');
  });
});
