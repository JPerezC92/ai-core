import { describe, expect, it } from 'vitest';

import { ValidatePreClose } from '#scripts/incident_workflow_pkg/application/validate_pre_close.ts';
import { makeHeader, makeSnapshot } from '#tests/support/incident-validator-fixtures.ts';

describe('pre-close required analysis files', () => {
  it('accepts a complete analysis working set', () => {
    const result = new ValidatePreClose().execute(makeSnapshot(), null, null, []);
    expect(result.violations).toEqual([]);
  });

  it('rejects a required name that was not loaded as a regular file', () => {
    const snapshot = makeSnapshot();
    const { 'state.md': _omitted, ...loaded } = snapshot.analysisContents;
    const result = new ValidatePreClose().execute({ ...snapshot, analysisContents: loaded }, null, null, []);
    expect(result.violations).toContain('PRE-CLOSE-2: required analysis file missing: state.md');
  });

  it('rejects an unexpected analysis file', () => {
    const snapshot = makeSnapshot({ workingAnalysisFiles: [...makeSnapshot().workingAnalysisFiles, 'notes.md'] });
    const result = new ValidatePreClose().execute(snapshot, null, null, []);
    expect(result.violations).toContain('PRE-CLOSE-2: unexpected analysis file present: notes.md');
  });

  it('reports more than one ticket record before collapse', () => {
    const result = new ValidatePreClose().execute(
      makeSnapshot({ ticketFileNames: ['ticket_1.md', 'ticket_2.md'] }), null, null, [],
    );
    expect(result.violations).toContain('PRE-CLOSE-1: multiple ticket_<id>.md records found: ticket_1.md, ticket_2.md');
  });

  it('reports a missing ticket record and missing durable companions together', () => {    const result = new ValidatePreClose().execute(
      makeSnapshot({ ticketFileNames: [], responseDraftPresent: false, screenshotsDirPresent: false, validationsDirPresent: false }),
      null, null, [],
    );
    expect(result.violations).toEqual(expect.arrayContaining([
      'PRE-CLOSE-0: ticket_<id>.md not found',
      'PRE-CLOSE-3: response-draft.md not found',
      'PRE-CLOSE-4: screenshots/ not found',
      'PRE-CLOSE-5: validations/ not found',
    ]));
  });

  it('reports a Phase that is not synthesize', () => {
    const result = new ValidatePreClose().execute(makeSnapshot(), null, { value: makeHeader({ Phase: 'identify' }) }, []);
    expect(result.violations).toContain("PRE-CLOSE-10: state.md Phase must be 'synthesize'");
  });

  it('reports an unparseable ticket and header separately', () => {
    const result = new ValidatePreClose().execute(makeSnapshot(), { error: 'bad ticket' }, { error: 'bad header' }, []);
    expect(result.violations).toEqual(expect.arrayContaining([
      'PRE-CLOSE-8: ticket record cannot be parsed: bad ticket',
      'PRE-CLOSE-9: state.md cannot be parsed: bad header',
    ]));
  });

  it('reports escaping and missing citations', () => {
    const result = new ValidatePreClose().execute(
      makeSnapshot({ unsafeTicketPaths: ['../outside.png'], missingTicketPaths: ['screenshots/response-1/gone.png'] }),
      null, null, [],
    );
    expect(result.violations).toEqual(expect.arrayContaining([
      'PRE-CLOSE-6: cited path escapes the ticket root: ../outside.png',
      'PRE-CLOSE-7: cited path is not an existing file: screenshots/response-1/gone.png',
    ]));
  });

  it('reports a citation that is not a response screenshot', () => {
    const result = new ValidatePreClose().execute(makeSnapshot({ citedPaths: ['downloads/x.png'] }), null, null, []);
    expect(result.violations).toContain('PRE-CLOSE-11: cited path is not screenshots/response-<digits>/<filename>: downloads/x.png');
  });
});
