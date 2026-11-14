/** Extract creation bodies and check completed PASS body structure, not truth. */

import type {
  Finding, ReviewDecisions, ReviewMetadata, ReviewPreparationError,
} from '#scripts/pr_content/domain/records.ts';
import { reviewError, isReviewError } from '#scripts/pr_content/domain/records.ts';

const CANONICAL_ORDER = [
  'Summary', 'Breaking changes', 'Test plan', 'Findings / blockers', 'Test evidence', 'Open debt',
];

const REQUIRED_SECTIONS = ['Summary', 'Test plan', 'Findings / blockers'];

function fullMatch(pattern: string, text: string): RegExpExecArray | null {
  return new RegExp(`^(?:${pattern})$`).exec(text);
}

function stripChars(text: string, chars: string): string {
  let start = 0;
  let end = text.length;
  while (start < end && chars.includes(text[start]!)) start += 1;
  while (end > start && chars.includes(text[end - 1]!)) end -= 1;
  return text.slice(start, end);
}

function cells(line: string): string[] {
  const parts = line.trim().split(/(?<!\\)\|/).slice(1, -1);
  return parts.map(cell => cell.trim().replaceAll('\\|', '|'));
}

/** Remove the creation-only title wrapper without normalizing body bytes. */
export function extractBody(draft: string): string | ReviewPreparationError {
  const match = /^Title: [^\r\n]+\r?\n\r?\n---\r?\n\r?\n/.exec(draft);
  if (match === null || !draft.slice(match[0].length).startsWith('## Summary')) {
    return reviewError('DRAFT_INVALID', 'creation draft title wrapper and Summary required');
  }
  return draft.slice(match[0].length);
}

