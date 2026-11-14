import { parse, YAMLParseError } from 'yaml';

import { InputError } from '#scripts/incident_workflow_pkg/domain/errors.ts';

export function loadFrontMatter(content: string, source: string): Record<string, unknown> {
  const lines = content.split(/\r\n|\n|\r/);
  if (lines[0] !== '---') {
    throw new InputError(`No YAML frontmatter block found in ${source}`);
  }

  const closing = lines.indexOf('---', 1);
  if (closing === -1) {
    throw new InputError(`Unclosed frontmatter in ${source}`);
  }

  let data: unknown;
  try {
    data = parse(lines.slice(1, closing).join('\n'), {
      version: '1.1',
      uniqueKeys: false,
    });
  } catch (error) {
    if (error instanceof YAMLParseError) {
      throw new InputError(`Invalid YAML frontmatter in ${source}: ${error.message}`);
    }
    throw error;
  }

  if (data === null || typeof data !== 'object' || Array.isArray(data) || Object.getPrototypeOf(data) !== Object.prototype) {
    throw new InputError(`Frontmatter is not a YAML mapping in ${source}`);
  }
  return data as Record<string, unknown>;
}
