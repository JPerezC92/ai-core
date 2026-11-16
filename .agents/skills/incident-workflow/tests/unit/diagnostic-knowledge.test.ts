import { describe, expect, it } from 'vitest';

import { ValidateDiagnosticKnowledge } from '#scripts/incident_workflow_pkg/application/validate_diagnostic_knowledge.ts';
import { makeRegister, makeRegisterRow } from '#tests/support/incident-validator-fixtures.ts';

const baseline = [
  '| ID | Symptom |',
  '|---|---|',
  '| S-05 | Network |',
  '',
].join('\n');

const emptyLocalSymptoms = ['| ID | Symptom |', '|---|---|', ''].join('\n');

function check(overrides: Partial<Parameters<ValidateDiagnosticKnowledge['execute']>[0]> = {}) {
  return new ValidateDiagnosticKnowledge().execute({
    baselineSymptoms: baseline,
    localSymptoms: emptyLocalSymptoms,
    localProblems: makeRegister(),
    localSymptomsPath: 'incidents/diagnostics/symptoms.md',
    localProblemsPath: 'incidents/diagnostics/problems.md',
    ...overrides,
  }).violations;
}

describe('diagnostic knowledge', () => {
  it('accepts a valid empty local register', () => {
    expect(check()).toEqual([]);
  });

  it('accepts a local class and a problem citing it', () => {
    expect(check({
      localSymptoms: '| ID | Symptom |\n|---|---|\n| LOCAL:S-01 | local class |\n',
      localProblems: makeRegister(makeRegisterRow({ symptom: 'LOCAL:S-01' })),
    })).toEqual([]);
  });

  it('reports a missing local symptom register instead of treating it as empty', () => {
    expect(check({ localSymptoms: null })).toEqual([
      'KNOWLEDGE-1: local symptom register missing: incidents/diagnostics/symptoms.md',
    ]);
  });

  it('reports a missing local problem register instead of treating it as empty', () => {
    expect(check({ localProblems: null })).toEqual([
      'KNOWLEDGE-2: local problem register missing: incidents/diagnostics/problems.md',
    ]);
  });

  it('reports a class defined twice in the local register', () => {
    expect(check({ localSymptoms: '| ID | Symptom |\n|---|---|\n| LOCAL:S-01 | a |\n| LOCAL:S-01 | b |\n' })).toEqual([
      'KNOWLEDGE-3: local symptom register defines an id twice: LOCAL:S-01',
    ]);
  });

  it('reports a local class that reuses a baseline id', () => {
    expect(check({ localSymptoms: '| ID | Symptom |\n|---|---|\n| S-05 | shadowed |\n' })).toEqual([
      'KNOWLEDGE-4: id defined in both baseline and local registers: S-05',
    ]);
  });

  it('reports a problem citing an unknown class', () => {
    expect(check({ localProblems: makeRegister(makeRegisterRow({ symptom: 'S-99' })) })).toEqual([
      'KNOWLEDGE-6: P-001 references an unknown symptom: S-99',
    ]);
  });

  it('reports a symptom cell containing a non-identifier segment', () => {
    expect(check({ localProblems: makeRegister(makeRegisterRow({ symptom: 'S-05, unclassified' })) })).toEqual([
      'KNOWLEDGE-5: P-001 Symptom cell has an invalid token: unclassified',
    ]);
  });
});
