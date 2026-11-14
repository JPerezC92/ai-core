import { describe, expect, it } from 'vitest';

import { parseProblemRegister } from '#scripts/incident_workflow_pkg/infrastructure/records.ts';
import { makeRegister, makeRegisterRow } from '#tests/support/incident-validator-fixtures.ts';

describe('problem register loader', () => {
  it('loads a well-formed incident row', () => {
    const rows = parseProblemRegister(makeRegister(makeRegisterRow()));
    expect(rows).toHaveLength(1);
    expect(rows[0]?.id).toBe('P-001');
    expect(rows[0]?.isIncident).toBe(true);
    expect(rows[0]?.lifecycle).toBe('active');
    expect(rows[0]?.isExactMatchEligible).toBe(true);
  });

  it('returns nothing for a register with no data rows', () => {
    expect(parseProblemRegister('## Register\n\n| ID | Date |\n|---|---|\n')).toEqual([]);
  });

  it('skips a row whose column count is wrong', () => {
    expect(parseProblemRegister(makeRegister('| P-002 | 2026-01-01 | incident |'))).toEqual([]);
  });

  it('skips a row whose lifecycle is not an allowed value', () => {
    expect(parseProblemRegister(makeRegister(makeRegisterRow({ lifecycle: 'bogus' })))).toEqual([]);
  });

  it('skips a row whose symptom references no class', () => {
    expect(parseProblemRegister(makeRegister(makeRegisterRow({ symptom: 'unclassified' })))).toEqual([]);
  });

  it('keeps well-formed rows and skips malformed siblings', () => {
    const rows = parseProblemRegister(makeRegister(
      makeRegisterRow({ id: 'P-001' }),
      makeRegisterRow({ id: 'P-002', team: 'bogus' }),
      makeRegisterRow({ id: 'P-003' }),
    ));
    expect(rows.map(row => row.id)).toEqual(['P-001', 'P-003']);
  });
});
