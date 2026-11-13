/** End-to-end behavior of the attribution scanner as a spawned process. */

import { spawnSync } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import {
  loadApprovedPolicy,
  makeAttributionLine,
  makeChangedFile,
  makeChangedFiles,
  makeCompleteSnapshot,
  makeFloatSchemaSnapshotText,
  makeMalformedSnapshot,
  makeSnapshotWithArtifactContent,
} from "../support/attribution-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const entryPoint = join(skillRoot, "scripts", "scan_attribution.ts");

/** The head object id the approved policy fixtures carry. */
const HEAD_SHA = "a".repeat(40);

/** The scan output of a complete snapshot that carries no attribution line. */
const CLEAN_SCAN_OUTPUT = [
  "{",
  '  "base": "origin/main",',
  '  "exclusions": [],',
  `  "head_sha": "${HEAD_SHA}",`,
  '  "matches": [],',
  '  "pr_number": 80',
  "}",
  "",
].join("\n");

/** The scan output of a snapshot whose title carries the first approved marker and identity. */
const MATCHED_SCAN_OUTPUT = [
  "{",
  '  "base": "origin/main",',
  '  "exclusions": [],',
  `  "head_sha": "${HEAD_SHA}",`,
  '  "matches": [',
  "    {",
  '      "identity": "OpenAI",',
  '      "line": 1,',
  '      "marker": "Co-authored-by:",',
  '      "path": null,',
  '      "source": "PR #80 title",',
  '      "surface": "pr-title"',
  "    }",
  "  ],",
  '  "pr_number": 80',
  "}",
  "",
].join("\n");

const temporaryDirectories: string[] = [];

interface CliRun {
  readonly status: number;
  readonly stdout: string;
  readonly stderr: string;
}

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-scan-e2e-"));
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

describe("scan_attribution as a spawned process", () => {
  it("accepts a schema written as a floating-point number in raw JSON text", () => {
    // Documented difference: JSON carries no integer/floating-point distinction,
    // so a `schema` written as `1.0` is accepted where a whole number is required.
    const directory = makeDirectory();
    const policyPath = join(directory, "policy.json");
    const snapshotPath = join(directory, "snapshot.json");
    writeFileSync(policyPath, JSON.stringify(loadApprovedPolicy()), "utf8");
    writeFileSync(snapshotPath, makeFloatSchemaSnapshotText(), "utf8");

    const run = runCli(["--policy", policyPath, "--snapshot", snapshotPath], directory);

    expect(run.status).toBe(0);
    expect(run.stdout).toBe(CLEAN_SCAN_OUTPUT);
    expect(run.stderr).toBe("");
  });

  it("reports a clean scan and its prepared exit status", () => {
    const directory = makeDirectory();
    const policyPath = join(directory, "policy.json");
    const snapshotPath = join(directory, "snapshot.json");
    writeFileSync(policyPath, JSON.stringify(loadApprovedPolicy()), "utf8");
    writeFileSync(snapshotPath, JSON.stringify(makeCompleteSnapshot()), "utf8");

    const run = runCli(["--policy", policyPath, "--snapshot", snapshotPath], directory);

    expect(run.status).toBe(0);
    expect(run.stdout).toBe(CLEAN_SCAN_OUTPUT);
    expect(run.stderr).toBe("");
  });

  it("reports a matched scan and its matching exit status", () => {
    const directory = makeDirectory();
    const policy = loadApprovedPolicy();
    const policyPath = join(directory, "policy.json");
    const snapshotPath = join(directory, "snapshot.json");
    writeFileSync(policyPath, JSON.stringify(policy), "utf8");
    writeFileSync(
      snapshotPath,
      JSON.stringify(
        makeSnapshotWithArtifactContent(
          "pr-title",
          makeAttributionLine(policy),
          makeChangedFiles(makeChangedFile()),
        ),
      ),
      "utf8",
    );

    const run = runCli(["--policy", policyPath, "--snapshot", snapshotPath], directory);

    expect(run.status).toBe(1);
    expect(run.stdout).toBe(MATCHED_SCAN_OUTPUT);
    expect(run.stderr).toBe("");
  });

  it("rejects a malformed snapshot with the snapshot diagnostic", () => {
    const directory = makeDirectory();
    const policyPath = join(directory, "policy.json");
    const snapshotPath = join(directory, "snapshot.json");
    writeFileSync(policyPath, JSON.stringify(loadApprovedPolicy()), "utf8");
    writeFileSync(snapshotPath, JSON.stringify(makeMalformedSnapshot()), "utf8");

    const run = runCli(["--policy", policyPath, "--snapshot", snapshotPath], directory);

    expect(run.status).toBe(2);
    expect(run.stdout).toBe('{"error": "snapshot pr_number must be a positive integer"}\n');
    expect(run.stderr).toBe("");
  });

  it("rejects an input file it cannot read", () => {
    const directory = makeDirectory();
    const policyPath = join(directory, "policy.json");
    writeFileSync(policyPath, JSON.stringify(loadApprovedPolicy()), "utf8");

    const run = runCli(
      ["--policy", policyPath, "--snapshot", join(directory, "absent.json")],
      directory,
    );

    expect(run.status).toBe(2);
    expect(run.stdout).toBe('{"error": "unable to read input file"}\n');
    expect(run.stderr).toBe("");
  });

  it("rejects an input file that is not valid UTF-8", () => {
    const directory = makeDirectory();
    const policyPath = join(directory, "policy.json");
    const snapshotPath = join(directory, "snapshot.json");
    writeFileSync(policyPath, JSON.stringify(loadApprovedPolicy()), "utf8");
    writeFileSync(snapshotPath, Buffer.from([0xff, 0xfe, 0x00]));

    const run = runCli(["--policy", policyPath, "--snapshot", snapshotPath], directory);

    expect(run.status).toBe(2);
    expect(run.stdout).toBe('{"error": "input is not valid UTF-8"}\n');
    expect(run.stderr).toBe("");
  });

  it("rejects an input file that is not valid JSON", () => {
    const directory = makeDirectory();
    const policyPath = join(directory, "policy.json");
    const snapshotPath = join(directory, "snapshot.json");
    writeFileSync(policyPath, JSON.stringify(loadApprovedPolicy()), "utf8");
    writeFileSync(snapshotPath, "{not json", "utf8");

    const run = runCli(["--policy", policyPath, "--snapshot", snapshotPath], directory);

    expect(run.status).toBe(2);
    expect(run.stdout).toBe('{"error": "input is not valid JSON"}\n');
    expect(run.stderr).toBe("");
  });
});
