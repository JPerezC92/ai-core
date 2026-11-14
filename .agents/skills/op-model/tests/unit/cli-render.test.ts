import { describe, expect, it } from 'vitest';

import type { Model } from '#scripts/op_model_lookup/domain/catalog.ts';
import { noMatchingModels, noModelsAvailable } from '#scripts/op_model_lookup/domain/catalog.ts';
import { renderSelection } from '#scripts/op_model_lookup/infrastructure/cli.ts';

function model(overrides: Partial<Model> = {}): Model {
  return {
    config: 'deepseek/deepseek-v4', id: 'deepseek-v4', provider: 'deepseek',
    name: 'deepseek-v4', costIn: 0, costOut: 0, ...overrides,
  };
}

describe('record rendering', () => {
  it('serializes the six contract fields with the reference spacing', () => {
    expect(renderSelection([model()], 'deep')).toBe(
      '{"config": "deepseek/deepseek-v4", "id": "deepseek-v4", "provider": "deepseek", "name": "deepseek-v4", "cost_in": 0.0, "cost_out": 0.0}\n',
    );
  });

  it('keeps a decimal point on a fractional cost', () => {
    expect(renderSelection([model({ costIn: 0.14, costOut: 3 })], 'deep')).toContain('"cost_in": 0.14, "cost_out": 3.0');
  });

  it('renders one line per selected model', () => {
    const rendered = renderSelection([model(), model({ config: 'a/b', id: 'b', provider: 'a', name: 'b' })], 'x');
    expect(rendered.trimEnd().split('\n')).toHaveLength(2);
  });
});

describe('grouped rendering', () => {
  it('groups by provider, sorted, with a trailing newline', () => {
    const rendered = renderSelection([
      model({ config: 'openai/gpt', id: 'gpt', provider: 'openai', name: 'gpt' }),
      model(),
    ], '');
    expect(rendered).toBe('## deepseek\n  deepseek/deepseek-v4\n\n## openai\n  openai/gpt\n\n');
  });

  it('shows a human name only when it differs from the model id', () => {
    expect(renderSelection([model({ name: 'DeepSeek V4' })], '')).toContain('  deepseek/deepseek-v4 | DeepSeek V4');
  });

  it('shows costs only when the source provides one', () => {
    expect(renderSelection([model({ costIn: 0.14, costOut: 3 })], ''))
      .toContain(' | in:0.14 per 1M | out:3.0 per 1M');
  });

  it('sorts models inside a provider by config', () => {
    const rendered = renderSelection([
      model({ config: 'a/z', id: 'z', provider: 'a', name: 'z' }),
      model({ config: 'a/b', id: 'b', provider: 'a', name: 'b' }),
    ], '');
    expect(rendered.indexOf('a/b')).toBeLessThan(rendered.indexOf('a/z'));
  });

  it('renders an empty selection as nothing', () => {
    expect(renderSelection([], '')).toBe('');
  });
});

describe('business outcomes carry their documented messages', () => {
  it('names the empty-catalog message', () => {
    expect(noModelsAvailable().message).toBe('No models parsed from `opencode models` output.');
  });

  it('names the unmatched-query message with the query and the listing hint', () => {
    const outcome = noMatchingModels('claude');
    expect(outcome.message).toContain('No match for claude in `opencode models`.');
    expect(outcome.message).toContain('.agents/skills/op-model/scripts/models.ts');
  });
});
