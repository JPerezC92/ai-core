import { describe, expect, it } from 'vitest';

import { ValidateAnalysis } from '#scripts/incident_workflow_pkg/application/validate_analysis.ts';
import { makeHeader, makeStepContents } from '#tests/support/incident-validator-fixtures.ts';

const ANALYSIS = '/fixture/analysis';
const CLOCK = () => new Date(2026, 0, 1, 0, 0, 0, 0);

describe('analysis step-set completeness', () => {
  it('warns about steps beyond the current phase without failing', () => {
    const files = makeStepContents();
    const written = { 'state.md': files['state.md']!, '01-identify.md': files['01-identify.md']! };

    const result = new ValidateAnalysis(CLOCK).execute(makeHeader({ Phase: 'identify' }), written, ANALYSIS);

    expect(result.warnings).toEqual([
      'INCOMPLETE-ANALYSIS: 02-investigate.md not yet written (current step rank: 01)',
      'INCOMPLETE-ANALYSIS: 03-synthesize.md not yet written (current step rank: 01)',
    ]);
    expect(result.violations).toEqual([]);
  });

  it('fails a completed phase whose steps are missing', () => {
    const files = makeStepContents();
    const written = { 'state.md': files['state.md']!, '01-identify.md': files['01-identify.md']! };

    const result = new ValidateAnalysis(CLOCK).execute(makeHeader({ Phase: 'synthesize' }), written, ANALYSIS);

    expect(result.violations).toEqual(expect.arrayContaining([
      `MISSING-STEP: 02-investigate.md not found in ${ANALYSIS}`,
      `MISSING-STEP: 03-synthesize.md not found in ${ANALYSIS}`,
    ]));
  });
});
