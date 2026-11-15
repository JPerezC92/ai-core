export type MatchRangePoint = {
  readonly line: number;
};

export type MatchRange = {
  readonly start: MatchRangePoint;
  readonly end: MatchRangePoint;
};

export type MatchRecord = {
  readonly file: string;
  readonly range: MatchRange;
  readonly text: string;
};
