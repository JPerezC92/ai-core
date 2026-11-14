import { spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, describe, expect, it } from 'vitest';

import { makePolicyDocument, writeMarkdown, writePolicy } from '#tests/support/markdown-text-fixtures.ts';

const entry = resolve(dirname(fileURLToPath(import.meta.url)), '../../scripts/check_markdown_text.ts');
const roots: string[] = [];

function temporaryRoot(): string {
  const root = mkdtempSync(join(tmpdir(), 'markdown-text-cli-'));
  roots.push(root);
  return root;
}

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

function run(args: string[]) {
  const result = spawnSync(process.execPath, [entry, ...args], { encoding: 'utf8' });
  if (result.error) throw result.error;
  return result;
}

describe('checker CLI', () => {
  it('exits 0 for clean Markdown', () => {
    const root = temporaryRoot();
    const policy = writePolicy(root);
    const document = writeMarkdown(root, 'clean.md', 'plain text\n');

    const result = run(['--policy', policy, document]);

    expect(result.status).toBe(0);
    expect(result.stdout).toBe('');
    expect(result.stderr).toBe('');
  });

  it('reports a finding with position and code point, without a character name', () => {
    const root = temporaryRoot();
    const policy = writePolicy(root);
    const document = writeMarkdown(root, 'bad.md', 'abc\u200bdef\n');

    const result = run(['--policy', policy, document]);

    expect(result.status).toBe(1);
    expect(result.stdout.trimEnd()).toBe(
      `${document.replaceAll('\\', '/')}:1:4: error no-invisible U+200B abcU+200Bdef`,
    );
    expect(result.stderr).toBe('');
  });

  it('exits 1 for editor drift against a supplied settings file', () => {
    const root = temporaryRoot();
    const policy = writePolicy(root);
    const document = writeMarkdown(root, 'clean.md', 'plain\n');
    const settings = writeMarkdown(root, 'settings.json', JSON.stringify({ editor: {} }));

    const result = run(['--policy', policy, '--check-editor', settings, document]);

    expect(result.status).toBe(1);
    expect(result.stdout).toContain(': error EDITOR-DRIFT missing=200b extra= mismatched=');
  });

  it('exits 2 when the policy is invalid', () => {
    const root = temporaryRoot();
    const policy = writePolicy(root, makePolicyDocument({ version: 2 }));
    const document = writeMarkdown(root, 'clean.md', 'plain\n');

    const result = run(['--policy', policy, document]);

    expect(result.status).toBe(2);
    expect(result.stderr).toContain('policy: unsupported policy version: 2');
  });

  it('exits 2 when --policy is missing', () => {
    const result = run(['some.md']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain('the following arguments are required: --policy');
  });

  it('exits 2 when no path is supplied', () => {
    const root = temporaryRoot();
    const policy = writePolicy(root);
    const result = run(['--policy', policy]);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain('the following arguments are required: paths');
  });

  it('keeps warnings from changing the exit status', () => {
    const root = temporaryRoot();
    const document = writeMarkdown(root, 'warn.md', 'ok \u{1f600}\n');
    const policy = writePolicy(root, makePolicyDocument({
      rules: [{
        id: 'no-emoji', severity: 'warning', class: 'symbol', rationale: 'fixture',
        ranges: [{ start: 0x1f600, end: 0x1f64f, start_hex: 'U+1F600', end_hex: 'U+1F64F' }],
      }],
    }));

    const result = run(['--policy', policy, document]);

    expect(result.status).toBe(0);
    expect(result.stdout).toContain('warning no-emoji U+1F600');
  });
});
