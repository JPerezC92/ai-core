/**
 * Integration: a reconciliation proposal over a synthetic destination.
 *
 * One behavioral concern — the proposal classifies every bound path and every
 * file a bound directory holds, states what a reconciliation would do about it,
 * and changes nothing under the destination. It is exercised through the real
 * readers over a disposable source and destination (T4), and the invariant it
 * asserts is the point of the milestone: the destination tree is byte-identical
 * before and after the proposal, including the absence of a report or blocker
 * this tool might have been tempted to write.
 *
 * One fixture states all four classes at once: a managed file, a locally modified
 * managed file, a superseded binding whose source is gone (preserved, never
 * deleted) and a superseded binding whose source still stands behind it
 * (deletable, because its bytes prove it carries nothing of its own), plus a
 * destination-owned file inside a managed directory.
 */

import { access, mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { ReconcileDestination } from "#application/reconcile-destination.ts";
import { BINDINGS_RELATIVE_PATH } from "#domain/constants.ts";
import { CLEARANCE_FILENAME } from "#domain/synchronization/constants.ts";
import { EXIT_DRIFT, renderReconciliation } from "#delivery/reporting.ts";
import { LocalFilesystemProbe } from "#infrastructure/filesystem-probe.ts";
import { createReconciliationReader } from "#infrastructure/reconciliation-reader.ts";
import { YamlBindingsStore } from "#infrastructure/synchronization/bindings-store.ts";
import { REVISION } from "#support/aicore-cli.factory.ts";
import {
  createTemporaryRoot,
  disposeTemporaryRoot,
} from "#support/disposable-root.ts";
import {
  makeBindingsDocument,
  makeClearanceText,
} from "#support/synchronization.factory.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-reconciliation-proposal-";

/** A managed source whose destination copy still matches it. */
const MANAGED_SOURCE = "assets/logo.txt";
const MANAGED_BODY = "AICore mark\n";

/** A managed source whose destination copy carries a local addition. */
const MODIFIED_SOURCE = "docs/rules.md";
const MODIFIED_BODY = "# Rules\n\nShared.\n";
const MODIFIED_DESTINATION_BODY = "# Rules\n\nShared.\n\nOur own addition.\n";

/** A second managed source, at another managed directory. */
const CURRENT_SOURCE = "skills/current/SKILL.md";
const CURRENT_BODY = "---\nname: current\n---\n\n# current\n";

/** A binding whose source left both the registry and the source tree. */
const ABSENT_SOURCE = "skills/old/SKILL.md";
const ABSENT_DESTINATION_BODY = "# old skill\n";

/** A binding whose source still stands in the tree but is no longer cleared. */
const UNCLEARED_SOURCE = "skills/legacy/notes.md";
const UNCLEARED_BODY = "legacy notes\n";

/** A destination file inside a managed directory that no binding names. */
const OWNED_PATH = "assets/local-note.txt";
const OWNED_BODY = "our own note\n";

const BOUND_PATHS: readonly (readonly [source: string, destination: string])[] = [
  [MANAGED_SOURCE, MANAGED_SOURCE],
  [MODIFIED_SOURCE, MODIFIED_SOURCE],
  [CURRENT_SOURCE, CURRENT_SOURCE],
  [ABSENT_SOURCE, ABSENT_SOURCE],
  [UNCLEARED_SOURCE, UNCLEARED_SOURCE],
];

let root: string;
let rootPrefix: string;
let sourceRoot: string;
let destinationRoot: string;

beforeEach(async () => {
  const created = await createTemporaryRoot(ROOT_PREFIX);
  root = created.root;
  rootPrefix = created.prefix;
  sourceRoot = join(root, "source");
  destinationRoot = join(root, "project-under-test");

  await writeSourceFile(MANAGED_SOURCE, MANAGED_BODY);
  await writeSourceFile(MODIFIED_SOURCE, MODIFIED_BODY);
  await writeSourceFile(CURRENT_SOURCE, CURRENT_BODY);
  await writeSourceFile(UNCLEARED_SOURCE, UNCLEARED_BODY);
  await writeFile(
    join(sourceRoot, CLEARANCE_FILENAME),
    makeClearanceText({
      [MANAGED_SOURCE]: { mode: "raw" },
      [MODIFIED_SOURCE]: { mode: "raw" },
      [CURRENT_SOURCE]: { mode: "raw" },
    }),
    "utf8",
  );

  await writeDestinationFile(MANAGED_SOURCE, MANAGED_BODY);
  await writeDestinationFile(MODIFIED_SOURCE, MODIFIED_DESTINATION_BODY);
  await writeDestinationFile(CURRENT_SOURCE, CURRENT_BODY);
  await writeDestinationFile(ABSENT_SOURCE, ABSENT_DESTINATION_BODY);
  await writeDestinationFile(UNCLEARED_SOURCE, UNCLEARED_BODY);
  await writeDestinationFile(OWNED_PATH, OWNED_BODY);

  await new YamlBindingsStore().save(
    join(destinationRoot, BINDINGS_RELATIVE_PATH),
    makeBindingsDocument({
      coreRevision: REVISION,
      editor: "opencode",
      bindings: BOUND_PATHS.map(([source, destination]) => ({
        source,
        destinations: [destination],
        declaredMode: "raw" as const,
      })),
    }),
  );
});

afterEach(async () => {
  await disposeTemporaryRoot(root, rootPrefix);
});

async function writeSourceFile(path: string, body: string): Promise<void> {
  const target = join(sourceRoot, path);
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, body, "utf8");
}

