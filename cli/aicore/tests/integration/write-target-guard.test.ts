/**
 * Integration: the write-target preflight across its real filesystem boundary.
 *
 * One behavioral concern — `LocalWriteTargetGuard` refuses the write-target
 * shapes the domain rule rejects, and returns no refusal for a fully-inside set.
 * The guard, the layout and the filesystem all run for real over a disposable
 * root (contract T4, T18); nothing is doubled (T17).
 *
 * Every case is reachable without a symbolic link, because this platform cannot
 * create a file symbolic link and a case that can only skip would protect
 * nothing. The domain rule refuses overlapping roots, a managed target that
 * escapes the destination root, one that resolves inside the source tree, one
 * that is not a regular file, two declared targets that resolve to one path, and
 * a root alias with a raw or merge destination — the non-link half of the safety
 * contract the adapter exists to enforce.
 */

import { link, mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { MODE_RAW, MODE_REGION } from "#domain/synchronization/constants.ts";
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

/** The root runtime file's name, which the layout resolves when none is detected. */
const ROOT_FILE = "AGENTS.md";

let root: string;
let rootPrefix: string;
let sourceRoot: string;
let destinationRoot: string;
const guard = new LocalWriteTargetGuard(new LocalFilesystemLayout());

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

	test("a fully-inside target set earns no refusal", async () => {
		expect(await guard.refuse(makeRequest())).toBeNull();
	});

	test("an init whose raw creation would become the implicit root is refused", async () => {
		// No root is recorded and the destination holds no instruction file, so a
		// raw destination named AGENTS.md would become the root file itself.
		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, {
				command: "init",
				newRawDestinations: new Set(["AGENTS.md"]),
			}),
		);

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toContain("default root would alias newly created raw destination");
	});

	test("a target that shares the inode of a source-tree file is refused", async () => {
		const sourceFile = join(sourceRoot, "shared-source.md");
		const payload = join(destinationRoot, PAYLOAD_RELATIVE);
		await writeFile(sourceFile, "# shared\n", "utf8");
		await mkdir(join(destinationRoot, "docs"), { recursive: true });
		// A hard link is an ordinary directory entry, not a symbolic link, so this
		// exercises the inode-aliasing rule rather than the link rule.
		await link(sourceFile, payload);

		const refusal = await guard.refuse(makeRequest());

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(
			`invalid write target: destination payload write target shares a source-tree file inode: ${payload}`,
		);
	});

	test("two declared outputs that share a filesystem inode are refused", async () => {
		const first = join(destinationRoot, "docs/first.md");
		const second = join(destinationRoot, "docs/second.md");
		await mkdir(join(destinationRoot, "docs"), { recursive: true });
		await writeFile(first, "# duplicated\n", "utf8");
		await link(first, second);

		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, {
				document: makeBindingsDocument({
					bindings: [
						{
							source: BOUND_SOURCE,
							destinations: ["docs/first.md", "docs/second.md"],
							declaredMode: MODE_REGION,
						},
					],
				}),
			}),
		);

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(
			`invalid write target: distinct write targets share a filesystem inode: ${first} and ${second}`,
		);
	});
});

describe("root and alias refusals", () => {
	test("overlapping source and destination roots are refused", async () => {
		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, { destinationRoot: join(sourceRoot, DESTINATION_DIRECTORY) }),
		);

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe("invalid write target: source and destination roots overlap");
	});

	test("a second output path that resolves to the same target is refused", async () => {
		// The bindings document and a payload are declared at one path: they are
		// distinct declarations, so writing both would write one target twice.
		const aliased = join(destinationRoot, PAYLOAD_RELATIVE);

		const refusal = await guard.refuse(makeRequest(PAYLOAD_RELATIVE, { bindingsPath: aliased }));

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(
			`invalid write target: distinct write targets alias after resolution: ${aliased} and ${aliased}`,
		);
	});

	test("an init whose root target aliases a non-region destination is refused", async () => {
		// The supported instruction file is absent, so this init has no explicit
		// root and a raw creation at that name would become the root itself.
		const refusal = await guard.refuse({
			command: "init",
			sourceRoot,
			destinationRoot,
			bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			document: makeBindingsDocument({
				root: null,
				bindings: [{ source: BOUND_SOURCE, destinations: [ROOT_FILE], declaredMode: MODE_RAW }],
			}),
			modes: new Map([[BOUND_SOURCE, MODE_RAW]]),
			newRawDestinations: new Set([ROOT_FILE]),
		});

		expect(refusal?.code).toBe("invalid");
		// The aliasing root/payload pair is refused before the later
		// planned-creation arm is reached; both refuse the same input.
		expect(refusal?.message).toBe(
			`invalid write target: root write target aliases non-region destination: ` +
				join(destinationRoot, ROOT_FILE),
		);
	});
});
