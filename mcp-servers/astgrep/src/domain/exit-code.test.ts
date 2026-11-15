import { describe, expect, it } from 'vitest';

import { isNoMatchExit } from './exit-code.ts';

describe('isNoMatchExit', () => {
  it('treats empty stdout on exit 1 as no-match', () => {
    expect(isNoMatchExit(1, '', ['ast-grep', 'run', '--json=stream'])).toBe(true);
  });

  it('treats JSON array or object stdout as no-match on exit 1', () => {
    expect(isNoMatchExit(1, '[]', ['ast-grep', 'scan', '--json'])).toBe(true);
    expect(isNoMatchExit(1, '[{"file":"a"}]', ['ast-grep', 'scan', '--json'])).toBe(true);
    expect(isNoMatchExit(1, '{"file":"a"}', ['ast-grep', 'run', '--json=stream'])).toBe(true);
  });

  it('does not treat other exit 1 stderr failures as no-match', () => {
    expect(isNoMatchExit(1, 'error: bad yaml', ['ast-grep', 'scan'])).toBe(false);
  });

  it('does not treat exit 2 as no-match', () => {
    expect(isNoMatchExit(2, '', ['ast-grep', 'run'])).toBe(false);
  });
});
