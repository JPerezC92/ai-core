import { join } from 'node:path';

import { ValidateAnalysis } from '#scripts/incident_workflow_pkg/application/validate_analysis.ts';
import { ValidateScaffold } from '#scripts/incident_workflow_pkg/application/validate_scaffold.ts';
import { ValidateStep } from '#scripts/incident_workflow_pkg/application/validate_step.ts';
import { ValidatePreClose } from '#scripts/incident_workflow_pkg/application/validate_pre_close.ts';
import { ValidateCloseOut } from '#scripts/incident_workflow_pkg/application/validate_close_out.ts';
import { InputError } from '#scripts/incident_workflow_pkg/domain/errors.ts';
import { REQUIRED_ANALYSIS_FILES, STEP_FILES, STEP_NAMES } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import type { ParsedRecord } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import type { ValidatorArguments } from '#scripts/incident_workflow_pkg/infrastructure/arguments.ts';
import { Filesystem } from '#scripts/incident_workflow_pkg/infrastructure/filesystem.ts';
import { parseProblemRegister, parseStateHeader, parseTicketRecord } from '#scripts/incident_workflow_pkg/infrastructure/records.ts';

/** An operating-system failure raised at the filesystem boundary. */
function isFilesystemError(error: unknown): error is Error & { code: unknown } {
  return error instanceof Error && 'code' in error && 'syscall' in error;
}

/** A reported rejection: rejected input or an operating-system failure. */
function isReportableError(error: unknown): error is Error {
  return error instanceof InputError || isFilesystemError(error);
}

function parseRecord<T>(parse: () => T): ParsedRecord<T> {
  try { return { value: parse() }; }
  catch (error) { if (error instanceof InputError) return { error: error.message }; throw error; }
}

export function runValidator(args: ValidatorArguments, clock: () => Date = () => new Date()): number {
  const files = new Filesystem();
  const writeFindings = (findings: { violations: string[]; warnings: string[] }): boolean => {
    for (const warning of findings.warnings) console.error(`WARN: ${warning}`);
    for (const violation of findings.violations) console.error(violation);
    return findings.violations.length === 0;
  };
  const registerPath = join(args.repoRoot, '.aicore', 'core', 'knowledge', 'diagnostics', 'problems.md');
  const loadRegister = () => files.isFile(registerPath) ? parseProblemRegister(files.readText(registerPath)) : [];

  if (args.mode.kind === 'pre-close' || args.mode.kind === 'close-out') {
    let snapshot;
    let preCloseRegister;
    try {
      snapshot = files.loadCloseOutSnapshot(args.analysisDir);
      if (args.mode.kind === 'pre-close') preCloseRegister = loadRegister();
    } catch (error) {
      if (args.mode.kind !== 'pre-close' || !isFilesystemError(error)) throw error;
      console.error(`PRE-CLOSE-IO: ${error.message}`);
      return 1;
    }
    if (args.mode.kind === 'close-out' && !snapshot.ticketFileNames.length) {
      console.error(`CLOSE-SKIPPED: ticket_<id>.md not found at ${args.analysisDir}`);
      return 2;
    }
    const ticket = snapshot.ticketContent !== null && snapshot.ticketFileNames.length === 1
      ? parseRecord(() => parseTicketRecord(snapshot.ticketContent!, snapshot.ticketFileNames[0]!)) : null;
    const stateContent = snapshot.analysisContents['state.md'];
    const header = stateContent === undefined ? null : parseRecord(() => parseStateHeader(stateContent, 'state.md'));
    const register = args.mode.kind === 'pre-close' ? preCloseRegister! : ticket !== null && 'value' in ticket ? loadRegister() : [];
    const findings = args.mode.kind === 'pre-close'
      ? new ValidatePreClose().execute(snapshot, ticket, header, register)
      : new ValidateCloseOut().execute(snapshot, ticket, register);
    if (!writeFindings(findings)) return 1;
    console.log(`ok  ${args.mode.kind}: ${args.analysisDir}  (${snapshot.ticketFileNames[0]})`);
    return 0;
  }

  let header;
  try { header = parseStateHeader(files.readText(join(args.analysisDir, 'state.md')), join(args.analysisDir, 'state.md')); }
  catch (error) {
    if (!isReportableError(error)) throw error;
    console.error(`HEADER-ERROR: ${error.message}`);
    return 1;
  }
  const contents = files.loadStepFiles(args.analysisDir);
  if (args.mode.kind === 'scaffold') {
    if (!writeFindings(new ValidateScaffold(clock).execute(header, contents, args.analysisDir))) return 1;
    console.log(`ok  scaffold: ${args.analysisDir}`);
    return 0;
  }
  if (args.mode.kind === 'step') {
    if (!writeFindings(new ValidateStep(clock).execute(header, contents, args.mode.step, args.analysisDir))) return 1;
    const filename = STEP_FILES[STEP_NAMES.indexOf(args.mode.step)];
    console.log(`ok  step ${args.mode.step} (${filename})  [analysis: ${args.analysisDir}]`);
    return 0;
  }
  if (!writeFindings(new ValidateAnalysis(clock).execute(header, contents, args.analysisDir))) return 1;
  console.log(`\nAnalysis: ${args.analysisDir}  Phase: ${header.Phase}\n`);
  console.log(`${'Analysis file'.padEnd(35)} Status`);
  console.log('-'.repeat(45));
  for (const name of REQUIRED_ANALYSIS_FILES) {
    console.log(`  ${name.padEnd(33)} ${files.isFile(join(args.analysisDir, name)) ? 'ok' : 'absent (not yet written)'}`);
  }
  console.log();
  return 0;
}
