import { describe, expect, it } from 'vitest';

import { formatFindText, formatMatchesAsText, parseMatches } from './matches.ts';

describe('parseMatches', () => {
  it('parses JSONL objects and skips warnings', () => {
    const stdout = [
      'warning: skip',
      '{"file":"a.ts","text":"one","range":{"start":{"line":0},"end":{"line":0}}}',
      '',
      '{"file":"b.ts","text":"two","range":{"start":{"line":1},"end":{"line":3}}}',
    ].join('\n');
    const { matches, totalMatches } = parseMatches(stdout, 0);
    expect(totalMatches).toBe(2);
    expect(matches).toHaveLength(2);
  });

  it('limits deserialized matches while counting the rest', () => {
    const stdout = [
      '{"file":"a.ts","text":"one"}',
      '{"file":"b.ts","text":"two"}',
      '{"file":"c.ts","text":"three"}',
    ].join('\n');
    const { matches, totalMatches } = parseMatches(stdout, 1);
    expect(totalMatches).toBe(3);
    expect(matches).toEqual([{ file: 'a.ts', text: 'one' }]);
  });
});

describe('formatMatchesAsText', () => {
  it('uses a single line header when start equals end', () => {
    const text = formatMatchesAsText([
      {
        file: 'src/a.ts',
        text: 'const x = 1;\n',
        range: { start: { line: 9 }, end: { line: 9 } },
      },
    ]);
    expect(text).toBe('src/a.ts:10\nconst x = 1;');
  });

  it('uses a range header for multi-line matches', () => {
    const text = formatMatchesAsText([
      {
        file: 'src/a.ts',
        text: 'fn()',
        range: { start: { line: 0 }, end: { line: 2 } },
      },
    ]);
    expect(text).toBe('src/a.ts:1-3\nfn()');
  });
});

describe('formatFindText', () => {
  it('returns No matches found when empty', () => {
    expect(formatFindText([], 0, 0)).toBe('No matches found');
  });

  it('adds a showing-first suffix when limited', () => {
    const text = formatFindText(
      [{ file: 'a.ts', text: 'x', range: { start: { line: 0 }, end: { line: 0 } } }],
      5,
      1,
    );
    expect(text.startsWith('Found 1 matches (showing first 1 of 5):\n\n')).toBe(true);
  });
});
