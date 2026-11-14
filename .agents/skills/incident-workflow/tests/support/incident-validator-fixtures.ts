import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import type { CloseOutSnapshot } from '#scripts/incident_workflow_pkg/domain/ports.ts';
import type { AnalysisHeader, TicketIdentification } from '#scripts/incident_workflow_pkg/domain/rules.ts';

/** A fully valid, fully filled state header; override one field per case. */
export function makeHeader(overrides: Partial<AnalysisHeader> = {}): AnalysisHeader {
  return {
    Phase: 'synthesize',
    SLA_due: '2099-01-01T00:00',
    Updated: '2000-01-01T00:00',
    Hypotheses_outstanding: '0/3',
    Query_budget: '0/6',
    Identification_verdict: 'no_match',
    Same_query_reruns: '0/2',
    ...overrides,
  };
}

/** A step file whose four required sections are present and filled. */
export function makeStepContent(): string {
  return [
    '> **Owner:** Investigator', '> **Pre:** none', '> **Reads:** none',
    '> **Writes:** none', '', '## Steps', '', 'step', '', '## Output',
    '', 'output', '', '## Gate', '', 'done', '', '## Abort conditions', '', 'halt', '',
  ].join('\n');
}

/** A close-out snapshot with every pre-close requirement satisfied. */
export function makeSnapshot(overrides: Partial<CloseOutSnapshot> = {}): CloseOutSnapshot {
  const step = makeStepContent();
  return {
    ticketFileNames: ['ticket_999999.md'],
    ticketContent: '---\nsymptom_ids: []\nknown_problem_ids: []\nidentification_verdict: no_match\n---\n',
    citedPaths: [],
    workingAnalysisFiles: ['01-identify.md', '02-investigate.md', '03-synthesize.md', 'state.md'],
    analysisContents: { '01-identify.md': step, '02-investigate.md': step, '03-synthesize.md': step, 'state.md': '---\n---\n' },
    responseDraftPresent: true,
    screenshotsDirPresent: true,
    validationsDirPresent: true,
    missingImagePaths: [],
    missingTicketPaths: [],
    unsafeTicketPaths: [],
    leftoverDownloadFiles: [],
    ...overrides,
  };
}

/** A durable post-close snapshot: the collapsed set with no working files left. */
export function makeClosedSnapshot(overrides: Partial<CloseOutSnapshot> = {}): CloseOutSnapshot {
  return makeSnapshot({
    workingAnalysisFiles: [], analysisContents: {}, responseDraftPresent: false, ...overrides,
  });
}

export function createIncidentFixture(root: string, citation = 'screenshots/response-1/01_source_entity.png') {
  const ticket = join(root, 'ticket');
  const analysis = join(ticket, 'analysis');
  mkdirSync(analysis, { recursive: true });
  mkdirSync(join(ticket, 'screenshots', 'response-1'), { recursive: true });
  mkdirSync(join(ticket, 'validations'));
  writeFileSync(join(ticket, 'screenshots', 'response-1', '01_source_entity.png'), 'fixture');
  writeFileSync(join(root, 'outside.png'), 'fixture');
  writeFileSync(join(ticket, 'response-draft.md'), 'fixture');
  writeFileSync(join(ticket, 'ticket_999999.md'), [
    '---', 'symptom_ids: []', 'known_problem_ids: []',
    'identification_verdict: no_match', '---', '', `- **path:** ${citation}`, '',
  ].join('\n'));
  writeFileSync(join(analysis, 'state.md'), [
    '---', 'Phase: "synthesize"', 'SLA-due: "2099-01-01T00:00"',
    'Updated: "2000-01-01T00:00"', 'Hypotheses-outstanding: "0/3"',
    'Query-budget: "0/6"', 'identification_verdict: "no_match"',
    'Same-query-reruns: "0/2"', '---', '',
  ].join('\n'));
  const step = makeStepContent();
  for (const name of ['01-identify.md', '02-investigate.md', '03-synthesize.md']) {
    writeFileSync(join(analysis, name), step);
  }
  return { root, ticket, analysis };
}

/** The four analysis files a completed working set holds. */
export function makeStepContents(overrides: Record<string, string> = {}): Record<string, string> {
  const step = makeStepContent();
  return {
    'state.md': '---\n---\n',
    '01-identify.md': step,
    '02-investigate.md': step,
    '03-synthesize.md': step,
    ...overrides,
  };
}

/** A parsed identification record; override one field per case. */
export function makeTicketRecord(overrides: Partial<TicketIdentification> = {}): TicketIdentification {
  return { symptom_ids: [], known_problem_ids: [], identification_verdict: 'no_match', ...overrides };
}

/** A register row; override one field to make it malformed in one dimension. */export interface RegisterRow {
  readonly id: string;
  readonly date: string;
  readonly team: string;
  readonly symptom: string;
  readonly system: string;
  readonly module: string;
  readonly problem: string;
  readonly discriminators: string;
  readonly exclusions: string;
  readonly evidence: string;
  readonly rootCause: string;
  readonly lifecycle: string;
  readonly allowExact: string;
  readonly status: string;
}

const REGISTER_COLUMNS = [
  'id', 'date', 'team', 'symptom', 'system', 'module', 'problem', 'discriminators',
  'exclusions', 'evidence', 'rootCause', 'lifecycle', 'allowExact', 'status',
] as const;

export function makeRegisterRow(overrides: Partial<RegisterRow> = {}): RegisterRow {
  return {
    id: 'P-001', date: '2026-01-01', team: 'incident', symptom: 'S-05',
    system: 'sys', module: 'mod', problem: 'slow CDN', discriminators: 'host=cdn-a',
    exclusions: 'host=cdn-b', evidence: 'log:42', rootCause: 'cache miss',
    lifecycle: 'active', allowExact: 'yes', status: 'open', ...overrides,
  };
}

/** A whole register document from rows, or from a raw malformed line. */
export function makeRegister(...rows: Array<RegisterRow | string>): string {
  const rendered = rows.map(row => typeof row === 'string'
    ? row
    : `| ${REGISTER_COLUMNS.map(column => row[column]).join(' | ')} |`);
  return [
    '## Register', '',
    `| ${REGISTER_COLUMNS.map(column => column).join(' | ')} |`,
    '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
    ...rendered, '',
  ].join('\n');
}

/** Rewrites `state.md` so the header carries a header written `minutesAgo` ago. */export function writeFreshState(analysis: string, minutesAgo: number): void {
  const updated = new Date(Date.now() - minutesAgo * 60_000);
  const pad = (value: number) => String(value).padStart(2, '0');
  const stamp = `${updated.getFullYear()}-${pad(updated.getMonth() + 1)}-${pad(updated.getDate())}T${pad(updated.getHours())}:${pad(updated.getMinutes())}`;
  writeFileSync(join(analysis, 'state.md'), [
    '---', 'Phase: "synthesize"', 'SLA-due: "2099-01-01T00:00"',
    `Updated: "${stamp}"`, 'Hypotheses-outstanding: "0/3"',
    'Query-budget: "0/6"', 'identification_verdict: "no_match"',
    'Same-query-reruns: "0/2"', '---', '',
  ].join('\n'));
}
