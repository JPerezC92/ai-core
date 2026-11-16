/**
 * Integration: the layout adapter's directory enumeration across its real
 * boundary.
 *
 * The enumeration defines what a cleared directory root puts in a distribution
 * set, so it is exercised against a real isolated filesystem in a disposable
 * root (contract T4, T18). Every assertion reads entry metadata with `lstat`, so
 * a delivered entry is proven to be a regular file rather than the target of a
 * link. The one assertion over the checkout's own skill root states a property
 * that holds whether or not that root's dependencies are installed, so it never
 * depends on the operator's install state.
 */

import { lstat, mkdir, symlink, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import { canCreateDirectoryLinks, canCreateSymlinks, createDirectoryLink } from "#support/core-sync-parity/fixtures.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-layout-";

/** The checkout root, four levels above this file's directory. */
const CHECKOUT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "..", "..");

/** The skill root the checkout-level assertion reads. */
const SKILL_ROOT = join(CHECKOUT, ".agents", "skills", "op-skill-creator");

let root: string;
let rootPrefix: string;
const layout = new LocalFilesystemLayout();
const directoryLinksAvailable = await canCreateDirectoryLinks();
const symlinksAvailable = await canCreateSymlinks();

beforeEach(async () => {
	const created = await createTemporaryRoot(ROOT_PREFIX);
	root = created.root;
	rootPrefix = created.prefix;
});

afterEach(async () => {
	await disposeTemporaryRoot(root, rootPrefix);
});

async function writeFixture(relativePath: string, content: string): Promise<void> {
	const absolute = join(root, relativePath);
	await mkdir(dirname(absolute), { recursive: true });
	await writeFile(absolute, content, "utf8");
}

describe("directory enumeration", () => {
	test("dependency installation directories, the version-control directory and interpreter caches never join", async () => {
		await writeFixture("SKILL.md", "skill body\n");
		await writeFixture("scripts/run.ts", "export const run = () => 0;\n");
		await writeFixture("node_modules/.bin/demo", "#!/bin/sh\n");
		await writeFixture("node_modules/demo/index.js", "module.exports = {};\n");
		await writeFixture(".git/config", "[core]\n");
		await writeFixture("__pycache__/module.cpython-312.pyc", "cache bytes\n");
		await writeFixture("scripts/legacy.pyc", "cache bytes\n");

		expect(await layout.enumerateFilesUnder(root)).toEqual(["SKILL.md", "scripts/run.ts"]);
	});

	test.skipIf(!directoryLinksAvailable)("a directory link is neither followed nor reported", async () => {
		await writeFixture("SKILL.md", "skill body\n");
		await writeFixture("references/guide.md", "reference body\n");
		await createDirectoryLink("references", join(root, "linked"));

		expect(await layout.enumerateFilesUnder(root)).toEqual(["SKILL.md", "references/guide.md"]);
	});

	test.skipIf(!symlinksAvailable)("a file-level link is neither followed nor reported", async () => {
		await writeFixture("SKILL.md", "skill body\n");
		await writeFixture("references/guide.md", "reference body\n");
		await symlink("references/guide.md", join(root, "guide-link.md"));

		expect(await layout.enumerateFilesUnder(root)).toEqual(["SKILL.md", "references/guide.md"]);
	});

	test("every delivered entry of a real skill root is a regular file that is not a link", async () => {
		const enumerated = await layout.enumerateFilesUnder(SKILL_ROOT);

		expect(enumerated).toContain("SKILL.md");
		expect(enumerated.filter((path) => path.includes("node_modules/"))).toEqual([]);
		for (const path of enumerated) {
			const observed = await lstat(join(SKILL_ROOT, path));
			expect(observed.isFile(), `${path} is not a regular file`).toBe(true);
			expect(observed.isSymbolicLink(), `${path} is a link`).toBe(false);
		}
	});
});
