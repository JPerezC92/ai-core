import { describe, expect, it } from 'vitest';

import { resolveSpawnFile, splitCommandPrefix } from './command-prefix.ts';

describe('splitCommandPrefix', () => {
  it('splits a posix wrapper command', () => {
    expect(splitCommandPrefix('uv run ast-grep', 'linux')).toEqual(['uv', 'run', 'ast-grep']);
  });

  it('strips wrapping quotes on win32', () => {
    expect(splitCommandPrefix('"C:\\\\bin\\\\ast-grep.exe"', 'win32')).toEqual([
      'C:\\\\bin\\\\ast-grep.exe',
    ]);
  });

  it('rejects an empty prefix', () => {
    expect(() => splitCommandPrefix('   ', 'linux')).toThrow(/AST_GREP_PATH must not be empty/);
  });
});

describe('resolveSpawnFile', () => {
  it('uses ast-grep.exe on win32 for the bare ast-grep token, never a shell or .cmd', () => {
    expect(resolveSpawnFile(['ast-grep'], 'win32')).toEqual(['ast-grep.exe']);
    expect(resolveSpawnFile(['ast-grep', 'run'], 'win32')).toEqual(['ast-grep.exe', 'run']);
    expect(resolveSpawnFile(['ast-grep'], 'linux')).toEqual(['ast-grep']);
    expect(resolveSpawnFile(['C:\\\\bin\\\\ast-grep.exe'], 'win32')).toEqual([
      'C:\\\\bin\\\\ast-grep.exe',
    ]);
    expect(resolveSpawnFile(['uv', 'run', 'ast-grep'], 'win32')).toEqual([
      'uv',
      'run',
      'ast-grep',
    ]);
  });
});
