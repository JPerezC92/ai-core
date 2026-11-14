import { describe, expect, it } from 'vitest';

import { execute } from '#scripts/op_model_lookup/application/find_models.ts';
import type {
  LookupOutcome, Model, ModelSource, NoMatchingModels, NoModelsAvailable,
} from '#scripts/op_model_lookup/domain/catalog.ts';

/** Narrow a lookup outcome to its business-failure branch. */
function asOutcome(value: LookupOutcome): NoModelsAvailable | NoMatchingModels {
  if (Array.isArray(value)) throw new Error('expected a business outcome, received a selection');
  return value as NoModelsAvailable | NoMatchingModels;
}

function model(overrides: Partial<Model> = {}): Model {
  return {
    config: 'deepseek/deepseek-v4', id: 'deepseek-v4', provider: 'deepseek',
    name: 'deepseek-v4', costIn: 0, costOut: 0, ...overrides,
  };
}

function source(models: readonly Model[], failure?: Error): ModelSource {
  return { fetch: () => { if (failure !== undefined) throw failure; return models; } };
}

describe('model lookup', () => {
  it('returns every model for an empty query', () => {
    const outcome = execute('', source([model(), model({ config: 'openai/gpt', id: 'gpt', provider: 'openai', name: 'gpt' })]));
    expect(Array.isArray(outcome) ? outcome.length : 0).toBe(2);
  });

  it('returns only matching models in encounter order', () => {
    const outcome = execute('openai', source([model(), model({ config: 'openai/gpt', id: 'gpt', provider: 'openai', name: 'gpt' })]));
    expect(Array.isArray(outcome) ? outcome.map(entry => entry.config) : []).toEqual(['openai/gpt']);
  });

  it('reports the empty catalog as a business outcome', () => {
    const outcome = asOutcome(execute('', source([])));
    expect([outcome.kind, outcome.code]).toEqual(['no-models', 'no_models_available']);
  });

  it('reports an unmatched query as a business outcome naming the query', () => {
    const outcome = asOutcome(execute('claude', source([model()])));
    expect([outcome.kind, outcome.code]).toEqual(['no-match', 'no_matching_models']);
    expect(outcome.kind === 'no-match' ? outcome.query : '').toBe('claude');
  });

  it('returns an empty selection rather than a failure for an empty query on a matching source', () => {
    const outcome = execute('', source([model({ config: 'a/b', id: 'b', provider: 'a', name: 'b' })]));
    expect(Array.isArray(outcome) ? outcome.length : -1).toBe(1);
  });

  it('propagates a boundary failure instead of converting it to an outcome', () => {
    expect(() => execute('', source([], new Error('boom')))).toThrow('boom');
  });
});
