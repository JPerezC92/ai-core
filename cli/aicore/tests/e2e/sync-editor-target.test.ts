/**
 * End to end: the Cursor editor target.
 *
 * One behavioral concern — a Cursor destination receives the shared content
 * identically, its agents in Cursor's own agent directory, and no project
 * configuration.
 */

import { readdir, readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, describe, expect, test } from "vitest";

import {
	REPRESENTATIVE_AGENT_FILES,
	REVISION,
	createRepresentativeFixture,
	invokeWithRevision,
	type RepresentativeFixture,
} from "#support/aicore-cli.e2e-harness.ts";

let fixture: RepresentativeFixture | undefined;

afterEach(async () => {
	await fixture?.dispose();
	fixture = undefined;
});

describe("cursor editor target", () => {
	test("a cursor destination receives its agents in .cursor/agents and no project configuration", async () => {
		const created = await createRepresentativeFixture();
		fixture = created;
		const { destination, source } = created;

		const result = await invokeWithRevision(
			[
				"init",
				"--source",
				source,
				"--destination",
				destination,
				"--bindings",
				join(destination, ".aicore", "core.yaml"),
				"--source-revision",
				REVISION,
				"--editor",
				"cursor",
				"--bind-cleared",
			],
			created,
		);

		expect(result.stdout, `stderr: ${result.stderr}`).toMatch(/initialized/);

		const cursorAgents = join(destination, ".cursor", "agents");
		expect((await stat(cursorAgents)).isDirectory()).toBeTruthy();
		await expect(stat(join(destination, ".opencode", "agents"))).rejects.toThrow();
		const agentFiles = (await readdir(cursorAgents)).filter((name) => name.endsWith(".md")).sort();
		expect(agentFiles).toEqual([...REPRESENTATIVE_AGENT_FILES]);

		expect((await stat(join(destination, ".agents", "skills", "git-commit", "SKILL.md"))).isFile()).toBeTruthy();
		expect((await stat(join(destination, ".aicore", "core", "knowledge", "agents.md"))).isFile()).toBeTruthy();

		await expect(stat(join(destination, ".opencode", "opencode.jsonc"))).rejects.toThrow();
		await expect(stat(join(destination, "opencode.jsonc"))).rejects.toThrow();
		await expect(stat(join(destination, "opencode.json"))).rejects.toThrow();
		await expect(stat(join(destination, ".secrets"))).rejects.toThrow();
		await expect(stat(join(destination, ".gitignore"))).rejects.toThrow();

		const bindings = await readFile(join(destination, ".aicore", "core.yaml"), "utf8");
		expect(bindings).toMatch(/^editor: cursor$/m);
	});
});
