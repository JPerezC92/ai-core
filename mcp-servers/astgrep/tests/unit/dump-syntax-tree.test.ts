import { describe, expect, it } from 'vitest';

import { DumpSyntaxTree } from '../../src/application/dump-syntax-tree.ts';
import { emptyMatchList, fakeAstGrepCli } from '../support/ast-grep-cli.factory.ts';

describe('DumpSyntaxTree', () => {
  it('returns dump text from the injected CLI', async () => {
    const operation = new DumpSyntaxTree(
      fakeAstGrepCli({
        dumpText: 'ROOT',
        patternMatches: emptyMatchList(),
        ruleMatches: emptyMatchList(),
        stdinMatches: [],
      }),
    );
    await expect(
      operation.execute({ code: 'const x = 1;', language: 'typescript' }),
    ).resolves.toBe('ROOT');
  });
});
