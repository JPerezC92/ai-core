/** Define attribution input, scan-result records and returned validation errors. */

/** The validated markers and identities used by the scanner. */
export interface AttributionPolicy {
  readonly schema: number;
  readonly self_excluded_file: string;
  readonly markers: readonly string[];
  readonly identities: readonly string[];
}

/** One complete PR or commit-message artifact. */
export interface Artifact {
  readonly surface: string;
  readonly source: string;
  readonly content: string;
}

/** One changed-file body in the immutable snapshot. */
export interface ChangedFile {
  readonly path: string;
  readonly content: string;
}

/** The complete PR content snapshot evaluated by the scanner. */
export interface Snapshot {
  readonly schema: number;
  readonly pr_number: number;
  readonly head_sha: string;
  readonly base: string;
  readonly artifacts: readonly Artifact[];
  readonly changed_files: readonly ChangedFile[];
}

/** A line-level attribution finding without source-text disclosure. */
export interface Match {
  readonly surface: string;
  readonly source: string | null;
  readonly path: string | null;
  readonly line: number;
  readonly marker: string;
  readonly identity: string;
}

/** The one policy-file exclusion applied to changed-file bodies. */
export interface Exclusion {
  readonly path: string;
  readonly reason: string;
}

/** Deterministic scan metadata, findings, and applied exclusions. */
export interface ScanResult {
  readonly pr_number: number;
  readonly head_sha: string;
  readonly base: string;
  readonly matches: readonly Match[];
  readonly exclusions: readonly Exclusion[];
}

/** Carry decoded, not yet validated inputs into the scan operation. */
export interface ScanInput {
  readonly snapshotValue: unknown;
  readonly policyValue: unknown;
}

/** Describe a rejected policy as a returned business-error value. */
export class PolicyValidationError {
  readonly code: "POLICY_INVALID" = "POLICY_INVALID";
  readonly message: string;

  constructor(message: string) {
    this.message = message;
  }
}

/** Describe a rejected snapshot as a returned business-error value. */
export class SnapshotValidationError {
  readonly code: "SNAPSHOT_INVALID" = "SNAPSHOT_INVALID";
  readonly message: string;

  constructor(message: string) {
    this.message = message;
  }
}
