import type { Problem } from './problem.ts';
import type { CloseOutSnapshot } from './ports.ts';

export interface AnalysisHeader {
  readonly Phase: string;
  readonly SLA_due: string;
  readonly Updated: string;
  readonly Hypotheses_outstanding: string;
  readonly Query_budget: string;
  readonly Identification_verdict: string;
  readonly Same_query_reruns: string;
}

export interface TicketIdentification {
  readonly symptom_ids: string[];
  readonly known_problem_ids: string[];
  readonly identification_verdict: string;
}

export const STEP_FILES = ['01-identify.md', '02-investigate.md', '03-synthesize.md'] as const;
export const STEP_NAMES = ['identify', 'investigate', 'synthesize'] as const;
export const REQUIRED_ANALYSIS_FILES = ['state.md', ...STEP_FILES];

export function checkPhase(header: AnalysisHeader): string[] {
  const value = header.Phase.trim();
  return STEP_NAMES.some(name => name === value)
    ? []
    : [`PHASE-ERROR: Phase value '${value}' not in allowed set (identify, investigate, synthesize)`];
}

export function checkIdentificationVerdict(header: AnalysisHeader): string[] {
  const value = header.Identification_verdict.trim();
  return ['pending', 'exact', 'structural', 'no_match'].includes(value)
    ? []
    : [`VERDICT-1: identification_verdict value '${value}' not in allowed set (exact, no_match, pending, structural)`];
}

export function checkKillSwitches(header: AnalysisHeader): string[] {
  const violations: string[] = [];
  const checks = [
    { field: 'Hypotheses-outstanding', value: header.Hypotheses_outstanding, code: 'KILL-1', limit: 3, label: 'hypothesis cap exceeded' },
    { field: 'Query-budget', value: header.Query_budget, code: 'KILL-2', limit: null, label: 'query budget exhausted' },
    { field: 'Same-query-reruns', value: header.Same_query_reruns, code: 'KILL-3', limit: 2, label: 're-run cap exceeded' },
  ];
  for (const check of checks) {
    const match = /^(\d+)\/(\d+)$/.exec(check.value.trim());
    if (match === null) {
      violations.push(`${check.code}: cannot parse ${check.field} — Expected N/M fraction, got: '${check.value}'`);
      continue;
    }
    const numerator = BigInt(match[1]!);
    const denominator = check.limit === null ? BigInt(match[2]!) : BigInt(check.limit);
    if (numerator > denominator) violations.push(`${check.code}: ${check.label} (${numerator} > ${denominator})`);
  }
  return violations;
}

/** Wall-clock reading of a local instant, so differences stay offset-independent. */
function wallClock(date: Date): Date {
  return new Date(Date.UTC(
    date.getFullYear(), date.getMonth(), date.getDate(),
    date.getHours(), date.getMinutes(), date.getSeconds(), date.getMilliseconds(),
  ));
}

function parseLocalTimestamp(value: string): Date | undefined {
  const text = value.trim();
  if (text.includes('<') || text.includes('Y')) return undefined;
  const match = /^(\d{4})-(\d{1,2})-(\d{1,2})T(\d{1,2}):(\d{1,2})$/.exec(text);
  if (!match) return undefined;
  const [year, month, day, hour, minute] = match.slice(1).map(Number) as [number, number, number, number, number];
  const date = new Date(Date.UTC(year, month - 1, day, hour, minute, 0, 0));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day || date.getUTCHours() !== hour || date.getUTCMinutes() !== minute) return undefined;
  return date;
}

export function checkSlaClock(header: AnalysisHeader, now: Date): string | undefined {
  const due = parseLocalTimestamp(header.SLA_due);
  const updated = parseLocalTimestamp(header.Updated);
  if (due === undefined || updated === undefined) return undefined;
  const window = due.getTime() - updated.getTime();
  if (window <= 0) return undefined;
  const remaining = due.getTime() - wallClock(now).getTime();
  const proportion = remaining / window;
  if (proportion >= 0.25) return undefined;
  return `SLA-WARN: ${Math.max(remaining / 3_600_000, 0).toFixed(1)} hours remaining (${(proportion * 100).toFixed(0)}% of window left)`;
}

export function checkConcurrentSession(header: AnalysisHeader, now: Date): string | undefined {
  const updated = parseLocalTimestamp(header.Updated);
  if (updated === undefined) return undefined;
  const elapsed = wallClock(now).getTime() - updated.getTime();
  if (elapsed >= 600_000) return undefined;
  return `CONCURRENT: another session updated ${Math.floor(elapsed / 60_000)} minutes ago (Updated: ${header.Updated})`;
}

