import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const entry = resolve(dirname(fileURLToPath(import.meta.url)), '../../scripts/models.ts');

function run(args: string[], env?: NodeJS.ProcessEnv) {
  const result = spawnSync(process.execPath, [entry, ...args], { encoding: 'utf8', env });
  if (result.error) throw result.error;
  return result;
}

describe('models CLI boundary', () => {
  it('reports a missing opencode executable without a fallback listing', () => {
    const result = run([], { ...process.env, PATH: '', Path: '' });

    expect(result.status).toBe(1);
    expect(result.stdout).toBe('');
    expect(result.stderr).toBe('ERROR: `opencode` not found on PATH. Cannot list models.\n');
  });
});

describe('models CLI against the live source', () => {
  const probe = spawnSync('opencode', ['--version'], { encoding: 'utf8' });
  const available = probe.error === undefined && probe.status === 0;

  it('lists grouped models when no query is supplied', () => {
    if (!available) return;
    const result = run([]);
    expect(result.status).toBe(0);
    if (result.stdout !== '') expect(result.stdout).toContain('## ');
  });

  it('reports an unmatched query with the documented message and exit status', () => {
    if (!available) return;
    const result = run(['zzzz-no-such-model-zzzz']);
    expect(result.status).toBe(1);
    expect(result.stderr).toContain('No match for zzzz-no-such-model-zzzz in `opencode models`.');
  });

  it('emits JSON lines for a matching query when the source has models', () => {
    if (!available) return;
    const listed = run([]);
    if (listed.stdout.trim() === '') return;
    const selector = /^ {2}([a-z0-9]+\/\S+)$/m.exec(listed.stdout)?.[1];
    if (selector === undefined) return;
    const result = run([selector]);
    expect(result.status).toBe(0);
    expect(result.stdout).toContain('"config": ');
    expect(result.stdout).toContain('"cost_in": ');
  });
});
