/**
 * End to end: enrollment and the subsequent update.
 *
 * Runs the real CLI against the real TypeScript engine, in process. A full
 * synchronization takes tens of seconds because the engine walks the whole
 * cleared set, so this module holds the single test that performs the writes:
 * enrollment, an updating run, and the run that follows the destination's own
 * `pending` reconciliation.
 *
 * The same fixture carries the OpenCode configuration concern — where the
 * configuration lands, that every source top-level key reached it, and that a
 * destination-owned agent model survives the updating write.
 */

import { readFile, stat, writeFile } from "node:fs/promises";
import { basename, join } from "node:path";
import { afterEach, describe, expect, test } from "vitest";

import { parseJsoncObject, type JsoncObject } from "#domain/synchronization/jsonc.ts";
import {
	CHECKOUT,
	REVISION,
	createFixture,
	invokeWithRevision,
	type Fixture,
} from "#support/aicore-cli.e2e-harness.ts";

/** The source-side configuration the OpenCode profile is delivered from. */
const SOURCE_CONFIG = join(CHECKOUT, ".opencode", "opencode.jsonc");

/** The configuration's destination path inside an OpenCode destination. */
const DESTINATION_CONFIG = join(".opencode", "opencode.jsonc");

/** The distributed agent whose destination frontmatter carries a model. */
const AGENT_PATH = join(".opencode", "agents", "forge.md");

/** A model selector the source does not define for any agent. */
const MODEL_LINE = 'model: "destination/own-model"';

let fixture: Fixture | undefined;

afterEach(async () => {
	await fixture?.dispose();
	fixture = undefined;
});

/** Read one JSONC configuration document, failing rather than returning null. */
async function readConfiguration(path: string): Promise<Record<string, unknown>> {
	const object = parseJsoncObject(await readFile(path, "utf8"));
	expect(object, `${path} must be a JSONC object`).not.toBeNull();
	if (object === null) {
		throw new Error(`${path} is not a JSONC object`);
	}
	return { ...object.value };
}

/** Read one value out of a parsed document by its member path. */
function at(document: Record<string, unknown>, path: readonly string[]): unknown {
	let current: unknown = document;
	for (const key of path) {
		if (typeof current !== "object" || current === null) {
			return undefined;
		}
		current = (current as Record<string, unknown>)[key];
	}
	return current;
}

/** Add one frontmatter key to a document, as a destination owner would. */
function withFrontmatterKey(text: string, line: string): string {
	const lines = text.split("\n");
	const close = lines.indexOf("---", 1);
	expect(close).toBeGreaterThan(0);
	lines.splice(close, 0, line);
	return lines.join("\n");
}

/** Clear the destination's own `pending` list, as its owner does. */
function clearPending(text: string): string {
	const lines = text.split("\n");
	const start = lines.indexOf("pending:");
	expect(start).toBeGreaterThanOrEqual(0);
	return [...lines.slice(0, start), "pending: []", ""].join("\n");
}

