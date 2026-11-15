import { AstGrepError } from '../domain/errors.ts';
import type { MatchRecord } from '../domain/matches.ts';
import type { AstGrepCli } from '../domain/ports.ts';

export type FindCodeByRuleInput = {
  readonly projectFolder: string;
  readonly yaml: string;
  readonly maxResults?: number;
  readonly outputFormat?: string;
};

export type FindCodeByRuleSuccess = {
  readonly matches: MatchRecord[];
  readonly totalMatches: number;
  readonly outputFormat: 'text' | 'json';
};

export class FindCodeByRule {
  private readonly cli: AstGrepCli;

  constructor(cli: AstGrepCli) {
    this.cli = cli;
  }

  async execute(input: FindCodeByRuleInput): Promise<FindCodeByRuleSuccess | AstGrepError> {
    const outputFormat = input.outputFormat ?? 'text';
    if (outputFormat !== 'text' && outputFormat !== 'json') {
      return new AstGrepError(
        'invalid_output_format',
        `Invalid output_format: ${outputFormat}. Must be 'text' or 'json'.`,
      );
    }
    const listed = await this.cli.searchRule(input.projectFolder, input.yaml);
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
