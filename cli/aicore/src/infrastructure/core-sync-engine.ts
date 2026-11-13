/**
 * The TypeScript synchronization engine: its single entry point.
 *
 * This is the composition root. It validates the command line, constructs the
 * local adapters, delegates to the requested use case, and serializes the
 * domain's outcome onto the operator's channels. No business rule lives here: a
 * command either runs one use case or is rejected before one starts.
 */

import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
import { EnrollDestinations } from "#application/synchronization/enroll-destinations.ts";
import type { EnrollmentRequest, SynchronizationRequest } from "#application/synchronization/requests.ts";
import { VerifyDestinations } from "#application/synchronization/verify-destinations.ts";
import { reportFileSystemFailure, reportMalformed, reportOutcome } from "#delivery/synchronization-report.ts";
import type { SynchronizationReport } from "#delivery/synchronization-report.ts";
import { REVISION_PATTERN, type CommandName } from "#domain/synchronization/constants.ts";
import {
  EDITOR_PROFILES,
  type EditorProfile,
  isEditorProfile,
} from "#domain/synchronization/editor-profile.ts";
import type { OperationOutcome } from "#domain/synchronization/failures.ts";

import { YamlBindingsStore } from "./synchronization/bindings-store.ts";
import { JsonClearanceStore } from "./synchronization/clearance-store.ts";
import { LocalDestinationFiles } from "./synchronization/local-destination-files.ts";
import { isFileSystemError } from "./synchronization/local-files.ts";
import { LocalFilesystemLayout } from "./synchronization/local-filesystem-layout.ts";
import { LocalSourceFiles } from "./synchronization/local-source-files.ts";
import { LocalWriteTargetGuard } from "./synchronization/write-target-guard.ts";

/** One command against the two roots. */
export type CoreSyncEngineRequest = {
  readonly command: CommandName;
  readonly sourceRoot: string;
  readonly destinationRoot: string;
  readonly bindingsPath: string;
  readonly sourceRevision: string;
  readonly bind?: readonly string[] | undefined;
  readonly bindRaw?: readonly string[] | undefined;
  readonly bindCleared?: boolean | undefined;
  readonly root?: string | undefined;
  /** The editor profile the run acts for; absent leaves the destination's own. */
  readonly editor?: string | undefined;
};

/** What one command reported. */
export type CoreSyncEngineOutcome = {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
};

/** The engine's own contract: identity plus one command per call. */
export type CoreSyncEngine = {
  readonly id: string;
  run(request: CoreSyncEngineRequest): Promise<CoreSyncEngineOutcome>;
};

/** Build the engine with its local adapters wired in. */
export function createCoreSyncEngine(): CoreSyncEngine {
  const layout = new LocalFilesystemLayout();
  const dependencies = {
    bindings: new YamlBindingsStore(),
    clearance: new JsonClearanceStore(),
    sources: new LocalSourceFiles(),
    destinations: new LocalDestinationFiles(),
    layout,
    guard: new LocalWriteTargetGuard(layout),
  };

  return {
    id: "typescript",
    async run(request: CoreSyncEngineRequest): Promise<CoreSyncEngineOutcome> {
      const rejected = validate(request);
      if (rejected !== null) {
        return rejected;
      }
      const outcome = await execute(dependencies, request).catch((error: unknown) => {
        // Only a genuine filesystem condition is a synchronization result. A
        // programming exception stays an exception: fabricating a business
        // outcome from it would report drift that never happened (C5).
        if (!isFileSystemError(error)) {
          throw error;
        }
        return reportFileSystemFailure(
          error instanceof Error ? error.message : String(error),
        );
      });
      return outcome;
    },
  };
}

/** Run the requested command against the supplied roots. */
async function execute(
  dependencies: ConstructorParameters<typeof VerifyDestinations>[0],
  request: CoreSyncEngineRequest,
): Promise<SynchronizationReport> {
  const base: SynchronizationRequest = {
    sourceRoot: request.sourceRoot,
    destinationRoot: request.destinationRoot,
    bindingsPath: request.bindingsPath,
    sourceRevision: request.sourceRevision,
    editor: requestedEditor(request),
  };
  let outcome: OperationOutcome;
  switch (request.command) {
    case "check":
      outcome = await new VerifyDestinations(dependencies).execute(base);
      break;
    case "apply":
      outcome = await new ApplyCoreRevision(dependencies).execute(base);
      break;
    case "init": {
      const enrollment: EnrollmentRequest = {
        ...base,
        regionDeclarations: request.bind ?? [],
        rawDeclarations: request.bindRaw ?? [],
        bindCleared: request.bindCleared ?? false,
        rootOverride: request.root ?? null,
      };
      outcome = await new EnrollDestinations(dependencies).execute(enrollment);
      break;
    }
  }
  return reportOutcome(outcome);
}

/**
 * The requested editor profile.
 *
 * The command line is validated before a command starts, so an editor that
 * reaches this point is one the engine implements; the fallback keeps the
 * request honest if that ever stops being true.
 */
function requestedEditor(request: CoreSyncEngineRequest): EditorProfile | undefined {
  const editor = request.editor;
  if (editor === undefined) {
    return undefined;
  }
  return isEditorProfile(editor) ? editor : undefined;
}

/**
 * Validate the command line before a command starts.
 *
 * A malformed `--source-revision`, an unknown `--editor` and a flag only `init`
 * accepts are argument errors: they exit `2` and touch nothing.
 */
function validate(request: CoreSyncEngineRequest): SynchronizationReport | null {
  if (!REVISION_PATTERN.test(request.sourceRevision)) {
    return reportMalformed(
      "argument --source-revision: must be a 40-character lowercase hex string",
    );
  }
  if (request.editor !== undefined && !isEditorProfile(request.editor)) {
    return reportMalformed(
      `argument --editor: unknown editor '${request.editor}' (supported: ${EDITOR_PROFILES.join(", ")})`,
    );
  }
  if (request.command !== "init") {
    const unsupported: string[] = [];
    if ((request.bind ?? []).length > 0) {
      unsupported.push("--bind");
    }
    if ((request.bindRaw ?? []).length > 0) {
      unsupported.push("--bind-raw");
    }
    if (request.bindCleared === true) {
      unsupported.push("--bind-cleared");
    }
    if (request.root !== undefined) {
      unsupported.push("--root");
    }
    if (unsupported.length > 0) {
      return reportMalformed(`unrecognized arguments: ${unsupported.join(" ")}`);
    }
  }
  return null;
}