export function checkStepFilesExist(
  contents: Readonly<Record<string, string>>,
  analysisDir: string,
  currentRank?: number,
): { violations: string[]; warnings: string[] } {
  const violations: string[] = [];
  const warnings: string[] = [];
  const highest = STEP_FILES.reduce((rank, name, index) => Object.hasOwn(contents, name) ? index + 1 : rank, 0);
  for (const [index, name] of STEP_FILES.entries()) {
    if (Object.hasOwn(contents, name)) continue;
    const rank = index + 1;
    if (rank <= (currentRank ?? highest)) violations.push(`MISSING-STEP: ${name} not found in ${analysisDir}`);
    else {
      const detail = currentRank === undefined ? `highest written rank: ${String(highest).padStart(2, '0')}` : `current step rank: ${String(currentRank).padStart(2, '0')}`;
      warnings.push(`INCOMPLETE-ANALYSIS: ${name} not yet written (${detail})`);
    }
  }
  return { violations, warnings };
}

const persistentTokens = new Set(['<now>', '<calculated>', '<ID>', '<SYSTEM>', '<timestamp>', '<sidecar-parent-dir>', '<sidecar-path>', '<python>']);

export function checkStepSections(content: string, filename: string, includeFillTokens: boolean): Array<[string, string]> {
  const findings: Array<[string, string]> = [];
  const headings = new Set<string>();
  const labels = new Set<string>();
  for (const line of content.split(/\r\n|\n|\r/)) {
    const heading = /^##\s+(.+)$/.exec(line);
    if (heading?.[1] !== undefined) headings.add(heading[1].trim());
    const label = /^>\s+\*\*(\w[\w\s-]*):\*\*/.exec(line);
    if (label?.[1] !== undefined) labels.add(label[1].trim());
  }
  for (const heading of ['Steps', 'Output', 'Gate', 'Abort conditions']) {
    if (!headings.has(heading)) findings.push([filename, `## ${heading}`]);
  }
  for (const label of ['Owner', 'Pre', 'Reads', 'Writes']) {
    if (!labels.has(label)) findings.push([filename, `**${label}:**`]);
  }
  if (includeFillTokens) {
    const withoutComments = content.replace(/<!--[\s\S]*?-->/g, '');
    for (const token of withoutComments.match(/<[^>]+>/g) ?? []) {
      if (!persistentTokens.has(token)) findings.push([filename, `UNFILLED-TOKEN: ${token}`]);
    }
  }
  return findings;
}

export type ParsedRecord<T> = { readonly value: T } | { readonly error: string };

function checkCitationShapes(paths: readonly string[], prefix: 'PRE-CLOSE-11' | 'CLOSE-8'): string[] {
  return paths.filter(path => !/^screenshots\/response-\d+\/[^/]+$/.test(path))
    .map(path => `${prefix}: cited path is not screenshots/response-<digits>/<filename>: ${path}`);
}

export function evaluatePreClose(
  snapshot: CloseOutSnapshot,
  ticket: ParsedRecord<TicketIdentification> | null,
  header: ParsedRecord<AnalysisHeader> | null,
  registerRows: readonly Problem[],
): string[] {
  const violations: string[] = [];
  if (!snapshot.ticketFileNames.length) violations.push('PRE-CLOSE-0: ticket_<id>.md not found');
  else if (snapshot.ticketFileNames.length > 1) violations.push(`PRE-CLOSE-1: multiple ticket_<id>.md records found: ${snapshot.ticketFileNames.join(', ')}`);
  const actual = new Set(snapshot.workingAnalysisFiles);
  const required = new Set(REQUIRED_ANALYSIS_FILES);
  for (const name of [...required].sort()) if (!Object.hasOwn(snapshot.analysisContents, name)) violations.push(`PRE-CLOSE-2: required analysis file missing: ${name}`);
  for (const name of [...actual].sort()) if (!required.has(name)) violations.push(`PRE-CLOSE-2: unexpected analysis file present: ${name}`);
  if (!snapshot.responseDraftPresent) violations.push('PRE-CLOSE-3: response-draft.md not found');
  if (!snapshot.screenshotsDirPresent) violations.push('PRE-CLOSE-4: screenshots/ not found');
  if (!snapshot.validationsDirPresent) violations.push('PRE-CLOSE-5: validations/ not found');
  for (const path of snapshot.unsafeTicketPaths) violations.push(`PRE-CLOSE-6: cited path escapes the ticket root: ${path}`);
  for (const path of snapshot.missingTicketPaths) violations.push(`PRE-CLOSE-7: cited path is not an existing file: ${path}`);
  violations.push(...checkCitationShapes(snapshot.citedPaths, 'PRE-CLOSE-11'));
  if (ticket !== null) {
    if ('error' in ticket) violations.push(`PRE-CLOSE-8: ticket record cannot be parsed: ${ticket.error}`);
    else violations.push(...checkIdentificationConsistency(ticket.value.identification_verdict, ticket.value.known_problem_ids, registerRows));
  }
  if (header !== null) {
    if ('error' in header) violations.push(`PRE-CLOSE-9: state.md cannot be parsed: ${header.error}`);
    else {
      violations.push(...checkPhase(header.value));
      if (header.value.Phase.trim() !== 'synthesize') violations.push("PRE-CLOSE-10: state.md Phase must be 'synthesize'");
      violations.push(...checkIdentificationVerdict(header.value), ...checkKillSwitches(header.value));
      const state = snapshot.analysisContents['state.md'];
      if (state !== undefined) {
        const text = state.replace(/<!--[\s\S]*?-->/g, '');
        for (const token of text.match(/<[^>]+>/g) ?? []) {
          if (!persistentTokens.has(token)) violations.push(`UNFILLED-TOKEN: ${token} in state.md`);
        }
      }
    }
  }
  for (const filename of STEP_FILES) {
    const content = snapshot.analysisContents[filename];
    if (content === undefined) continue;
    for (const [, item] of checkStepSections(content, filename, true)) {
      violations.push(item.startsWith('UNFILLED-TOKEN:') ? `${item} in ${filename}` : `MISSING-SECTION: ${filename} is missing ${item}`);
    }
  }
  return violations;
}

