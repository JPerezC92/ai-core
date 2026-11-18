/**
 * Integration: the write-target preflight across its real filesystem boundary.
 *
 * One behavioral concern — `LocalWriteTargetGuard` refuses the write-target
 * shapes the domain rule rejects, and returns no refusal for a fully-inside set.
 * The guard, the layout and the filesystem all run for real over a disposable
 * root (contract T4, T18); nothing is doubled (T17).
 *
 * Every case except one is reachable without a symbolic link, because this
 * platform cannot create a file symbolic link and a case that can only skip
 * would protect nothing. The domain rule refuses a managed target that escapes
 * the destination root, one that resolves inside the source tree, and one that
 * is not a regular file — the non-link half of the safety contract the adapter
 * exists to enforce. The link half is executed here through a real directory
 * junction, which Windows creates without elevation and POSIX creates as a
 * directory symbolic link, so the `symbolicLink` refusal is covered rather than
 * assumed.
 */

import { lstat, mkdir, readFile, readdir, symlink, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { MODE_REGION } from "#domain/synchronization/constants.ts";
import type { WriteTargetRequest } from "#domain/synchronization/ports.ts";
import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import { LocalWriteTargetGuard } from "#infrastructure/synchronization/write-target-guard.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";
import { BOUND_SOURCE, makeBindingsDocument } from "#support/synchronization.factory.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-write-target-guard-";

/** The two roots the guard compares, as siblings under the disposable root. */
const SOURCE_DIRECTORY = "source";
const DESTINATION_DIRECTORY = "destination";

/** The bindings document's path, relative to the destination root. */
const BINDINGS_RELATIVE = ".aicore/core.yaml";

/** A managed payload destination that stays inside the destination root. */
const PAYLOAD_RELATIVE = "docs/guide.md";

/** A destination declaration whose `..` segment lands outside the destination root. */
const ESCAPING_PAYLOAD_RELATIVE = "../outside/payload.md";

/**
 * Relative path of a directory outside the destination root that the junction
 * points at. A write through the link would land inside it, so it is the
 * evidence that the refusal prevented a mutation.
 */
const LINKED_TARGET_DIRECTORY = "linked-payload";

/** A file inside the link target, left untouched by a refused command. */
const LINKED_SENTINEL = "sentinel.txt";

/** The sentinel's content, compared before and after the guarded attempt. */
const LINKED_SENTINEL_CONTENT = "untouched\n";

let root: string;
let rootPrefix: string;
let sourceRoot: string;
let destinationRoot: string;
const guard = new LocalWriteTargetGuard(new LocalFilesystemLayout());

/**
 * Create a directory link at `path` pointing at the directory `target`.
 *
 * Windows refuses a directory symbolic link without an elevated privilege but
 * creates a junction without elevation; POSIX creates a directory symbolic
 * link. Both are the same non-regular entry the guard's `symbolicLink`
 * observation reports, so the platform branch stays here and never reaches an
 * assertion.
 */
async function createDirectoryLink(target: string, path: string): Promise<void> {
	await mkdir(dirname(path), { recursive: true });
	await symlink(resolve(target), path, process.platform === "win32" ? "junction" : "dir");
}

beforeEach(async () => {
	const created = await createTemporaryRoot(ROOT_PREFIX);
	root = created.root;
	rootPrefix = created.prefix;
	sourceRoot = join(root, SOURCE_DIRECTORY);
	destinationRoot = join(root, DESTINATION_DIRECTORY);
	await mkdir(sourceRoot, { recursive: true });
	await mkdir(destinationRoot, { recursive: true });
});

afterEach(async () => {
	await disposeTemporaryRoot(root, rootPrefix);
});

/**
 * One `apply` request for this case, binding the factory's source to `payload`.
 *
 * The roots and topology are this module's fixture; the document comes from the
 * shared factory so the case states only the value it varies (T15).
 */
function makeRequest(
	payload: string = PAYLOAD_RELATIVE,
	overrides: Partial<WriteTargetRequest> = {},
): WriteTargetRequest {
	return {
		command: "apply",
		sourceRoot,
		destinationRoot,
		bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
		document: makeBindingsDocument({
			bindings: [{ source: BOUND_SOURCE, destinations: [payload], declaredMode: MODE_REGION }],
		}),
		modes: new Map([[BOUND_SOURCE, MODE_REGION]]),
		newRawDestinations: new Set<string>(),
		...overrides,
	};
}

describe("write-target preflight", () => {
	test("a destination declaration that escapes the destination root is refused", async () => {
		const refusal = await guard.refuse(makeRequest(ESCAPING_PAYLOAD_RELATIVE));

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(
			`invalid write target: destination payload write target escapes destination root: ` +
				`${join(destinationRoot, ESCAPING_PAYLOAD_RELATIVE)}`,
		);
	});

	test("a target that resolves inside the source tree is refused", async () => {
		const bindingsPath = join(sourceRoot, BINDINGS_RELATIVE);

		const refusal = await guard.refuse(makeRequest(PAYLOAD_RELATIVE, { bindingsPath }));

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(
			`invalid write target: bindings write target resolves inside source tree: ${bindingsPath}`,
		);
	});

	test("a target that already exists as a directory where a file is expected is refused", async () => {
		await mkdir(join(destinationRoot, PAYLOAD_RELATIVE), { recursive: true });

		const refusal = await guard.refuse(makeRequest());

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(
			`invalid write target: destination payload write target is not a regular file: ` +
				`${join(destinationRoot, PAYLOAD_RELATIVE)}`,
		);
	});

	test("a managed target that is a symbolic link is refused as a link, not as a non-regular file", async () => {
		const targetDirectory = join(root, LINKED_TARGET_DIRECTORY);
		await mkdir(targetDirectory, { recursive: true });
		await writeFile(join(targetDirectory, LINKED_SENTINEL), LINKED_SENTINEL_CONTENT, "utf8");
		const managedPath = join(destinationRoot, PAYLOAD_RELATIVE);
		await createDirectoryLink(targetDirectory, managedPath);

		expect((await lstat(managedPath)).isSymbolicLink()).toBe(true);

		const refusal = await guard.refuse(makeRequest());

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(
			`invalid write target: destination payload write target is a symbolic link: ${managedPath}`,
		);
		expect(refusal?.message).not.toContain("is not a regular file");
		expect((await lstat(managedPath)).isSymbolicLink()).toBe(true);
		expect(await readdir(targetDirectory)).toEqual([LINKED_SENTINEL]);
		expect(await readFile(join(targetDirectory, LINKED_SENTINEL), "utf8")).toBe(LINKED_SENTINEL_CONTENT);
	});

	test("a fully-inside target set earns no refusal", async () => {
		expect(await guard.refuse(makeRequest())).toBeNull();
	});
});
