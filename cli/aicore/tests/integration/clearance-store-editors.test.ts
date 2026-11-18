/**
 * Integration: the clearance registry across its real boundary.
 *
 * One behavioral concern — a registry read from a real temporary file names a
 * destination or an omission for every enrolled editor, and an entry that names
 * only some of them is rejected rather than silently reused. The rejection's
 * diagnostic renders an invalid `role` value verbatim — a primitive as its text,
 * a mapping or list as JSON — so the operator reads the value that was rejected
 * (contract T4).
 */

import { writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { CLEARANCE_FILENAME } from "#domain/synchronization/constants.ts";
import { JsonClearanceStore } from "#infrastructure/synchronization/clearance-store.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";
import { makeClearanceText } from "#support/synchronization.factory.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-clearance-editors-";

const CLEARED_PATH = ".opencode/opencode.jsonc";

let root: string;
let rootPrefix: string;
const store = new JsonClearanceStore();

beforeEach(async () => {
	const created = await createTemporaryRoot(ROOT_PREFIX);
	root = created.root;
	rootPrefix = created.prefix;
});

afterEach(async () => {
	await disposeTemporaryRoot(root, rootPrefix);
});

/** Write one registry into this case's temporary source root. */
async function writeRegistry(cleared: Readonly<Record<string, Readonly<Record<string, unknown>>>>): Promise<void> {
	await writeFile(join(root, CLEARANCE_FILENAME), makeClearanceText(cleared), "utf8");
}

describe("per-editor destinations", () => {
	test("an entry that names one editor and omits another is rejected", async () => {
		await writeRegistry({
			[CLEARED_PATH]: {
				mode: "merge",
				editors: { opencode: { destination: CLEARED_PATH } },
			},
		});

		const loaded = await store.load(root);

		expect(loaded.exists).toBe(true);
		expect(loaded.entries).toBeNull();
		expect(loaded.reason).toMatch(/does not name every editor: cursor/);
	});

	test("an entry that names every enrolled editor is accepted", async () => {
		await writeRegistry({
			[CLEARED_PATH]: {
				mode: "merge",
				editors: {
					opencode: { destination: CLEARED_PATH },
					cursor: { omitted: true },
				},
			},
		});

		const loaded = await store.load(root);

		expect(loaded.reason).toBeNull();
		const entry = loaded.entries?.get(CLEARED_PATH);
		expect(entry?.editors?.get("opencode")).toEqual({
			kind: "delivered",
			destination: CLEARED_PATH,
		});
		expect(entry?.editors?.get("cursor")).toEqual({ kind: "omitted" });
	});
});

/** The diagnostic a registry whose only defect is the role value reports. */
async function reasonForRole(role: unknown): Promise<string> {
	await writeRegistry({ "docs/a.md": { mode: "region", role } });
	const loaded = await store.load(root);
	expect(loaded.entries, `role ${JSON.stringify(role)} was accepted`).toBeNull();
	return loaded.reason ?? "";
}

describe("invalid role diagnostics", () => {
	test("a primitive role is rendered exactly as before", async () => {
		expect(await reasonForRole("owner")).toBe("cleared record for docs/a.md has an invalid role: owner");
		expect(await reasonForRole(7)).toBe("cleared record for docs/a.md has an invalid role: 7");
		expect(await reasonForRole(false)).toBe("cleared record for docs/a.md has an invalid role: false");
		expect(await reasonForRole(null)).toBe("cleared record for docs/a.md has an invalid role: null");
	});

	test("a mapping role is rendered as JSON instead of collapsing it", async () => {
		expect(await reasonForRole({ nested: "value" })).toBe(
			'cleared record for docs/a.md has an invalid role: {"nested":"value"}',
		);
	});

	test("a list role is rendered as JSON instead of joining its members", async () => {
		expect(await reasonForRole(["a", "b"])).toBe('cleared record for docs/a.md has an invalid role: ["a","b"]');
		expect(await reasonForRole([1, 2])).toBe("cleared record for docs/a.md has an invalid role: [1,2]");
	});
});
