/**
 * Use case: verify every destination against the pinned source revision.
 *
 * Read-only apart from the root runtime file's reconciliation blocker, which
 * `check` synchronizes so a destination cannot be reported current while its
 * outstanding reconciliation is invisible. The blocker is synced before the
 * revision and payload comparisons, and every comparison stops at the first
 * difference: one drift report per run is the operator contract.
 */

import {
  CLEARANCE_FILENAME,
  MODE_MERGE,
  MODE_RAW,
} from "#domain/synchronization/constants.ts";
import {
  bindingModeConflict,
  nonRegionDestinations,
  normalizePending,
  unclearedSources,
} from "#domain/synchronization/bindings.ts";
import {
  drift,
  failed,
  invalid,
  succeeded,
  type OperationOutcome,
} from "#domain/synchronization/failures.ts";
import { isMerged } from "#domain/synchronization/merge.ts";
import { frontmatterIsCurrent, splitFrontmatter } from "#domain/synchronization/frontmatter.ts";
import { splitRegions } from "#domain/synchronization/regions.ts";
import type {
  BindingsStore,
  ClearanceStore,
  DestinationFiles,
  FilesystemLayout,
  SourceFiles,
  WriteTargetGuard,
} from "#domain/synchronization/ports.ts";

import { invalidClearance, readClearanceModes } from "./clearance-modes.ts";
import { projectName } from "./project-name.ts";
import type { SynchronizationRequest } from "./requests.ts";

/** Collaborators the verification needs. */
export type VerifyDestinationsDependencies = {
  readonly bindings: BindingsStore;
  readonly clearance: ClearanceStore;
  readonly sources: SourceFiles;
  readonly destinations: DestinationFiles;
  readonly layout: FilesystemLayout;
  readonly guard: WriteTargetGuard;
};

export class VerifyDestinations {
  readonly #dependencies: VerifyDestinationsDependencies;

  constructor(dependencies: VerifyDestinationsDependencies) {
    this.#dependencies = dependencies;
  }