/** Split unique canonical headings while retaining section content verbatim. */
export function parseSections(body: string): Record<string, string> | ReviewPreparationError {
  const error = reviewError('BODY_INVALID', 'unique canonical sections with content required');
  if (typeof body !== 'string') return error;

  const matches = [...body.matchAll(/^## ([^\r\n]+)(?:\r?\n|$)/gm)];
  const names = matches.map(match => match[1]!);
  if (matches.length === 0 || matches[0]!.index !== 0) return error;
  if (new Set(names).size !== names.length) return error;
  if (names.some(name => !CANONICAL_ORDER.includes(name))) return error;
  const sorted = [...names].sort((left, right) => CANONICAL_ORDER.indexOf(left) - CANONICAL_ORDER.indexOf(right));
  if (names.some((name, index) => name !== sorted[index])) return error;
  if (REQUIRED_SECTIONS.some(name => !names.includes(name))) return error;

  const sections: Record<string, string> = {};
  for (const [index, match] of matches.entries()) {
    const start = match.index! + match[0].length;
    const end = index + 1 < matches.length ? matches[index + 1]!.index! : body.length;
    const content = body.slice(start, end);
    if (content.trim() === '') return error;
    sections[match[1]!] = content;
  }
  return sections;
}

/** Parse the canonical finding schema without judging resolution evidence. */
export function parseFindings(content: string): Finding[] | ReviewPreparationError {
  const error = reviewError('BODY_INVALID', 'canonical finding table required');
  const trimmed = content.trim();
  if (trimmed === 'No findings.' || trimmed === 'No review findings yet.') return [];

  const lines = content.split(/\r\n|\n|\r/).filter(line => line.trim() !== '');
  if (lines.length < 3 || lines[0] !== '| ID | Severity | Status | Evidence | Owner / resolution |') {
    return error;
  }
  if (fullMatch('\\|(?:\\s*:?-+:?\\s*\\|){5}', lines[1]!) === null) return error;
  if (lines.slice(2).some(line => !line.trim().startsWith('|') || !line.trim().endsWith('|'))) return error;

  const rows = lines.slice(2).map(cells);
  for (const row of rows) {
    if (row.length !== 5 || row.some(cell => cell === '')) return error;
    if (fullMatch('F[1-9][0-9]*', row[0]!) === null) return error;
    if (!['BLOCK', 'ADVISORY'].includes(stripChars(row[1]!, '`'))) return error;
    if (!['OPEN', 'IN PROGRESS', 'FIXED', 'DEFERRED', 'REJECTED'].includes(stripChars(row[2]!, '`'))) return error;
  }
  const ids = rows.map(row => row[0]!);
  if (new Set(ids).size !== ids.length) return error;
  if (ids.some((id, index) => id !== `F${index + 1}`)) return error;

  return rows.map(row => ({
    id: row[0]!,
    severity: stripChars(row[1]!, '`'),
    status: stripChars(row[2]!, '`'),
    evidence: row[3]!,
    resolution: row[4]!,
  }));
}

/** Check structural correspondence only; owners establish actual evidence truth. */
export function validateBody(
  body: string,
  metadata: ReviewMetadata,
  decisions: ReviewDecisions = { notApplicable: [], acceptance: [], debt: [] },
): ReviewPreparationError | undefined {
  const error = reviewError('BODY_INVALID', 'completed canonical review body required');
  if (typeof body !== 'string') return error;

  const lines = body.replace(/\s+$/, '').split(/\r\n|\n|\r/);
  const last = lines[lines.length - 1] ?? '';
  const verdict = fullMatch('\\[(PASS|ADVISORY)\\] — (.+)', last);
  if (verdict === null) return error;

  const content = body.slice(0, body.lastIndexOf(last));
  if (/^\[(?:PASS|ADVISORY|BLOCK)\] —/m.test(content)) return error;

  const sections = parseSections(content);
  if (isReviewError(sections)) return sections;
  if (/^Title:/m.test(body)) return error;

  const findings = parseFindings(sections['Findings / blockers'] ?? '');
  if (isReviewError(findings)) return findings;
  if ((sections['Findings / blockers'] ?? '').trim() === 'No review findings yet.') return error;

  const unresolved = findings.filter(finding => !['FIXED', 'REJECTED'].includes(finding.status));
  if (verdict[1] === 'PASS' && unresolved.length > 0) return error;

  const accepted = new Map(decisions.acceptance.map(entry => [entry.target, entry]));
  const debts = new Map(decisions.debt.map(entry => [entry.target, entry]));
  const unresolvedIds = new Set(unresolved.map(finding => finding.id));
  if (accepted.size !== unresolvedIds.size || [...accepted.keys()].some(id => !unresolvedIds.has(id))) return error;
  if (verdict[1] === 'ADVISORY' && (unresolved.length === 0 || unresolved.some(finding => finding.severity !== 'ADVISORY'))) {
    return error;
  }
  for (const entry of accepted.values()) {
    if (!verdict[2]!.includes(entry.actor) || !verdict[2]!.includes(entry.date)) return error;
  }

  const deferred = new Set(findings.filter(finding => finding.status === 'DEFERRED').map(finding => finding.id));
  if ([...deferred].some(id => !debts.has(id))) return error;
  if (debts.size > 0) {
    const expectedDebt = decisions.debt.map(entry =>
      `- ${entry.target} — ${entry.destination}, authorized by ${entry.actor} on ${entry.date}`);
    const openDebt = (sections['Open debt'] ?? '').trim().split(/\r\n|\n|\r/);
    if (openDebt.length !== expectedDebt.length || openDebt.some((line, index) => line !== expectedDebt[index])) {
      return error;
    }
    for (const finding of findings) {
      if (!deferred.has(finding.id)) continue;
      if (debts.get(finding.id)!.destination !== finding.resolution.split(' — ')[0]) return error;
    }
  } else if (Object.hasOwn(sections, 'Open debt')) {
    return error;
  }

  const plan = (sections['Test plan'] ?? '').trim().split(/\r\n|\n|\r/);
  if (plan.length < 2 || plan.some(line => fullMatch('- \\[[ x]\\] .+', line) === null)) return error;
  const items = plan.map(line => line.slice(6));
  if (new Set(items).size !== items.length) return error;

  const excluded = new Set(decisions.notApplicable.map(entry => entry.target));
  const unchecked = new Set(plan.filter(line => line.startsWith('- [ ]')).map(line => line.slice(6)));
  if (unchecked.size !== excluded.size || [...unchecked].some(item => !excluded.has(item))) return error;
  const activeItems = items.filter(item => !excluded.has(item));
  if (activeItems.length === 0) return Object.hasOwn(sections, 'Test evidence') ? error : undefined;
  if (!Object.hasOwn(sections, 'Test evidence')) return error;

  const evidence = (sections['Test evidence'] ?? '').trim().split(/\r\n|\n|\r/);
  const baseMatch = evidence.length > 2 ? fullMatch('- Base: `([^`]+)`', evidence[2]!) : null;
  if (baseMatch === null) return error;
  const base = baseMatch[1]!;
  if (base.includes('$') || base.split('/').at(-1) !== metadata.baseRefName) return error;

  const header = [
    `- PR: \`#${metadata.number}\``,
    `- Immutable head SHA: \`${metadata.headRefOid}\``,
    `- Base: \`${base}\``,
    `- Scope command: \`git diff "${base}"...${metadata.headRefOid}\``,
  ];
  if (evidence.length < 4 || header.some((line, index) => evidence[index] !== line)) return error;

  const tail = evidence.slice(4).filter(line => line.trim() !== '');
  if (tail.length !== activeItems.length + 2) return error;
  if (tail[0] !== '| Test-plan item | Literal action/input | Observed result | Executor |') return error;
  if (tail[1] !== '|---|---|---|---|') return error;

  const rows = tail.slice(2).map(cells);
  if (rows.some(row => row.length !== 4 || row.some(cell => cell === ''))) return error;
  const firstColumn = rows.map(row => row[0]!);
  if (new Set(firstColumn).size !== rows.length) return error;
  if (firstColumn.length !== activeItems.length || firstColumn.some(item => !activeItems.includes(item))) return error;
  return undefined;
}
