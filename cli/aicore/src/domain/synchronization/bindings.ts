/**
 * The bindings document: its schema rule, its declarations, and the pending rule.
 *
 * The document's *schema* is the contract's; its YAML spelling is not, so the
 * representation mapping lives at the infrastructure boundary and this module
 * sees plain parsed data. A binding carries no persisted mode in the contract —
 * the source clearance owns the distribution mode — so `declaredMode` is only
 * the in-memory hint a persisted `mode:` key or an `init` declaration supplies,
 * and it is dropped when the document is written again.
 */

import {
  BINDING_MODES,
  type BindingMode,
  MODE_MERGE,
  MODE_RAW,
  MODE_REGION,
  REVISION_PATTERN,
  SCHEMA_VERSION,
} from "./constants.ts";
import { type SynchronizationFailure, invalid } from "./failures.ts";
import { isSafeRelativePath } from "./paths.ts";

/** One source file and the destination files that mirror it. */
export type BindingEntry = {
  readonly source: string;
  readonly destinations: readonly string[];
  /** The declaration hint; never persisted. */
  readonly declaredMode: BindingMode;
};

/** The bindings document. */
export type BindingsDocument = {
  readonly coreRevision: string | null;
  readonly root: string | null;
  readonly bindings: readonly BindingEntry[];
  readonly pending: readonly string[];
};

/** The document's persisted shape, as plain data for the representation writer. */
export type BindingsRecord = {
  readonly schema: number;
  readonly core_revision: string | null;
  readonly root?: string;
  readonly bindings: readonly {
    readonly source: string;
    readonly destinations: readonly string[];
  }[];
  readonly pending: readonly string[];
};

/**
 * Validate a parsed bindings document.
 *
 * `null` reports a malformed document: a wrong schema label, an unsafe or
 * duplicated path, an invalid revision, or a shape the schema does not allow.
 * Validation happens before any filesystem operation uses a path from it.
 */
export function parseBindingsDocument(data: unknown): BindingsDocument | null {
  if (!isRecord(data) || data["schema"] !== SCHEMA_VERSION) {
    return null;
  }
  const revision = readRevision(data["core_revision"]);
  if (revision === undefined) {
    return null;
  }
  const rawBindings = data["bindings"];
  if (!Array.isArray(rawBindings)) {
    return null;
  }
  const seen = new Set<string>();
  const bindings: BindingEntry[] = [];
  for (const rawEntry of rawBindings) {
    const entry = readBindingEntry(rawEntry, seen);
    if (entry === null) {
      return null;
    }
    bindings.push(entry);
  }
  const root = readOptionalPath(data["root"]);
  if (root === undefined) {
    return null;
  }
  const rawPending = data["pending"] ?? [];
  if (!Array.isArray(rawPending) || !rawPending.every((item) => typeof item === "string")) {
    return null;
  }
  return {
    coreRevision: revision,
    root,
    bindings,
    pending: rawPending as string[],
  };
}

/** Project a validated document onto its persisted shape. */
export function bindingsRecord(document: BindingsDocument): BindingsRecord {
  const record: BindingsRecord = {
    schema: SCHEMA_VERSION,
    core_revision: document.coreRevision,
    ...(document.root === null ? {} : { root: document.root }),
    bindings: document.bindings.map((entry) => ({
      source: entry.source,
      destinations: [...entry.destinations],
    })),
    pending: [...document.pending],
  };
  return record;
}

/** The outcome of merging `init` binding declarations into a document. */
export type DeclarationMerge = {
  readonly document: BindingsDocument;
  /** Destinations this run declared raw, for the implicit-root guard. */
  readonly newRawDestinations: ReadonlySet<string>;
  readonly failure: SynchronizationFailure | null;
};

/**
 * Merge `--bind` and `--bind-raw` declarations into a document before preflight.
 *
 * A repeatable declaration is idempotent for an identical mapping; a destination
 * already mapped to a different source is a metadata conflict.
 */
export function withInitDeclarations(
  document: BindingsDocument,
  regionSpecs: readonly string[],
  rawSpecs: readonly string[],
): DeclarationMerge {
  const destinationSources = new Map<string, string>();
  for (const entry of document.bindings) {
    for (const destination of entry.destinations) {
      destinationSources.set(destination, entry.source);
    }
  }
  const bindings = document.bindings.map((entry) => ({ ...entry }));
  const newRawDestinations = new Set<string>();
  const declarations: readonly (readonly [string, BindingMode])[] = [
    ...regionSpecs.map((spec) => [spec, MODE_REGION] as const),
    ...rawSpecs.map((spec) => [spec, MODE_RAW] as const),
  ];

  for (const [spec, mode] of declarations) {
    const declaration = parseInitBindingSpec(spec);
    if (declaration === null) {
      return {
        document,
        newRawDestinations: new Set<string>(),
        failure: invalid(`invalid init binding: malformed or unsafe binding declaration: ${spec}`),
      };
    }
    const existingSource = destinationSources.get(declaration.destination);
    if (existingSource !== undefined) {
      if (existingSource !== declaration.source) {
        return {
          document,
          newRawDestinations: new Set<string>(),
          failure: invalid(
            `invalid init binding: destination mapping conflicts for ${declaration.destination}`,
          ),
        };
      }
      continue;
    }
    const index = bindings.findIndex((entry) => entry.source === declaration.source);
    if (index === -1) {
      bindings.push({
        source: declaration.source,
        destinations: [declaration.destination],
        declaredMode: mode,
      });
    } else {
      const found = bindings[index];
      if (found === undefined) {
        continue;
      }
      bindings[index] = {
        source: found.source,
        destinations: [...found.destinations, declaration.destination],
        declaredMode: found.declaredMode,
      };
    }
    destinationSources.set(declaration.destination, declaration.source);
    if (mode === MODE_RAW) {
      newRawDestinations.add(declaration.destination);
    }
  }
  return {
    document: { ...document, bindings },
    newRawDestinations,
    failure: null,
  };
}

