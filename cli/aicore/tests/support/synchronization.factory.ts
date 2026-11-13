/**
 * Shared test data for the synchronization engine's ports and documents.
 *
 * Contract T15: test data comes from a factory, never from inline literals
 * scattered across modules. The documents here are domain data — a bindings
 * document, a command request and a clearance registry — so a test states the
 * one value it varies and takes the rest from here.
 *
 * Ports are not built here: a test that doubles a port constructs its own
 * `MockProxy`, so no mock is shared between cases.
 */

import type {
  EnrollmentRequest,
  SynchronizationRequest,
} from "#application/synchronization/requests.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import { parseClearanceDocument } from "#domain/synchronization/clearance.ts";
import { CLEARANCE_SCHEMA } from "#domain/synchronization/constants.ts";
import type { ClearanceLoad } from "#domain/synchronization/ports.ts";

import { REVISION } from "./aicore-cli.factory.ts";

/** The source root a run reads from. */
export const SOURCE_ROOT = "G:/projects/ai-core";

/** The destination root a run writes to. */
export const SYNCHRONIZATION_DESTINATION_ROOT = "G:/projects/destination";

/** The bindings document's path inside that destination. */
export const SYNCHRONIZATION_BINDINGS_PATH = `${SYNCHRONIZATION_DESTINATION_ROOT}/.aicore/core.yaml`;

/** The one cleared source the default documents describe. */
export const BOUND_SOURCE = "AGENTS.md";

/** A bindings document binding `AGENTS.md` to itself under one editor. */
export function makeBindingsDocument(
  overrides: Partial<BindingsDocument> = {},
): BindingsDocument {
  return {
    coreRevision: REVISION,
    root: null,
    editor: "opencode",
    bindings: [
      { source: BOUND_SOURCE, destinations: [BOUND_SOURCE], declaredMode: "region" },
    ],
    pending: [],
    ...overrides,
  };
}

/** One command's inputs, naming the roots and the revision a run needs. */
export function makeSynchronizationRequest(
  overrides: Partial<SynchronizationRequest> = {},
): SynchronizationRequest {
  return {
    sourceRoot: SOURCE_ROOT,
    destinationRoot: SYNCHRONIZATION_DESTINATION_ROOT,
    bindingsPath: SYNCHRONIZATION_BINDINGS_PATH,
    sourceRevision: REVISION,
    editor: undefined,
    ...overrides,
  };
}

/**
 * A clearance registry's text for the given cleared records.
 *
 * The document wrapper and its schema label are the factory's, so a case states
 * only the records under test and the real reader parses what a source root
 * actually holds.
 */
export function makeClearanceText(
  cleared: Readonly<Record<string, Readonly<Record<string, unknown>>>>,
): string {
  return `${JSON.stringify({ schema: CLEARANCE_SCHEMA, cleared }, null, 2)}\n`;
}

/**
 * A clearance store's load result for the given cleared records.
 *
 * A use-case case supplies the parsed registry its port would hand it, built
 * from the same factory text an integration case writes to a source root, so
 * there is one clearance document shape in the suite rather than a hand-built
 * second one.
 */
export function makeClearanceLoad(
  cleared: Readonly<Record<string, Readonly<Record<string, unknown>>>>,
): ClearanceLoad {
  const parsed = parseClearanceDocument(JSON.parse(makeClearanceText(cleared)));
  if (!parsed.ok) {
    throw new Error(`factory clearance text is unreadable: ${parsed.reason}`);
  }
  return { entries: parsed.entries, exists: true, reason: null };
}

/** The destination the registry declares for `BOUND_SOURCE` once it has moved. */
export const RELOCATED_BOUND_DESTINATION = ".opencode/AGENTS.md";

/**
 * A clearance load whose `BOUND_SOURCE` record declares another destination than
 * the bindings record holds.
 *
 * A record that names its destinations names every editor, so the delivery the
 * `opencode` enrollment receives is the one that moved.
 */
export function makeRelocatedClearanceLoad(): ClearanceLoad {
  return makeClearanceLoad({
    [BOUND_SOURCE]: {
      mode: "region",
      editors: {
        opencode: { destination: RELOCATED_BOUND_DESTINATION },
        cursor: { destination: `cursor/${BOUND_SOURCE}` },
      },
    },
  });
}

/** One enrollment's inputs: a synchronization request with no declarations. */
export function makeEnrollmentRequest(
  overrides: Partial<EnrollmentRequest> = {},
): EnrollmentRequest {
  return {
    ...makeSynchronizationRequest(),
    regionDeclarations: [],
    rawDeclarations: [],
    bindCleared: false,
    rootOverride: null,
    ...overrides,
  };
}
