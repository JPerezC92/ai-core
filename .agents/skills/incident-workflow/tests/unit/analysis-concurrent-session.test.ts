import { describe, expect, it } from 'vitest';

import { ValidateAnalysis } from '#scripts/incident_workflow_pkg/application/validate_analysis.ts';
import { makeHeader, makeStepContents } from '#tests/support/incident-validator-fixtures.ts';

const ANALYSIS = '/fixture/analysis';

function warningsAt(updated: string, now: Date): string[] {
  const runner = new ValidateAnalysis(() => now);
  return runner.execute(makeHeader({ Updated: updated }), makeStepContents(), ANALYSIS).warnings;
}

describe('concurrent-session clock', () => {
  it('warns when the header was updated two minutes ago', () => {
    expect(warningsAt('2026-10-31T12:00', new Date(2026, 9, 31, 12, 2, 0, 0)))
      .toContain('CONCURRENT: another session updated 2 minutes ago (Updated: 2026-10-31T12:00)');
  });

  it('stays silent once ten minutes have passed', () => {
    expect(warningsAt('2026-10-31T12:00', new Date(2026, 9, 31, 12, 10, 0, 0))
      .filter(warning => warning.startsWith('CONCURRENT'))).toEqual([]);
  });

  it('skips an unfilled placeholder silently', () => {
    expect(warningsAt('YYYY-MM-DDTHH:MM', new Date(2026, 9, 31, 12, 2, 0, 0))
      .filter(warning => warning.startsWith('CONCURRENT'))).toEqual([]);
  });
});
