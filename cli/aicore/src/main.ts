/**
 * Composition root: parse the command line, wire adapters, and serialize results.
 *
 * The only place concrete infrastructure is constructed (contract C4) and the
 * only place transport encodings exist (C6, P2). Everything below depends on
 * ports or on the application operations it is composed from.
 */

import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
	ADVANCED_COMMANDS,
	LOCAL_CONFIG_OVERRIDE_ENV_VAR,
	REVISION_ENV_VAR,
	SUPPORTED_EDITORS,
} from "#domain/constants.ts";
import { parseInvocation } from "#domain/rules/invocation.ts";
import type { OperatorSettings } from "#domain/settings.ts";
import type {
	BindingsStore,
	ClearanceStore,
	DestinationFiles,
	FilesystemLayout,
	SourceFiles,
	WriteTargetGuard,
} from "#domain/synchronization/ports.ts";
import { RunAdvancedCommand, type AdvancedCommandDependencies } from "#application/run-advanced-command.ts";
import { ReconcileDestination } from "#application/reconcile-destination.ts";
import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
import { EnrollDestinations } from "#application/synchronization/enroll-destinations.ts";
import { VerifyDestinations } from "#application/synchronization/verify-destinations.ts";
import { toCommandArguments } from "#delivery/command-arguments.ts";
import {
	EXIT_INVALID,
	EXIT_OK,
	exitStatusForFailure,
	renderReconciliation,
	renderReport,
	renderSync,
} from "#delivery/reporting.ts";
import { ConsoleStreamWriter, type StreamWriter } from "#delivery/stream-writer.ts";
import {
	reportFileSystemFailure,
	reportMalformed,
	reportOutcome,
	reportSynchronizationFailure,
	type SynchronizationReport,
} from "#delivery/synchronization-report.ts";
import { RunDestinationProbe } from "#delivery/run-destination.ts";
import { LocalFilesystemProbe } from "#infrastructure/filesystem-probe.ts";
import { createReconciliationReader } from "#infrastructure/reconciliation-reader.ts";
import { CorruptSelectionError, LocalJsonSelectionStore } from "#infrastructure/selection-store.ts";
import { YamlBindingsStore } from "#infrastructure/synchronization/bindings-store.ts";
import { JsonClearanceStore } from "#infrastructure/synchronization/clearance-store.ts";
import { LocalDestinationFiles } from "#infrastructure/synchronization/local-destination-files.ts";
import { isFileSystemError } from "#infrastructure/synchronization/local-files.ts";
import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import { LocalSourceFiles } from "#infrastructure/synchronization/local-source-files.ts";
import { LocalWriteTargetGuard } from "#infrastructure/synchronization/write-target-guard.ts";

/** The AICore checkout root: three levels above this module's directory. */
export function checkoutRoot(): string {
	const here = dirname(fileURLToPath(import.meta.url));
	return join(here, "..", "..", "..");
}

export const USAGE = `aicore — synchronization CLI

Usage:
  pnpm aicore sync [--target <path>] [--editor <editor>] [--source-revision <40-hex>]
  pnpm aicore reconcile --target <path>
  pnpm aicore check --source <dir> --destination <dir> --bindings <file> --source-revision <40-hex>
  pnpm aicore apply --source <dir> --destination <dir> --bindings <file> --source-revision <40-hex>
  pnpm aicore init  --source <dir> --destination <dir> --bindings <file> --source-revision <40-hex>

Options for sync:
  --target <path>          destination project; remembered for later runs.
                           Relative --target paths are resolved against the
                           current working directory.
  --editor <editor>        editor to distribute for (${SUPPORTED_EDITORS.join(", ")}).
                           Each editor receives the shared content and its own agent
                           directory; only an editor with a merge target receives the
                           project configuration.
  --source-revision <hex>  source revision to pin, or set $${REVISION_ENV_VAR}
  -h, --help               show this message

A destination's editor is fixed by its enrollment; changing it is a
destination-owned migration, not something a synchronization performs.

Advanced commands (${ADVANCED_COMMANDS.join(", ")}) pass their arguments straight
to the existing synchronization engine and keep its exit status unchanged.

reconcile is not a synchronization. It reads --target's bindings, the source
clearance registry and the source tree, and prints a proposal: every bound path
and every file a bound directory holds, classified as managed, superseded,
locally modified or destination-owned, with what a reconciliation would do about
it. It writes nothing under the destination — no bindings, no report, no blocker
— and a path whose ownership cannot be established is reported as preserved
rather than proposed for deletion.

The tool never runs Git. The source revision must be supplied by the operator or
by the release owner, so Herald 📯 (Release Manager) remains the only Git executor.

Environment:
  ${REVISION_ENV_VAR}       source revision to pin when --source-revision is absent
  ${LOCAL_CONFIG_OVERRIDE_ENV_VAR}   override the operator-local selection file path

Exit status: 0 current, applied, or a proposal with nothing for the destination
owner to do; 1 drift reported by the engine, or a proposal the destination owner
must act on; 2 invalid input or unavailable configuration.`;

