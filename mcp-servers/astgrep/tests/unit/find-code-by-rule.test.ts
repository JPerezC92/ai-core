import { describe, expect, it } from 'vitest';

import { FindCodeByRule } from '#application/find-code-by-rule.ts';
import { isAstGrepError } from '#domain/errors.ts';
import {
  createMatch,
  emptyMatchList,
  fakeAstGrepCli,
  matchList,
} from '#support/ast-grep-cli.factory.ts';

describe('FindCodeByRule', () => {
  it('returns matches for text format', async () => {
    const operation = new FindCodeByRule(
      fakeAstGrepCli({
        dumpText: '',
        patternMatches: emptyMatchList(),
        ruleMatches: matchList([createMatch('a.ts', 'fn()')]),
        stdinMatches: [],
      }),
    );
    const result = await operation.execute({
      projectFolder: '/tmp',
      yaml: 'id: demo',
      outputFormat: 'text',
    });
    expect(isAstGrepError(result)).toBe(false);
    if (!isAstGrepError(result)) {
      expect(result.matches).toHaveLength(1);
      expect(result.outputFormat).toBe('text');
    }
  });

  it('returns invalid_output_format for unknown format', async () => {
    const operation = new FindCodeByRule(
      fakeAstGrepCli({
        dumpText: '',
        patternMatches: emptyMatchList(),
        ruleMatches: emptyMatchList(),
        stdinMatches: [],
      }),
    );
    const result = await operation.execute({
      projectFolder: '/tmp',
      yaml: 'id: demo',
      outputFormat: 'csv',
    });
    expect(isAstGrepError(result) && result.message).toMatch(/Invalid output_format/);
  });
});
