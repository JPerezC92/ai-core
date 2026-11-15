import type { MatchRecord } from '../../src/domain/matches.ts';
import type { AstGrepCli, MatchList } from '../../src/domain/ports.ts';

export type FakeCliState = {
  dumpText: string;
  patternMatches: MatchList;
  ruleMatches: MatchList;
  stdinMatches: MatchRecord[];
  failSearch?: Error;
};

export function fakeAstGrepCli(state: FakeCliState): AstGrepCli {
  return {
    async dumpQuery(): Promise<string> {
      return state.dumpText;
    },
    async searchPattern(): Promise<MatchList> {
      if (state.failSearch) {
        throw state.failSearch;
      }
      return state.patternMatches;
    },
    async searchRule(): Promise<MatchList> {
      if (state.failSearch) {
        throw state.failSearch;
      }
      return state.ruleMatches;
    },
    async matchRuleOnCode(): Promise<MatchRecord[]> {
      if (state.failSearch) {
        throw state.failSearch;
      }
      return state.stdinMatches;
    },
  };
}

export function createMatch(file: string, text = ''): MatchRecord {
  return {
    file,
    range: { start: { line: 0 }, end: { line: 0 } },
    text,
  };
}

export function emptyMatchList(): MatchList {
  return { matches: [], totalMatches: 0 };
}

export function matchList(matches: MatchRecord[]): MatchList {
  return { matches, totalMatches: matches.length };
}
