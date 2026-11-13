/**
 * Integration: a reconciliation proposal for a destination that needs no action.
 *
 * One behavioral concern — a destination whose every bound path is *managed* and
 * still carries its source, and which holds no unbound file inside a managed
 * directory, is reported as needing nothing from its owner. That is the whole
 * point of the proposal's exit status: `kept` is the only action that means "no
 * one has to decide or act", so this suite asserts the ok status and the line
 * that says it, and rejects every other classification by name.
 *
 * The drift path — locally modified, superseded, destination-owned — is the
 * sibling module's concern; here the fixture is deliberately the other end of the
 * same rule, and the read-only property is asserted over the whole destination
 * tree rather than promised.
 */

import { access, mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { ReconcileDestination } from "#application/reconcile-destination.ts";
import { BINDINGS_RELATIVE_PATH } from "#domain/constants.ts";
import type { ReconciliationProposal } from "#domain/synchronization/reconciliation-proposal.ts";
import { CLEARANCE_FILENAME } from "#domain/synchronization/constants.ts";
import { EXIT_OK, renderReconciliation } from "#delivery/reporting.ts";
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
const ROOT_PREFIX = "aicore-cli-reconciliation-no-drift-";

/** A managed source whose destination copy still matches it. */
const MANAGED_SOURCE = "assets/logo.txt";
const MANAGED_BODY = "AICore mark\n";

/** A second managed source, in a directory of its own. */
const RULES_SOURCE = "docs/rules.md";
const RULES_BODY = "# Rules\n\nShared.\n";

/** A third managed source, one directory deeper. */
const CURRENT_SOURCE = "skills/current/SKILL.md";
const CURRENT_BODY = "---\nname: current\n---\n\n# current\n";

/** Every bound path is managed and current in this fixture. */
const BOUND_PATHS: readonly (readonly [source: string, destination: string, body: string])[] = [
  [MANAGED_SOURCE, MANAGED_SOURCE, MANAGED_BODY],
  [RULES_SOURCE, RULES_SOURCE, RULES_BODY],
  [CURRENT_SOURCE, CURRENT_SOURCE, CURRENT_BODY],
];

/** The class counts a proposal with nothing to report prints. */
const NO_ACTION_COUNTS = `reconcile: managed ${BOUND_PATHS.length}, superseded 0, ` +
  "locally modified 0, destination-owned 0.";

/** The sentence the ok status exists to support. */
const NO_ACTION_LINE = "reconcile: nothing requires the destination owner's action.";

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

  for (const [source, , body] of BOUND_PATHS) {
    await writeSourceFile(source, body);
    await writeDestinationFile(source, body);
  }

  await writeFile(
    join(sourceRoot, CLEARANCE_FILENAME),
    makeClearanceText(
      Object.fromEntries(
        BOUND_PATHS.map(([source]) => [source, { mode: "raw" as const }]),
      ),
    ),
    "utf8",
  );

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
async function propose(): Promise<{
  proposal: ReconciliationProposal;
  stdout: string[];
  status: number;
  stderr: string[];
}> {
  const outcome = await new ReconcileDestination({
    checkoutRoot: sourceRoot,
    files: new LocalFilesystemProbe(),
    ...createReconciliationReader(),
  }).execute({ target: destinationRoot });

  expect(outcome.ok).toBe(true);
  if (!outcome.ok) {
    return {
      proposal: { destination: destinationRoot, entries: [], requiresAction: false },
      stdout: [],
      status: -1,
      stderr: [outcome.failure.message],
    };
  }
  return { proposal: outcome.value, ...renderReconciliation(outcome.value) };
}

describe("the proposal for a destination that needs no action", () => {
  test("reports the ok exit status and states that nothing requires action", async () => {
    const rendered = await propose();

    expect(rendered.stderr).toEqual([]);
    expect(rendered.proposal.requiresAction).toBe(false);
    expect(rendered.status).toBe(EXIT_OK);

    // Every bound path is kept and managed, in the domain and in the rendering.
    expect(rendered.proposal.entries.map((entry) => entry.classification)).toEqual([
      "managed",
      "managed",
      "managed",
    ]);
    expect(rendered.proposal.entries.every((entry) => entry.action === "kept")).toBe(true);
    for (const [, destination] of BOUND_PATHS) {
      expect(lineFor(rendered.stdout, destination)).toMatch(/^reconcile: kept\s+managed\s+/u);
    }

    // No entry is locally modified, superseded or destination-owned: the counts
    // line is the summary that would contradict the ok status if one were.
    expect(rendered.stdout).toContain(NO_ACTION_COUNTS);
    expect(rendered.stdout).toContain(NO_ACTION_LINE);
    expect(rendered.stdout.some((line) => line.includes("must decide or act"))).toBe(false);
  });

  test("changes nothing under the destination", async () => {
    const before = await snapshotTree(destinationRoot);

    await propose();

    const after = await snapshotTree(destinationRoot);
    expect(after).toEqual(before);
    expect([...after.keys()].some((path) => path.startsWith(".aicore/reconciliation"))).toBe(
      false,
    );
    await expect(access(join(destinationRoot, ".aicore", "reconciliation"))).rejects.toThrow();
    // A proposal that rewrote the destination's own bindings would no longer be
    // the read-only proposal this tool reports itself as.
    expect(await readFile(join(destinationRoot, BINDINGS_RELATIVE_PATH), "utf8")).toContain(
      MANAGED_SOURCE,
    );
  });
});
