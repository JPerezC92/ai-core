import { describe, expect, it } from 'vitest';

import { ValidatePreClose } from '#scripts/incident_workflow_pkg/application/validate_pre_close.ts';
import { parseProblemRegister } from '#scripts/incident_workflow_pkg/infrastructure/records.ts';
import { makeHeader, makeRegister, makeRegisterRow, makeSnapshot, makeTicketRecord } from '#tests/support/incident-validator-fixtures.ts';

function preClose(verdict: string, citedProblemIds: string[], register = '') {
  const ticket = { value: makeTicketRecord({ known_problem_ids: citedProblemIds, identification_verdict: verdict }) };
  return new ValidatePreClose().execute(
    makeSnapshot(), ticket, { value: makeHeader() }, parseProblemRegister(register),
  ).violations;
}

const INCIDENT_ACTIVE = makeRegister(makeRegisterRow());

describe('pre-close identification verdicts', () => {
  it('accepts a pending verdict', () => {
    expect(preClose('pending', [], '')).toEqual([]);
  });

  it('accepts no_match against an empty register', () => {
    expect(preClose('no_match', [], '')).toEqual([]);
  });

  it('rejects no_match that cites a problem', () => {
    expect(preClose('no_match', ['P-001'], INCIDENT_ACTIVE))
      .toEqual(["VERDICT-2: no_match must not cite a P-NNN (cited: ['P-001'])"]);
  });

  it('rejects exact or structural without a citation', () => {
    expect(preClose('exact', [], INCIDENT_ACTIVE)).toEqual(['VERDICT-3: exact requires a cited incident P-NNN']);
    expect(preClose('structural', [], INCIDENT_ACTIVE)).toEqual(['VERDICT-3: structural requires a cited incident P-NNN']);
  });

  it('rejects a cited id absent from the register', () => {
    expect(preClose('structural', ['P-999'], INCIDENT_ACTIVE))
      .toEqual(['VERDICT-4: cited P-999 is not an incident P-NNN row']);
  });

  it('rejects exact citing more than one problem', () => {
    const register = makeRegister(makeRegisterRow(), makeRegisterRow({ id: 'P-002' }));
    expect(preClose('exact', ['P-001', 'P-002'], register))
      .toContain("VERDICT-5: exact requires exactly one cited P-NNN (cited: ['P-001', 'P-002'])");
  });

  it('rejects exact citing a candidate row', () => {
    const register = makeRegister(makeRegisterRow({ lifecycle: 'candidate' }));
    expect(preClose('exact', ['P-001'], register))
      .toContain('VERDICT-6: exact requires an active P-NNN (P-001 is candidate)');
  });

  it('rejects exact citing a row without allow_exact', () => {
    const register = makeRegister(makeRegisterRow({ allowExact: 'no' }));
    expect(preClose('exact', ['P-001'], register))
      .toContain('VERDICT-7: exact requires allow_exact=yes (P-001 is no)');
  });

  it('rejects structural citing a resolved row', () => {
    const register = makeRegister(makeRegisterRow({ lifecycle: 'resolved' }));
    expect(preClose('structural', ['P-001'], register))
      .toContain('VERDICT-8: structural requires candidate|active|mitigated (P-001 is resolved)');
  });

  it('rejects structural citing more than one problem', () => {
    const register = makeRegister(makeRegisterRow(), makeRegisterRow({ id: 'P-002' }));
    expect(preClose('structural', ['P-001', 'P-002'], register))
      .toContain("VERDICT-9: structural requires exactly one cited P-NNN (cited: ['P-001', 'P-002'])");
  });

  it('accepts a well-formed exact verdict', () => {
    expect(preClose('exact', ['P-001'], INCIDENT_ACTIVE)).toEqual([]);
  });
});
