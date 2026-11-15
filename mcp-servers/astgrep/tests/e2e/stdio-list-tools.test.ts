import { Client } from '@modelcontextprotocol/client';
import { InMemoryTransport } from '@modelcontextprotocol/server';
import { describe, expect, it } from 'vitest';

import { DumpSyntaxTree } from '../../src/application/dump-syntax-tree.ts';
import { FindCode } from '../../src/application/find-code.ts';
import { FindCodeByRule } from '../../src/application/find-code-by-rule.ts';
import { TestMatchCodeRule } from '../../src/application/test-match-code-rule.ts';
import { createAstGrepServer } from '../../src/mcp/ast-grep-server.ts';
import { emptyMatchList, fakeAstGrepCli } from '../support/ast-grep-cli.factory.ts';

describe('ast-grep MCP assembled server', () => {
  it('lists the four tools', async () => {
    const cli = fakeAstGrepCli({
      dumpText: 'ROOT',
      patternMatches: emptyMatchList(),
      ruleMatches: emptyMatchList(),
      stdinMatches: [],
    });
    const server = createAstGrepServer(
      {
        dumpSyntaxTree: new DumpSyntaxTree(cli),
        findCode: new FindCode(cli),
        findCodeByRule: new FindCodeByRule(cli),
        testMatchCodeRule: new TestMatchCodeRule(cli),
      },
      ['typescript'],
    );
    const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
    const client = new Client({ name: 'astgrep-e2e', version: '0.0.0' });
    await server.connect(serverTransport);
    await client.connect(clientTransport);
    try {
      const listed = await client.listTools();
      const names = listed.tools.map((tool) => tool.name).sort();
      expect(names).toEqual([
        'dump_syntax_tree',
        'find_code',
        'find_code_by_rule',
        'test_match_code_rule',
      ]);
    } finally {
      await client.close();
      await server.close();
    }
  });
});
