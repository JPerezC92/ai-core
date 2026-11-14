/** Typed retirement outcomes, independent of CLI presentation. */

/** Complete calendar days a record must be closed before it can be a deletion candidate. */
export const REQUIRED_COMPLETE_DAYS = 7;

export type RetirementDecision =
  | {
      readonly kind: "candidate";
      readonly closedOn: string;
      readonly ageDays: number;
    }
  | {
      readonly kind: "excluded";
      readonly reason: string;
    };

/** One record's outcome. A candidate is a proposal only: nothing is deleted by this module. */
export class RetirementReport {
  readonly path: string;
  readonly decision: RetirementDecision;

  constructor(path: string, decision: RetirementDecision) {
    this.path = path;
    this.decision = decision;
  }
}

export class NoTaskRecordsError {
  readonly code = "NO_TASK_RECORDS";
  readonly message = "no task records found";
}

export type RetirementResult = RetirementReport | NoTaskRecordsError;
