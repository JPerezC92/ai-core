import { describe, expect, it } from 'vitest';

import { loadFrontMatter } from '#scripts/incident_workflow_pkg/infrastructure/frontmatter.ts';
import { frontMatterFixtures } from '#tests/support/incident-yaml-fixtures.ts';

describe('incident YAML frontmatter', () => {
  it('loads nested mappings and lists', () => {
    const fixture = frontMatterFixtures();
    expect(loadFrontMatter(fixture.nested, fixture.source)).toEqual({
      root: { nested: ['alpha', 'beta'] },
    });
  });

  it('preserves scalar types and quoted text', () => {
    const fixture = frontMatterFixtures();
    expect(loadFrontMatter(fixture.scalars, fixture.source)).toEqual({
      text: 'yes', count: 12, enabled: true, empty: null,
    });
  });

  it('rejects malformed YAML with its source', () => {
    const fixture = frontMatterFixtures();
    expect(() => loadFrontMatter(fixture.malformed, fixture.source))
      .toThrow('Invalid YAML frontmatter in sample.md:');
  });

  it('rejects missing frontmatter', () => {
    const fixture = frontMatterFixtures();
    expect(() => loadFrontMatter(fixture.absent, fixture.source))
      .toThrow('No YAML frontmatter block found in sample.md');
  });

  it('rejects unclosed frontmatter', () => {
    const fixture = frontMatterFixtures();
    expect(() => loadFrontMatter(fixture.unclosed, fixture.source))
      .toThrow('Unclosed frontmatter in sample.md');
  });

  it('rejects non-mapping frontmatter', () => {
    const fixture = frontMatterFixtures();
    expect(() => loadFrontMatter(fixture.nonmapping, fixture.source))
      .toThrow('Frontmatter is not a YAML mapping in sample.md');
  });
});
