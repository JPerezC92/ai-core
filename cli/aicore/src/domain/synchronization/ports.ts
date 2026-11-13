/**
 * The synchronization domain's ports.
 *
 * Each port is one external capability expressed in domain types: a persisted
 * bindings document, the clearance registry, the read-only source tree, the
 * destination's files, path/layout questions, and the write-target preflight.
 * Implementations live in infrastructure; the application sees only these.
 */

import type { BindingMode, CommandName } from "./constants.ts";
import type { BindingsDocument } from "./bindings.ts";
import type { ClearanceEntry } from "./clearance.ts";
import type { SynchronizationFailure } from "./failures.ts";
import type { ReconciliationEntry } from "./reconciliation.ts";
import type { SourceCoreRead } from "./regions.ts";

/** The clearance registry, read from the source root. */
export type ClearanceLoad = {
  /** The parsed registry, or `null` when absent or unreadable. */
  readonly entries: ReadonlyMap<string, ClearanceEntry> | null;
  /** Whether the registry file exists at all. */
  readonly exists: boolean;
  /** Why a present registry was rejected, or `null` when it parsed. */
  readonly reason: string | null;
};

export interface BindingsStore {
  /** Read and validate the bindings document; `null` when absent or malformed. */
  load(path: string): Promise<BindingsDocument | null>;
  /** Write the bindings document, creating its directory when absent. */
  save(path: string, document: BindingsDocument): Promise<void>;
  /** Write the reconciliation report beside the bindings document. */
  writeReport(
    bindingsPath: string,
    entries: readonly ReconciliationEntry[],
    revision: string,
  ): Promise<void>;
}

export interface ClearanceStore {
  load(sourceRoot: string): Promise<ClearanceLoad>;
}

/** The read-only source tree. */
export interface SourceFiles {
  /** Read a source document's core; `null` when the file is absent. */
  readCore(path: string): Promise<SourceCoreRead | null>;
  /** Read a source file's bytes verbatim, without decoding. */
  readBytes(path: string): Promise<Uint8Array | null>;
  /** Read a source file's whole text, without newline translation. */
  readText(path: string): Promise<string | null>;
}

/** The destination's files. */
export interface DestinationFiles {
  readText(path: string): Promise<string | null>;
  readBytes(path: string): Promise<Uint8Array | null>;
  /** Write text, terminating every line in LF. */
  writeText(path: string, content: string): Promise<void>;
  /** Write bytes exactly as given. */
  writeBytes(path: string, content: Uint8Array): Promise<void>;
}

/** Path and layout questions about the two roots. */
export interface FilesystemLayout {
  exists(path: string): Promise<boolean>;
  isFile(path: string): Promise<boolean>;
  ensureDirectory(path: string): Promise<void>;
  /** Join a relative POSIX path onto a root path. */
  join(root: string, relative: string): string;
  /** The directory that contains `path`. */
  parent(path: string): string;
  /** Every regular file under `root`, as root-relative POSIX paths. */
  enumerateFilesUnder(root: string): Promise<readonly string[]>;
  /** The destination root runtime file's path. */
  resolveRootFile(destinationRoot: string, document: BindingsDocument): Promise<string>;
  /** The destination instruction root present on disk, or `null`. */
  detectRootFile(destinationRoot: string): Promise<string | null>;
  /** Bring the root runtime file's blocker in line with `pending`, worded for the document's editor. */
  syncBlocker(
    destinationRoot: string,
    document: BindingsDocument,
    pending: readonly string[],
  ): Promise<void>;
}

/** Everything the write-target preflight needs to know about a command. */
export type WriteTargetRequest = {
  readonly command: CommandName;
  readonly sourceRoot: string;
  readonly destinationRoot: string;
  readonly bindingsPath: string;
  readonly document: BindingsDocument;
  readonly modes: ReadonlyMap<string, BindingMode>;
  readonly newRawDestinations: ReadonlySet<string>;
};

export interface WriteTargetGuard {
  /** Return the refusal these write targets earn, or `null` when all are safe. */
  refuse(request: WriteTargetRequest): Promise<SynchronizationFailure | null>;
}
