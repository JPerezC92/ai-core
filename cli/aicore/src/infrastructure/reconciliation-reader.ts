/**
 * Infrastructure: the read-only adapters a reconciliation proposal is given.
 *
 * The proposal's collaborators are supplied in one place, and each is supplied
 * under the narrow read-only port rather than the wider engine port it also
 * implements, so the operation cannot reach a writer even by accident. Nothing
 * here decides anything: it wires adapters it does not interpret.
 */

import type { BindingsReader } from "#domain/ports/bindings-reader.ts";
import type { DestinationReader } from "#domain/ports/destination-reader.ts";
import type { PathInspection } from "#domain/ports/path-inspection.ts";
import type { ClearanceStore, SourceFiles } from "#domain/synchronization/ports.ts";

import { YamlBindingsStore } from "./synchronization/bindings-store.ts";
import { JsonClearanceStore } from "./synchronization/clearance-store.ts";
import { LocalDestinationFiles } from "./synchronization/local-destination-files.ts";
import { LocalFilesystemLayout } from "./synchronization/local-filesystem-layout.ts";
import { LocalSourceFiles } from "./synchronization/local-source-files.ts";

/** The capabilities a reconciliation proposal may hold. */
export type ReconciliationReader = {
  readonly bindings: BindingsReader;
  readonly clearance: ClearanceStore;
  readonly sources: SourceFiles;
  readonly destinations: DestinationReader;
  readonly layout: PathInspection;
};

/** Build the readers with their local adapters wired in. */
export function createReconciliationReader(): ReconciliationReader {
  return {
    bindings: new YamlBindingsStore(),
    clearance: new JsonClearanceStore(),
    sources: new LocalSourceFiles(),
    destinations: new LocalDestinationFiles(),
    layout: new LocalFilesystemLayout(),
  };
}
