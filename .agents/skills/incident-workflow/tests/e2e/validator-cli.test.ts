import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, describe, expect, it } from 'vitest';

import { createIncidentFixture as createFixture, writeFreshState } from '#tests/support/incident-validator-fixtures.ts';

const entry = resolve(dirname(fileURLToPath(import.meta.url)), '../../scripts/validate_incident_workflow.ts');
const temporaryDirectories: string[] = [];

function createIncidentFixture(citation?: string) {
  const root = mkdtempSync(join(tmpdir(), 'incident-validator-test-'));
  temporaryDirectories.push(root);
  return createFixture(root, citation);
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

function runValidator(args: string[]) {
  const result = spawnSync(process.execPath, [entry, ...args], { encoding: 'utf8' });
  if (result.error) throw result.error;
  return result;
}

describe('incident validator CLI modes', () => {
  it('validates a completed analysis by default', () => {
    const fixture = createIncidentFixture();
    const result = runValidator([fixture.analysis]);
    expect(result.status).toBe(0);
    expect(result.stdout).toContain(`Analysis: ${fixture.analysis}  Phase: synthesize`);
    expect(result.stderr).toBe('');
  });

  it('validates a complete scaffold', () => {
    const fixture = createIncidentFixture();
    const result = runValidator([fixture.analysis, '--scaffold']);
    expect(result.status).toBe(0);
    expect(result.stdout).toBe(`ok  scaffold: ${fixture.analysis}\n`);
    expect(result.stderr).toBe('');
  });

  it('validates one named step', () => {
    const fixture = createIncidentFixture();
    const result = runValidator([fixture.analysis, '--step', 'identify']);
    expect(result.status).toBe(0);
    expect(result.stdout).toBe(`ok  step identify (01-identify.md)  [analysis: ${fixture.analysis}]\n`);
    expect(result.stderr).toBe('');
  });

  it('validates the complete pre-close set', () => {
    const fixture = createIncidentFixture();
    const result = runValidator([fixture.ticket, '--pre-close', '--repo-root', fixture.root]);
    expect(result.status).toBe(0);
    expect(result.stdout).toBe(`ok  pre-close: ${fixture.ticket}  (ticket_999999.md)\n`);
    expect(result.stderr).toBe('');
  });

  it('rejects an escaping path before close', () => {
    const fixture = createIncidentFixture('../outside.png');
    const result = runValidator([fixture.ticket, '--pre-close', '--repo-root', fixture.root]);
    expect(result.status).toBe(1);
    expect(result.stdout).toBe('');
    expect(result.stderr).toContain('PRE-CLOSE-6: cited path escapes the ticket root: ../outside.png');
  });

  it('rejects a close-out while working files remain', () => {
    const fixture = createIncidentFixture();
    const result = runValidator([fixture.ticket, '--close-out', '--repo-root', fixture.root]);
    expect(result.status).toBe(1);
    expect(result.stdout).toBe('');
    expect(result.stderr).toContain('CLOSE-1: working analysis file remains after close:');
    expect(result.stderr).toContain('CLOSE-2: response-draft.md remains after close');
  });

  it('skips a close-out that has no ticket record with exit status 2', () => {
    const empty = mkdtempSync(join(tmpdir(), 'incident-validator-test-'));
    temporaryDirectories.push(empty);
    const result = runValidator([empty, '--close-out']);
    expect(result.status).toBe(2);
    expect(result.stdout).toBe('');
    expect(result.stderr).toBe(`CLOSE-SKIPPED: ticket_<id>.md not found at ${empty}\n`);
  });

  it('rejects a command line without an analysis directory with exit status 2', () => {
    const result = runValidator([]);
    expect(result.status).toBe(2);
    expect(result.stdout).toBe('');
    expect(result.stderr).toContain('error: the following arguments are required: analysis_dir');
  });

  it('rejects an invalid --step choice with exit status 2', () => {
    const result = runValidator(['/fixture', '--step', 'guess']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain("argument --step: invalid choice: 'guess' (choose from 'identify', 'investigate', 'synthesize')");
  });

  it('prints usage for --help with exit status 0', () => {
    const result = runValidator(['--help']);
    expect(result.status).toBe(0);
    expect(result.stdout).toContain('usage: validate_incident_workflow.ts');
    expect(result.stdout).toContain('Exit code 0 = pass, 1 = fail, 2 = close-out skipped.');
    expect(result.stderr).toBe('');
  });

  it('reports warnings on stderr without changing the exit status', () => {
    const fixture = createIncidentFixture();
    writeFreshState(fixture.analysis, 2);

    const result = runValidator([fixture.analysis, '--scaffold']);

    expect(result.status).toBe(0);
    expect(result.stderr).toContain('WARN: CONCURRENT: another session updated 2 minutes ago');
  });

  it('rejects conflicting modes with exit status 2', () => {
    const result = runValidator(['/fixture', '--scaffold', '--pre-close']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain('argument --pre-close: not allowed with argument --scaffold');
  });

  it('rejects an unrecognised argument with exit status 2', () => {
    const result = runValidator(['/fixture', '--unknown']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain('unrecognized arguments: --unknown');
  });

  it('rejects an ambiguous option abbreviation with exit status 2', () => {
    const result = runValidator(['/fixture', '--s']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain('ambiguous option: --s');
  });

  it('accepts -h as help with exit status 0', () => {
    const result = runValidator(['-h']);
    expect(result.status).toBe(0);
    expect(result.stdout).toContain('usage: validate_incident_workflow.ts');
  });

  it('accepts the analysis directory after an end-of-options separator', () => {
    const fixture = createIncidentFixture();
    const result = runValidator(['--', fixture.analysis]);
    expect(result.status).toBe(0);
    expect(result.stdout).toContain(`Analysis: ${fixture.analysis}  Phase: synthesize`);
  });

  it('rejects an inline argument on a flag with exit status 2', () => {
    const result = runValidator(['/fixture', '--scaffold=x']);
    expect(result.status).toBe(2);
    expect(result.stderr).toContain("argument --scaffold: ignored explicit argument 'x'");
  });

  it('reports an unreadable state header', () => {
    const root = mkdtempSync(join(tmpdir(), 'incident-validator-test-'));
    temporaryDirectories.push(root);
    const analysis = join(root, 'analysis');
    mkdirSync(analysis, { recursive: true });

    const result = runValidator([analysis]);

    expect(result.status).toBe(1);
    expect(result.stderr).toMatch(/^HEADER-ERROR: /);
  });
});