async function writeDestinationFile(path: string, body: string): Promise<void> {
  const target = join(destinationRoot, path);
  await mkdir(dirname(target), { recursive: true });
  await writeFile(target, body, "utf8");
}

/** Every file under a root, with its bytes, so "unchanged" is a comparison. */
async function snapshotTree(target: string): Promise<ReadonlyMap<string, string>> {
  const collected = new Map<string, string>();
  const walk = async (directory: string, prefix: string): Promise<void> => {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const path = prefix === "" ? entry.name : `${prefix}/${entry.name}`;
      if (entry.isDirectory()) {
        await walk(join(directory, entry.name), path);
        continue;
      }
      collected.set(path, (await readFile(join(directory, entry.name))).toString("hex"));
    }
  };
  await walk(target, "");
  return collected;
}

/** The proposal line about one destination path. */
function lineFor(stdout: readonly string[], path: string): string {
  const found = stdout.find((line) => line.includes(` ${path} — `));
  expect(found, `no proposal line names ${path}`).toBeDefined();
  return found ?? "";
}

/** Propose a destination's reconciliation the way the assembled command does. */
async function propose(): Promise<{ stdout: string[]; status: number; stderr: string[] }> {
  const proposal = await new ReconcileDestination({
    checkoutRoot: sourceRoot,
    files: new LocalFilesystemProbe(),
    ...createReconciliationReader(),
  }).execute({ target: destinationRoot });

  expect(proposal.ok).toBe(true);
  if (!proposal.ok) {
    return { stdout: [], status: -1, stderr: [proposal.failure.message] };
  }
  return renderReconciliation(proposal.value);
}

describe("the reconciliation proposal", () => {
  test("classifies every path, proposes what each needs, and writes nothing", async () => {
    const before = await snapshotTree(destinationRoot);

    const rendered = await propose();

    expect(rendered.stderr).toEqual([]);
    expect(rendered.status).toBe(EXIT_DRIFT);

    // managed: bound to a cleared source that still exists and still declares it.
    expect(lineFor(rendered.stdout, MANAGED_SOURCE)).toMatch(/^reconcile: kept\s+managed\s+/u);
    expect(lineFor(rendered.stdout, CURRENT_SOURCE)).toMatch(/^reconcile: kept\s+managed\s+/u);

    // locally modified: managed, and the destination content is no longer its source's.
    expect(lineFor(rendered.stdout, MODIFIED_SOURCE)).toMatch(
      /^reconcile: preserved\s+locally modified\s+/u,
    );

    // superseded, source gone: ownership cannot be established, so preserved.
    expect(lineFor(rendered.stdout, ABSENT_SOURCE)).toMatch(
      /^reconcile: preserved\s+superseded\s+/u,
    );
    expect(lineFor(rendered.stdout, ABSENT_SOURCE)).toContain("ownership not established");

    // superseded, source still standing and byte-identical: deletable without loss.
    expect(lineFor(rendered.stdout, UNCLEARED_SOURCE)).toMatch(
      /^reconcile: deleted\s+superseded\s+/u,
    );

    // destination-owned: inside a managed directory, backed by no source.
    expect(lineFor(rendered.stdout, OWNED_PATH)).toMatch(
      /^reconcile: kept\s+destination-owned\s+/u,
    );
    expect(rendered.stdout).toContain(
      "reconcile: managed 2, superseded 2, locally modified 1, destination-owned 1.",
    );

    // The read-only property, asserted over the whole tree rather than promised.
    const after = await snapshotTree(destinationRoot);
    expect(after).toEqual(before);
    expect([...after.keys()].some((path) => path.startsWith(".aicore/reconciliation"))).toBe(
      false,
    );
    await expect(access(join(destinationRoot, ".aicore", "reconciliation"))).rejects.toThrow();
    // A reconciliation that rewrote the destination's own bindings would have
    // dropped the stale binding instead of proposing what to do about it.
    expect(await readFile(join(destinationRoot, BINDINGS_RELATIVE_PATH), "utf8")).toContain(
      ABSENT_SOURCE,
    );
  });
});
