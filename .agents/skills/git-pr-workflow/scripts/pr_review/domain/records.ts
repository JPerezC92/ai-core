/** Define the workflow-side inventory record, prepared body, and returned failures. */

import type { Artifact, ChangedFile } from "#scripts/attribution_scan/domain/records.ts";

/** Carry validated immutable content independently of locally authored prose. */
export interface LocalInventory {
  readonly schema: number;
  readonly pr_number: number;
  readonly head_sha: string;
  readonly base: string;
  readonly commit_messages: readonly Artifact[];
  readonly changed_files: readonly ChangedFile[];
}

/** Return a stable rejection code and explanation without raising it. */
export class ReviewPreparationError {
  readonly code: string;
  readonly message: string;

  constructor(code: string, message: string) {
    this.code = code;
    this.message = message;
  }
}

/** Preserve a structurally checked body without claiming evidence truth. */
export class PreparedBody {
  readonly body: string;

  constructor(body: string) {
    this.body = body;
  }
}
