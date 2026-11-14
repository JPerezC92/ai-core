export function frontMatterFixtures() {
  return {
    source: 'sample.md',
    nested: '---\nroot:\n  nested:\n    - alpha\n    - beta\n---\nBody\n',
    scalars: '---\ntext: "yes"\ncount: 12\nenabled: true\nempty: null\n---\n',
    malformed: '---\nitems: [one,\n---\n',
    absent: 'Body without frontmatter\n',
    unclosed: '---\nvalue: one\n',
    nonmapping: '---\n- one\n- two\n---\n',
  };
}
