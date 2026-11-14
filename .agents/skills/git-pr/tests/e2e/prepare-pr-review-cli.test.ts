import { spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, describe, expect, it } from 'vitest';

import { makeCompletedBody, makeMetadata } from '#tests/support/review-content-fixtures.ts';

const entry = resolve(dirname(fileURLToPath(import.meta.url)), '../../scripts/prepare_pr_review.ts');
const roots: string[] = [];
const DRAFT = `Title: feat: review content preparation\n\n---\n\n${makeCompletedBody()}`;

function root(): string {
  const path = mkdtempSync(join(tmpdir(), 'prepare-pr-review-test-'));
  roots.push(path);
  return path;
}

function write(path: string, content: string): string {
  writeFileSync(path, content);
  return path;
}

function run(args: string[]) {
  const result = spawnSync(process.execPath, [entry, ...args], { encoding: 'utf8' });
  if (result.error) throw result.error;
  return result;
}

afterEach(() => {
  for (const path of roots.splice(0)) rmSync(path, { recursive: true, force: true });
});

describe('initialize command', () => {
  it('creates the working body from a creation draft', () => {
    const directory = root();
    const draft = write(join(directory, 'draft.md'), DRAFT);
    const working = join(directory, 'working-body.md');

    const result = run(['initialize', '--draft', draft, '--working-body', working]);

    expect(result.status).toBe(0);
    expect(result.stdout).toBe('{"status": "prepared", "command": "initialize"}\n');
    expect(readFileSync(working, 'utf8')).toBe(makeCompletedBody());
  });

  it('rejects a malformed draft with the documented payload', () => {
    const directory = root();
    const draft = write(join(directory, 'draft.md'), '## Summary\n\ntext\n');

    const result = run(['initialize', '--draft', draft, '--working-body', join(directory, 'w.md')]);

    expect(result.status).toBe(1);
    expect(result.stdout).toBe('{"code": "DRAFT_INVALID", "message": "creation draft title wrapper and Summary required"}\n');
  });

  it('never overwrites an existing working body', () => {
    const directory = root();
    const draft = write(join(directory, 'draft.md'), DRAFT);
    const working = write(join(directory, 'working-body.md'), 'existing\n');

    const result = run(['initialize', '--draft', draft, '--working-body', working]);

    expect(result.status).toBe(2);
    expect(result.stderr).toContain('input/output failure:');
    expect(readFileSync(working, 'utf8')).toBe('existing\n');
  });
});

describe('validate command', () => {
  it('accepts a fresh completed body', () => {
    const directory = root();
    const metadata = JSON.stringify(makeMetadata());
    const baseline = write(join(directory, 'baseline.json'), metadata);
    const current = write(join(directory, 'current.json'), metadata);
    const working = write(join(directory, 'working-body.md'), makeCompletedBody());

    const result = run(['validate', '--baseline', baseline, '--current', current, '--working-body', working]);

    expect(result.status).toBe(0);
    expect(result.stdout).toBe('{"status": "prepared", "command": "validate"}\n');
  });

  it('rejects diverged metadata with the documented code', () => {
    const directory = root();
    const baseline = write(join(directory, 'baseline.json'), JSON.stringify(makeMetadata()));
    const current = write(join(directory, 'current.json'), JSON.stringify(makeMetadata({ headRefOid: 'ffffffffffffffffffffffffffffffffffffffff' })));
    const working = write(join(directory, 'working-body.md'), makeCompletedBody());

    const result = run(['validate', '--baseline', baseline, '--current', current, '--working-body', working]);

    expect(result.status).toBe(1);
    expect(result.stdout).toBe('{"code": "REMOTE_DIVERGED", "message": "remote metadata differs from accepted baseline"}\n');
  });

  it('exits 2 when a supplied file is unreadable', () => {
    const directory = root();
    const baseline = write(join(directory, 'baseline.json'), JSON.stringify(makeMetadata()));

    const result = run(['validate', '--baseline', baseline, '--current', join(directory, 'absent.json'), '--working-body', join(directory, 'w.md')]);

    expect(result.status).toBe(2);
    expect(result.stderr).toContain('input/output failure:');
  });

  it('exits 2 when a JSON input is malformed', () => {
    const directory = root();
    const baseline = write(join(directory, 'baseline.json'), '{');
    const current = write(join(directory, 'current.json'), JSON.stringify(makeMetadata()));
    const working = write(join(directory, 'working-body.md'), makeCompletedBody());

    const result = run(['validate', '--baseline', baseline, '--current', current, '--working-body', working]);

    expect(result.status).toBe(2);
    expect(result.stderr).toContain('input/output failure:');
  });
});

describe('command line contract', () => {
  it('rejects a missing subcommand', () => {
    const result = run([]);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain('the following arguments are required: command');
  });

  it('rejects an unknown subcommand', () => {
    const result = run(['publish']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain("argument command: invalid choice: 'publish'");
  });

  it('rejects a missing required option', () => {
    const result = run(['initialize', '--draft', 'd.md']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain('the following arguments are required: --working-body');
  });

  it('writes no artifact when the command line is rejected', () => {
    const directory = root();
    const working = join(directory, 'working-body.md');
    run(['initialize', '--draft', join(directory, 'draft.md')]);
    expect(existsSync(working)).toBe(false);
  });
});
