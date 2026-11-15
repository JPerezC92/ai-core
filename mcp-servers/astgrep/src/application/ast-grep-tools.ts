import { formatFindText, parseMatches, type MatchRecord } from '../domain/matches.ts';
import type { AstGrepCli } from '../domain/ports.ts';

export class AstGrepTools {
  private readonly process: AstGrepCli;

  constructor(process: AstGrepCli) {
    this.process = process;
  }

  async dumpSyntaxTree(code: string, language: string, format = 'cst'): Promise<string> {
    const result = await this.process.run('run', [
      '--pattern',
      code,
      '--lang',
      language,
      `--debug-query=${format}`,
    ]);
    return result.stderr.trim();
  }

  async findCode(
    projectFolder: string,
    pattern: string,
    language = '',
    maxResults = 0,
    outputFormat = 'text',
  ): Promise<string | MatchRecord[]> {
    assertOutputFormat(outputFormat);
    const args = ['--pattern', pattern];
    if (language.length > 0) {
      args.push('--lang', language);
    }
    const result = await this.process.run('run', [...args, '--json=stream', projectFolder]);
    const { matches, totalMatches } = parseMatches(result.stdout, maxResults);
    if (outputFormat === 'text') {
      return formatFindText(matches, totalMatches, maxResults);
    }
    return matches;
  }

  async findCodeByRule(
    projectFolder: string,
    yaml: string,
    maxResults = 0,
    outputFormat = 'text',
  ): Promise<string | MatchRecord[]> {
    assertOutputFormat(outputFormat);
    const result = await this.process.run('scan', [
      '--inline-rules',
      yaml,
      '--json=stream',
      projectFolder,
    ]);
    const { matches, totalMatches } = parseMatches(result.stdout, maxResults);
    if (outputFormat === 'text') {
      return formatFindText(matches, totalMatches, maxResults);
    }
    return matches;
  }

  async testMatchCodeRule(code: string, yaml: string): Promise<MatchRecord[]> {
    const result = await this.process.run(
      'scan',
      ['--inline-rules', yaml, '--json', '--stdin'],
      code,
    );
    const parsed = JSON.parse(result.stdout.trim() || '[]') as unknown;
    if (!Array.isArray(parsed) || parsed.length === 0) {
      throw new Error(
        'No matches found for the given code and rule. Try adding `stopBy: end` to your inside/has rule.',
      );
    }
    return parsed as MatchRecord[];
  }
}

function assertOutputFormat(outputFormat: string): void {
  if (outputFormat !== 'text' && outputFormat !== 'json') {
    throw new Error(`Invalid output_format: ${outputFormat}. Must be 'text' or 'json'.`);
  }
}
