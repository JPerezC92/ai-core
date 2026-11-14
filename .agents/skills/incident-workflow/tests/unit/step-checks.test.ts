import { describe, expect, it } from 'vitest';

import { ValidateStep } from '#scripts/incident_workflow_pkg/application/validate_step.ts';
import { STEP_FILES } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import { makeHeader, makeStepContent } from '#tests/support/incident-validator-fixtures.ts';

const ANALYSIS = '/fixture/analysis';
const CLOCK = () => new Date(2026, 0, 1, 0, 0, 0, 0);

function check(step: string, content?: string) {
  const files: Record<string, string> = {};
  const filename = STEP_FILES[['identify', 'investigate', 'synthesize'].indexOf(step)];
  if (content !== undefined && filename !== undefined) files[filename] = content;
  return new ValidateStep(CLOCK).execute(makeHeader(), files, step, ANALYSIS);
}

describe('step validation', () => {
  it('accepts a completed step', () => {
    expect(check('identify', makeStepContent()).violations).toEqual([]);
  });

  it('reports a step that has not been written yet', () => {
    expect(check('identify').violations)
      .toContain(`STEP-NOT-WRITTEN: step identify (01-identify.md) not yet written in ${ANALYSIS}`);
  });

  it('reports an unfilled token', () => {
    const content = makeStepContent().replace('step', '<fill>');
    expect(check('identify', content).violations).toContain('UNFILLED-TOKEN: <fill> in 01-identify.md');
  });

  it('reports every unfilled token in order', () => {
    const content = makeStepContent().replace('step', '<title>').replace('output', '<what supports this>');
    expect(check('investigate', content).violations).toEqual([
      'UNFILLED-TOKEN: <title> in 02-investigate.md',
      'UNFILLED-TOKEN: <what supports this> in 02-investigate.md',
    ]);
  });

  it('reports a missing required section', () => {
    expect(check('synthesize', '## Steps\n\nstep\n').violations)
      .toContain('MISSING-SECTION: 03-synthesize.md is missing ## Output');
  });
});
