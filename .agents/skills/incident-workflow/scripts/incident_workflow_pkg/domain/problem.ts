export interface ProblemFields {
  readonly id: string;
  readonly date: string;
  readonly team: string;
  readonly symptom: string;
  readonly system: string;
  readonly module: string;
  readonly problem: string;
  readonly discriminators: string;
  readonly exclusions: string;
  readonly evidence: string;
  readonly rootCause: string;
  readonly lifecycle: string;
  readonly allowExact: string;
  readonly status: string;
}

export interface ProblemError {
  readonly code: string;
  readonly message: string;
}

export class Problem {
  private readonly fields: ProblemFields;

  private constructor(fields: ProblemFields) {
    this.fields = Object.freeze({ ...fields });
  }

  static create(fields: ProblemFields): Problem | ProblemError {
    if (!['incident', 'dev'].includes(fields.team)) return { code: 'invalid_team', message: fields.team };
    if (!['candidate', 'active', 'mitigated', 'resolved', 'retired'].includes(fields.lifecycle)) {
      return { code: 'invalid_lifecycle', message: fields.lifecycle };
    }
    if (!['yes', 'no'].includes(fields.allowExact)) return { code: 'invalid_allow_exact', message: fields.allowExact };
    if (!['open', 'closed'].includes(fields.status)) return { code: 'invalid_status', message: fields.status };
    if (!/S-\d{2}/.test(fields.symptom)) return { code: 'missing_symptom_reference', message: fields.symptom };
    return new Problem(fields);
  }

  get id(): string { return this.fields.id; }
  get lifecycle(): string { return this.fields.lifecycle; }
  get allowExact(): string { return this.fields.allowExact; }
  get isIncident(): boolean { return this.fields.team === 'incident'; }
  get isMatchable(): boolean { return ['candidate', 'active', 'mitigated'].includes(this.fields.lifecycle); }
  get isExactMatchEligible(): boolean { return this.fields.lifecycle === 'active' && this.fields.allowExact === 'yes'; }

  activate(): Problem | ProblemError {
    if (this.fields.lifecycle !== 'candidate') return { code: 'illegal_transition', message: this.id };
    return new Problem({ ...this.fields, lifecycle: 'active', allowExact: 'yes' });
  }
}
