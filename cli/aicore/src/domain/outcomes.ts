/**
 * Domain outcomes for the synchronization CLI.
 *
 * Business operations return typed values, never transport encodings
 * (architecture contract C6). A synchronization run is the domain results its
 * operations produced, and turning them into process exit codes and operator
 * copy is the delivery edge's job.
 */

import type { SupportedEditor } from "./constants.ts";
import type { OperationOutcome } from "./synchronization/failures.ts";

export type SynchronizeOutcome = {
	/** Absolute destination path the run acted on. */
	readonly destination: string;
	readonly editor: SupportedEditor;
	/** True when this run enrolled a destination rather than updating one. */
	readonly enrolled: boolean;
	/** The write operation and, when it ran, the verification operation's result. */
	readonly runs: readonly OperationOutcome[];
	/** True when the verification operation reported the destination is current. */
	readonly current: boolean;
};
