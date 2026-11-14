import { describe, expect, it } from 'vitest';

import { ValidateScaffold } from '#scripts/incident_workflow_pkg/application/validate_scaffold.ts';
import { makeHeader, makeStepContent, makeStepContents } from '#tests/support/incident-validator-fixtures.ts';

const ANALYSIS = '/fixture/analysis';
const CLOCK = () => new Date(2026, 0, 1, 0, 0, 0, 0);

function scaffold(header = makeHeader(), files = makeStepContents()) {
  return new ValidateScaffold(CLOCK).execute(header, files, ANALYSIS);
}

describe('scaffold structure checks', () => {
  it('accepts a complete scaffold', () => {
    expect(scaffold().violations).toEqual([]);
  });

  it('allows unfilled tokens because a scaffold is structural only', () => {
    const files = makeStepContents({ '01-identify.md': makeStepContent().replace('step', '<fill>') });
    expect(scaffold(makeHeader(), files).violations).toEqual([]);
  });

  it('reports a missing step file', () => {
    const files = makeStepContents();
    delete files['02-investigate.md'];
    expect(scaffold(makeHeader(), files).violations)
      .toContain(`MISSING-STEP: 02-investigate.md not found in ${ANALYSIS}`);
  });

  it('reports a missing required section', () => {
    const files = makeStepContents({ '01-identify.md': '## Steps\n\nstep\n' });
    const violations = scaffold(makeHeader(), files).violations;
    expect(violations).toEqual(expect.arrayContaining([
      'MISSING-SECTION: 01-identify.md is missing ## Output',
      'MISSING-SECTION: 01-identify.md is missing ## Gate',
      'MISSING-SECTION: 01-identify.md is missing ## Abort conditions',
      'MISSING-SECTION: 01-identify.md is missing **Owner:**',
    ]));
  });

  it('reports a Phase outside the allowed set', () => {
    expect(scaffold(makeHeader({ Phase: 'bogus' })).violations)
      .toContain("PHASE-ERROR: Phase value 'bogus' not in allowed set (identify, investigate, synthesize)");
  });

  it('reports a verdict outside the allowed set', () => {
    expect(scaffold(makeHeader({ Identification_verdict: 'maybe' })).violations)
      .toContain("VERDICT-1: identification_verdict value 'maybe' not in allowed set (exact, no_match, pending, structural)");
  });

  it('reports a query budget overrun', () => {
    expect(scaffold(makeHeader({ Query_budget: '7/6' })).violations)
      .toContain('KILL-2: query budget exhausted (7 > 6)');
  });

  it('does not trip the switch when the budget is exactly consumed', () => {
    expect(scaffold(makeHeader({ Query_budget: '6/6' })).violations).toEqual([]);
  });

  it('reports a fraction it cannot parse', () => {
    expect(scaffold(makeHeader({ Hypotheses_outstanding: 'many' })).violations)
      .toContain("KILL-1: cannot parse Hypotheses-outstanding — Expected N/M fraction, got: 'many'");
  });

  it('reports a hypothesis cap exceeded', () => {
    expect(scaffold(makeHeader({ Hypotheses_outstanding: '4/3' })).violations)
      .toContain('KILL-1: hypothesis cap exceeded (4 > 3)');
  });

  it('reports a same-query re-run cap exceeded', () => {
    expect(scaffold(makeHeader({ Same_query_reruns: '3/2' })).violations)
      .toContain('KILL-3: re-run cap exceeded (3 > 2)');
  });

  it('reports a query budget it cannot parse', () => {
    expect(scaffold(makeHeader({ Query_budget: 'unknown' })).violations)
      .toContain("KILL-2: cannot parse Query-budget — Expected N/M fraction, got: 'unknown'");
  });
});
