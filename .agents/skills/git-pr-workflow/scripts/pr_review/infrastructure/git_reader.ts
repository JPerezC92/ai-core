/** Read local Git inventory through argv-only commands with no network or GitHub access. */

import { spawnSync } from "node:child_process";
import type { GitInventoryPort } from "../domain/ports.ts";

/** The one external binary the reader shells out to. */
const GIT_EXECUTABLE = "git";

/** The bounded runtime of one Git read. */
const COMMAND_TIMEOUT_SECONDS = 120;

/** The largest captured Git output one read accepts. */
const MAX_OUTPUT_BYTES = 64 * 1024 * 1024;

/** The completed result of one Git invocation. */
interface GitCommandResult {
  readonly status: number;
  readonly stdout: Buffer;
  readonly stderr: Buffer;
}

/** Report an unavailable or failing Git process as a boundary failure, not a business value. */
export class GitBoundaryError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "GitBoundaryError";
  }
}

/** Decode captured Git output strictly so no content is silently replaced. */
function decodeGitOutput(raw: Buffer): string {
  try {
    return new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(raw);
  } catch {
    throw new GitBoundaryError("git output was not valid UTF-8");
  }
}

/** Map NUL-separated name-status fields to a status and destination-path pair. */
export function parseStatusEntries(text: string): Array<[string, string]> {
  const fields = text.split("\0");
  const entries: Array<[string, string]> = [];
  let index = 0;
  while (index < fields.length) {
    const status = fields[index] ?? "";
    index += 1;
    if (status === "") continue;
    const width = status.charAt(0) === "R" || status.charAt(0) === "C" ? 2 : 1;
    const paths = fields.slice(index, index + width);
    const destination = paths[paths.length - 1];
    if (paths.length !== width || destination === undefined || destination === "") {
      throw new GitBoundaryError("git name-status output was malformed");
    }
    entries.push([status, destination]);
    index += width;
  }
  return entries;
}

/** Compose the revision range one inventory read covers. */
function revisionRange(ancestor: string, head: string): string {
  return `${ancestor}..${head}`;
}

export class GitReader implements GitInventoryPort {
  private readonly cwd: string | undefined;
  private readonly executable: string | null | undefined;

  constructor(options: { cwd?: string; executable?: string | null } = {}) {
    this.cwd = options.cwd;
    this.executable = options.executable;
  }

  /** Return the object id a revision resolves to, or absence when it does not resolve. */
  resolveCommit(revision: string): string | null {
    const completed = this.run(["rev-parse", "--verify", revision], true);
    if (completed.status !== 0) return null;
    const commit = decodeGitOutput(completed.stdout).trim();
    return commit === "" ? null : commit;
  }

  /** Return the common ancestor of two revisions, or absence when they share none. */
  mergeBase(first: string, second: string): string | null {
    const completed = this.run(["merge-base", first, second], true);
    if (completed.status !== 0) return null;
    const ancestor = decodeGitOutput(completed.stdout).trim();
    return ancestor === "" ? null : ancestor;
  }

  /** Return the commit ids contained in one revision range in Git order. */
  listCommits(ancestor: string, head: string): string[] {
    const completed = this.run(["rev-list", revisionRange(ancestor, head)]);
    return decodeGitOutput(completed.stdout)
      .split("\n")
      .filter((line) => line !== "");
  }

  /** Return one commit message without the trailing newlines the log format appends. */
  readMessage(commit: string): string {
    const completed = this.run(["log", "--format=%B", "-1", commit]);
    return decodeGitOutput(completed.stdout).replace(/\n+$/u, "");
  }

  /** Return the exact changed path inventory, including deleted paths. */
  listChangedPaths(ancestor: string, head: string): string[] {
    const completed = this.run(["diff", "--name-only", "-z", revisionRange(ancestor, head)]);
    return decodeGitOutput(completed.stdout)
      .split("\0")
      .filter((path) => path !== "");
  }

  /** Return the paths the range deletes, so no body is read for them. */
  listDeletedPaths(ancestor: string, head: string): string[] {
    const completed = this.run(["diff", "--name-status", "-z", revisionRange(ancestor, head)]);
    const entries = parseStatusEntries(decodeGitOutput(completed.stdout));
    return entries.filter(([status]) => status.endsWith("D")).map(([, path]) => path);
  }

  /** Return one file body as committed at the supplied commit. */
  readFile(commit: string, path: string): string {
    const completed = this.run(["show", `${commit}:${path}`]);
    return decodeGitOutput(completed.stdout);
  }

  /** Run one read-only Git argv with no shell, no optional locks, and a bounded timeout. */
  private run(arguments_: readonly string[], allowFailure = false): GitCommandResult {
    if (this.executable === null) {
      throw new GitBoundaryError(`${GIT_EXECUTABLE} executable was not found on PATH`);
    }
    const completed = spawnSync(this.executable ?? GIT_EXECUTABLE, [...arguments_], {
      cwd: this.cwd,
      encoding: "buffer",
      shell: false,
      timeout: COMMAND_TIMEOUT_SECONDS * 1000,
      maxBuffer: MAX_OUTPUT_BYTES,
      env: { ...process.env, GIT_OPTIONAL_LOCKS: "0" },
      windowsHide: true,
    });
    if (completed.error) {
      const code = (completed.error as NodeJS.ErrnoException).code;
      if (code === "ENOENT") {
        throw new GitBoundaryError(`${GIT_EXECUTABLE} executable was not found on PATH`);
      }
      throw new GitBoundaryError(
        `${GIT_EXECUTABLE} could not be executed: ${completed.error.message}`,
      );
    }
    const status = completed.status ?? 1;
    if (status !== 0 && !allowFailure) {
      const detail = decodeGitOutput(completed.stderr).trim();
      throw new GitBoundaryError(`${GIT_EXECUTABLE} exited with ${status}: ${detail}`);
    }
    return { status, stdout: completed.stdout, stderr: completed.stderr };
  }
}
