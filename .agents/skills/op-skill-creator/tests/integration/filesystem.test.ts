import { mkdtempSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';

import { isDomainError } from '#scripts/markdown_text_pkg/domain/models.ts';
import { MarkdownFilesystem, PolicyLoader, firstDuplicateJsonKey } from '#scripts/markdown_text_pkg/infrastructure/filesystem.ts';
import {
  makePolicyDocument, writeDirectory, writeMarkdown, writePolicy,
} from '#tests/support/markdown-text-fixtures.ts';

const roots: string[] = [];

function temporaryRoot(): string {
  const root = mkdtempSync(join(tmpdir(), 'markdown-text-test-'));
  roots.push(root);
  return root;
}

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

describe('markdown discovery', () => {
  it('finds markdown files and skips excluded and non-markdown entries', () => {
    const root = temporaryRoot();
    writeMarkdown(root, 'a.md', 'text');
    writeMarkdown(root, 'b.MD', 'text');
    writeMarkdown(root, 'notes.txt', 'text');
    writeDirectory(root, 'output');
    writeMarkdown(join(root, 'output'), 'ignored.md', 'text');

    const result = new MarkdownFilesystem().discover([root]);

    expect(result.failures).toEqual([]);
    expect(result.targets.map(target => target.displayPath).sort())
      .toEqual([`${root.replaceAll('\\', '/')}/a.md`, `${root.replaceAll('\\', '/')}/b.MD`]);
  });

  it('reports a missing path', () => {
    const root = temporaryRoot();
    const result = new MarkdownFilesystem().discover([join(root, 'missing.md')]);
    expect(result.targets).toEqual([]);
    expect(result.failures[0]?.code).toBe('input');
    expect(result.failures[0]?.message).toContain('missing path:');
  });

  it('reports an explicit non-markdown file', () => {
    const root = temporaryRoot();
    const path = writeMarkdown(root, 'notes.txt', 'text');
    const result = new MarkdownFilesystem().discover([path]);
    expect(result.failures[0]?.message).toContain('not a markdown file:');
  });

  it('does not follow a symlinked root', () => {
    const root = temporaryRoot();
    writeMarkdown(root, 'a.md', 'text');
    const link = join(root, 'link.md');
    try {
      symlinkSync(join(root, 'a.md'), link);
    } catch {
      return; // platform without symlink rights
    }
    const result = new MarkdownFilesystem().discover([link]);
    expect(result.failures[0]?.message).toContain('symlink not followed:');
  });

  it('deduplicates a repeated root', () => {
    const root = temporaryRoot();
    writeMarkdown(root, 'a.md', 'text');
    const result = new MarkdownFilesystem().discover([root, root]);
    expect(result.targets).toHaveLength(1);
  });
});

describe('policy loading', () => {
  it('loads a valid policy', () => {
    const root = temporaryRoot();
    const loaded = new PolicyLoader().load(writePolicy(root));
    expect(isDomainError(loaded) ? loaded.message : loaded.id).toBe('fixture-policy');
  });

  it('reports a missing policy path', () => {
    const root = temporaryRoot();
    const loaded = new PolicyLoader().load(join(root, 'absent.json'));
    expect(isDomainError(loaded) ? loaded.message : '').toContain('missing policy path:');
  });

  it('rejects duplicate JSON keys', () => {
    const root = temporaryRoot();
    const path = writeMarkdown(root, 'policy.json', '{"version": 1, "version": 2}');
    const loaded = new PolicyLoader().load(path);
    expect(isDomainError(loaded) ? loaded.message : '').toBe('invalid policy JSON: duplicate key version');
  });

  it('rejects a JSON root that is not an object', () => {
    const root = temporaryRoot();
    const path = writeMarkdown(root, 'policy.json', '[]');
    const loaded = new PolicyLoader().load(path);
    expect(isDomainError(loaded) ? loaded.message : '').toBe('policy JSON root must be an object');
  });

  it('rejects invalid JSON', () => {
    const root = temporaryRoot();
    const path = writeMarkdown(root, 'policy.json', '{');
    const loaded = new PolicyLoader().load(path);
    expect(isDomainError(loaded) ? loaded.message : '').toContain('invalid policy JSON:');
  });
});

describe('duplicate key detection', () => {
  it('ignores duplicate-looking text inside strings', () => {
    expect(firstDuplicateJsonKey('{"a": "x\\"y", "b": "a"}')).toBeUndefined();
  });

  it('allows the same key in different objects', () => {
    expect(firstDuplicateJsonKey('{"a": {"k": 1}, "b": {"k": 2}}')).toBeUndefined();
  });

  it('finds a repeated key in a nested object', () => {
    expect(firstDuplicateJsonKey('{"a": {"k": 1, "k": 2}}')).toBe('k');
  });
});
