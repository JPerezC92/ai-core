import { AstGrepError } from '../domain/errors.ts';
import type { MatchRecord } from '../domain/matches.ts';
import type { AstGrepCli } from '../domain/ports.ts';

export type FindCodeInput = {
  readonly projectFolder: string;
  readonly pattern: string;
  readonly language?: string;
  readonly maxResults?: number;
  readonly outputFormat?: string;
};

export type FindCodeSuccess = {
  readonly matches: MatchRecord[];
  readonly totalMatches: number;
  readonly outputFormat: 'text' | 'json';
};

export class FindCode {
  private readonly cli: AstGrepCli;

  constructor(cli: AstGrepCli) {
    this.cli = cli;
  }

  async execute(input: FindCodeInput): Promise<FindCodeSuccess | AstGrepError> {
    const outputFormat = input.outputFormat ?? 'text';
    if (outputFormat !== 'text' && outputFormat !== 'json') {
      return new AstGrepError(
        'invalid_output_format',
        `Invalid output_format: ${outputFormat}. Must be 'text' or 'json'.`,
      );
    }
    const listed = await this.cli.searchPattern(
      input.projectFolder,
      input.pattern,
      input.language ?? '',
    );
    const maxResults = input.maxResults ?? 0;
    const matches =
      maxResults > 0 ? listed.matches.slice(0, maxResults) : listed.matches;
    return {
      matches,
      totalMatches: listed.totalMatches,
      outputFormat,
    };
  }
}
