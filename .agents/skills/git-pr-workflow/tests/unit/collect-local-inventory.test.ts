import { describe, expect, it } from "vitest";
import { CollectLocalInventory } from "#scripts/pr_review/application/collect_local_inventory.ts";
import { PrepareLocalSnapshot } from "#scripts/pr_review/application/prepare_local_snapshot.ts";
import type { GitInventoryPort } from "#scripts/pr_review/domain/ports.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import {
  createBody,
  createLocalDraft,
  createLocalSnapshot,
  createPaths,
  createSnapshot,
} from "#tests/support/review-fixtures.ts";

const HEAD_REVISION = "HEAD";
const ANCESTOR_COMMIT = "b".repeat(40);
const RESOLVED_BASE_COMMIT = "c".repeat(40);

/** The named defects a reader double may carry. */
type InventoryDefect =
  | "empty-range"
  | "unresolved-base"
  | "unresolved-head"
  | "merge-base-unresolved"
  | "no-paths"
  | "path-set-mismatch";

/** Stand in for the Git port and record the ranges the operation requests. */
class RecordingReader implements GitInventoryPort {
  readonly mergeBaseArguments: Array<[string, string]> = [];
  readonly commitRanges: Array<[string, string]> = [];
  readonly pathRanges: Array<[string, string]> = [];
  private readonly revisions: Map<string, string | null>;
  private readonly ancestor: string | null;
  private readonly commits: string[];
  private readonly changedPaths: string[];
  private readonly deletedPaths: string[];
  private readonly messages: Map<string, string>;
  private readonly bodies: Map<string, string>;

  constructor(options: {
    revisions: Map<string, string | null>;
    ancestor: string | null;
    commits: string[];
    changedPaths: string[];
    deletedPaths: string[];
    messages: Map<string, string>;
    bodies: Map<string, string>;
  }) {
    this.revisions = options.revisions;
    this.ancestor = options.ancestor;
    this.commits = options.commits;
    this.changedPaths = options.changedPaths;
    this.deletedPaths = options.deletedPaths;
    this.messages = options.messages;
    this.bodies = options.bodies;
  }

  resolveCommit(revision: string): string | null {
    return this.revisions.get(revision) ?? null;
  }

  mergeBase(first: string, second: string): string | null {
    this.mergeBaseArguments.push([first, second]);
    return this.ancestor;
  }

  listCommits(ancestor: string, head: string): string[] {
    this.commitRanges.push([ancestor, head]);
    return [...this.commits];
  }

  readMessage(commit: string): string {
    const message = this.messages.get(commit);
    if (message === undefined) throw new Error(`no configured message for ${commit}`);
    return message;
  }

  listChangedPaths(ancestor: string, head: string): string[] {
    this.pathRanges.push([ancestor, head]);
    return [...this.changedPaths];
  }

  listDeletedPaths(): string[] {
    return [...this.deletedPaths];
  }

  readFile(_commit: string, path: string): string {
    const body = this.bodies.get(path);
    if (body === undefined) throw new Error(`no configured body for ${path}`);
    return body;
  }
}

/** Build the port double from the shared fixtures, applying one named defect. */
function createReader(defect?: InventoryDefect): RecordingReader {
  const snapshot = createSnapshot();
  const head = snapshot.head_sha;
  const base = snapshot.base;
  const changedPaths = createPaths();
  const commit = snapshot.artifacts[2];
  const revisions = new Map<string, string | null>([
    [HEAD_REVISION, head],
    [base, RESOLVED_BASE_COMMIT],
  ]);
  let commits = [head];
  let ancestor: string | null = ANCESTOR_COMMIT;
  let deletedPaths = [changedPaths[1] ?? ""];
  const messages = new Map<string, string>();
  const bodies = new Map<string, string>();
  if (commit !== undefined) messages.set(commit.source, commit.content);
  const firstFile = snapshot.changed_files[0];
  if (firstFile !== undefined) bodies.set(firstFile.path, firstFile.content);
  if (defect === "empty-range") {
    commits = [];
  } else if (defect === "unresolved-head") {
    revisions.set(HEAD_REVISION, null);
  } else if (defect === "unresolved-base") {
    revisions.set(base, null);
  } else if (defect === "merge-base-unresolved") {
    ancestor = null;
  } else if (defect === "no-paths") {
    changedPaths.length = 0;
  } else if (defect === "path-set-mismatch") {
    deletedPaths = ["src/unlisted.py"];
  }
  return new RecordingReader({
    revisions,
    ancestor,
    commits,
    changedPaths,
    deletedPaths,
    messages,
    bodies,
  });
}

/** Build the command inputs from the shared review fixtures. */
function createRequest(): {
  prNumber: number;
  base: string;
  draft: string;
  body: string;
} {
  const snapshot = createSnapshot();
  return {
    prNumber: snapshot.pr_number,
    base: snapshot.base,
    draft: createLocalDraft(),
    body: createBody(),
  };
}

/** Run the collection operation over one reader double. */
function collect(reader: RecordingReader): unknown {
  const request = createRequest();
  return new CollectLocalInventory(reader, new PrepareLocalSnapshot()).execute(
    request.prNumber,
    request.base,
    request.draft,
    request.body,
  );
}

describe("CollectLocalInventory.execute", () => {
  it("assembles the local snapshot and retains the deleted path", () => {
    const reader = createReader();

    const result = collect(reader);

    expect(result).toEqual(createLocalSnapshot());
    const head = createSnapshot().head_sha;
    expect(reader.mergeBaseArguments).toEqual([[RESOLVED_BASE_COMMIT, head]]);
    expect(reader.commitRanges).toEqual([[ANCESTOR_COMMIT, head]]);
    expect(reader.pathRanges).toEqual([[ANCESTOR_COMMIT, head]]);
  });

  it("rejects an unresolved head, an unresolved base ref and an unresolved merge base", () => {
    for (const defect of ["unresolved-head", "unresolved-base", "merge-base-unresolved"] as const) {
      const result = collect(createReader(defect));

      expect(result).toBeInstanceOf(ReviewPreparationError);
      expect(result).toMatchObject({
        code:
          defect === "merge-base-unresolved" ? "GIT_MERGE_BASE_UNRESOLVED" : "GIT_REVISION_UNRESOLVED",
      });
    }
  });

  it("rejects an empty commit range and an empty changed path list", () => {
    const emptyRange = collect(createReader("empty-range"));
    expect(emptyRange).toBeInstanceOf(ReviewPreparationError);
    expect(emptyRange).toMatchObject({ code: "GIT_COMMIT_RANGE_EMPTY" });

    const noPaths = collect(createReader("no-paths"));
    expect(noPaths).toBeInstanceOf(ReviewPreparationError);
    expect(noPaths).toMatchObject({ code: "GIT_PATHS_EMPTY" });
  });

  it("rejects a deleted path outside the changed path inventory", () => {
    const result = collect(createReader("path-set-mismatch"));

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({ code: "SNAPSHOT_PATHS_MISMATCH" });
  });
});
