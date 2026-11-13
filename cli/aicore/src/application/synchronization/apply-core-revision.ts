/**
 * Use case: splice each source core into its destinations and pin the revision.
 *
 * A region destination's core region is replaced and its frontmatter identity
 * keys are refreshed from the source; an unrefreshable frontmatter keeps its
 * text and is named in the result message. A declared but absent region or raw
 * target is recreated, because a declaration must not depend on when it was
 * recorded. A merge destination is never created here: only a first enrollment
 * creates one.
 *
 * Writes happen only after every destination has been classified, so a later
 * refusal cannot leave a directory or a half-applied payload behind.
 */

import {
  CLEARANCE_FILENAME,
  MODE_MERGE,
  MODE_RAW,
} from "#domain/synchronization/constants.ts";
import {
  bindingModeConflict,
  destinationDrift,
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
import { splitFrontmatter } from "#domain/synchronization/frontmatter.ts";
import { mergeTopLevel } from "#domain/synchronization/merge.ts";
import { editorMismatch, effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import {
  protectedBytes,
  renderInitFile,
  renderWithRegion,
  splitRegions,
} from "#domain/synchronization/regions.ts";
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

/** Collaborators the update needs. */
export type ApplyCoreRevisionDependencies = {
  readonly bindings: BindingsStore;
  readonly clearance: ClearanceStore;
  readonly sources: SourceFiles;
  readonly destinations: DestinationFiles;
  readonly layout: FilesystemLayout;
  readonly guard: WriteTargetGuard;
};

/** One pending text write. */
type TextWrite = {
  readonly path: string;
  readonly content: string;
};

/** One pending byte write. */
type ByteWrite = {
  readonly path: string;
  readonly content: Uint8Array;
};

export class ApplyCoreRevision {
  readonly #dependencies: ApplyCoreRevisionDependencies;

  constructor(dependencies: ApplyCoreRevisionDependencies) {
    this.#dependencies = dependencies;
  }

  async execute(request: SynchronizationRequest): Promise<OperationOutcome> {
    const { bindings, clearance: clearanceStore, sources, destinations, layout, guard } =
      this.#dependencies;

    const document = await bindings.load(request.bindingsPath);
    if (document === null) {
      return failed(invalid(`invalid bindings: ${request.bindingsPath}`));
    }

    const mismatch = editorMismatch(document.editor, request.editor);
    if (mismatch !== null) {
      return failed(mismatch);
    }
    const editor = effectiveEditor(request.editor, document.editor);

    const clearance = await readClearanceModes(
      clearanceStore,
      layout,
      request.sourceRoot,
      editor,
    );

    const refusal = await guard.refuse({
      command: "apply",
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
    if (clearance.entries !== null) {
      const relocated = destinationDrift(document, clearance.entries, clearance.destinations);
      if (relocated !== null) {
        return failed(relocated);
      }
    }

    const textWrites: TextWrite[] = [];
    const byteWrites: ByteWrite[] = [];
    const created: string[] = [];
    const notes: string[] = [];

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
          if (!(await layout.isFile(destinationPath))) {
            if (await layout.exists(destinationPath)) {
              return failed(drift(`missing destination: ${destinationPath}`));
            }
            created.push(destination);
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
          if (!(await layout.isFile(destinationPath))) {
            return failed(
              drift(
                `missing destination: ${destinationPath} ` +
                  "(merge mode cannot create it; the destination must exist)",
              ),
            );
          }
          const destinationText = await destinations.readText(destinationPath);
          if (destinationText === null) {
            return failed(drift(`missing destination: ${destinationPath}`));
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
        if (!(await layout.isFile(destinationPath))) {
          if (await layout.exists(destinationPath)) {
            return failed(drift(`missing destination: ${destinationPath}`));
          }
          textWrites.push({
            path: destinationPath,
            content: renderInitFile("", read.core, sourceFrontmatter).text,
          });
          created.push(destination);
          continue;
        }
        const destinationContent = await destinations.readText(destinationPath);
        const split = destinationContent === null ? null : splitRegions(destinationContent);
        if (split === null) {
          return failed(invalid(`invalid destination markers: ${destinationPath}`));
        }
        const rendered = renderWithRegion(split, read.core, sourceFrontmatter);
        if (rendered.skipped !== "") {
          notes.push(
            `frontmatter not refreshed: ${destinationPath} (${rendered.skipped})`,
          );
        }
        const newSplit = splitRegions(rendered.text);
        if (newSplit === null || protectedBytes(newSplit) !== protectedBytes(split)) {
          return failed(invalid(`outside-marker mismatch: ${destinationPath}`));
        }
        textWrites.push({ path: destinationPath, content: rendered.text });
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

    const pending = normalizePending(
      document.pending,
      nonRegionDestinations(document, clearance.modes),
    );
    const pinned = { ...document, coreRevision: request.sourceRevision, pending };
    await bindings.save(request.bindingsPath, pinned);
    await layout.syncBlocker(request.destinationRoot, pinned, pending);

    const parts = ["applied", ...notes];
    if (created.length > 0) {
      parts.push(`created: ${created.join(", ")}`);
    }
    return succeeded(parts.join("; "));
  }
}
