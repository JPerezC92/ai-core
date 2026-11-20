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

/** The collected local Git inventory and the exact paths the commit range changed. */
export interface CollectedInventory {
	readonly inventory: LocalInventory;
	readonly paths: readonly string[];
}

/** One value a supplied JSON capture may carry. */
export type CaptureValue = string | number | boolean | null | CaptureValue[] | { readonly [key: string]: CaptureValue };

/** One supplied pull-request capture, typed as its own field set rather than a fixed schema. */
export interface Capture {
	readonly fields: Readonly<Record<string, CaptureValue>>;
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