/**
 * The synchronization adapters one command runs over.
 *
 * One explicit data-only record: the application operations declare the ports
 * they need, and the composition root supplies the same adapters to each of
 * them.
 */
type SynchronizationDependencies = {
	readonly bindings: BindingsStore;
	readonly clearance: ClearanceStore;
	readonly sources: SourceFiles;
	readonly destinations: DestinationFiles;
	readonly layout: FilesystemLayout;
	readonly guard: WriteTargetGuard;
};

function operatorSettings(environment: Readonly<Record<string, string | undefined>>): OperatorSettings {
	return {
		sourceRevision: environment[REVISION_ENV_VAR],
		localConfigPath: environment[LOCAL_CONFIG_OVERRIDE_ENV_VAR],
	};
}

/** Build the three synchronization operations over the local adapters. */
function createSynchronizationOperations(): AdvancedCommandDependencies {
	const layout = new LocalFilesystemLayout();
	const dependencies: SynchronizationDependencies = {
		bindings: new YamlBindingsStore(),
		clearance: new JsonClearanceStore(),
		sources: new LocalSourceFiles(),
		destinations: new LocalDestinationFiles(),
		layout,
		guard: new LocalWriteTargetGuard(layout),
	};

	return {
		check: new VerifyDestinations(dependencies),
		apply: new ApplyCoreRevision(dependencies),
		enroll: new EnrollDestinations(dependencies),
	};
}

/** Write one reported result and return its exit status. */
function writeReport(writer: StreamWriter, report: SynchronizationReport): number {
	const rendered = renderReport(report);
	writer.writeStdout(rendered.stdout);
	writer.writeStderr(rendered.stderr);
	return rendered.status;
}

export async function main(
	argv: readonly string[],
	environment: Readonly<Record<string, string | undefined>> = process.env,
	writer: StreamWriter = new ConsoleStreamWriter(),
): Promise<number> {
	const parsed = parseInvocation(argv);
	if (!parsed.ok) {
		writer.writeStderr([parsed.failure.message]);
		return exitStatusForFailure(parsed.failure);
	}

	const invocation = parsed.value;
	if (invocation.kind === "help" || invocation.help) {
		writer.writeStdout([USAGE]);
		return EXIT_OK;
	}

	const root = checkoutRoot();
	const settings = operatorSettings(environment);
	const operations = createSynchronizationOperations();
	// The destination a `sync` run resolved, so a boundary failure it raises can be
	// rendered the way a failed write always was. Reconcile builds its own probe.
	const syncFiles = new RunDestinationProbe(new LocalFilesystemProbe());

	try {
		if (invocation.kind === "reconcile") {
			const proposal = await new ReconcileDestination({
				checkoutRoot: root,
				files: new LocalFilesystemProbe(),
				...createReconciliationReader(),
			}).execute({ target: invocation.target });

			if (!proposal.ok) {
				writer.writeStderr([proposal.failure.message]);
				return exitStatusForFailure(proposal.failure);
			}

			const rendered = renderReconciliation(proposal.value);
			writer.writeStdout(rendered.stdout);
			writer.writeStderr(rendered.stderr);
			return rendered.status;
		}

		if (invocation.kind === "advanced") {
			const arguments_ = toCommandArguments(invocation.command, invocation.passthrough);
			if (!arguments_.ok) {
				return writeReport(writer, reportMalformed(arguments_.message));
			}

			const outcome = await new RunAdvancedCommand(operations).execute(arguments_);
			return writeReport(writer, reportOutcome(outcome));
		}

		const result = await new SynchronizeDestination({
			checkoutRoot: root,
			settings,
			...operations,
			files: syncFiles,
			selections: new LocalJsonSelectionStore(root, settings.localConfigPath),
		}).execute({
			target: invocation.target,
			editor: invocation.editor,
			revision: invocation.revision,
		});

		if (!result.ok) {
			writer.writeStderr([result.failure.message]);
			return exitStatusForFailure(result.failure);
		}

		const rendered = renderSync(result.value);
		writer.writeStdout(rendered.stdout);
		writer.writeStderr(rendered.stderr);
		return rendered.status;
	} catch (error) {
		if (error instanceof CorruptSelectionError) {
			writer.writeStderr([error.message]);
			return EXIT_INVALID;
		}
		// A genuine filesystem condition is a synchronization result at the
		// published exit contract: the destination is not current, and a later
		// `check` is required. A programming exception stays an exception, because
		// a fabricated drift report would claim drift that never happened (C5).
		if (isFileSystemError(error)) {
			const reason = error instanceof Error ? error.message : String(error);
			// A `sync` run reports the destination it failed on the way a failed write
			// always did; a command that resolved no destination keeps the bare
			// diagnostic.
			const destination = syncFiles.destination;
			return writeReport(
				writer,
				destination === null
					? reportFileSystemFailure(reason)
					: reportSynchronizationFailure(destination, reason),
			);
		}
		throw error;
	}
}

function invokedDirectly(): boolean {
	const entry = process.argv[1];
	if (entry === undefined) {
		return false;
	}
	return resolve(entry) === resolve(fileURLToPath(import.meta.url));
}

if (invokedDirectly()) {
	process.exitCode = await main(process.argv.slice(2));
}
