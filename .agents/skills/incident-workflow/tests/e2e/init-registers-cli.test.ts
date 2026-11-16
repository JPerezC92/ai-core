import { execFile } from 'node:child_process';
import { mkdtempSync, existsSync, readFileSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

import { afterAll, describe, expect, it } from 'vitest';

const run = promisify(execFile);
const SCRIPT = fileURLToPath(
  new URL('../../scripts/init_local_registers.ts', import.meta.url),
);
const roots: string[] = [];

function makeRoot(): string {
  const root = mkdtempSync(join(tmpdir(), 'aicore-init-registers-'));
  roots.push(root);
  return root;
}

afterAll(() => {
  for (const root of roots) rmSync(root, { recursive: true, force: true });
});

async function invoke(root: string): Promise<{ status: number; stdout: string }> {
  try {
    const result = await run(process.execPath, [SCRIPT, root], { windowsHide: true });
    return { status: 0, stdout: result.stdout };
  } catch (error) {
    const failure = error as { code?: number; stdout?: string };
    return { status: typeof failure.code === 'number' ? failure.code : 1, stdout: failure.stdout ?? '' };
  }
}

describe('init_local_registers entry point', () => {
  it('creates both registers in an empty project root', async () => {
    const root = makeRoot();
    const outcome = await invoke(root);

    expect(outcome.status).toBe(0);
    expect(outcome.stdout).toContain('created incidents/diagnostics/symptoms.md');
    expect(outcome.stdout).toContain('created incidents/diagnostics/problems.md');
    expect(existsSync(join(root, 'incidents', 'diagnostics', 'symptoms.md'))).toBe(true);
    expect(existsSync(join(root, 'incidents', 'diagnostics', 'problems.md'))).toBe(true);
  });

  it('keeps existing registers byte-identical on a second run', async () => {
    const root = makeRoot();
    expect((await invoke(root)).status).toBe(0);

    const symptomsPath = join(root, 'incidents', 'diagnostics', 'symptoms.md');
    const authored = '| ID | Symptom |\n|---|---|\n| LOCAL:S-01 | mine |\n';
    writeFileSync(symptomsPath, authored, 'utf8');

    const second = await invoke(root);
    expect(second.status).toBe(0);
    expect(second.stdout).toContain('kept incidents/diagnostics/symptoms.md');
    expect(readFileSync(symptomsPath, 'utf8')).toBe(authored);
  });

  it('reports a malformed existing register without repairing it', async () => {
    const root = makeRoot();
    mkdirSync(join(root, 'incidents', 'diagnostics'), { recursive: true });
    const symptomsPath = join(root, 'incidents', 'diagnostics', 'symptoms.md');
    const malformed = '| ID | Symptom |\n|---|---|\n| LOCAL:S-01 | a |\n| LOCAL:S-01 | b |\n';
    writeFileSync(symptomsPath, malformed, 'utf8');

    const outcome = await invoke(root);

    expect(outcome.status).toBe(1);
    expect(readFileSync(symptomsPath, 'utf8')).toBe(malformed);
  });
});
