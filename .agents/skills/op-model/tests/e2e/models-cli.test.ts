import { spawnSync } from "node:child_process";
import { chmodSync, linkSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import { create, listingOf } from "#tests/support/model.factory.ts";

/**
 * End to end: the assembled `models` command and its presentation contract.
 *
 * Every case spawns the real entry point. The external program is a controlled
 * substitute written by this file, so no case depends on an installed `opencode`
 * binary and no case can pass without executing the command it claims to test
 * (T5, T18).
 */
const entry = resolve(dirname(fileURLToPath(import.meta.url)), "../../scripts/models.ts");

const temporaryDirectories: string[] = [];

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

/**
 * Materialise a controlled `opencode` substitute that prints `stdout`.
 *
 * The substitute is this file's own interpreter under the name the composition
 * root binds: a shell shim on POSIX, and on Windows the interpreter itself, with
 * the payload in the extensionless `models` file it resolves from the working
 * directory. A platform that refuses the link fails the case rather than
 * skipping it.
 */
function createControlledCommand(stdout: string): string {
	const directory = mkdtempSync(join(tmpdir(), "op-model-cli-"));
	temporaryDirectories.push(directory);
	const body = `process.stdout.write(${JSON.stringify(stdout)});`;

	if (process.platform === "win32") {
		linkSync(process.execPath, join(directory, "opencode.exe"));
		writeFileSync(join(directory, "models"), body, "utf8");
		return directory;
	}

	const payload = join(directory, "command.mjs");
	writeFileSync(payload, body, "utf8");
	const shim = join(directory, "opencode");
	writeFileSync(shim, `#!/bin/sh\nexec "${process.execPath}" "${payload}" "$@"\n`, "utf8");
	chmodSync(shim, 0o755);
	return directory;
}

/** Run the assembled command, optionally with an isolated PATH and working directory. */
function runControlled(args: string[], stdout: string) {
	const directory = createControlledCommand(stdout);
	const result = spawnSync(process.execPath, [entry, ...args], {
		encoding: "utf8",
		env: { ...process.env, PATH: directory, Path: directory },
		cwd: directory,
	});
	if (result.error) throw result.error;
	return result;
}

/** Run the assembled command with no `opencode` reachable at all. */
function runWithoutSource(args: string[]) {
	const result = spawnSync(process.execPath, [entry, ...args], {
		encoding: "utf8",
		env: { ...process.env, PATH: "", Path: "" },
		cwd: process.cwd(),
	});
	if (result.error) throw result.error;
	return result;
}

describe("missing executable", () => {
	it("reports the diagnostic without a fallback listing", () => {
		const result = runWithoutSource([]);

		expect(result.status).toBe(1);
		expect(result.stdout).toBe("");
		expect(result.stderr).toBe("ERROR: `opencode` not found on PATH. Cannot list models.\n");
	});
});

describe("grouped listing", () => {
	it("groups by provider and sorts both the providers and the selectors", () => {
		const listing = listingOf([
			create({ config: "a/z", id: "z", provider: "a", name: "z" }),
			create({ config: "openai/gpt", id: "gpt", provider: "openai", name: "gpt" }),
			create({ config: "a/b", id: "b", provider: "a", name: "b" }),
		]);

		const result = runControlled([], listing);

		expect(result.status).toBe(0);
		expect(result.stderr).toBe("");
		expect(result.stdout).toBe("## a\n  a/b\n  a/z\n\n## openai\n  openai/gpt\n\n");
	});
});

describe("query selection", () => {
	it("serializes each match as a JSON line carrying the six contract fields", () => {
		const listing = listingOf([
			create(),
			create({ config: "deepseek/deepseek-v4-flash", id: "deepseek-v4-flash" }),
		]);

		const result = runControlled(["deepseek"], listing);

		expect(result.status).toBe(0);
		expect(result.stdout).toBe(
			'{"config": "deepseek/deepseek-v4", "id": "deepseek-v4", "provider": "deepseek", "name": "deepseek-v4", "cost_in": 0.0, "cost_out": 0.0}\n' +
				'{"config": "deepseek/deepseek-v4-flash", "id": "deepseek-v4-flash", "provider": "deepseek", "name": "deepseek-v4-flash", "cost_in": 0.0, "cost_out": 0.0}\n',
		);
	});
});

describe("business outcomes", () => {
	it("reports each outcome on stderr with exit 1 and no listing", () => {
		const unmatched = runControlled(["zzzz-no-such-model-zzzz"], listingOf([create()]));
		expect(unmatched.status).toBe(1);
		expect(unmatched.stdout).toBe("");
		expect(unmatched.stderr).toContain("No match for zzzz-no-such-model-zzzz in `opencode models`.");
		expect(unmatched.stderr).toContain(".agents/skills/op-model/scripts/models.ts");

		const emptyCatalog = runControlled([], "");
		expect(emptyCatalog.status).toBe(1);
		expect(emptyCatalog.stdout).toBe("");
		expect(emptyCatalog.stderr).toBe("No models parsed from `opencode models` output.\n");
	});
});
