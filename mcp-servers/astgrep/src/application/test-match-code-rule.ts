import { AstGrepError, NO_MATCH_MESSAGE } from '../domain/errors.ts';
import type { MatchRecord } from '../domain/matches.ts';
import type { AstGrepCli } from '../domain/ports.ts';

export type TestMatchCodeRuleInput = {
  readonly code: string;
  readonly yaml: string;
};

export class TestMatchCodeRule {
  private readonly cli: AstGrepCli;

  constructor(cli: AstGrepCli) {
    this.cli = cli;
  }

  async execute(input: TestMatchCodeRuleInput): Promise<MatchRecord[] | AstGrepError> {
    const matches = await this.cli.matchRuleOnCode(input.code, input.yaml);
    if (matches.length === 0) {
      return new AstGrepError('no_match', NO_MATCH_MESSAGE);
    }
    return matches;
  }
}