  async execute(request: SynchronizationRequest): Promise<OperationOutcome> {
    const { bindings, clearance: clearanceStore, sources, destinations, layout, guard } =
      this.#dependencies;

    const document = await bindings.load(request.bindingsPath);
    if (document === null) {
      return failed(invalid(`invalid bindings: ${request.bindingsPath}`));
    }

    const clearance = await readClearanceModes(clearanceStore, layout, request.sourceRoot);

    const refusal = await guard.refuse({
      command: "check",
      sourceRoot: request.sourceRoot,
      destinationRoot: request.destinationRoot,
      bindingsPath: request.bindingsPath,
      document,
      modes: clearance.modes,
      newRawDestinations: new Set<string>(),
    });
    if (refusal !== null) {
      return failed(refusal);
    }

    const clearancePath = layout.join(request.sourceRoot, CLEARANCE_FILENAME);
    if (!clearance.exists) {
      return failed(drift(`missing clearance file: ${clearancePath}`));
    }
    if (clearance.entries === null) {
      return failed(invalidClearance(clearancePath, clearance));
    }

    for (const entry of document.bindings) {
      const conflict = bindingModeConflict(entry, clearance.modes);
      if (conflict !== null) {
        return failed(conflict);
      }
    }
    const uncleared = unclearedSources(document, new Set(clearance.modes.keys()));
    if (uncleared.length > 0) {
      return failed(drift(`source not cleared for distribution: ${uncleared.join(", ")}`));
    }

    const sourceCores = new Map<string, string>();
    const sourceFrontmatters = new Map<string, string>();
    for (const entry of document.bindings) {
      const mode = clearance.modes.get(entry.source);
      if (mode === MODE_RAW || mode === MODE_MERGE) {
        continue;
      }
      const sourcePath = layout.join(request.sourceRoot, entry.source);
      const read = await sources.readCore(sourcePath);
      if (read === null) {
        return failed(drift(`missing source: ${sourcePath}`));
      }
      if (read.kind === "malformed") {
        return failed(invalid(`invalid source markers: ${sourcePath}`));
      }
      sourceCores.set(entry.source, read.core);
      const text = await sources.readText(sourcePath);
      sourceFrontmatters.set(
        entry.source,
        text === null ? "" : splitFrontmatter(text).frontmatter,
      );
    }

    const nonRegion = nonRegionDestinations(document, clearance.modes);
    const stalePending = document.pending.filter((path) => nonRegion.has(path));
    await layout.syncBlocker(
      request.destinationRoot,
      document,
      normalizePending(document.pending, nonRegion),
    );

    if (stalePending.length > 0) {
      return failed(
        drift(
          "stale raw-bound pending paths cannot be reconciled: " +
            `${stalePending.join(", ")}; run apply or init to normalize the stale binding state`,
        ),
      );
    }

    if (document.coreRevision !== request.sourceRevision) {
      return failed(drift("revision drift: bindings revision does not match source"));
    }

    for (const entry of document.bindings) {
      const mode = clearance.modes.get(entry.source);
      const sourcePath = layout.join(request.sourceRoot, entry.source);
      if (mode === MODE_RAW) {
        const sourceBytes = await sources.readBytes(sourcePath);
        if (sourceBytes === null) {
          return failed(drift(`missing source: ${sourcePath}`));
        }
        for (const destination of entry.destinations) {
          const destinationPath = layout.join(request.destinationRoot, destination);
          const destinationBytes = await destinations.readBytes(destinationPath);
          if (destinationBytes === null) {
            return failed(drift(`missing destination: ${destinationPath}`));
          }
          if (!sameBytes(destinationBytes, sourceBytes)) {
            return failed(drift(`raw drift: ${destinationPath}`));
          }
        }
        continue;
      }
      if (mode === MODE_MERGE) {
        const sourceText = await sources.readText(sourcePath);
        if (sourceText === null) {
          return failed(drift(`missing source: ${sourcePath}`));
        }
        for (const destination of entry.destinations) {
          const destinationPath = layout.join(request.destinationRoot, destination);
          if (!(await layout.isFile(destinationPath))) {
            return failed(drift(`missing destination: ${destinationPath}`));
          }
          const destinationText = await destinations.readText(destinationPath);
          if (destinationText === null) {
            return failed(drift(`missing destination: ${destinationPath}`));
          }
          const merged = isMerged(sourceText, destinationText, projectName(request.destinationRoot));
          if (merged === null) {
            return failed(invalid(`invalid JSONC: ${destinationPath}`));
          }
          if (!merged) {
            return failed(drift(`merge drift: ${destinationPath}`));
          }
        }
        continue;
      }
      const sourceCore = sourceCores.get(entry.source) ?? "";
      const sourceFrontmatter = sourceFrontmatters.get(entry.source) ?? "";
      for (const destination of entry.destinations) {
        const destinationPath = layout.join(request.destinationRoot, destination);
        if (!(await layout.isFile(destinationPath))) {
          return failed(drift(`missing destination: ${destinationPath}`));
        }
        const destinationContent = await destinations.readText(destinationPath);
        const split = destinationContent === null ? null : splitRegions(destinationContent);
        if (split === null) {
          return failed(invalid(`invalid destination markers: ${destinationPath}`));
        }
        if (split.region !== sourceCore) {
          return failed(drift(`region drift: ${destinationPath}`));
        }
        const destinationFrontmatter = splitFrontmatter(split.before).frontmatter;
        if (!frontmatterIsCurrent(destinationFrontmatter, sourceFrontmatter)) {
          return failed(drift(`frontmatter drift: ${destinationPath}`));
        }
      }
    }

    if (document.pending.length > 0) {
      return failed(drift("pending changes: destination is not current"));
    }
    return succeeded("current");
  }
}

function sameBytes(left: Uint8Array, right: Uint8Array): boolean {
  if (left.length !== right.length) {
    return false;
  }
  return left.every((byte, index) => byte === right[index]);
}
