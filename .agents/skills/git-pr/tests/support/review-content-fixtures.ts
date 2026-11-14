/** Shared fixtures for PR review content preparation. */

export const HEAD_SHA = 'abc1234def5678abc1234def5678abc1234def56';
export const BASE_REF = 'main';

/** A completed review body that satisfies every structural rule. */
export function makeCompletedBody(overrides: {
  summary?: string;
  items?: string[];
  findings?: string;
  verdict?: string;
} = {}): string {
  const summary = overrides.summary ?? 'Adds the review preparation commands.\n';
  const items = overrides.items ?? ['Run the focused suite', 'Confirm the import map resolves'];
  const findings = overrides.findings ?? 'No findings.\n';
  const verdict = overrides.verdict ?? '[PASS] — 0 open findings';
  const plan = items.map(item => `- [x] ${item}`).join('\n');
  const rows = items.map(item => `| ${item} | \`pnpm vitest run\` | passed | Cipher |`).join('\n');
  return [
    '## Summary', '', summary,
    '## Test plan', '', plan, '',
    '## Findings / blockers', '', findings,
    '## Test evidence', '',
    `- PR: \`#12\``,
    `- Immutable head SHA: \`${HEAD_SHA}\``,
    `- Base: \`origin/${BASE_REF}\``,
    `- Scope command: \`git diff "origin/${BASE_REF}"...${HEAD_SHA}\``,
    '',
    '| Test-plan item | Literal action/input | Observed result | Executor |',
    '|---|---|---|---|',
    rows,
    '',
    verdict,
    '',
  ].join('\n');
}

/** Externally supplied metadata; never authenticated by these checks. */
export function makeMetadata(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    number: 12,
    headRefOid: HEAD_SHA,
    baseRefName: BASE_REF,
    headRefName: 'feat/review-content',
    state: 'OPEN',
    title: 'feat: review content preparation',
    body: makeCompletedBody(),
    ...overrides,
  };
}

/** A metadata record whose body carries the supplied completed body. */
export function metadataWithBody(body: string): Record<string, unknown> {
  return makeMetadata({ body });
}
