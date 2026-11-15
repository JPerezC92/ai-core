import { mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

import { describe, expect, it } from 'vitest';

import { AstGrepTools } from './ast-grep-tools.ts';
import { AstGrepProcess } from '../infrastructure/ast-grep-process.ts';

function astGrepAvailable(): boolean {
  const result = spawnSync('ast-grep', ['--version'], { encoding: 'utf8', shell: process.platform === 'win32' });
  return result.status === 0;
}

const available = astGrepAvailable();

describe.skipIf(!available)('ast-grep CLI tools', () => {
  const tools = new AstGrepTools(
    new AstGrepProcess({
      commandPrefix: 'ast-grep',
      configPath: undefined,
      platform: process.platform,
    }),
  );

  it('dumps a typescript CST on stderr', async () => {
    const dump = await tools.dumpSyntaxTree('const x = 1;', 'typescript', 'cst');
    expect(dump.length).toBeGreaterThan(0);
  });

  it('finds code with text and json formats and reports no-match', async () => {
    const folder = await mkdtemp(join(tmpdir(), 'astgrep-mcp-'));
    await writeFile(join(folder, 'sample.ts'), 'const hello = 1;\nconst other = 2;\n', 'utf8');
    const text = await tools.findCode(folder, 'const $NAME = $VALUE', 'typescript', 0, 'text');
    expect(typeof text === 'string' && text.startsWith('Found ')).toBe(true);
    const json = await tools.findCode(folder, 'const $NAME = $VALUE', 'typescript', 0, 'json');
    expect(Array.isArray(json) && json.length >= 1).toBe(true);
    const none = await tools.findCode(folder, 'class $NAME', 'typescript', 0, 'text');
    expect(none).toBe('No matches found');
  });

  it('finds by YAML rule and rejects bad yaml', async () => {
    const folder = await mkdtemp(join(tmpdir(), 'astgrep-mcp-'));
    await writeFile(join(folder, 'sample.ts'), 'function demo() {}\n', 'utf8');
    const yaml = ['id: demo', 'language: typescript', 'rule:', '  pattern: function $NAME() {}'].join('\n');
    const text = await tools.findCodeByRule(folder, yaml, 0, 'text');
    expect(typeof text === 'string' && text.includes('function demo()')).toBe(true);
    await expect(
      tools.findCodeByRule(folder, 'not: valid', 0, 'text'),
    ).rejects.toThrow(/failed with exit code/);
  });

  it('tests a rule against stdin code', async () => {
    const yaml = ['id: demo', 'language: typescript', 'rule:', '  pattern: const $N = $V'].join('\n');
    const matches = await tools.testMatchCodeRule('const a = 1;', yaml);
    expect(matches.length).toBeGreaterThan(0);
    await expect(tools.testMatchCodeRule('class X {}', yaml)).rejects.toThrow(
      /No matches found for the given code and rule/,
    );
  });
});

if (!available) {
  it('skips live CLI because ast-grep is not on PATH', () => {
    expect(available).toBe(false);
  });
}
