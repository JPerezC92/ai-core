import { describe, expect, it } from 'vitest';

import { TestMatchCodeRule } from '../../src/application/test-match-code-rule.ts';
import { isAstGrepError, NO_MATCH_MESSAGE } from '../../src/domain/errors.ts';
import { createMatch, emptyMatchList, fakeAstGrepCli } from '../support/ast-grep-cli.factory.ts';

describe('TestMatchCodeRule', () => {
  it('returns matches when the CLI finds some', async () => {
    const operation = new TestMatchCodeRule(
      fakeAstGrepCli({
        dumpText: '',
        patternMatches: emptyMatchList(),
        ruleMatches: emptyMatchList(),
        stdinMatches: [createMatch('', 'const a = 1;')],
      }),
    );
    const result = await operation.execute({ code: 'const a = 1;', yaml: 'id: demo' });
    expect(isAstGrepError(result)).toBe(false);
    if (!isAstGrepError(result)) {
      expect(result).toHaveLength(1);
    }
  });

  it('returns no_match with the Python MCP message', async () => {
    const operation = new TestMatchCodeRule(
      fakeAstGrepCli({
        dumpText: '',
        patternMatches: emptyMatchList(),
        ruleMatches: emptyMatchList(),
        stdinMatches: [],
      }),
    );
    const result = await operation.execute({ code: 'class X {}', yaml: 'id: demo' });
    expect(isAstGrepError(result) && result.code).toBe('no_match');
    expect(isAstGrepError(result) && result.message).toBe(NO_MATCH_MESSAGE);
  });
});
