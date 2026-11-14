import { describe, expect, it } from 'vitest';

import { ValidateAnalysis } from '#scripts/incident_workflow_pkg/application/validate_analysis.ts';
import { makeHeader, makeStepContents } from '#tests/support/incident-validator-fixtures.ts';

const ANALYSIS = '/fixture/analysis';

function warningsFor(slaDue: string, updated: string, now: Date): string[] {
  const runner = new ValidateAnalysis(() => now);
  return runner.execute(makeHeader({ SLA_due: slaDue, Updated: updated }), makeStepContents(), ANALYSIS).warnings;
}

describe('SLA clock window', () => {
  // The window spans the autumnal transition. Elapsed time across it is 25 hours
  // in an offset-aware reading but 24 hours of wall clock, which is the window the
  // reference arithmetic measures. A 5-of-24-hour remainder is 21% of the window;
  // measuring 25 hours instead would report 20%.
  it('measures the window by wall clock across a transition', () => {
    const warnings = warningsFor('2026-11-01T12:00', '2026-10-31T12:00', new Date(2026, 10, 1, 7, 0, 0, 0));
    expect(warnings).toContain('SLA-WARN: 5.0 hours remaining (21% of window left)');
  });

  it('stays silent while more than a quarter of the window remains', () => {
    const warnings = warningsFor('2026-11-01T12:00', '2026-10-31T12:00', new Date(2026, 10, 1, 1, 0, 0, 0));
    expect(warnings.filter(warning => warning.startsWith('SLA-WARN'))).toEqual([]);
  });

  it('skips unfilled placeholder values silently', () => {
    const warnings = warningsFor('YYYY-MM-DDTHH:MM', '2026-10-31T12:00', new Date(2026, 10, 1, 7, 0, 0, 0));
    expect(warnings.filter(warning => warning.startsWith('SLA-WARN'))).toEqual([]);
  });

  it('keeps warnings out of the violation set', () => {
    const runner = new ValidateAnalysis(() => new Date(2026, 10, 1, 7, 0, 0, 0));
    const result = runner.execute(makeHeader({ SLA_due: '2026-11-01T12:00', Updated: '2026-10-31T12:00' }), makeStepContents(), ANALYSIS);
    expect(result.violations).toEqual([]);
  });
});