describe("enrollment and update", () => {
	test("enrollment writes the payload, then a second run updates using the saved selection", async () => {
		const created = await createFixture();
		fixture = created;
		const { destination, configPath } = created;

		const first = await invokeWithRevision(["sync", "--target", destination, "--editor", "opencode"], created);

		// Enrollment succeeds; verification then reports the pending reconciliation
		// the destination project itself must clear. Neither state is overridden.
		expect(first.stdout).toMatch(/initialized/);
		expect(first.status).not.toBe(0);

		const bindings = await readFile(join(destination, ".aicore", "core.yaml"), "utf8");
		expect(bindings).toMatch(/^schema: 1$/m);
		// The bindings record the pinned revision; the contract fixes that value,
		// not the YAML dialect, so the revision may be written quoted or plain.
		expect(bindings).toMatch(new RegExp(`^core_revision: (?:"${REVISION}"|'${REVISION}'|${REVISION})$`, "m"));
		expect(bindings).toMatch(/^pending:$/m);

		// Native discovery locations and shipped documentation are present.
		expect((await stat(join(destination, ".opencode", "agents"))).isDirectory()).toBeTruthy();
		expect((await stat(join(destination, ".aicore", "core", "knowledge", "agents.md"))).isFile()).toBeTruthy();
		expect((await stat(join(destination, ".aicore", "core", "architecture", "README.md"))).isFile()).toBeTruthy();
		expect(
			(await stat(join(destination, ".aicore", "core", "odd", "tasks", "_template.md"))).isFile(),
		).toBeTruthy();

		// The engine's own skill is never distributed to a destination.
		await expect(stat(join(destination, ".opencode", "skills", "core-sync"))).rejects.toThrow();

		// The project configuration lands in the editor's own directory, and no
		// duplicate configuration file is produced at the destination root.
		const destinationConfig = join(destination, DESTINATION_CONFIG);
		expect((await stat(destinationConfig)).isFile()).toBeTruthy();
		expect((await stat(join(destination, ".secrets"))).isDirectory()).toBeTruthy();
		expect((await readFile(join(destination, ".secrets", "context7-api-key"))).byteLength).toBe(0);
		expect(await readFile(join(destination, ".gitignore"), "utf8")).toMatch(/^\.secrets\/$/m);
		await expect(stat(join(destination, "opencode.jsonc"))).rejects.toThrow();
		await expect(stat(join(destination, "opencode.json"))).rejects.toThrow();

		// Every source top-level key reached the merged destination document, and
		// every key but `mcp` carries the source value.
		const source = await readConfiguration(SOURCE_CONFIG);
		const merged = await readConfiguration(destinationConfig);
		const sourceKeys = Object.keys(source);
		expect(sourceKeys.length).toBeGreaterThan(0);
		for (const key of sourceKeys) {
			expect(Object.hasOwn(merged, key), `merged configuration is missing ${key}`).toBe(true);
		}
		for (const key of sourceKeys.filter((candidate) => candidate !== "mcp")) {
			expect(merged[key]).toEqual(source[key]);
		}

		// The `mcp` key merges by server name: the `qmd` index is retargeted to this
		// destination's folder name, and the Context7 header resolves the secret
		// against the destination's own project directory.
		expect(at(merged, ["mcp", "servers", "qmd", "command"])).toContain(basename(destination));
		expect(at(merged, ["mcp", "servers", "context7", "headers", "CONTEXT7_API_KEY"])).toBe(
			"{file:../.secrets/context7-api-key}",
		);

		// Analysis MCP ships with portable launchers. system-one does not ship.
		// No command names an AICore-only path.
		const servers = at(merged, ["mcp", "servers"]);
		expect(servers).toEqual(expect.any(Object));
		const serverNames = Object.keys(servers as Record<string, unknown>);
		expect(serverNames).not.toContain("system-one");
		expect(serverNames).toContain("astgrep");
		expect(serverNames).toContain("semgrep");
		expect(at(merged, ["mcp", "servers", "astgrep", "command"])).toEqual([
			"uvx",
			"--from",
			"git+https://github.com/ast-grep/ast-grep-mcp@149e20d47bb7125fb0c1451feea2f48a98742034",
			"ast-grep-server",
		]);
		expect(at(merged, ["mcp", "servers", "semgrep", "command"])).toEqual([
			"uvx",
			"--from",
			"semgrep==1.182.1",
			"semgrep",
			"mcp",
		]);
		expect(JSON.stringify(servers)).not.toMatch(/mcp-servers\//);
		expect(JSON.stringify(servers)).not.toMatch(/\.opencode\/tooling\//);

		const destinationConfigText = await readFile(destinationConfig, "utf8");
		const destinationObject = parseJsoncObject(destinationConfigText);
		expect(destinationObject).not.toBeNull();
		if (destinationObject === null) {
			throw new Error("destination configuration is not a JSONC object");
		}
		await writeFile(
			destinationConfig,
			withDestinationOwnedSettings(destinationConfigText, destinationObject),
			"utf8",
		);

		// The explicit selection was recorded in the isolated selection file.
		const saved = JSON.parse(await readFile(configPath, "utf8"));
		expect(saved.editor).toBe("opencode");
		expect(saved.target).toBe(destination);

		// A destination-owned model selection: the distributed agent keeps the
		// frontmatter key the source does not define.
		const agentPath = join(destination, AGENT_PATH);
		await writeFile(agentPath, withFrontmatterKey(await readFile(agentPath, "utf8"), MODEL_LINE), "utf8");

		// A second run needs no arguments and updates instead of re-enrolling.
		const second = await invokeWithRevision(["sync"], created);
		expect(second.stdout).toMatch(/applied/);
		expect(second.stdout).not.toMatch(/initialized/);

		// The updating write left the destination-owned model exactly as it was.
		const updatedAgent = await readFile(agentPath, "utf8");
		expect(updatedAgent).toContain(MODEL_LINE);
		expect(updatedAgent.match(/^model:/gmu) ?? []).toHaveLength(1);

		const afterApply = await readConfiguration(destinationConfig);
		expect(afterApply.formatter).toBe(true);
		const afterServers = at(afterApply, ["mcp", "servers"]) as Record<string, unknown>;
		expect(afterServers.destinationOnly).toEqual({
			type: "remote",
			url: "https://example.invalid/mcp",
		});
		expect(Array.isArray(afterApply.permissions)).toBe(true);
		expect((afterApply.permissions as unknown[]).length).toBeGreaterThan(0);
		await expect(stat(join(destination, "opencode.jsonc"))).rejects.toThrow();

		// Once the destination clears its own `pending`, the same payload verifies
		// as current — the configuration included.
		const bindingsPath = join(destination, ".aicore", "core.yaml");
		await writeFile(bindingsPath, clearPending(await readFile(bindingsPath, "utf8")), "utf8");

		const third = await invokeWithRevision(["sync"], created);
		expect(third.stderr).toBe("");
		expect(third.status).toBe(0);
		expect(third.stdout).toMatch(/is current \(opencode\)/);
		expect(await readFile(agentPath, "utf8")).toContain(MODEL_LINE);
	});
});

/**
 * Add a destination-only top-level key and MCP server, and empty the core
 * permission list, as a destination owner would before a later apply.
 */
function withDestinationOwnedSettings(text: string, object: JsoncObject): string {
	const permissions = object.members.find((member) => member.key === "permissions");
	expect(permissions, "the enrolled configuration must define permissions").toBeDefined();
	if (permissions === undefined) {
		throw new Error("permissions member missing");
	}
	const mcp = object.members.find((member) => member.key === "mcp");
	expect(mcp?.members).not.toBeNull();
	const servers = mcp?.members?.members.find((member) => member.key === "servers");
	expect(servers?.members).not.toBeNull();
	if (servers?.members === null || servers === undefined) {
		throw new Error("mcp.servers member missing");
	}
	const insertAt = servers.valueStart + 1;
	const withServer =
		text.slice(0, insertAt) +
		'\n            "destinationOnly": { "type": "remote", "url": "https://example.invalid/mcp" },' +
		text.slice(insertAt);
	const withPermissions = `${withServer.slice(0, permissions.valueStart)}[]${withServer.slice(permissions.valueEnd)}`;
	return withPermissions.replace(/^\{\s*/u, '{\n    "formatter": true,\n    ');
}
