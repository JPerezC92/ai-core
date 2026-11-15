import { describe, expect, it } from 'vitest';

import { FindCode } from '../../src/application/find-code.ts';
import { isAstGrepError } from '../../src/domain/errors.ts';
import {
  createMatch,
  emptyMatchList,
  fakeAstGrepCli,
  matchList,
} from '../support/ast-grep-cli.factory.ts';

describe('FindCode', () => {
  it('returns sliced matches for json format', async () => {
    const operation = new FindCode(
      fakeAstGrepCli({
        dumpText: '',
        patternMatches: matchList([createMatch('a.ts'), createMatch('b.ts'), createMatch('c.ts')]),
        ruleMatches: emptyMatchList(),
        stdinMatches: [],
      }),
    );
    const result = await operation.execute({
      projectFolder: '/tmp',
      pattern: 'const $N = $V',
      maxResults: 1,
      outputFormat: 'json',
    });
    expect(isAstGrepError(result)).toBe(false);
    if (!isAstGrepError(result)) {
      expect(result.matches).toEqual([createMatch('a.ts')]);
      expect(result.totalMatches).toBe(3);
      expect(result.outputFormat).toBe('json');
    }
  });

  it('returns invalid_output_format without calling a throw', async () => {
    const operation = new FindCode(
      fakeAstGrepCli({
        dumpText: '',
        patternMatches: emptyMatchList(),
        ruleMatches: emptyMatchList(),
        stdinMatches: [],
      }),
    );
    const result = await operation.execute({
      projectFolder: '/tmp',
      pattern: 'x',
      outputFormat: 'xml',
    });
    expect(isAstGrepError(result) && result.code).toBe('invalid_output_format');
  });
});
