/**
 * The engine seam the parity corpus judges.
 *
 * The corpus states outcomes; an engine produces them. This module defines the
 * one interface between the two, so a new engine is dropped in by binding the
 * seam — never by editing a case.
 *
 * The seam binds the TypeScript engine. It lives at
 * `cli/aicore/src/infrastructure/core-sync-engine.ts` and exports
 * `createCoreSyncEngine(): EngineUnderTest`.
 */

import { fileURLToPath } from "node:url";

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

/**
 * Resolve the engine the corpus judges.
 *
 * The TypeScript engine is the only binding; the seam names the module it must
 * provide, and every case runs against it.
 */
export async function resolveEngineUnderTest(): Promise<EngineUnderTest> {
  return createTypeScriptEngine();
}

/**
 * Load the TypeScript engine under test.
 *
 * The module is imported through a runtime-computed URL, so the seam names one
 * module path and the corpus's cases stay independent of the engine's layout.
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
