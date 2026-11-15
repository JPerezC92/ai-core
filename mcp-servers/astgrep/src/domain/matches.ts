export type MatchRecord = Record<string, unknown>;

export function parseMatches(
  stdout: string,
  maxResults = 0,
): { matches: MatchRecord[]; totalMatches: number } {
  const matches: MatchRecord[] = [];
  let totalLines = 0;
  for (const raw of stdout.split(/\r?\n/)) {
    const line = raw.trim();
    if (line.length === 0 || !line.startsWith('{')) {
      continue;
    }
    totalLines += 1;
    if (!maxResults || matches.length < maxResults) {
      matches.push(JSON.parse(line) as MatchRecord);
    }
  }
  return { matches, totalMatches: totalLines };
}

export function formatMatchesAsText(matches: readonly MatchRecord[]): string {
  if (matches.length === 0) {
    return '';
  }
  const blocks: string[] = [];
  for (const match of matches) {
    const filePath = typeof match.file === 'string' ? match.file : '';
    const range = match.range;
    const startLine =
      range && typeof range === 'object' && range !== null
        ? nestedLine(range, 'start') + 1
        : 1;
    const endLine =
      range && typeof range === 'object' && range !== null
        ? nestedLine(range, 'end') + 1
        : 1;
    const matchText =
      typeof match.text === 'string' ? match.text.replace(/[\r\n]+$/u, '') : '';
    const header =
      startLine === endLine ? `${filePath}:${startLine}` : `${filePath}:${startLine}-${endLine}`;
    blocks.push(`${header}\n${matchText}`);
  }
  return blocks.join('\n\n');
}

function nestedLine(range: object, key: 'start' | 'end'): number {
  const side = (range as Record<string, unknown>)[key];
  if (side && typeof side === 'object' && side !== null && 'line' in side) {
    const line = (side as { line?: unknown }).line;
    return typeof line === 'number' ? line : 0;
  }
  return 0;
}

export function formatFindText(
  matches: readonly MatchRecord[],
  totalMatches: number,
  maxResults: number,
): string {
  if (matches.length === 0) {
    return 'No matches found';
  }
  let header = `Found ${matches.length} matches`;
  if (maxResults && totalMatches > maxResults) {
    header += ` (showing first ${maxResults} of ${totalMatches})`;
  }
  return `${header}:\n\n${formatMatchesAsText(matches)}`;
}
