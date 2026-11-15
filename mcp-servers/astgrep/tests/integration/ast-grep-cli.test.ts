import { mkdtemp, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { describe, expect, it } from 'vitest';

import { DumpSyntaxTree } from '#application/dump-syntax-tree.ts';
import { FindCode } from '#application/find-code.ts';
import { FindCodeByRule } from '#application/find-code-by-rule.ts';
import { TestMatchCodeRule } from '#application/test-match-code-rule.ts';
import { isAstGrepError } from '#domain/errors.ts';
import { AstGrepProcess } from '#infrastructure/adapters/ast-grep-process.ts';
import { astGrepAvailable } from '#support/cli-available.ts';

const available = astGrepAvailable();

const cli = new AstGrepProcess({
  commandPrefix: 'ast-grep',
  configPath: undefined,
  platform: process.platform,
});

describe.skipIf(!available)('ast-grep CLI tools', () => {
  it('dumps a typescript CST on stderr', async () => {
    const dump = await new DumpSyntaxTree(cli).execute({
      code: 'const x = 1;',
      language: 'typescript',
      format: 'cst',
    });
    expect(dump.length).toBeGreaterThan(0);
  });

  it('finds code with text and json formats and reports no-match', async () => {
    const folder = await mkdtemp(join(tmpdir(), 'astgrep-mcp-'));
    await writeFile(join(folder, 'sample.ts'), 'const hello = 1;\nconst other = 2;\n', 'utf8');
    const findCode = new FindCode(cli);
    const text = await findCode.execute({
      projectFolder: folder,
      pattern: 'const $NAME = $VALUE',
      language: 'typescript',
      outputFormat: 'text',
    });
    expect(isAstGrepError(text)).toBe(false);
    if (!isAstGrepError(text)) {
      expect(text.matches.length).toBeGreaterThanOrEqual(1);
    }
    const json = await findCode.execute({
      projectFolder: folder,
      pattern: 'const $NAME = $VALUE',
      language: 'typescript',
      outputFormat: 'json',
    });
    expect(!isAstGrepError(json) && json.matches.length >= 1).toBe(true);
    const none = await findCode.execute({
      projectFolder: folder,
      pattern: 'class $NAME',
      language: 'typescript',
      outputFormat: 'text',
    });
    expect(!isAstGrepError(none) && none.matches.length === 0).toBe(true);
  });

  it('finds by YAML rule and rejects bad yaml', async () => {
    const folder = await mkdtemp(join(tmpdir(), 'astgrep-mcp-'));
    await writeFile(join(folder, 'sample.ts'), 'function demo() {}\n', 'utf8');
    const yaml = ['id: demo', 'language: typescript', 'rule:', '  pattern: function $NAME() {}'].join(
      '\n',
    );
    const findByRule = new FindCodeByRule(cli);
    const text = await findByRule.execute({
      projectFolder: folder,
      yaml,
      outputFormat: 'text',
    });
    expect(!isAstGrepError(text) && text.matches.length >= 1).toBe(true);
    await expect(
      findByRule.execute({ projectFolder: folder, yaml: 'not: valid', outputFormat: 'text' }),
    ).rejects.toThrow(/failed with exit code/);
  });

  it('tests a rule against stdin code including no-match', async () => {
    const yaml = ['id: demo', 'language: typescript', 'rule:', '  pattern: const $N = $V'].join('\n');
    const testMatch = new TestMatchCodeRule(cli);
    const matches = await testMatch.execute({ code: 'const a = 1;', yaml });
    expect(!isAstGrepError(matches) && matches.length > 0).toBe(true);
    const none = await testMatch.execute({ code: 'class X {}', yaml });
    expect(isAstGrepError(none) && none.code).toBe('no_match');
  });
});

if (!available) {
  it('skips live CLI because ast-grep is not on PATH', () => {
    expect(available).toBe(false);
  });
}