/** Parse one exact `SOURCE=DEST` declaration with safe paths. */
export function parseInitBindingSpec(
  spec: string,
): { readonly source: string; readonly destination: string } | null {
  const separator = spec.indexOf("=");
  if (separator === -1 || spec.indexOf("=", separator + 1) !== -1) {
    return null;
  }
  const source = spec.slice(0, separator);
  const destination = spec.slice(separator + 1);
  if (!isSafeRelativePath(source) || !isSafeRelativePath(destination)) {
    return null;
  }
  return { source, destination };
}

/** Look up a bound source's operational mode in the expanded mode map. */
export function sourceMode(
  source: string,
  modes: ReadonlyMap<string, BindingMode>,
): BindingMode | undefined {
  return modes.get(source);
}

/**
 * Return the raw-declaration conflict for an entry, if it has one.
 *
 * A persisted or declared `raw` whose source clearance is not `raw` fails closed:
 * the declaration is a leftover hint, and silence would let the wrong mode win.
 */
export function bindingModeConflict(
  entry: BindingEntry,
  modes: ReadonlyMap<string, BindingMode>,
): SynchronizationFailure | null {
  const mode = modes.get(entry.source);
  if (entry.declaredMode === MODE_RAW && mode !== undefined && mode !== MODE_RAW) {
    return invalid(
      `binding mode 'raw' conflicts with source clearance mode '${mode}' for ${entry.source}`,
    );
  }
  return null;
}

/** Return the destinations whose source is declared raw or merge in clearance. */
export function nonRegionDestinations(
  document: BindingsDocument,
  modes: ReadonlyMap<string, BindingMode>,
): ReadonlySet<string> {
  const destinations = new Set<string>();
  for (const entry of document.bindings) {
    const mode = modes.get(entry.source);
    if (mode === MODE_RAW || mode === MODE_MERGE) {
      for (const destination of entry.destinations) {
        destinations.add(destination);
      }
    }
  }
  return destinations;
}

/** Return the pending paths that still have a region to reconcile. */
export function normalizePending(
  pending: readonly string[],
  nonRegion: ReadonlySet<string>,
): readonly string[] {
  return pending.filter((path) => !nonRegion.has(path));
}

/** Return distinct bound sources absent from clearance, in document order. */
export function unclearedSources(
  document: BindingsDocument,
  cleared: ReadonlySet<string>,
): readonly string[] {
  const uncleared: string[] = [];
  const seen = new Set<string>();
  for (const entry of document.bindings) {
    if (!cleared.has(entry.source) && !seen.has(entry.source)) {
      seen.add(entry.source);
      uncleared.push(entry.source);
    }
  }
  return uncleared;
}

function readBindingEntry(
  rawEntry: unknown,
  seenDestinations: Set<string>,
): BindingEntry | null {
  if (!isRecord(rawEntry)) {
    return null;
  }
  const source = rawEntry["source"];
  const destinations = rawEntry["destinations"];
  const rawMode = rawEntry["mode"] ?? MODE_REGION;
  if (typeof source !== "string" || !isSafeRelativePath(source)) {
    return null;
  }
  if (!Array.isArray(destinations) || destinations.length === 0) {
    return null;
  }
  const mode = BINDING_MODES.find((candidate) => candidate === rawMode);
  if (mode === undefined) {
    return null;
  }
  const resolved: string[] = [];
  for (const destination of destinations) {
    if (typeof destination !== "string" || !isSafeRelativePath(destination)) {
      return null;
    }
    if (seenDestinations.has(destination)) {
      return null;
    }
    seenDestinations.add(destination);
    resolved.push(destination);
  }
  return { source, destinations: resolved, declaredMode: mode };
}

/** Return the pinned revision, `null` for none, or `undefined` when invalid. */
function readRevision(value: unknown): string | null | undefined {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value !== "string" || !REVISION_PATTERN.test(value)) {
    return undefined;
  }
  return value;
}

/** Return the optional root path, `null` for none, or `undefined` when invalid. */
function readOptionalPath(value: unknown): string | null | undefined {
  if (value === null || value === undefined) {
    return null;
  }
  if (typeof value !== "string" || !isSafeRelativePath(value)) {
    return undefined;
  }
  return value;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
