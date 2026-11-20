import { spawnSync } from "node:child_process";
import {
	cpSync,
	existsSync,
	mkdirSync,
	mkdtempSync,
	readFileSync,
	readdirSync,
	realpathSync,
	rmSync,
	writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";

import { makeCreationInput, TITLE } from "#tests/support/publication-fixtures.ts";

const entry = resolve(dirname(fileURLToPath(import.meta.url)), "../../scripts/prepare_pr_review.ts");
const roots: string[] = [];

function root(): string {
	const path = mkdtempSync(join(tmpdir(), "prepare-pr-review-test-"));
	roots.push(path);
	return path;
}

function write(path: string, content: string): string {
	writeFileSync(path, content);
	return path;
}

afterEach(() => {
	for (const path of roots.splice(0)) rmSync(path, { recursive: true, force: true });
});

describe("standalone content skill", () => {
	it("generates a body and receipt from an isolated copy with only its provisioned runtime dependency", () => {
		const directory = root();
		const runtime = join(directory, "skill");
		const sourceRoot = resolve(dirname(entry), "..");
		mkdirSync(runtime, { recursive: true });
		cpSync(join(sourceRoot, "package.json"), join(runtime, "package.json"));
		cpSync(join(sourceRoot, "scripts"), join(runtime, "scripts"), { recursive: true });
		const runtimeModules = join(runtime, "node_modules");
		mkdirSync(runtimeModules, { recursive: true });
		cpSync(realpathSync(join(sourceRoot, "node_modules", "zod")), join(runtimeModules, "zod"), {
			recursive: true,
			dereference: true,
		});
		const input = write(join(directory, "publication.json"), makeCreationInput());
		const body = join(directory, "body.md");
		const env = { ...process.env };
		delete env.NODE_PATH;
		delete env.NODE_OPTIONS;

		const result = spawnSync(
			process.execPath,
			[join(runtime, "scripts", "prepare_pr_review.ts"), "--input", input, "--output", body],
			{ cwd: runtime, encoding: "utf8", env },
		);

		expect(result.status).toBe(0);
		expect(readdirSync(runtimeModules)).toEqual(["zod"]);
		expect(existsSync(join(runtimeModules, "vitest"))).toBe(false);
		expect(JSON.parse(readFileSync(`${body}.receipt.json`, "utf8"))).toEqual({
			status: "prepared",
			title: TITLE,
		});
	});
});
