/**
 * Use case: enroll markerless destinations and refresh already-marked ones.
 *
 * Enrollment is the only command that creates a merge target, and only when this
 * run newly binds it and it is absent: every later `init`, and `apply`, report a
 * missing merge destination as drift. A created or recreated region target takes
 * the source's frontmatter, the source core, and an empty project region, so a
 * declaration does not depend on when it was recorded. A newly enrolled or
 * rewritten region destination is recorded in `pending` and in the reconciliation
 * report; raw and merge destinations are non-region and record neither.
 *
 * An already-bound source whose clearance record now declares another
 * destination is the drift `apply` and `check` refuse, refused here before any
 * write: enrollment never moves a destination, and never reports a diverged
 * binding as initialized.
 */

import {
  ACTION_INITIALIZED,
  ACTION_REFRESHED,
  CLEARANCE_FILENAME,
  MODE_MERGE,
  MODE_RAW,
  MODE_REGION,
  ROLE_ROOT,
} from "#domain/synchronization/constants.ts";
import {
  bindingModeConflict,
  destinationDrift,
  nonRegionDestinations,
  normalizePending,
  parseInitBindingSpec,
  unclearedSources,
  withInitDeclarations,
} from "#domain/synchronization/bindings.ts";
import {
  drift,
  failed,
  invalid,
  succeeded,
  type OperationOutcome,
  type SynchronizationFailure,
} from "#domain/synchronization/failures.ts";
import { splitFrontmatter } from "#domain/synchronization/frontmatter.ts";
import { mergeTopLevel } from "#domain/synchronization/merge.ts";
import { hasExactCoreMarkerLines } from "#domain/synchronization/markers.ts";
import type { ReconciliationEntry } from "#domain/synchronization/reconciliation.ts";
import { protectedBytes, renderInitFile, renderWithRegion, splitRegions } from "#domain/synchronization/regions.ts";
import { editorMismatch, effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import type { BindingMode } from "#domain/synchronization/constants.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { ClearanceEntry } from "#domain/synchronization/clearance.ts";
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
import type { EnrollmentRequest } from "./requests.ts";

/** Collaborators enrollment needs. */
export type EnrollDestinationsDependencies = {
  readonly bindings: BindingsStore;
  readonly clearance: ClearanceStore;
  readonly sources: SourceFiles;
  readonly destinations: DestinationFiles;
  readonly layout: FilesystemLayout;
  readonly guard: WriteTargetGuard;
};

type TextWrite = { readonly path: string; readonly content: string };
type ByteWrite = { readonly path: string; readonly content: Uint8Array };

type BulkEnrollment = {
  readonly document: BindingsDocument;
  readonly newRawDestinations: ReadonlySet<string>;
  readonly newMergeDestinations: ReadonlySet<string>;
};

export class EnrollDestinations {
  readonly #dependencies: EnrollDestinationsDependencies;

  constructor(dependencies: EnrollDestinationsDependencies) {
    this.#dependencies = dependencies;
  }

  async execute(request: EnrollmentRequest): Promise<OperationOutcome> {
    const { bindings, clearance: clearanceStore, sources, destinations, layout, guard } =
      this.#dependencies;

    const loaded = await bindings.load(request.bindingsPath);
    if (loaded === null && !request.bindCleared) {
      return failed(invalid(`invalid bindings: ${request.bindingsPath}`));
    }
    const base: BindingsDocument = loaded ?? {
      coreRevision: request.sourceRevision,
      root: null,
      editor: null,
      bindings: [],
      pending: [],
    };

    // A destination with no bindings file is not enrolled for any editor yet, so
    // this enrollment chooses one; an enrolled destination keeps the editor it
    // was enrolled for.
    const mismatch = loaded === null ? null : editorMismatch(base.editor, request.editor);
    if (mismatch !== null) {
      return failed(mismatch);
    }
    const editor = effectiveEditor(request.editor, base.editor);

    const declared = withInitDeclarations(
      base,
      request.regionDeclarations,
      request.rawDeclarations,
    );
    if (declared.failure !== null) {
      return failed(declared.failure);
    }

    const clearance = await readClearanceModes(
      clearanceStore,
      layout,
      request.sourceRoot,
      editor,
    );

    const bulk = request.bindCleared && clearance.entries !== null
      ? await this.#bulkEnroll(
          declared.document,
          request,
          clearance.entries,
          clearance.modes,
          clearance.destinations,
          layout,
        )
      : null;
    if (bulk !== null && "failure" in bulk) {
      return failed(bulk.failure);
    }
    const document = bulk === null ? declared.document : bulk.document;
    const newRawDestinations = new Set<string>([
      ...declared.newRawDestinations,
      ...(bulk === null ? [] : bulk.newRawDestinations),
    ]);
    const newMergeDestinations = bulk === null ? new Set<string>() : bulk.newMergeDestinations;

    const refusal = await guard.refuse({
      command: "init",
      sourceRoot: request.sourceRoot,
      destinationRoot: request.destinationRoot,
      bindingsPath: request.bindingsPath,
      document,
      modes: clearance.modes,
      newRawDestinations,
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

    for (const [spec, declaredMode] of [
      ...request.rawDeclarations.map((value) => [value, MODE_RAW] as const),
      ...request.regionDeclarations.map((value) => [value, MODE_REGION] as const),
    ]) {
      const parsed = parseInitBindingSpec(spec);
      if (parsed === null) {
        continue;
      }
      const actual = clearance.modes.get(parsed.source);
      if (actual !== undefined && actual !== declaredMode) {
        return failed(
          invalid(
            `declared ${declaredMode} for ${parsed.source} conflicts with source clearance mode '${actual}'`,
          ),
        );
      }
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
    // Same refusal, at the same position, as `apply` and `check`: an already-bound
    // source whose record now declares another destination is drift, not a state
    // enrollment silently delivers. Nothing is written, because the changed
    // destination is the destination owner's migration.
    const relocated = destinationDrift(
      document,
      clearance.entries,
      clearance.destinations,
    );
    if (relocated !== null) {
      return failed(relocated);
    }

    const textWrites: TextWrite[] = [];
    const byteWrites: ByteWrite[] = [];
    const reportEntries: ReconciliationEntry[] = [];
    const notes: string[] = [];
    let pending: readonly string[] = normalizePending(
      document.pending,
      nonRegionDestinations(document, clearance.modes),
    );
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
            if (await layout.exists(destinationPath)) {
              return failed(drift(`missing destination: ${destinationPath}`));
            }
            byteWrites.push({ path: destinationPath, content: sourceBytes });
            continue;
          }
          if (equalBytes(destinationBytes, sourceBytes)) {
            continue;
          }
          byteWrites.push({ path: destinationPath, content: sourceBytes });
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
          const destinationText = await destinations.readText(destinationPath);
          if (destinationText === null) {
            if (!newMergeDestinations.has(destination) || (await layout.exists(destinationPath))) {
              return failed(
                drift(
                  `missing destination: ${destinationPath} ` +
                    "(merge mode cannot create it; the destination must exist)",
                ),
              );
            }
            const created = mergeTopLevel(
              sourceText,
              "{}",
              projectName(request.destinationRoot),
            );
            if (created === null) {
              return failed(invalid(`invalid JSONC: ${sourcePath}`));
            }
            textWrites.push({ path: destinationPath, content: created });
            continue;
          }
          const mergedText = mergeTopLevel(
            sourceText,
            destinationText,
            projectName(request.destinationRoot),
          );
          if (mergedText === null) {
            return failed(invalid(`invalid JSONC: ${destinationPath}`));
          }
          if (mergedText !== destinationText) {
            textWrites.push({ path: destinationPath, content: mergedText });
          }
        }
        continue;
      }

      const read = await sources.readCore(sourcePath);
      if (read === null) {
        return failed(drift(`missing source: ${sourcePath}`));
      }
      if (read.kind === "malformed") {
        return failed(invalid(`invalid source markers: ${sourcePath}`));
      }
      const sourceText = await sources.readText(sourcePath);
      const sourceFrontmatter =
        sourceText === null ? "" : splitFrontmatter(sourceText).frontmatter;

      for (const destination of entry.destinations) {
        const destinationPath = layout.join(request.destinationRoot, destination);
        const destinationContent = await destinations.readText(destinationPath);
        if (destinationContent === null) {
          if (await layout.exists(destinationPath)) {
            return failed(drift(`missing destination: ${destinationPath}`));
          }
          textWrites.push({
            path: destinationPath,
            content: renderInitFile("", read.core, sourceFrontmatter).text,
          });
          reportEntries.push({ destination, source: entry.source, action: ACTION_INITIALIZED });
          pending = appendOnce(pending, destination);
          continue;
        }
        const split = splitRegions(destinationContent);
        if (split === null) {
          if (hasExactCoreMarkerLines(destinationContent)) {
            return failed(invalid(`invalid destination markers: ${destinationPath}`));
          }
          const rendered = renderInitFile(destinationContent, read.core, sourceFrontmatter);
          if (rendered.skipped !== "") {
            notes.push(`frontmatter not refreshed: ${destinationPath} (${rendered.skipped})`);
          }
          textWrites.push({ path: destinationPath, content: rendered.text });
          reportEntries.push({ destination, source: entry.source, action: ACTION_INITIALIZED });
          pending = appendOnce(pending, destination);
          continue;
        }
        const rendered = renderWithRegion(split, read.core, sourceFrontmatter);
        if (rendered.skipped !== "") {
          notes.push(`frontmatter not refreshed: ${destinationPath} (${rendered.skipped})`);
        }
        const newSplit = splitRegions(rendered.text);
        if (newSplit === null || protectedBytes(newSplit) !== protectedBytes(split)) {
          return failed(invalid(`outside-marker mismatch: ${destinationPath}`));
        }
        if (rendered.text === destinationContent) {
          continue;
        }
        textWrites.push({ path: destinationPath, content: rendered.text });
        if (newSplit.region === split.region) {
          continue;
        }
        reportEntries.push({ destination, source: entry.source, action: ACTION_REFRESHED });
        pending = appendOnce(pending, destination);
      }
    }

    for (const write of textWrites) {
      await layout.ensureDirectory(layout.parent(write.path));
      await destinations.writeText(write.path, write.content);
    }
    for (const write of byteWrites) {
      await layout.ensureDirectory(layout.parent(write.path));
      await destinations.writeBytes(write.path, write.content);
    }

    if (reportEntries.length > 0) {
      await bindings.writeReport(request.bindingsPath, reportEntries, request.sourceRevision);
    }

    const pinned: BindingsDocument = {
      ...document,
      coreRevision: request.sourceRevision,
      pending,
      editor,
    };
    await bindings.save(request.bindingsPath, pinned);
    await layout.syncBlocker(request.destinationRoot, pinned, pending);

    return succeeded(["initialized", ...notes].join("; "));
  }

  /**
   * Enroll every cleared source that is not already bound.
   *
   * A directory root's expansion supplies the mode each file takes and the
   * destination the editor receives it at; the root-role source maps to the
   * destination instruction root, and destinations this run discovers absent
   * become the creation set.
   */
  async #bulkEnroll(
    document: BindingsDocument,
    request: EnrollmentRequest,
    entries: ReadonlyMap<string, ClearanceEntry>,
    modes: ReadonlyMap<string, BindingMode>,
    destinations: ReadonlyMap<string, string>,
    layout: FilesystemLayout,
  ): Promise<BulkEnrollment | { readonly failure: SynchronizationFailure }> {
    const bindings = document.bindings.map((entry) => ({ ...entry }));
    const bound = new Set(bindings.map((entry) => entry.source));
    let rootDestination = document.root;
    let rootSource: string | null = null;

    for (const [source, entry] of entries) {
      if (entry.kind !== "file" || entry.role !== ROLE_ROOT) {
        continue;
      }
      rootSource = source;
      const existing = bindings.find((candidate) => candidate.source === source);
      if (existing !== undefined) {
        rootDestination = existing.destinations[0] ?? null;
      } else if (request.rootOverride !== null) {
        rootDestination = request.rootOverride;
      } else {
        rootDestination = await layout.detectRootFile(request.destinationRoot);
      }
      if (rootDestination === null) {
        return { failure: drift("destination instruction root not found; pass --root") };
      }
    }

    const newRawDestinations = new Set<string>();
    const newMergeDestinations = new Set<string>();
    for (const [source, mode] of modes) {
      if (bound.has(source)) {
        continue;
      }
      const destination =
        source === rootSource && rootDestination !== null
          ? rootDestination
          : (destinations.get(source) ?? source);
      bindings.push({ source, destinations: [destination], declaredMode: mode });
      bound.add(source);
      if (!(await layout.exists(layout.join(request.destinationRoot, destination)))) {
        if (mode === MODE_RAW) {
          newRawDestinations.add(destination);
        } else if (mode === MODE_MERGE) {
          newMergeDestinations.add(destination);
        }
      }
    }

    return {
      document: { ...document, bindings, root: rootDestination },
      newRawDestinations,
      newMergeDestinations,
    };
  }
}

function appendOnce(pending: readonly string[], path: string): readonly string[] {
  return pending.includes(path) ? pending : [...pending, path];
}

function equalBytes(left: Uint8Array, right: Uint8Array): boolean {
  if (left.length !== right.length) {
    return false;
  }
  return left.every((byte, index) => byte === right[index]);
}
