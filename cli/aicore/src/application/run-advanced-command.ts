/**
 * Application operation: run one advanced synchronization command.
 *
 * This is the CLI's command router: it owns the argument-validity policy for the
 * advanced command line — the source-revision syntax, an editor the profiles do
 * not implement, and a declaration flag only `init` accepts — and, once the
 * arguments are accepted, dispatches to the operation that performs the command.
 * Collaborators are injected through the constructor (architecture contract C3),
 * and the returned value is the dispatched operation's own domain result: no
 * exit status, no operator copy, no stream writing (C6, P2).
 */

import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
import { EnrollDestinations } from "#application/synchronization/enroll-destinations.ts";
import type { EnrollmentRequest, SynchronizationRequest } from "#application/synchronization/requests.ts";
import { VerifyDestinations } from "#application/synchronization/verify-destinations.ts";
import { REVISION_PATTERN } from "#domain/synchronization/constants.ts";
import { EDITOR_PROFILES, isEditorProfile } from "#domain/synchronization/editor-profile.ts";
import { failed, invalid, type OperationOutcome } from "#domain/synchronization/failures.ts";

/** The operations one advanced command can dispatch to. */
export type AdvancedCommandDependencies = {
	readonly check: VerifyDestinations;
	readonly apply: ApplyCoreRevision;
	readonly enroll: EnrollDestinations;
};

/** What one advanced command was asked to do, and the arguments it was given. */
export type AdvancedRequest =
	| {
			readonly command: "check" | "apply";
			/** The typed request the command runs once its arguments are accepted. */
			readonly request: SynchronizationRequest;
			/** The editor the operator named, before the profile contract is applied. */
			readonly requestedEditor: string | undefined;
			/** Declaration arguments the operator supplied, which only `init` accepts. */
			readonly initOnlyArguments: readonly string[];
	  }
	| {
			readonly command: "init";
			readonly request: EnrollmentRequest;
			readonly requestedEditor: string | undefined;
			readonly initOnlyArguments: readonly string[];
	  };

export class RunAdvancedCommand {
	readonly #operations: AdvancedCommandDependencies;

	constructor(operations: AdvancedCommandDependencies) {
		this.#operations = operations;
	}

	async execute(request: AdvancedRequest): Promise<OperationOutcome> {
		const rejected = validate(request);
		if (rejected !== null) {
			return rejected;
		}

		switch (request.command) {
			case "check":
				return this.#operations.check.execute(request.request);
			case "apply":
				return this.#operations.apply.execute(request.request);
			case "init":
				return this.#operations.enroll.execute(request.request);
		}
	}
}

/**
 * Validate the command's arguments before a command starts.
 *
 * A malformed `--source-revision`, an editor the profiles do not implement and a
 * flag only `init` accepts are argument errors: they are reported as invalid
 * input and touch nothing.
 */
function validate(request: AdvancedRequest): OperationOutcome | null {
	if (!REVISION_PATTERN.test(request.request.sourceRevision)) {
		return failed(invalid("argument --source-revision: must be a 40-character lowercase hex string"));
	}
	const editor = request.requestedEditor;
	if (editor !== undefined && !isEditorProfile(editor)) {
		return failed(
			invalid(`argument --editor: unknown editor '${editor}' (supported: ${EDITOR_PROFILES.join(", ")})`),
		);
	}
	if (request.initOnlyArguments.length > 0) {
		return failed(invalid(`unrecognized arguments: ${request.initOnlyArguments.join(" ")}`));
	}
	return null;
}
