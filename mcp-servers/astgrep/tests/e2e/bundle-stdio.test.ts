import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { describe, expect, it } from 'vitest';

const here = dirname(fileURLToPath(import.meta.url));
const bundlePath = join(here, '..', '..', 'dist', 'stdio.mjs');

describe('committed ast-grep MCP bundle', () => {
  it('lists four tools over stdio without uvx or python', async () => {
    const transport = new StdioClientTransport({
      command: process.execPath,
      args: [bundlePath],
      stderr: 'pipe',
      cwd: join(here, '..', '..', '..', '..'),
    });
    const client = new Client({ name: 'astgrep-bundle-e2e', version: '0.0.0' });
    await client.connect(transport);
    try {
      const listed = await client.listTools();
      const names = listed.tools.map((tool) => tool.name).sort();
      expect(names).toEqual([
        'dump_syntax_tree',
        'find_code',
        'find_code_by_rule',
        'test_match_code_rule',
      ]);
      const dumped = await client.callTool({
        name: 'dump_syntax_tree',
        arguments: { code: 'const x = 1;', language: 'typescript', format: 'cst' },
      });
      expect(dumped.isError).toBeFalsy();
      const text = dumped.content.find((part) => part.type === 'text');
      expect(text && 'text' in text && text.text.length > 0).toBe(true);
    } finally {
      await client.close();
    }
  });
});
