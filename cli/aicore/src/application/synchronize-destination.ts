/**
 * Application operation: synchronize one destination.
 *
 * One business operation, one `execute()`, collaborators injected through the
 * constructor (architecture contract C3). It returns a typed domain result or a
 * typed failure and performs no delivery: no exit status, no operator copy, no
 * stream writing (C6, P2).
 *
 * Every safety decision stays inside the engine, which this operation delegates
 * to without weakening.
 */

import {
  BINDINGS_RELATIVE_PATH,
  type SupportedEditor,
} from "#domain/constants.ts";
import { fail, succeed, type Result } from "#domain/failures.ts";
import type { SynchronizeOutcome } from "#domain/outcomes.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { SelectionStore } from "#domain/ports/selection-store.ts";
import type { OperatorSettings } from "#domain/settings.ts";
import { resolveEditor, resolveRevision } from "#domain/rules/invocation.ts";
import {
  resolveDestinationEditor,
  resolveDestinationPath,
  selectionToSave,
} from "#domain/rules/selection.ts";

export type SynchronizeRequest = {
  readonly target: string | undefined;
  readonly editor: string | undefined;
  readonly revision: string | undefined;
};

export type SynchronizeDependencies = {
  readonly checkoutRoot: string;
  readonly settings: OperatorSettings;
  readonly engine: EngineRunner;
  readonly files: FilesystemProbe;
  readonly selections: SelectionStore;
};

export class SynchronizeDestination {
  readonly #dependencies: SynchronizeDependencies;

  constructor(dependencies: SynchronizeDependencies) {
    this.#dependencies = dependencies;
  }

  async execute(request: SynchronizeRequest): Promise<Result<SynchronizeOutcome>> {
    const { engine, files, selections, settings, checkoutRoot } = this.#dependencies;

    // Editor and revision syntax are resolved before any filesystem question, so
    // an unsupported editor is reported even when the destination is unset.
    const requestedEditorResult = this.#resolveRequestedEditor(request.editor);
    if (!requestedEditorResult.ok) {
      return requestedEditorResult;
    }
    const requestedEditor = requestedEditorResult.value;

    const revisionResult = resolveRevision(request.revision, settings.sourceRevision);
    if (!revisionResult.ok) {
      return revisionResult;
    }
    const revision = revisionResult.value;

    const saved = await selections.read();

    const destinationResult = resolveDestinationPath(request.target, saved);
    if (!destinationResult.ok) {
      return destinationResult;
    }
    const destination = files.resolve(destinationResult.value);

    if (!(await files.isDirectory(destination))) {
      return fail(
        "invalid-destination",
        `destination is not a directory: ${destination}. Nothing was written.`,
      );
    }
    if (files.isInside(checkoutRoot, destination)) {
      return fail(
        "invalid-destination",
        `destination is inside the AICore checkout: ${destination}. ` +
          "The source tree is read-only to synchronization; choose a separate project.",
      );
    }

    const bindingsPath = `${destination}/${BINDINGS_RELATIVE_PATH}`;
    const destinationIsBound = await files.isFile(bindingsPath);

    const editorResult = resolveDestinationEditor(
      requestedEditor,
      saved,
      destination,
      destinationIsBound,
    );
    if (!editorResult.ok) {
      return editorResult;
    }
    const editor: SupportedEditor = editorResult.value;

    const engineArguments = [
      "--source",
      checkoutRoot,
      "--destination",
      destination,
      "--bindings",
      bindingsPath,
      "--source-revision",
      revision,
    ];

    const writeRun = destinationIsBound
      ? await engine.run("apply", engineArguments)
      : await engine.run("init", [...engineArguments, "--bind-cleared"]);

    if (writeRun.status !== 0) {
      return succeed({
        destination,
        editor,
        enrolled: !destinationIsBound,
        runs: [writeRun],
        current: false,
      });
    }

    const selection = selectionToSave(request.target, requestedEditor, destination, editor);
    if (selection !== undefined) {
      await selections.write(selection);
    }

    const verificationRun = await engine.run("check", engineArguments);

    return succeed({
      destination,
      editor,
      enrolled: !destinationIsBound,
      runs: [writeRun, verificationRun],
      current: verificationRun.status === 0,
    });
  }

  #resolveRequestedEditor(
    requested: string | undefined,
  ): Result<SupportedEditor | undefined> {
    if (requested === undefined) {
      return succeed(undefined);
    }
    const resolved = resolveEditor(requested);
    return resolved.ok ? succeed(resolved.value) : resolved;
  }
}
