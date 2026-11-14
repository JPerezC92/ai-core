import { InputError } from '#scripts/incident_workflow_pkg/domain/errors.ts';
import { Problem } from '#scripts/incident_workflow_pkg/domain/problem.ts';
import type { ProblemFields } from '#scripts/incident_workflow_pkg/domain/problem.ts';
import type { AnalysisHeader, TicketIdentification } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import { loadFrontMatter } from './frontmatter.ts';

function scalarText(value: unknown): string {
  if (value === null) return 'None';
  if (value === true) return 'True';
  if (value === false) return 'False';
  return String(value);
}

function stringList(value: unknown): string[] {
  if (value === null || value === undefined) return [];
  if (Array.isArray(value)) return value.map(scalarText).map(item => item.trim()).filter(Boolean);
  const text = scalarText(value).trim();
  if (!text || text === '[]') return [];
  return text.split(',').map(item => item.trim()).filter(Boolean);
}

export function parseStateHeader(content: string, source: string): AnalysisHeader {
  const data = loadFrontMatter(content, source);
  const fields = ['Phase', 'SLA-due', 'Updated', 'Hypotheses-outstanding', 'Query-budget', 'identification_verdict', 'Same-query-reruns'];
  const missing = fields.filter(field => !Object.hasOwn(data, field)).sort();
  if (missing.length) throw new InputError(`Missing header fields in ${source}: [${missing.map(field => `'${field}'`).join(', ')}]`);
  return {
    Phase: scalarText(data.Phase), SLA_due: scalarText(data['SLA-due']), Updated: scalarText(data.Updated),
    Hypotheses_outstanding: scalarText(data['Hypotheses-outstanding']), Query_budget: scalarText(data['Query-budget']),
    Identification_verdict: scalarText(data.identification_verdict), Same_query_reruns: scalarText(data['Same-query-reruns']),
  };
}

export function parseTicketRecord(content: string, source: string): TicketIdentification {
  const data = loadFrontMatter(content, source);
  return {
    symptom_ids: stringList(data.symptom_ids),
    known_problem_ids: stringList(data.known_problem_ids),
    identification_verdict: scalarText(Object.hasOwn(data, 'identification_verdict') ? data.identification_verdict : 'pending').trim(),
  };
}

export function parseProblemRegister(content: string): Problem[] {
  const rows: Problem[] = [];
  for (const line of content.split(/\r\n|\n|\r/)) {
    const trimmed = line.trim();
    if (!trimmed.startsWith('|')) continue;
    const cells = trimmed.replace(/^\|+|\|+$/g, '').split('|').map(cell => cell.trim());
    if (cells.length !== 14 || !/^P-\d+$/.test(cells[0] ?? '')) continue;
    const [id, date, team, symptom, system, module, problem, discriminators, exclusions, evidence, rootCause, lifecycle, allowExact, status] = cells;
    const fields: ProblemFields = {
      id: id!, date: date!, team: team!, symptom: symptom!, system: system!, module: module!, problem: problem!,
      discriminators: discriminators!, exclusions: exclusions!, evidence: evidence!, rootCause: rootCause!,
      lifecycle: lifecycle!, allowExact: allowExact!, status: status!,
    };
    const result = Problem.create(fields);
    if (result instanceof Problem) rows.push(result);
  }
  return rows;
}

export function checkRegisterRows(content: string): string[] {
  const violations: string[] = [];
  const lines = content.split(/\r\n|\n|\r/);
  for (const [index, line] of lines.entries()) {
    const trimmed = line.trim();
    if (!trimmed.startsWith('|')) continue;
    const cells = trimmed.replace(/^\|+|\|+$/g, '').split('|').map(cell => cell.trim());
    const id = cells[0] ?? '';
    if (!/^P-\d+$/.test(id)) continue;
    if (cells.length !== 14) {
      violations.push(`REGISTER-1: ${id} (line ${index + 1}) has ${cells.length} columns, expected 14`);
      continue;
    }
    const [problemId, date, team, symptom, system, module, problem, discriminators, exclusions, evidence, rootCause, lifecycle, allowExact, status] = cells;
    const result = Problem.create({
      id: problemId!, date: date!, team: team!, symptom: symptom!, system: system!, module: module!, problem: problem!,
      discriminators: discriminators!, exclusions: exclusions!, evidence: evidence!, rootCause: rootCause!,
      lifecycle: lifecycle!, allowExact: allowExact!, status: status!,
    });
    if (result instanceof Problem) continue;
    const quoted = `'${result.message}'`;
    switch (result.code) {
      case 'invalid_team': violations.push(`REGISTER-2: ${id} Team ${quoted} not in (dev, incident)`); break;
      case 'invalid_lifecycle': violations.push(`REGISTER-3: ${id} Lifecycle ${quoted} not in (active, candidate, mitigated, resolved, retired)`); break;
      case 'invalid_allow_exact': violations.push(`REGISTER-4: ${id} Allow_exact ${quoted} not in (no, yes)`); break;
      case 'invalid_status': violations.push(`REGISTER-5: ${id} Status ${quoted} not in (closed, open)`); break;
      case 'missing_symptom_reference': violations.push(`REGISTER-6: ${id} Symptom ${quoted} references no S-xx`); break;
      default: violations.push(`${result.code}: ${id} ${result.message}`);
    }
  }
  return violations;
}
