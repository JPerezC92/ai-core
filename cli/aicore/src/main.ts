/**
 * Composition root: parse the command line, wire adapters, and serialize results.
 *
 * The only place concrete infrastructure is constructed (contract C4) and the
 * only place transport encodings exist (C6, P2). Everything below depends on
 * ports.
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
import { RunAdvancedCommand } from "#application/run-advanced-command.ts";
import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import {
  EXIT_INVALID,
  EXIT_OK,
  exitStatusForFailure,
  renderAdvanced,
  renderSync,
} from "#delivery/reporting.ts";
import { ConsoleStreamWriter } from "#delivery/stream-writer.ts";
import { createCoreSyncEngine } from "#infrastructure/core-sync-engine.ts";
import { CoreSyncEngineRunner, EngineUnavailableError } from "#infrastructure/engine-runner.ts";
import { LocalFilesystemProbe } from "#infrastructure/filesystem-probe.ts";
import {
  CorruptSelectionError,
  LocalJsonSelectionStore,
} from "#infrastructure/selection-store.ts";

/** The AICore checkout root: three levels above this module's directory. */
export function checkoutRoot(): string {
  const here = dirname(fileURLToPath(import.meta.url));
  return join(here, "..", "..", "..");
}

export const USAGE = `aicore — synchronization CLI

Usage:
  pnpm aicore sync [--target <path>] [--editor <editor>] [--source-revision <40-hex>]
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

The tool never runs Git. The source revision must be supplied by the operator or
by the release owner, so Herald 📯 (Release Manager) remains the only Git executor.

Environment:
  ${REVISION_ENV_VAR}       source revision to pin when --source-revision is absent
  ${LOCAL_CONFIG_OVERRIDE_ENV_VAR}   override the operator-local selection file path

Exit status: 0 current or applied, 1 drift reported by the engine, 2 invalid input
or unavailable configuration.`;

function operatorSettings(
  environment: Readonly<Record<string, string | undefined>>,
): OperatorSettings {
  return {
    sourceRevision: environment[REVISION_ENV_VAR],
    localConfigPath: environment[LOCAL_CONFIG_OVERRIDE_ENV_VAR],
  };
}

export async function main(
  argv: readonly string[],
  environment: Readonly<Record<string, string | undefined>> = process.env,
): Promise<number> {
  const writer = new ConsoleStreamWriter();

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
  const engine = new CoreSyncEngineRunner(createCoreSyncEngine());

  try {
    if (invocation.kind === "advanced") {
      const outcome = await new RunAdvancedCommand(engine).execute({
        command: invocation.command,
        passthrough: invocation.passthrough,
      });
      const rendered = renderAdvanced(outcome);

      writer.writeStdout(rendered.stdout);
      writer.writeStderr(rendered.stderr);
      return rendered.status;
    }

    const result = await new SynchronizeDestination({
      checkoutRoot: root,
      settings,
      engine,
      files: new LocalFilesystemProbe(),
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
    if (error instanceof EngineUnavailableError) {
      writer.writeStderr([error.message]);
      return EXIT_INVALID;
    }
    if (error instanceof CorruptSelectionError) {
      writer.writeStderr([error.message]);
      return EXIT_INVALID;
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
