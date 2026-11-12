/**
 * Shared harness for the end-to-end suite.
 *
 * Contract T15: shared test data lives in a helper, never inline. This module
 * also isolates operator state (T18): every invocation points the CLI at a
 * throwaway selection file, so the developer's real selection is never read or
 * written, and an interrupted or concurrent run cannot corrupt it.
 */

import { execFile } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

import { createTemporaryRoot, disposeTemporaryRoot } from "./disposable-root.ts";

const run = promisify(execFile);

/** Prefix that identifies a root this harness owns. */
const FIXTURE_PREFIX = "aicore-e2e-";

export const CHECKOUT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "..");
export const CLI_ENTRY = join(CHECKOUT, "cli", "aicore", "src", "main.ts");

/** A valid 40-character lowercase hex revision. */
export const REVISION = "0123456789abcdef0123456789abcdef01234567";

/** A disposable destination directory plus its isolated selection file. */
export type Fixture = {
  readonly destination: string;
  readonly configPath: string;
  readonly root: string;
  dispose(): Promise<void>;
};

export async function createFixture(agentsBody?: string): Promise<Fixture> {
  const { root, prefix } = await createTemporaryRoot(FIXTURE_PREFIX);
  const destination = join(root, "destination");
  await mkdir(destination, { recursive: true });
  await writeFile(
    join(destination, "AGENTS.md"),
    agentsBody ?? "# Fixture project\n\nA disposable destination for end-to-end verification.\n",
    "utf8",
  );

  return {
    destination,
    configPath: join(root, "local.json"),
    root,
    async dispose(): Promise<void> {
      // Ownership is re-validated here, immediately before deletion.
      await disposeTemporaryRoot(root, prefix);
    },
  };
}

export type Invocation = {
  readonly status: number;
  readonly stdout: string;
  readonly stderr: string;
};

/**
 * Invoke the CLI as an operator would.
 *
 * `AICORE_LOCAL_CONFIG` redirects the selection file, so no test reads or writes
 * the real operator selection.
 */
export async function invoke(
  arguments_: readonly string[],
  options: {
    readonly fixture: Fixture;
    readonly revision?: string | undefined;
  },
): Promise<Invocation> {
  const env: Record<string, string> = {};
  for (const [key, value] of Object.entries(process.env)) {
    if (value !== undefined) {
      env[key] = value;
    }
  }
  delete env["AICORE_SOURCE_REVISION"];
  delete env["AICORE_LOCAL_CONFIG"];

  if (options.revision !== undefined && options.revision !== "") {
    env["AICORE_SOURCE_REVISION"] = options.revision;
  }
  env["AICORE_LOCAL_CONFIG"] = options.fixture.configPath;

  try {
    const { stdout, stderr } = await run(process.execPath, [CLI_ENTRY, ...arguments_], {
      cwd: CHECKOUT,
      env,
      maxBuffer: 32 * 1024 * 1024,
      windowsHide: true,
    });
    return { status: 0, stdout, stderr };
  } catch (error) {
    const failure = error as { code?: number | string; stdout?: string; stderr?: string };
    return {
      status: typeof failure.code === "number" ? failure.code : 1,
      stdout: failure.stdout ?? "",
      stderr: failure.stderr ?? "",
    };
  }
}

/** Invoke with the default valid revision. */
export function invokeWithRevision(
  arguments_: readonly string[],
  fixture: Fixture,
): Promise<Invocation> {
  return invoke(arguments_, { fixture, revision: REVISION });
}
