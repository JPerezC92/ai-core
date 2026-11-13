/**
 * The engine seam the parity corpus judges.
 *
 * The corpus states outcomes; an engine produces them. This module defines the
 * one interface between the two, so a new engine is dropped in by binding the
 * seam — never by editing a case.
 *
 * Two bindings exist:
 *
 * - `typescript` — the engine under test. It must live at
 *   `cli/aicore/src/infrastructure/core-sync-engine.ts` and export
 *   `createCoreSyncEngine(): EngineUnderTest`. It is used automatically once
 *   that module exists.
 * - `python-reference` — the reference implementation, used as the corpus's
 *   provenance oracle while the TypeScript engine is absent. It runs the
 *   documented CLI of the Python engine over the same synthetic fixtures.
 *
 * `AICORE_PARITY_ENGINE` selects a binding explicitly: `typescript` or
 * `python-reference`.
 */

import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const run = promisify(execFile);

/** The command a case asks an engine to run. */
export type EngineCommand = "check" | "apply" | "init";

/** Everything an engine needs to run one command over one fixture. */
export type EngineRequest = {
  readonly command: EngineCommand;
  readonly sourceRoot: string;
  readonly destinationRoot: string;
  readonly bindingsPath: string;
  readonly sourceRevision: string;
  readonly bind?: readonly string[] | undefined;
  readonly bindRaw?: readonly string[] | undefined;
  readonly bindCleared?: boolean | undefined;
  readonly root?: string | undefined;
};

/** What an engine reports back. */
export type EngineOutcome = {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
};

/** The interface an engine implementation must expose to be judged. */
export type EngineUnderTest = {
  /** A stable identifier, used in failure messages. */
  readonly id: string;
  run(request: EngineRequest): Promise<EngineOutcome>;
};

/** The module the TypeScript engine must provide. */
export const TYPESCRIPT_ENGINE_MODULE = new URL(
  "../../../src/infrastructure/core-sync-engine.ts",
  import.meta.url,
);

/** The repository root, derived from this module's own location. */
const REPOSITORY_ROOT = new URL("../../../../../", import.meta.url);

/** The documented entry point of the Python reference engine. */
const REFERENCE_SCRIPT = fileURLToPath(
  new URL(".opencode/skills/core-sync/scripts/core_sync.py", REPOSITORY_ROOT),
);

/**
 * Resolve the engine the corpus judges.
 *
 * The TypeScript engine wins as soon as it exists; the reference engine is the
 * fallback that keeps the corpus executable while it does not.
 */
export async function resolveEngineUnderTest(): Promise<EngineUnderTest> {
  const selected = process.env["AICORE_PARITY_ENGINE"];
  if (selected === "python-reference") {
    return createReferenceEngine();
  }
  if (selected === "typescript") {
    return createTypeScriptEngine();
  }
  if (existsSync(fileURLToPath(TYPESCRIPT_ENGINE_MODULE))) {
    return createTypeScriptEngine();
  }
  return createReferenceEngine();
}

/**
 * Load the TypeScript engine under test.
 *
 * The module is imported through a runtime-computed URL so the corpus compiles
 * and runs while the engine is still absent.
 */
export async function createTypeScriptEngine(): Promise<EngineUnderTest> {
  const loaded = (await import(TYPESCRIPT_ENGINE_MODULE.href)) as {
    createCoreSyncEngine?: () => EngineUnderTest;
  };
  const factory = loaded.createCoreSyncEngine;
  if (typeof factory !== "function") {
    throw new Error(
      `the TypeScript engine at ${fileURLToPath(TYPESCRIPT_ENGINE_MODULE)} must export createCoreSyncEngine()`,
    );
  }
  return factory();
}

/**
 * The Python reference engine, run exactly as an operator would run it.
 *
 * It is the corpus's provenance oracle: it answers "what does the reference do
 * with this fixture", never "what should this fixture expect".
 */
export function createReferenceEngine(): EngineUnderTest {
  return {
    id: "python-reference",
    async run(request: EngineRequest): Promise<EngineOutcome> {
      const arguments_ = [
        REFERENCE_SCRIPT,
        request.command,
        "--source",
        request.sourceRoot,
        "--destination",
        request.destinationRoot,
        "--bindings",
        request.bindingsPath,
        "--source-revision",
        request.sourceRevision,
      ];
      for (const binding of request.bind ?? []) {
        arguments_.push("--bind", binding);
      }
      for (const binding of request.bindRaw ?? []) {
        arguments_.push("--bind-raw", binding);
      }
      if (request.bindCleared === true) {
        arguments_.push("--bind-cleared");
      }
      if (request.root !== undefined) {
        arguments_.push("--root", request.root);
      }
      try {
        const { stdout, stderr } = await run(referenceInterpreter(), arguments_, {
          cwd: fileURLToPath(REPOSITORY_ROOT),
          windowsHide: true,
          maxBuffer: 32 * 1024 * 1024,
        });
        return { exitCode: 0, stdout: normalise(stdout), stderr: normalise(stderr) };
      } catch (error) {
        const failure = error as { code?: number | string; stdout?: string; stderr?: string };
        return {
          exitCode: typeof failure.code === "number" ? failure.code : 1,
          stdout: normalise(failure.stdout ?? ""),
          stderr: normalise(failure.stderr ?? ""),
        };
      }
    },
  };
}

/** The repository's own interpreter, which holds the engine's dependencies. */
function referenceInterpreter(): string {
  const relative = process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python";
  return fileURLToPath(new URL(relative, REPOSITORY_ROOT));
}

/**
 * Normalise line endings in a captured stream.
 *
 * The reference writes its messages through the platform's text mode, which
 * translates a line feed on Windows. The translation is a platform artefact,
 * not an engine behaviour, so it is removed before the corpus compares.
 */
function normalise(text: string): string {
  return text.replace(/\r\n/gu, "\n");
}
