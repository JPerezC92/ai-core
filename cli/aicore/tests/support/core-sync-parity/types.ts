/**
 * The data model of the behavioral-parity corpus.
 *
 * The corpus is data, not assertions: every case states the synthetic fixture
 * it runs against, the command(s) it runs, and the outcome it expects. A case
 * never computes its expectation from an engine's actual behaviour, so the same
 * table can judge a different engine without a single line of it changing.
 *
 * Expected outcomes are byte-level wherever the contract fixes bytes (region,
 * raw and merge payloads, the root runtime file's blocker block). Where the
 * contract fixes a document's *schema* but not its serialization (the bindings
 * file, the reconciliation report), the expectation is the parsed document, and
 * the corpus says so in the case's provenance.
 */

import type { BindingsDocument, ReportDocument } from "./document.ts";

/** The behavioural concerns the corpus covers; one per integration spec file. */
export type Concern =
  | "region-mode"
  | "raw-mode"
  | "merge-mode"
  | "marker-contract"
  | "bindings-schema"
  | "exit-contract"
  | "safety-refusals"
  | "idempotence"
  | "binding-declarations"
  | "root-role"
  | "clearance-integrity";

/**
 * Where a case's expected outcome came from.
 *
 * `contract` cites the governing text. `reference` records behaviour the
 * contract does not spell out and that was read from the Python reference
 * engine — never contract text, and always flagged for the coordinator.
 */
export type Provenance = {
  readonly contract: readonly string[];
  readonly reference: readonly string[];
};

/** A regular file the fixture materialises, with its exact bytes. */
export type FixtureFile = {
  readonly path: string;
  readonly content: string;
};

/** A symbolic link the fixture materialises, relative to its own root. */
export type FixtureLink = {
  readonly path: string;
  readonly target: string;
};

/** A hard link the fixture materialises, from `path` to an existing `target`. */
export type FixtureHardLink = {
  readonly path: string;
  readonly target: string;
};

/** The synthetic source and destination trees one case runs against. */
export type FixtureSpec = {
  /** Files written under the source root. */
  readonly sourceFiles?: readonly FixtureFile[];
  /** Symbolic links created under the source root. */
  readonly sourceLinks?: readonly FixtureLink[];
  /** Hard links created under the source root, pointing at `target`. */
  readonly sourceHardLinks?: readonly FixtureHardLink[];
  /** Files written under the destination root. */
  readonly destinationFiles?: readonly FixtureFile[];
  /** Symbolic links created under the destination root. */
  readonly destinationLinks?: readonly FixtureLink[];
  /** Hard links created under the destination root, pointing at `target`. */
  readonly destinationHardLinks?: readonly FixtureHardLink[];
  /** Directories created under the destination root. */
  readonly destinationDirectories?: readonly string[];
  /**
   * The source's `distribution-clearance.json` text. `null` means the file is
   * absent; `""` means the file exists and is malformed.
   */
  readonly clearance?: string | null;
  /** The bindings file text. `null` means the file is absent. */
  readonly bindings?: string | null;
  /** Places the source root inside the destination root, so the roots overlap. */
  readonly nestedSourceInsideDestination?: boolean;
};

/** One command invocation inside a case. */
export type InvocationSpec = {
  readonly command: "check" | "apply" | "init";
  readonly bind?: readonly string[];
  readonly bindRaw?: readonly string[];
  readonly bindCleared?: boolean;
  readonly root?: string;
  /** Replaces the revision argument, for the argument-validation cases. */
  readonly revisionOverride?: string;
};

/**
 * What the engine's standard error must look like.
 *
 * `empty` is the contract's success shape (a successful command writes its
 * result to standard output and nothing to standard error). `exact` pins a
 * whole message. `contains` pins diagnostic *class* tokens, because the
 * reference's messages embed absolute temporary paths and cannot be compared
 * verbatim.
 */
export type StderrExpectation =
  | { readonly kind: "empty" }
  | { readonly kind: "exact"; readonly value: string }
  | { readonly kind: "contains"; readonly value: readonly string[] };

/** The observable outcome of one invocation. */
export type StepExpectation = {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: StderrExpectation;
};

/** One entry of the expected filesystem tree. */
export type TreeEntry =
  | { readonly kind: "file"; readonly path: string; readonly content: string }
  | {
      readonly kind: "blocker";
      readonly path: string;
      readonly prefix: string;
      readonly suffix: string;
      readonly bodyContains: readonly string[];
    }
  | {
      readonly kind: "jsonc";
      readonly path: string;
      readonly content: string;
      readonly mustContain?: readonly string[];
    }
  | { readonly kind: "bindings"; readonly path: string; readonly document: BindingsDocument }
  | { readonly kind: "report"; readonly path: string; readonly document: ReportDocument }
  | { readonly kind: "directory"; readonly path: string }
  | { readonly kind: "symlink"; readonly path: string; readonly target: string };

/** One case of the corpus. */
export type ParityCase = {
  readonly id: string;
  readonly concern: Concern;
  readonly title: string;
  readonly provenance: Provenance;
  readonly fixture: FixtureSpec;
  readonly steps: readonly InvocationSpec[];
  readonly expectations: readonly StepExpectation[];
  /** The expected destination tree after the last step. */
  readonly destinationTree: readonly TreeEntry[];
  /** The expected source tree after the last step; the source is read-only. */
  readonly sourceTree?: readonly TreeEntry[];
};
