/**
 * Application operation: propose one destination's reconciliation, read-only.
 *
 * One business operation, one `execute()` (contract C3). It reads the
 * destination's bindings, the source clearance registry and the source tree,
 * classifies every path the bindings mention and every file the bindings'
 * destination directories hold, and returns the proposal as a typed domain
 * result. It holds no write capability at all: its ports can read a bindings
 * document, a source, a destination file and a path, and nothing else, so
 * "writes nothing under the destination" is a property of the operation's
 * collaborators rather than a promise in its prose.
 *
 * The classification itself is the domain's rule; this operation establishes the
 * facts the rule needs — what the registry declares, what the source holds, what
 * the destination holds, and whether those contents still agree — and never
 * decides a class of its own.
 */

import { readClearanceModes } from "#application/synchronization/clearance-modes.ts";
import { projectName } from "#application/synchronization/project-name.ts";
import { BINDINGS_RELATIVE_PATH } from "#domain/constants.ts";
import { fail, succeed, type Result } from "#domain/failures.ts";
import type { BindingsReader } from "#domain/ports/bindings-reader.ts";
import type { DestinationReader } from "#domain/ports/destination-reader.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { PathInspection } from "#domain/ports/path-inspection.ts";
import {
  CLEARANCE_FILENAME,
  MODE_MERGE,
  MODE_RAW,
  MODE_REGION,
  type BindingMode,
} from "#domain/synchronization/constants.ts";
import { effectiveEditor } from "#domain/synchronization/editor-profile.ts";
import { isMerged } from "#domain/synchronization/merge.ts";
import { parentDirectory } from "#domain/synchronization/paths.ts";
import type { ClearanceStore, SourceFiles } from "#domain/synchronization/ports.ts";
import {
  classifyBoundPath,
  destinationOwnedEntry,
  proposalRequiresAction,
  type BoundPathObservation,
  type ProposalEntry,
  type ReconciliationProposal,
} from "#domain/synchronization/reconciliation-proposal.ts";
import { splitRegions } from "#domain/synchronization/regions.ts";

/** What the proposal is asked about. */
export type ReconcileRequest = {
  /** The destination project to inspect. */
  readonly target: string;
};

/** Collaborators the proposal needs. Every one of them is read-only. */
export type ReconcileDependencies = {
  /** The AICore checkout the sources and the clearance registry are read from. */
  readonly checkoutRoot: string;
  readonly files: FilesystemProbe;
  readonly bindings: BindingsReader;
  readonly clearance: ClearanceStore;
  readonly sources: SourceFiles;
  readonly destinations: DestinationReader;
  readonly layout: PathInspection;
};

/** One bound path, with everything the inspection needs to look it up. */
type BoundPath = {
  readonly destinationRoot: string;
  readonly source: string;
  readonly destinationPath: string;
  readonly mode: BindingMode | null;
  readonly declaredDestination: string | null;
};

export class ReconcileDestination {
  readonly #dependencies: ReconcileDependencies;

  constructor(dependencies: ReconcileDependencies) {
    this.#dependencies = dependencies;
  }

