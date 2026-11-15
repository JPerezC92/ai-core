import type { MatchRecord } from './matches.ts';

export type CliResult = {
  readonly stdout: string;
  readonly stderr: string;
  readonly returncode: number;
};

export type MatchList = {
  readonly matches: MatchRecord[];
  readonly totalMatches: number;
};

export type AstGrepCli = {
  dumpQuery(code: string, language: string, format: string): Promise<string>;
  searchPattern(
    projectFolder: string,
    pattern: string,
    language: string,
  ): Promise<MatchList>;
  searchRule(projectFolder: string, yaml: string): Promise<MatchList>;
  matchRuleOnCode(code: string, yaml: string): Promise<MatchRecord[]>;
};