export function evaluateCloseOut(snapshot: CloseOutSnapshot): string[] {
  const violations: string[] = [];
  if (!snapshot.ticketFileNames.length) violations.push('CLOSE-0: ticket_<id>.md not found');
  else if (snapshot.ticketFileNames.length > 1) violations.push(`CLOSE-6: multiple ticket_<id>.md records found: ${snapshot.ticketFileNames.join(', ')}`);
  for (const name of snapshot.workingAnalysisFiles) violations.push(`CLOSE-1: working analysis file remains after close: ${name}`);
  if (snapshot.responseDraftPresent) violations.push('CLOSE-2: response-draft.md remains after close');
  if (!snapshot.screenshotsDirPresent) violations.push('CLOSE-3: screenshots/ missing from the durable set');
  if (!snapshot.validationsDirPresent) violations.push('CLOSE-4: validations/ missing from the durable set');
  for (const path of snapshot.missingImagePaths) violations.push(`CLOSE-5: cited image path is not an existing file inside the ticket folder: ${path}`);
  violations.push(...checkCitationShapes(snapshot.citedPaths, 'CLOSE-8'));
  for (const path of snapshot.leftoverDownloadFiles) violations.push(`CLOSE-9: unused download file remains after close: ${path}`);
  return violations;
}

export function checkIdentificationConsistency(
  verdict: string,
  citedProblemIds: readonly string[],
  registerRows: readonly Problem[],
): string[] {
  const cited = [...new Set(citedProblemIds)];
  const formatted = `[${cited.map(id => `'${id}'`).join(', ')}]`;
  const violations: string[] = [];
  if (verdict === 'pending') return violations;
  if (verdict === 'no_match') {
    if (cited.length) violations.push(`VERDICT-2: no_match must not cite a P-NNN (cited: ${formatted})`);
    return violations;
  }
  if (verdict !== 'exact' && verdict !== 'structural') return violations;
  if (!cited.length) return [`VERDICT-3: ${verdict} requires a cited incident P-NNN`];
  const incident = registerRows.filter(row => row.isIncident);
  for (const id of cited) {
    if (!incident.some(row => row.id === id)) violations.push(`VERDICT-4: cited ${id} is not an incident P-NNN row`);
  }
  const matched = incident.filter(row => cited.includes(row.id));
  if (verdict === 'exact') {
    if (cited.length !== 1) violations.push(`VERDICT-5: exact requires exactly one cited P-NNN (cited: ${formatted})`);
    for (const row of matched) {
      if (row.lifecycle !== 'active') violations.push(`VERDICT-6: exact requires an active P-NNN (${row.id} is ${row.lifecycle})`);
      if (row.allowExact !== 'yes') violations.push(`VERDICT-7: exact requires allow_exact=yes (${row.id} is ${row.allowExact})`);
    }
  } else {
    if (cited.length !== 1) violations.push(`VERDICT-9: structural requires exactly one cited P-NNN (cited: ${formatted})`);
    for (const row of matched) {
      if (!row.isMatchable) violations.push(`VERDICT-8: structural requires candidate|active|mitigated (${row.id} is ${row.lifecycle})`);
    }
  }
  return violations;
}
