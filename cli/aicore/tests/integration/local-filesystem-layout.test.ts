/**
 * Integration: the layout adapter across its real filesystem boundary.
 *
 * Three concerns live here, all exercised against a real isolated filesystem in
 * a disposable root (contract T4, T18).
 *
 * The directory enumeration defines what a cleared directory root puts in a
 * distribution set. Every assertion reads entry metadata with `lstat`, so a
 * delivered entry is proven to be a regular file rather than the target of a
 * link. The one assertion over the checkout's own skill root states a property
 * that holds whether or not that root's dependencies are installed, so it never
 * depends on the operator's install state.
 *
 * The instruction-root detection resolves the destination's root runtime file:
 * a supported instruction file is detected, another name is never guessed, and
 * a recorded root is resolved at the recorded path.
 *
 * The post-payload blocker planning decides what the reconciliation blocker
 * write should contain, given the pending payload writes: the planned content
 * is compared against the content the executor's own writes leave behind, so a
 * projection that disagrees with the execution cannot pass unnoticed.
 */

import { lstat, mkdir, readFile, symlink, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import { removeFile, writeBytesFile, writeTextFile } from "#infrastructure/synchronization/local-files.ts";
import { syncReconciliationBlocker } from "#domain/synchronization/reconciliation.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";
import { makeBindingsDocument } from "#support/synchronization.factory.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-layout-";

/** Prefix for the throwaway roots the capability probes create. */
const PROBE_PREFIX = "aicore-cli-layout-probe-";

/**
 * Create a link at `path` that points at the directory `target`.
 *
 * Windows refuses a directory symbolic link without an elevated privilege but
 * creates a junction without elevation, and a junction is the same non-regular
 * entry the distribution rule must skip; POSIX creates a directory symbolic
 * link. Both are created here so a case expresses the platform-independent rule.
 */
async function createDirectoryLink(target: string, path: string): Promise<void> {
	await symlink(resolve(dirname(path), target), path, process.platform === "win32" ? "junction" : "dir");
}

/** Return `true` when this platform lets the suite create a directory link. */
async function canCreateDirectoryLinks(): Promise<boolean> {
	const created = await createTemporaryRoot(PROBE_PREFIX);
	try {
		await mkdir(join(created.root, "target"), { recursive: true });
		await createDirectoryLink("target", join(created.root, "link"));
		return true;
	} catch {
		return false;
	} finally {
		await disposeTemporaryRoot(created.root, created.prefix);
	}
}

/**
 * Return `true` when this platform lets the suite create a symbolic link.
 *
 * Windows refuses symbolic links without an elevated privilege, so the
 * file-link case is reported as skipped there rather than as covered.
 */
async function canCreateSymlinks(): Promise<boolean> {
	const created = await createTemporaryRoot(PROBE_PREFIX);
	try {
		await symlink("target", join(created.root, "link"));
		return true;
	} catch {
		return false;
	} finally {
		await disposeTemporaryRoot(created.root, created.prefix);
	}
}

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

describe("instruction root detection", () => {
	const document = makeBindingsDocument({ root: null });

	test("a destination whose instruction file has another name is not detected, and no name is guessed", async () => {
		await writeFixture("CLAUDE.md", "# this project's instructions\n");

		// Detection reads only the supported instruction file.
		expect(await layout.detectRootFile(root)).toBeNull();
		// With nothing to detect the root path is the supported file's own path,
		// which the reader reports missing, so the enrollment refuses instead.
		expect(await layout.resolveRootFile(root, document)).toBe(join(root, "AGENTS.md"));
	});

	test("a destination holding the supported instruction file detects and resolves it", async () => {
		await writeFixture("AGENTS.md", "# shared instructions\n");

		expect(await layout.detectRootFile(root)).toBe("AGENTS.md");
		expect(await layout.resolveRootFile(root, document)).toBe(join(root, "AGENTS.md"));
	});

	test("a document recording a root resolves at the recorded path", async () => {
		await writeFixture("AGENTS.md", "# shared instructions\n");
		await writeFixture("docs/CLAUDE.md", "# another file\n");

		expect(await layout.resolveRootFile(root, makeBindingsDocument({ root: "docs/CLAUDE.md" }))).toBe(
			join(root, "docs", "CLAUDE.md"),
		);
	});
});

describe("post-payload blocker planning", () => {
	const document = makeBindingsDocument({ root: null });
	const pending = ["example.md"];
	const body = "# instructions\n";
	const expected = (text: string) => syncReconciliationBlocker(text, pending, "opencode", []);

	test("plans against a newly created implicit root without creating it", async () => {
		const path = join(root, "AGENTS.md");
		const result = await layout.planBlocker(
			root,
			document,
			pending,
			[],
			[{ kind: "text-write", path, content: "# instructions\r\n" }],
		);
		expect(result).toEqual({ path, content: expected(body) });
		await expect(lstat(path)).rejects.toMatchObject({ code: "ENOENT" });
	});

	test("selects the explicit root even when AGENTS exists", async () => {
		await writeFixture("AGENTS.md", "# other\n");
		await writeFixture("custom.md", body);
		const path = join(root, "custom.md");
		const result = await layout.planBlocker(root, makeBindingsDocument({ root: "custom.md" }), pending, [], []);
		expect(result).toEqual({ path, content: expected(body) });
		expect(await readFile(path, "utf8")).toBe(body);
	});

	test("reads existing root content and plans a blocker mutation", async () => {
		await writeFixture("AGENTS.md", body);
		const path = join(root, "AGENTS.md");
		expect(await layout.planBlocker(root, document, pending, [], [])).toEqual({ path, content: expected(body) });
		expect(await readFile(path, "utf8")).toBe(body);
	});

	test("omits a blocker write when content is already current", async () => {
		await writeFixture("AGENTS.md", expected(body));
		expect(await layout.planBlocker(root, document, pending, [], [])).toBeNull();
	});

	test("does not plan a blocker on a retired implicit root", async () => {
		await writeFixture("AGENTS.md", body);
		const path = join(root, "AGENTS.md");
		expect(await layout.planBlocker(root, document, pending, [], [{ kind: "file-delete", path }])).toBeNull();
		expect(await readFile(path, "utf8")).toBe(body);
	});

	test("uses the last ordered byte write as the root's effective UTF-8 content", async () => {
		await writeFixture("AGENTS.md", "# old\n");
		const path = join(root, "AGENTS.md");
		const result = await layout.planBlocker(
			root,
			document,
			pending,
			[],
			[
				{ kind: "file-delete", path },
				{ kind: "byte-write", path, content: new TextEncoder().encode(body) },
			],
		);
		expect(result).toEqual({ path, content: expected(body) });
	});

	test("projection agrees with execution after ordered payload writes", async () => {
		const path = join(root, "AGENTS.md");
		await writeFixture("AGENTS.md", "# prior\n");
		const bytes = new TextEncoder().encode("# bytes\r\n");
		const projected = await layout.planBlocker(
			root,
			document,
			pending,
			[],
			[
				{ kind: "file-delete", path },
				{ kind: "byte-write", path, content: bytes },
				{ kind: "text-write", path, content: "# final\r\nline\r" },
			],
		);
		expect(await readFile(path, "utf8")).toBe("# prior\n");
		await removeFile(path);
		await writeBytesFile(path, bytes);
		await writeTextFile(path, "# final\r\nline\r");
		await layout.syncBlocker(root, document, pending, []);
		expect(projected).toEqual({ path, content: await readFile(path, "utf8") });
	});

	test("a byte-written file with a byte order mark projects what its own read produces", async () => {
		const path = join(root, "AGENTS.md");
		const bytes = new Uint8Array([0xef, 0xbb, 0xbf, ...new TextEncoder().encode("# bytes\n")]);
		const projected = await layout.planBlocker(
			root,
			document,
			pending,
			[],
			[{ kind: "byte-write", path, content: bytes }],
		);
		await writeBytesFile(path, bytes);
		await layout.syncBlocker(root, document, pending, []);
		// The projection keeps the byte order mark, exactly as the read that
		// follows the write produces it.
		expect(projected).toEqual({ path, content: await readFile(path, "utf8") });
		expect(projected?.content.startsWith("﻿")).toBe(true);
	});
});
