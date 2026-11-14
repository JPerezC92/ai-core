import { describe, expect, it } from 'vitest';

import { ValidateCloseOut } from '#scripts/incident_workflow_pkg/application/validate_close_out.ts';
import { makeClosedSnapshot, makeRegister, makeRegisterRow, makeTicketRecord } from '#tests/support/incident-validator-fixtures.ts';
import { parseProblemRegister } from '#scripts/incident_workflow_pkg/infrastructure/records.ts';

function violations(snapshot = makeClosedSnapshot()) {
  return new ValidateCloseOut().execute(snapshot, null, []).violations;
}

describe('close-out postconditions', () => {
  it('accepts a completed durable set', () => {
    expect(violations()).toEqual([]);
  });

  it('reports a missing ticket record', () => {
    expect(violations(makeClosedSnapshot({ ticketFileNames: [] }))).toContain('CLOSE-0: ticket_<id>.md not found');
  });

  it('reports more than one ticket record', () => {
    expect(violations(makeClosedSnapshot({ ticketFileNames: ['ticket_1.md', 'ticket_2.md'] })))
      .toContain('CLOSE-6: multiple ticket_<id>.md records found: ticket_1.md, ticket_2.md');
  });

  it('reports a working analysis file left in place', () => {
    expect(violations(makeClosedSnapshot({ workingAnalysisFiles: ['state.md'] })))
      .toContain('CLOSE-1: working analysis file remains after close: state.md');
  });

  it('reports a surviving response draft', () => {
    expect(violations(makeClosedSnapshot({ responseDraftPresent: true })))
      .toContain('CLOSE-2: response-draft.md remains after close');
  });

  it('reports the durable directories the collapse must keep', () => {
    expect(violations(makeClosedSnapshot({ screenshotsDirPresent: false, validationsDirPresent: false })))
      .toEqual(expect.arrayContaining([
        'CLOSE-3: screenshots/ missing from the durable set',
        'CLOSE-4: validations/ missing from the durable set',
      ]));
  });

  it('reports a cited image that does not exist', () => {
    expect(violations(makeClosedSnapshot({ missingImagePaths: ['screenshots/response-1/gone.png'] })))
      .toContain('CLOSE-5: cited image path is not an existing file inside the ticket folder: screenshots/response-1/gone.png');
  });

  it('reports a citation that is not a response screenshot', () => {
    expect(violations(makeClosedSnapshot({ citedPaths: ['downloads/x.png'] })))
      .toContain('CLOSE-8: cited path is not screenshots/response-<digits>/<filename>: downloads/x.png');
  });

  it('reports a leftover download', () => {
    expect(violations(makeClosedSnapshot({ leftoverDownloadFiles: ['downloads/report.csv'] })))
      .toContain('CLOSE-9: unused download file remains after close: downloads/report.csv');
  });

  it('reports an unparseable durable ticket record', () => {
    const result = new ValidateCloseOut().execute(makeClosedSnapshot(), { error: 'bad ticket' }, []);
    expect(result.violations).toContain('CLOSE-7: ticket record cannot be parsed: bad ticket');
  });

  it('checks the durable verdict against the register', () => {
    const register = parseProblemRegister(makeRegister(makeRegisterRow()));
    const result = new ValidateCloseOut().execute(
      makeClosedSnapshot(),
      { value: makeTicketRecord({ known_problem_ids: ['P-999'], identification_verdict: 'structural' }) },
      register,
    );
    expect(result.violations).toContain('VERDICT-4: cited P-999 is not an incident P-NNN row');
  });
});
