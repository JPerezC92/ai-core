import { describe, expect, it } from 'vitest';

import { normalize, parseRecords, matches } from '#scripts/op_model_lookup/domain/catalog.ts';
import type { Model } from '#scripts/op_model_lookup/domain/catalog.ts';

function model(overrides: Partial<Model> = {}): Model {
  return {
    config: 'deepseek/deepseek-v4', id: 'deepseek-v4', provider: 'deepseek',
    name: 'deepseek-v4', costIn: 0, costOut: 0, ...overrides,
  };
}

describe('catalog parsing', () => {
  it('parses selector lines into models with zero costs', () => {
    const parsed = parseRecords('deepseek/deepseek-v4\nopenai/gpt-5.1\n');
    expect(parsed.models).toEqual([
      { config: 'deepseek/deepseek-v4', id: 'deepseek-v4', provider: 'deepseek', name: 'deepseek-v4', costIn: 0, costOut: 0 },
      { config: 'openai/gpt-5.1', id: 'gpt-5.1', provider: 'openai', name: 'gpt-5.1', costIn: 0, costOut: 0 },
    ]);
    expect(parsed.issues).toEqual([]);
  });

  it('skips blank lines without recording issues', () => {
    expect(parseRecords('\n  \n\n').issues).toEqual([]);
  });

  it('records a non-selector line as an issue and keeps parsing', () => {
    const parsed = parseRecords('not a selector\ndeepseek/deepseek-v4\n');
    expect(parsed.models).toHaveLength(1);
    expect(parsed.issues).toEqual([
      { code: 'unrecognized_line', message: 'not a selector: not a provider/model selector' },
    ]);
  });

  it('trims surrounding whitespace before matching', () => {
    expect(parseRecords('  openai/gpt-5.1  \n').models[0]?.config).toBe('openai/gpt-5.1');
  });

  it('rejects a selector whose provider starts with punctuation', () => {
    expect(parseRecords('-bad/model\n').models).toEqual([]);
  });
});

describe('query normalization', () => {
  it('lowercases and strips non-alphanumerics', () => {
    expect(normalize('DeepSeek V4-Flash')).toBe('deepseekv4flash');
  });

  it('reduces punctuation-only text to empty', () => {
    expect(normalize('---')).toBe('');
  });
});

describe('model matching', () => {
  it('matches everything for an empty query', () => {
    expect(matches('', model())).toBe(true);
  });

  it('matches a provider fragment', () => {
    expect(matches('deep', model())).toBe(true);
  });

  it('matches the human name rather than the config only', () => {
    expect(matches('V4', model({ config: 'x/y', id: 'y', name: 'DeepSeek V4' }))).toBe(true);
  });

  it('normalizes separators on both sides', () => {
    expect(matches('deepseek v4', model())).toBe(true);
  });

  it('rejects an unrelated query', () => {
    expect(matches('claude', model())).toBe(false);
  });

  it('treats a punctuation-only query as matching everything', () => {
    expect(matches('...', model())).toBe(true);
  });
});
