/** End-to-end behavior of the prepare-local command against a real local Git repository. */

import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import {
  createBody,
  createCommittedRepository,
  createExpectedGitSnapshot,
  createFixtureEnvironment,
  createLocalDraft,
} from "#tests/support/review-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const entryPoint = join(skillRoot, "scripts", "prepare_pr_evidence.ts");

const temporaryDirectories: string[] = [];

interface CliRun {
  readonly status: number;
  readonly stdout: string;
  readonly stderr: string;
}

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-local-e2e-"));
  temporaryDirectories.push(directory);
  return directory;
}

/** Run the entry point as a spawned process and capture its status and streams. */
function runCli(args: readonly string[], cwd: string): CliRun {
  const completed = spawnSync(process.execPath, [entryPoint, ...args], {
    cwd,
    encoding: "utf8",
    env: createFixtureEnvironment(),
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

describe("prepare-local as a spawned process", () => {
  it("prepares the snapshot from the same local repository", () => {
    const root = makeDirectory();
    const repository = createCommittedRepository(join(root, "repository"));
    const draft = join(root, "pr-draft.md");
    const body = join(root, "pr-working-body.md");
    const output = join(root, "snapshot.json");
    writeFileSync(draft, createLocalDraft(), "utf8");
    writeFileSync(body, createBody(), "utf8");

    const run = runCli(
      [
        "prepare-local",
        "--pr",
        "80",
        "--base",
        repository.base,
        "--draft",
        draft,
        "--working-body",
        body,
        "--output",
        output,
      ],
      repository.directory,
    );

    expect(run.status).toBe(0);
    expect(run.stdout).toBe('{"status": "prepared", "command": "prepare-local"}\n');
    expect(run.stderr).toBe("");
    expect(readFileSync(output, "utf8")).toBe(
      `${JSON.stringify(createExpectedGitSnapshot(repository.base, repository.head), null, 2)}\n`,
    );
  });

  it("rejects an unresolved base ref without creating an output", () => {
    const root = makeDirectory();
    const repository = createCommittedRepository(join(root, "repository"));
    const draft = join(root, "pr-draft.md");
    const body = join(root, "pr-working-body.md");
    const output = join(root, "snapshot.json");
    writeFileSync(draft, createLocalDraft(), "utf8");
    writeFileSync(body, createBody(), "utf8");

    const run = runCli(
      [
        "prepare-local",
        "--pr",
        "80",
        "--base",
        "refs/heads/unresolved",
        "--draft",
        draft,
        "--working-body",
        body,
        "--output",
        output,
      ],
      repository.directory,
    );

    expect(run.status).toBe(1);
    expect(run.stdout).toBe(
      '{"code": "GIT_REVISION_UNRESOLVED", "message": "base ref must resolve to a commit: refs/heads/unresolved"}\n',
    );
    expect(run.stderr).toBe("");
    expect(existsSync(output)).toBe(false);
  });

  it("leaves an existing output untouched and reports an input/output failure", () => {
    const root = makeDirectory();
    const repository = createCommittedRepository(join(root, "repository"));
    const draft = join(root, "pr-draft.md");
    const body = join(root, "pr-working-body.md");
    const output = join(root, "snapshot.json");
    writeFileSync(draft, createLocalDraft(), "utf8");
    writeFileSync(body, createBody(), "utf8");
    writeFileSync(output, "existing\n", "utf8");

    const run = runCli(
      [
        "prepare-local",
        "--pr",
        "80",
        "--base",
        repository.base,
        "--draft",
        draft,
        "--working-body",
        body,
        "--output",
        output,
      ],
      repository.directory,
    );

    // The fixed contract is the `input/output failure: ` prefix and exit status 2;
    // the detail after the prefix is this runtime's own error wording.
    expect(run.status).toBe(2);
    expect(run.stdout).toBe("");
    expect(run.stderr).toBe(
      `input/output failure: EEXIST: file already exists, open '${output}'\n`,
    );
    expect(readFileSync(output, "utf8")).toBe("existing\n");
  });
});
