/** The distributed skill must run from an isolated copy with no development package. */

import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import { loadApprovedPolicy, makeCompleteSnapshot } from "../support/attribution-fixtures.ts";
import {
  createBody,
  createLocalDraft,
  createLocalInventory,
  createLocalSnapshot,
  createPaths,
} from "../support/review-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const runtimeFiles = [
  "scripts/prepare_pr_evidence.ts",
  "scripts/scan_attribution.ts",
  "scripts/pr_review/domain/records.ts",
  "scripts/pr_review/domain/ports.ts",
  "scripts/pr_review/domain/snapshot_assembly.ts",
  "scripts/pr_review/application/assemble_review_snapshot.ts",
  "scripts/pr_review/application/collect_local_inventory.ts",
  "scripts/pr_review/application/prepare_local_snapshot.ts",
  "scripts/pr_review/application/verify_persisted_body.ts",
  "scripts/pr_review/infrastructure/filesystem.ts",
  "scripts/pr_review/infrastructure/git_reader.ts",
  "scripts/attribution_scan/domain/records.ts",
  "scripts/attribution_scan/domain/validation.ts",
  "scripts/attribution_scan/domain/matching.ts",
  "scripts/attribution_scan/application/scan_attribution.ts",
];
/** The copy carries the runtime modules and the ESM boundary that makes them modules. */
const copyFiles = ["package.json", ...runtimeFiles];
const temporaryDirectories: string[] = [];

function createEnvironment(): { runtime: string; fixtures: string } {
  const root = mkdtempSync(join(tmpdir(), "git-pr-workflow-isolated-e2e-"));
  temporaryDirectories.push(root);
  const runtime = join(root, "isolated-skill");
  const fixtures = join(root, "fixtures");
  for (const file of copyFiles) {
    const destination = join(runtime, file);
    mkdirSync(dirname(destination), { recursive: true });
    cpSync(join(skillRoot, file), destination);
  }
  mkdirSync(fixtures, { recursive: true });
  return { runtime, fixtures };
}

/** Runs the copied entry point with the environment's Node binary and no dependency paths. */
function runIsolatedNode(runtime: string, entry: string, args: string[]): ReturnType<typeof spawnSync> {
  const environment = { ...process.env };
  delete environment["NODE_PATH"];
  delete environment["NODE_OPTIONS"];
  return spawnSync(process.execPath, [join(runtime, "scripts", entry), ...args], {
    cwd: runtime,
    encoding: "utf8",
    env: environment,
  });
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("the distributed skill in an isolated source-only copy", () => {
  it("scans a snapshot with no development package present", () => {
    const { runtime, fixtures } = createEnvironment();
    const policyPath = join(fixtures, "policy.json");
    const snapshotPath = join(fixtures, "snapshot.json");
    writeFileSync(policyPath, JSON.stringify(loadApprovedPolicy()), "utf8");
    writeFileSync(snapshotPath, JSON.stringify(makeCompleteSnapshot()), "utf8");

    const run = runIsolatedNode(runtime, "scan_attribution.ts", [
      "--policy",
      policyPath,
      "--snapshot",
      snapshotPath,
    ]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(0);
    expect(JSON.parse(String(run.stdout))).toMatchObject({ matches: [], exclusions: [] });
    expect(String(run.stderr)).toBe("");
    expect(readdirSync(runtime).sort()).toEqual(["package.json", "scripts"]);
    expect(existsSync(join(runtime, "node_modules"))).toBe(false);
    expect(existsSync(join(runtime, "cli", "aicore"))).toBe(false);
  });

  it("prepares a snapshot with the evidence entry point and no development package present", () => {
    const { runtime, fixtures } = createEnvironment();
    const draft = join(fixtures, "pr-draft.md");
    const body = join(fixtures, "pr-working-body.md");
    const inventory = join(fixtures, "inventory.json");
    const paths = join(fixtures, "paths.json");
    const output = join(fixtures, "snapshot.json");
    writeFileSync(draft, createLocalDraft(), "utf8");
    writeFileSync(body, createBody(), "utf8");
    writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
    writeFileSync(paths, JSON.stringify(createPaths()), "utf8");

    const run = runIsolatedNode(runtime, "prepare_pr_evidence.ts", [
      "prepare-snapshot",
      "--draft",
      draft,
      "--working-body",
      body,
      "--input",
      inventory,
      "--paths",
      paths,
      "--output",
      output,
    ]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(0);
    expect(String(run.stderr)).toBe("");
    expect(readFileSync(output, "utf8")).toBe(
      `${JSON.stringify(createLocalSnapshot(), null, 2)}\n`,
    );
  });
});
