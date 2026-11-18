/**
 * The engine seam the parity corpus judges.
 *
 * The corpus states outcomes; an engine produces them. This module defines the
 * one interface between the two, so a new engine is dropped in by binding the
 * seam — never by editing a case.
 *
 * The seam binds the assembled CLI entry point, `cli/aicore/src/main.ts`: it
 * builds the command's own argument vector from the request a case declares,
 * runs the entry point in process against a recording writer, and reports the
 * exit status and the bytes the entry point wrote. The corpus therefore judges
 * the assembled engine's observable behaviour, not one adapter's.
 */

import { fileURLToPath } from "node:url";

import type { StreamWriter } from "#delivery/stream-writer.ts";

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
export const TYPESCRIPT_ENGINE_MODULE = new URL("../../../src/main.ts", import.meta.url);

/** The identifier the bound entry point reports in a failure message. */
const ENGINE_ID = "typescript";

/** A writer that records the bytes the entry point wrote. */
class RecordingWriter implements StreamWriter {
	#stdout = "";
	#stderr = "";

	get stdout(): string {
		return this.#stdout;
	}

	get stderr(): string {
		return this.#stderr;
	}

	writeStdout(lines: readonly string[]): void {
		for (const line of lines) {
			this.#stdout += `${line}\n`;
		}
	}

	writeStderr(lines: readonly string[]): void {
		for (const line of lines) {
			this.#stderr += `${line}\n`;
		}
	}
}

/**
 * Resolve the engine the corpus judges.
 *
 * The TypeScript entry point is the only binding; the seam names the module it
 * must provide, and every case runs against it.
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
		main?: (
			argv: readonly string[],
			environment: Readonly<Record<string, string | undefined>>,
			writer: StreamWriter,
		) => Promise<number>;
	};
	const entryPoint = loaded.main;
	if (typeof entryPoint !== "function") {
		throw new Error(`the CLI entry point at ${fileURLToPath(TYPESCRIPT_ENGINE_MODULE)} must export main()`);
	}

	return {
		id: ENGINE_ID,
		async run(request: EngineRequest): Promise<EngineOutcome> {
			const writer = new RecordingWriter();
			const exitCode = await entryPoint(toArguments(request), {}, writer);
			return { exitCode, stdout: writer.stdout, stderr: writer.stderr };
		},
	};
}

/** The published command line one request names. */
function toArguments(request: EngineRequest): readonly string[] {
	const arguments_: string[] = [
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

	for (const declaration of request.bind ?? []) {
		arguments_.push("--bind", declaration);
	}
	for (const declaration of request.bindRaw ?? []) {
		arguments_.push("--bind-raw", declaration);
	}
	if (request.bindCleared === true) {
		arguments_.push("--bind-cleared");
	}
	if (request.root !== undefined) {
		arguments_.push("--root", request.root);
	}

	return arguments_;
}
