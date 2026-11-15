import type { AstGrepCli } from '#domain/ports.ts';

export type DumpSyntaxTreeInput = {
  readonly code: string;
  readonly language: string;
  readonly format?: string;
};

export class DumpSyntaxTree {
  private readonly cli: AstGrepCli;

  constructor(cli: AstGrepCli) {
    this.cli = cli;
  }

  async execute(input: DumpSyntaxTreeInput): Promise<string> {
    return this.cli.dumpQuery(input.code, input.language, input.format ?? 'cst');
  }
}
