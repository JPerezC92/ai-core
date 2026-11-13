/** End-to-end behavior of the evidence CLI as a spawned process. */

import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import {
  createBody,
  createLocalDraft,
  createLocalInventory,
  createLocalSnapshot,
  createMetadata,
  createPaths,
  createSnapshot,
} from "../support/review-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const entryPoint = join(skillRoot, "scripts", "prepare_pr_evidence.ts");

const temporaryDirectories: string[] = [];

interface CliRun {
  readonly status: number;
  readonly stdout: string;
  readonly stderr: string;
}

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-prepare-e2e-"));
  temporaryDirectories.push(directory);
  return directory;
}

/** Run the entry point as a spawned process and capture its status and streams. */
function runCli(args: readonly string[], cwd: string): CliRun {
  const completed = spawnSync(process.execPath, [entryPoint, ...args], {
    cwd,
    encoding: "utf8",
    env: process.env,
  });
  if (completed.error) throw completed.error;
  return {
    status: completed.status ?? -1,
    stdout: completed.stdout,
    stderr: completed.stderr,
  };
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("prepare_pr_evidence as a spawned process", () => {
  it("prepares the local snapshot and reports the prepared status", () => {
    const directory = makeDirectory();
    const draft = join(directory, "pr-draft.md");
    const body = join(directory, "pr-working-body.md");
    const inventory = join(directory, "inventory.json");
    const paths = join(directory, "paths.json");
    const output = join(directory, "snapshot.json");
    writeFileSync(draft, createLocalDraft(), "utf8");
    writeFileSync(body, createBody(), "utf8");
    writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
    writeFileSync(paths, JSON.stringify(createPaths()), "utf8");

    const run = runCli(
      [
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
      ],
      directory,
    );

    expect(run.status).toBe(0);
    expect(run.stdout).toBe('{"status": "prepared", "command": "prepare-snapshot"}\n');
    expect(run.stderr).toBe("");
    expect(readFileSync(output, "utf8")).toBe(
      `${JSON.stringify(createLocalSnapshot(), null, 2)}\n`,
    );
    expect(JSON.parse(readFileSync(output, "utf8"))).toEqual(createLocalSnapshot());
  });

  it("rejects a path inventory that is not the exact diff inventory", () => {
    const directory = makeDirectory();
    const draft = join(directory, "pr-draft.md");
    const body = join(directory, "pr-working-body.md");
    const inventory = join(directory, "inventory.json");
    const paths = join(directory, "paths.json");
    const output = join(directory, "snapshot.json");
    writeFileSync(draft, createLocalDraft(), "utf8");
    writeFileSync(body, createBody(), "utf8");
    writeFileSync(inventory, JSON.stringify(createLocalInventory()), "utf8");
    writeFileSync(paths, JSON.stringify(["src/unlisted-path"]), "utf8");

    const run = runCli(
      [
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
      ],
      directory,
    );

    expect(run.status).toBe(1);
    expect(run.stdout).toBe(
      '{"code": "SNAPSHOT_PATHS_MISMATCH", "message": "snapshot paths must equal the exact diff inventory"}\n',
    );
    expect(run.stderr).toBe("");
    expect(existsSync(output)).toBe(false);
  });

  it("assembles a scanner snapshot from a supplied complete snapshot", () => {
    const directory = makeDirectory();
    const collected = join(directory, "collected.json");
    const paths = join(directory, "paths.json");
    const output = join(directory, "snapshot.json");
    writeFileSync(collected, JSON.stringify(createSnapshot()), "utf8");
    writeFileSync(paths, JSON.stringify(createPaths()), "utf8");

    const run = runCli(
      ["snapshot", "--input", collected, "--paths", paths, "--output", output],
      directory,
    );

    expect(run.status).toBe(0);
    expect(run.stdout).toBe('{"status": "prepared", "command": "snapshot"}\n');
    expect(run.stderr).toBe("");
    expect(readFileSync(output, "utf8")).toBe(
      `${JSON.stringify(createSnapshot(), null, 2)}\n`,
    );
  });

  it("verifies an unchanged persisted capture and rejects a diverged one", () => {
    const directory = makeDirectory();
    const baseline = join(directory, "baseline.json");
    const current = join(directory, "current.json");
    const body = join(directory, "pr-working-body.md");
    writeFileSync(baseline, JSON.stringify(createMetadata()), "utf8");
    writeFileSync(current, JSON.stringify(createMetadata()), "utf8");
    writeFileSync(body, createBody(), "utf8");
    const arguments_ = [
      "verify",
      "--baseline",
      baseline,
      "--current",
      current,
      "--working-body",
      body,
    ];

    const verified = runCli(arguments_, directory);

    expect(verified.status).toBe(0);
    expect(verified.stdout).toBe('{"status": "prepared", "command": "verify"}\n');
    expect(verified.stderr).toBe("");

    writeFileSync(current, JSON.stringify(createMetadata({ body: "Changed remotely" })), "utf8");
    const diverged = runCli(arguments_, directory);

    expect(diverged.status).toBe(1);
    expect(diverged.stdout).toBe(
      '{"code": "READBACK_DIVERGED", "message": "persisted body differs from the intended publication"}\n',
    );
    expect(diverged.stderr).toBe("");
  });

  it("rejects a command line it cannot accept, naming the TypeScript entry point", () => {
    const directory = makeDirectory();

    const run = runCli(["prepare-local", "--pr", "0"], directory);

    expect(run.status).toBe(2);
    expect(run.stdout).toBe("");
    expect(run.stderr).toBe(
      "usage: prepare_pr_evidence.ts prepare-local --pr PR --base BASE --draft DRAFT --working-body WORKING-BODY --output OUTPUT\n" +
        "prepare_pr_evidence.ts prepare-local: error: argument --pr: a positive integer is required: 0\n",
    );
  });

  it("rejects a command line that names no command", () => {
    const directory = makeDirectory();

    const run = runCli([], directory);

    expect(run.status).toBe(2);
    expect(run.stdout).toBe("");
    expect(run.stderr).toBe(
      "usage: prepare_pr_evidence.ts <command> [options]\n" +
        "prepare_pr_evidence.ts: error: the following arguments are required: command\n",
    );
  });

  it("rejects a command name outside the four composed commands", () => {
    const directory = makeDirectory();

    const run = runCli(["publish"], directory);

    expect(run.status).toBe(2);
    expect(run.stdout).toBe("");
    expect(run.stderr).toBe(
      "usage: prepare_pr_evidence.ts <command> [options]\n" +
        "prepare_pr_evidence.ts: error: argument command: invalid choice: 'publish' " +
        "(choose from 'snapshot', 'prepare-snapshot', 'prepare-local', 'verify')\n",
    );
  });

  it("reports an unreadable input as an input/output failure", () => {
    const directory = makeDirectory();
    const input = join(directory, "absent-input.json");
    const paths = join(directory, "absent-paths.json");
    const output = join(directory, "snapshot.json");

    const run = runCli(
      ["snapshot", "--input", input, "--paths", paths, "--output", output],
      directory,
    );

    // The fixed contract is the `input/output failure: ` prefix and exit status 2;
    // the detail after the prefix is this runtime's own error wording.
    expect(run.status).toBe(2);
    expect(run.stdout).toBe("");
    expect(run.stderr).toBe(
      `input/output failure: ENOENT: no such file or directory, open '${input}'\n`,
    );
    expect(existsSync(output)).toBe(false);
  });
});