  async execute(request: ReconcileRequest): Promise<Result<ReconciliationProposal>> {
    const { checkoutRoot, files, bindings, clearance, layout } = this.#dependencies;

    const destinationRoot = files.resolve(request.target);
    if (!(await files.isDirectory(destinationRoot))) {
      return fail(
        "invalid-destination",
        `destination is not a directory: ${destinationRoot}. Nothing was read.`,
      );
    }

    const bindingsPath = layout.join(destinationRoot, BINDINGS_RELATIVE_PATH);
    const document = await bindings.load(bindingsPath);
    if (document === null) {
      // Absent and malformed are different answers: an unenrolled destination has
      // nothing to reconcile, a written one that cannot be read is a defect.
      return (await files.isFile(bindingsPath))
        ? fail("invalid-bindings", `invalid bindings: ${bindingsPath}. Nothing was proposed.`)
        : fail(
            "unavailable-configuration",
            `no bindings: ${bindingsPath}. The destination is not enrolled, so there is ` +
              "nothing to reconcile.",
          );
    }

    const editor = effectiveEditor(undefined, document.editor);
    const expanded = await readClearanceModes(clearance, layout, checkoutRoot, editor);

    const clearancePath = layout.join(checkoutRoot, CLEARANCE_FILENAME);
    if (!expanded.exists) {
      return fail(
        "unavailable-configuration",
        `missing clearance file: ${clearancePath}. Nothing was proposed.`,
      );
    }
    if (expanded.entries === null) {
      const reason = expanded.reason === null ? "" : `: ${expanded.reason}`;
      return fail(
        "unavailable-configuration",
        `unreadable clearance file: ${clearancePath}${reason}. Nothing was proposed.`,
      );
    }

    const boundPaths = new Set<string>();
    const bound: ProposalEntry[] = [];
    for (const binding of document.bindings) {
      for (const destinationPath of binding.destinations) {
        boundPaths.add(destinationPath);
        bound.push(
          classifyBoundPath(
            await this.#observe({
              destinationRoot,
              source: binding.source,
              destinationPath,
              mode: expanded.modes.get(binding.source) ?? null,
              declaredDestination: expanded.destinations.get(binding.source) ?? null,
            }),
          ),
        );
      }
    }

    const entries = [...bound, ...(await this.#destinationOwned(destinationRoot, boundPaths))];
    entries.sort((left, right) =>
      left.path < right.path ? -1 : left.path > right.path ? 1 : 0,
    );

    return succeed({
      destination: destinationRoot,
      entries,
      requiresAction: proposalRequiresAction(entries),
    });
  }

  /** Establish what one bound path's inspection shows. */
  async #observe(bound: BoundPath): Promise<BoundPathObservation> {
    const { checkoutRoot, layout } = this.#dependencies;

    const sourcePath = layout.join(checkoutRoot, bound.source);
    const destinationPath = layout.join(bound.destinationRoot, bound.destinationPath);
    const sourcePresent = await layout.isFile(sourcePath);
    const destinationPresent = await layout.isFile(destinationPath);
    const bothPresent = sourcePresent && destinationPresent;

    const identical = bothPresent ? await this.#sameBytes(sourcePath, destinationPath) : false;
    const matchesSource = bothPresent
      ? await this.#matchesSource(bound.mode, sourcePath, destinationPath, bound.destinationRoot, identical)
      : false;

    return {
      source: bound.source,
      destination: bound.destinationPath,
      mode: bound.mode,
      declaredDestination: bound.declaredDestination,
      sourcePresent,
      destinationPresent,
      matchesSource,
      identical,
    };
  }

  /** Return whether the destination holds exactly the source file's bytes. */
  async #sameBytes(sourcePath: string, destinationPath: string): Promise<boolean> {
    const { sources, destinations } = this.#dependencies;
    const sourceBytes = await sources.readBytes(sourcePath);
    const destinationBytes = await destinations.readBytes(destinationPath);
    if (sourceBytes === null || destinationBytes === null) {
      return false;
    }
    return sameBytes(sourceBytes, destinationBytes);
  }

  /**
   * Return whether the destination holds what its source declares.
   *
   * The question is asked in the mode the binding is cleared under, which is the
   * same comparison the destination's own verification makes: a raw payload byte
   * for byte, a merged document key for key, and a region payload by its core
   * region — a refreshed identity key is not a local modification.
   *
   * `false` covers both "it differs" and "it cannot be read well enough to say",
   * because a proposal must not turn an unreadable document into a claim.
   */
  async #matchesSource(
    mode: BindingMode | null,
    sourcePath: string,
    destinationPath: string,
    destinationRoot: string,
    identical: boolean,
  ): Promise<boolean> {
    if (mode === MODE_RAW) {
      return identical;
    }
    if (mode === MODE_MERGE) {
      return await this.#mergeMatches(sourcePath, destinationPath, destinationRoot);
    }
    if (mode === MODE_REGION) {
      return await this.#regionMatches(sourcePath, destinationPath);
    }
    return false;
  }

  /** Return whether the destination carries this source's core region. */
  async #regionMatches(sourcePath: string, destinationPath: string): Promise<boolean> {
    const { sources, destinations } = this.#dependencies;
    const read = await sources.readCore(sourcePath);
    if (read === null || read.kind === "malformed") {
      return false;
    }
    const destinationText = await destinations.readText(destinationPath);
    if (destinationText === null) {
      return false;
    }
    const split = splitRegions(destinationText);
    return split !== null && split.region === read.core;
  }

  /** Return whether every source top-level key is present in the destination. */
  async #mergeMatches(
    sourcePath: string,
    destinationPath: string,
    destinationRoot: string,
  ): Promise<boolean> {
    const { sources, destinations } = this.#dependencies;
    const sourceText = await sources.readText(sourcePath);
    const destinationText = await destinations.readText(destinationPath);
    if (sourceText === null || destinationText === null) {
      return false;
    }
    return isMerged(sourceText, destinationText, projectName(destinationRoot)) === true;
  }

  /**
   * The files the destination holds in a directory its bindings manage, with no
   * binding naming them.
   *
   * Only the directories the bindings actually deliver into are inspected, and
   * the destination root itself is never one of them: the destination owns its
   * own project, and a proposal does not claim it. A path with a source
   * counterpart is a bound destination by construction — the registry expanded
   * it — so "no binding names it" is the same question as "no source stands
   * behind it".
   */
  async #destinationOwned(
    destinationRoot: string,
    boundPaths: ReadonlySet<string>,
  ): Promise<ProposalEntry[]> {
    const { layout } = this.#dependencies;

    const managedRoots = new Set<string>();
    for (const path of boundPaths) {
      const parent = parentDirectory(path);
      if (parent !== "") {
        managedRoots.add(parent);
      }
    }

    const owned = new Map<string, ProposalEntry>();
    for (const root of managedRoots) {
      for (const relative of await layout.enumerateFilesUnder(layout.join(destinationRoot, root))) {
        const path = `${root}/${relative}`;
        if (boundPaths.has(path) || owned.has(path)) {
          continue;
        }
        owned.set(path, destinationOwnedEntry(path));
      }
    }
    return [...owned.values()];
  }
}

/** Return whether two byte sequences are equal. */
function sameBytes(left: Uint8Array, right: Uint8Array): boolean {
  if (left.length !== right.length) {
    return false;
  }
  return left.every((byte, index) => byte === right[index]);
}
