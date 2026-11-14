import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';

import { Filesystem } from '#scripts/incident_workflow_pkg/infrastructure/filesystem.ts';

const roots: string[] = [];
const STATE = '---\nPhase: "synthesize"\n---\n';

function temporaryRoot(): string {
  const root = mkdtempSync(join(tmpdir(), 'incident-safety-test-'));
  roots.push(root);
  return root;
}

afterEach(() => {
  for (const root of roots.splice(0)) rmSync(root, { recursive: true, force: true });
});

describe('pre-close filesystem snapshot', () => {
  it('records a regular state.md and its content', () => {
    const ticket = join(temporaryRoot(), 'ticket');
    mkdirSync(join(ticket, 'analysis'), { recursive: true });
    writeFileSync(join(ticket, 'analysis', 'state.md'), STATE);

    const snapshot = new Filesystem().loadCloseOutSnapshot(ticket);

    expect(snapshot.workingAnalysisFiles).toContain('state.md');
    expect(snapshot.analysisContents['state.md']).toBe(STATE);
  });

  it('does not count a directory as a working analysis file', () => {
    const ticket = join(temporaryRoot(), 'ticket');
    mkdirSync(join(ticket, 'analysis', 'state.md'), { recursive: true });

    const snapshot = new Filesystem().loadCloseOutSnapshot(ticket);

    expect(snapshot.workingAnalysisFiles).not.toContain('state.md');
    expect(snapshot.analysisContents).not.toHaveProperty('state.md');
  });

  it('keeps well-formed ticket records and ignores siblings', () => {
    const ticket = join(temporaryRoot(), 'ticket');
    mkdirSync(ticket, { recursive: true });
    writeFileSync(join(ticket, 'ticket_999999.md'), '---\nsymptom_ids: []\n---\n');
    writeFileSync(join(ticket, 'notes.md'), 'not a ticket');

    const snapshot = new Filesystem().loadCloseOutSnapshot(ticket);

    expect(snapshot.ticketFileNames).toEqual(['ticket_999999.md']);
  });

  it('tolerates an absent ticket directory', () => {
    const ticket = join(temporaryRoot(), 'missing');

    const snapshot = new Filesystem().loadCloseOutSnapshot(ticket);

    expect(snapshot.ticketFileNames).toEqual([]);
    expect(snapshot.workingAnalysisFiles).toEqual([]);
  });
});
