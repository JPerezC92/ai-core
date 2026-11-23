/**
 * Integration: the write-target preflight across its real filesystem boundary.
 *
 * One behavioral concern — `LocalWriteTargetGuard` refuses the write-target
 * shapes the domain rule rejects, and returns no refusal for a fully-inside set.
 * The guard, the layout, the readers and the filesystem all run for real over a
 * disposable root (contract T4, T18); nothing the preflight observes is doubled
 * (T17) — the operation-level cases double the document stores only, because
 * those are what the operation reads its document from.
 *
 * Every case is reachable without a symbolic link, because this platform cannot
 * create a file symbolic link and a case that can only skip would protect
 * nothing. The domain rule refuses overlapping roots, a managed target that
 * escapes the destination root, one that resolves inside the source tree, one
 * that is not a regular file, two declared targets that resolve to one path, and
 * a root alias with a raw or merge destination — the non-link half of the safety
 * contract the adapter exists to enforce.
 *
 * The module also holds the two operation-level outcomes the preflight decides:
 * a credential hard-linked to a source file is left untouched when the secret
 * setup has nothing to do, and a write-time filesystem failure surfaces as such
 * instead of becoming a refusal of a plan the run would never perform. Both are
 * proved through the assembled operation, so the preflight's effect on the
 * destination's own files is covered and not only its own diagnostics.
 */

import { link, lstat, mkdir, readFile, symlink, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";
import { mock } from "vitest-mock-extended";

import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
import { EnrollDestinations } from "#application/synchronization/enroll-destinations.ts";
import { MODE_RAW, MODE_REGION } from "#domain/synchronization/constants.ts";
import type { BindingsStore, ClearanceStore, WriteTargetRequest } from "#domain/synchronization/ports.ts";
import { LocalDestinationFiles } from "#infrastructure/synchronization/local-destination-files.ts";
import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import { LocalSourceFiles } from "#infrastructure/synchronization/local-source-files.ts";
import { LocalWriteTargetGuard } from "#infrastructure/synchronization/write-target-guard.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";
import {
	BOUND_SOURCE,
	makeBindingsDocument,
	makeClearanceLoad,
	makeEnrollmentRequest,
	makeSynchronizationRequest,
} from "#support/synchronization.factory.ts";

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
	test("an unchanged raw enrollment is not refused merely because its destination aliases its source", async () => {
		const payload = "payload.txt";
		await writeFile(join(sourceRoot, payload), "unchanged\n");
		await link(join(sourceRoot, payload), join(destinationRoot, payload));
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				editor: "cursor",
				bindings: [{ source: payload, destinations: [payload], declaredMode: MODE_RAW }],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [payload]: { mode: "raw" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new EnrollDestinations({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeEnrollmentRequest({
				editor: "cursor",
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(true);
		expect(await readFile(join(sourceRoot, payload), "utf8")).toBe("unchanged\n");
		expect(await readFile(join(destinationRoot, payload), "utf8")).toBe("unchanged\n");
	});

	test("a credential creation through a directory junction into the source is refused before any write", async () => {
		await mkdir(join(destinationRoot, ".opencode"));
		await writeFile(join(destinationRoot, ".opencode", "opencode.jsonc"), "{}\n");
		await writeFile(join(destinationRoot, ".gitignore"), ".secrets/\n");
		await symlink(sourceRoot, join(destinationRoot, ".secrets"), "junction");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(makeBindingsDocument({ bindings: [] }));
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({}));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(false);
		await expect(readFile(join(sourceRoot, "context7-api-key"))).rejects.toMatchObject({ code: "ENOENT" });
		expect(bindings.save).not.toHaveBeenCalled();
	});

	test("an unsafe retired raw destination is not deleted", async () => {
		const retired = "retired.txt";
		const source = join(sourceRoot, "source-file");
		const destination = join(destinationRoot, retired);
		await writeFile(source, "owned\n");
		await link(source, destination);
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({ bindings: [{ source: retired, destinations: [retired], declaredMode: MODE_RAW }] }),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [retired]: { mode: "raw" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(false);
		expect(await readFile(destination, "utf8")).toBe("owned\n");
		expect(bindings.save).not.toHaveBeenCalled();
	});

	test("a planned OpenCode configuration cannot precede an unsafe conditional ignore write", async () => {
		const configuration = ".opencode/opencode.jsonc";
		const sourceIgnore = join(sourceRoot, "source-ignore");
		const destinationConfiguration = join(destinationRoot, configuration);
		await mkdir(join(sourceRoot, ".opencode"));
		await writeFile(join(sourceRoot, configuration), "{}\n");
		await writeFile(sourceIgnore, "local-rule\n");
		await link(sourceIgnore, join(destinationRoot, ".gitignore"));
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [{ source: configuration, destinations: [configuration], declaredMode: MODE_RAW }],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [configuration]: { mode: "raw" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(false);
		await expect(readFile(destinationConfiguration)).rejects.toMatchObject({ code: "ENOENT" });
		expect(await readFile(sourceIgnore, "utf8")).toBe("local-rule\n");
		expect(bindings.save).not.toHaveBeenCalled();
	});

	test("an existing credential hard-linked to a source is untouched when secret setup is a no-op", async () => {
		const source = join(sourceRoot, "source-credential");
		const secrets = join(destinationRoot, ".secrets");
		const credential = join(secrets, "context7-api-key");
		await writeFile(source, "private\n");
		await mkdir(secrets);
		await link(source, credential);
		await mkdir(join(destinationRoot, ".opencode"));
		await writeFile(join(destinationRoot, ".opencode", "opencode.jsonc"), "{}");
		await writeFile(join(destinationRoot, ".gitignore"), ".secrets/\n");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(makeBindingsDocument({ bindings: [] }));
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({}));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(true);
		expect(await readFile(source, "utf8")).toBe("private\n");
		expect(await readFile(credential, "utf8")).toBe("private\n");
		expect(await readFile(join(destinationRoot, ".gitignore"), "utf8")).toBe(".secrets/\n");
	});

	test("a non-directory secret parent surfaces the write-time error after the ignore rule is applied", async () => {
		const secrets = join(destinationRoot, ".secrets");
		const ignore = join(destinationRoot, ".gitignore");
		await writeFile(secrets, "not a directory\n");
		await writeFile(ignore, "local-rule\n");
		await mkdir(join(destinationRoot, ".opencode"));
		await writeFile(join(destinationRoot, ".opencode", "opencode.jsonc"), "{}");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(makeBindingsDocument({ bindings: [] }));
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({}));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		// The preflight does not refuse: the secret parent already exists, so the
		// directory creation is never performed. The credential write is what
		// fails, and it fails the way a failed write always fails.
		//
		// Acknowledged pre-existing gap: `EEXIST` is missing from the engine's
		// filesystem-error classification, whose owner is
		// `infrastructure/synchronization/local-files.ts`. Until that set names
		// it, the CLI rethrows this error instead of rendering the drift
		// diagnostic; the case pins the write-time failure and the exit class,
		// not the rendering.
		await expect(
			useCase.execute(
				makeSynchronizationRequest({
					sourceRoot,
					destinationRoot,
					bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
				}),
			),
		).rejects.toMatchObject({ code: "EEXIST" });

		// The ignore rule was applied before the credential write failed, and the
		// destination's own file is untouched.
		expect(await readFile(ignore, "utf8")).toBe("local-rule\n.secrets/\n");
		expect(await readFile(secrets, "utf8")).toBe("not a directory\n");
		expect(bindings.save).not.toHaveBeenCalled();
	});

	test("an ignore file hard-linked to a source file is refused before either file changes", async () => {
		const source = join(sourceRoot, "source-ignore");
		const ignore = join(destinationRoot, ".gitignore");
		const original = "local-rule\n";
		await writeFile(source, original);
		await link(source, ignore);
		await mkdir(join(destinationRoot, ".opencode"));
		await writeFile(join(destinationRoot, ".opencode", "opencode.jsonc"), "{}");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(makeBindingsDocument({ bindings: [] }));
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({}));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(false);
		expect(await readFile(source, "utf8")).toBe(original);
		expect(await readFile(ignore, "utf8")).toBe(original);
		expect(bindings.save).not.toHaveBeenCalled();
	});

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

describe("reads over a directory and the secret setup's writes", () => {
	test("a binding that owns the instruction root is refused before the root is overwritten", async () => {
		const rootFile = join(destinationRoot, ROOT_FILE);
		await writeFile(rootFile, "# the destination's own instructions\n");
		await writeFile(join(sourceRoot, BOUND_SOURCE), "# the source\n");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [{ source: BOUND_SOURCE, destinations: [ROOT_FILE], declaredMode: MODE_RAW }],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "raw" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		// A raw binding on the instruction root aliases it: the refusal is the
		// malformed-input class, not a drift report.
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toBe(
			`invalid write target: root write target aliases non-region destination: ${rootFile}`,
		);
		expect(await readFile(rootFile, "utf8")).toBe("# the destination's own instructions\n");
		expect(bindings.save).not.toHaveBeenCalled();
	});

	test("a managed destination that is a directory is refused as an unsafe write target", async () => {
		const payload = join(destinationRoot, PAYLOAD_RELATIVE);
		await mkdir(payload, { recursive: true });
		await writeFile(join(sourceRoot, BOUND_SOURCE), "# the source\n");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [{ source: BOUND_SOURCE, destinations: [PAYLOAD_RELATIVE], declaredMode: MODE_REGION }],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "region" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		// A directory where a destination belongs is an unsafe write target, not
		// a missing file.
		expect(failure?.code).toBe("invalid");
		expect(failure?.message).toBe(`invalid write target: read path is not a regular file: ${payload}`);
		expect(bindings.save).not.toHaveBeenCalled();
	});

	test("a read path that exists as a directory is refused for a payload owner", async () => {
		const payload = join(destinationRoot, PAYLOAD_RELATIVE);
		await mkdir(payload, { recursive: true });

		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, { phase: "read", readPaths: [{ path: payload, owner: "payload" }] }),
		);

		expect(refusal?.code).toBe("invalid");
		// The guard's own read-phase refusal for a payload-owned read, the
		// counterpart of the secret owner's tolerance in the next case.
		expect(refusal?.message).toBe(`invalid write target: read path is not a regular file: ${payload}`);
	});

	test("the secret setup's own read tolerates a directory where the ignore file belongs", async () => {
		const ignore = join(destinationRoot, ".gitignore");
		await mkdir(ignore, { recursive: true });

		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, { phase: "read", readPaths: [{ path: ignore, owner: "secret" }] }),
		);

		expect(refusal).toBeNull();
	});

	test("a secret-owned file write over a directory is not refused before the write raises", async () => {
		const ignore = join(destinationRoot, ".gitignore");
		await mkdir(ignore, { recursive: true });

		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, {
				phase: "mutations",
				mutations: [{ path: ignore, kind: "file-write", owner: "secret" }],
			}),
		);

		expect(refusal).toBeNull();
	});

	test("a payload-owned file write over a directory is still refused", async () => {
		const payload = join(destinationRoot, PAYLOAD_RELATIVE);
		await mkdir(payload, { recursive: true });

		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, {
				phase: "mutations",
				mutations: [{ path: payload, kind: "file-write", owner: "payload" }],
			}),
		);

		expect(refusal?.code).toBe("invalid");
		// The guard's own refusal text for a payload-owned write, which the
		// assembled-operation case does not assert: that one reaches the
		// read-phase refusal instead.
		expect(refusal?.message).toBe(
			`invalid write target: destination payload write target is not a regular file: ${payload}`,
		);
	});

	test("a directory creation whose target already exists as a file is still refused", async () => {
		const secrets = join(destinationRoot, ".secrets");
		await writeFile(secrets, "not a directory\n");

		const refusal = await guard.refuse(
			makeRequest(PAYLOAD_RELATIVE, {
				phase: "mutations",
				mutations: [{ path: secrets, kind: "directory-create", owner: "directory" }],
			}),
		);

		expect(refusal?.code).toBe("invalid");
		expect(refusal?.message).toBe(`invalid write target: directory write target is not a directory: ${secrets}`);
	});
});

describe("a managed path reached through a symlinked ancestor", () => {
	/** The directory inside the destination root a junction may point at. */
	const INSIDE_RELATIVE = "real";
	/** The junction's own name inside the destination root. */
	const LINK_RELATIVE = "linked";
	/** The managed destination reached through that junction. */
	const LINKED_PAYLOAD_RELATIVE = `${LINK_RELATIVE}/payload.md`;

	/**
	 * Create a directory junction.
	 *
	 * A junction is the platform's directory link: it needs no elevated
	 * privilege on Windows, and on POSIX it is the same non-regular entry the
	 * distribution rule skips.
	 */
	async function createJunction(target: string, path: string): Promise<void> {
		await symlink(target, path, "junction");
	}

	/**
	 * The three shapes the commands run: the phase-less shape `check` runs,
	 * and the read and mutation phases `apply` and `init` run.
	 */
	function shapesFor(payload: string): readonly WriteTargetRequest[] {
		const path = join(destinationRoot, payload);
		return [
			makeRequest(payload),
			makeRequest(payload, { phase: "read", readPaths: [{ path, owner: "payload" }] }),
			makeRequest(payload, {
				phase: "mutations",
				mutations: [{ path, kind: "file-write", owner: "payload" }],
			}),
		];
	}

	test("a managed path whose ancestor link resolves inside the destination root is accepted", async () => {
		await mkdir(join(destinationRoot, INSIDE_RELATIVE), { recursive: true });
		await createJunction(join(destinationRoot, INSIDE_RELATIVE), join(destinationRoot, LINK_RELATIVE));

		// The pre-change preflight accepted this layout, and every command's
		// shape agrees on it.
		for (const shape of shapesFor(LINKED_PAYLOAD_RELATIVE)) {
			expect(await guard.refuse(shape), shape.phase ?? "check").toBeNull();
		}
	});

	test("a managed target that is itself a symbolic link is refused", async () => {
		const linkedTarget = "linked-target";
		await mkdir(join(destinationRoot, INSIDE_RELATIVE), { recursive: true });
		await createJunction(join(destinationRoot, INSIDE_RELATIVE), join(destinationRoot, linkedTarget));
		expect((await lstat(join(destinationRoot, linkedTarget))).isSymbolicLink()).toBe(true);

		for (const shape of shapesFor(linkedTarget)) {
			const refusal = await guard.refuse(shape);
			expect(refusal?.code, shape.phase ?? "check").toBe("invalid");
			expect(refusal?.message, shape.phase ?? "check").toBe(
				`invalid write target: destination payload write target is a symbolic link: ` +
					`${join(destinationRoot, linkedTarget)}`,
			);
		}
	});

	test("a managed path whose ancestor link resolves outside the destination root is refused", async () => {
		const outside = join(root, "outside");
		await mkdir(outside, { recursive: true });
		await createJunction(outside, join(destinationRoot, LINK_RELATIVE));

		const path = join(destinationRoot, LINKED_PAYLOAD_RELATIVE);
		// The read phase keeps its published diagnostic, byte for byte.
		const readRefusal = await guard.refuse(
			makeRequest(LINKED_PAYLOAD_RELATIVE, {
				phase: "read",
				readPaths: [{ path, owner: "payload" }],
			}),
		);
		expect(readRefusal?.code).toBe("invalid");
		expect(readRefusal?.message).toBe(`invalid write target: read path escapes destination root: ${path}`);

		// The write shapes refuse the same layout as an escaping write target.
		for (const shape of shapesFor(LINKED_PAYLOAD_RELATIVE).filter((request) => request.phase !== "read")) {
			const refusal = await guard.refuse(shape);
			expect(refusal?.code, shape.phase ?? "check").toBe("invalid");
			expect(refusal?.message, shape.phase ?? "check").toBe(
				`invalid write target: destination payload write target escapes destination root: ${path}`,
			);
		}
	});

	test("a managed path whose ancestor link resolves into the source tree is refused", async () => {
		await createJunction(sourceRoot, join(destinationRoot, LINK_RELATIVE));

		for (const shape of shapesFor(LINKED_PAYLOAD_RELATIVE)) {
			const refusal = await guard.refuse(shape);
			expect(refusal?.code, shape.phase ?? "check").toBe("invalid");
		}
	});

	test("an update whose destination is reached through an inside link completes", async () => {
		await mkdir(join(destinationRoot, INSIDE_RELATIVE), { recursive: true });
		await createJunction(join(destinationRoot, INSIDE_RELATIVE), join(destinationRoot, LINK_RELATIVE));
		await writeFile(join(sourceRoot, BOUND_SOURCE), "# the source\n");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [
					{ source: BOUND_SOURCE, destinations: [LINKED_PAYLOAD_RELATIVE], declaredMode: MODE_REGION },
				],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "region" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(true);
		// The payload lands in the directory the junction points at.
		expect(await readFile(join(destinationRoot, INSIDE_RELATIVE, "payload.md"), "utf8")).toContain("core:begin");
		expect(bindings.save).toHaveBeenCalled();
	});

	test("an update whose destination is reached through an outside link is refused before any write", async () => {
		const outside = join(root, "outside");
		await mkdir(outside, { recursive: true });
		await createJunction(outside, join(destinationRoot, LINK_RELATIVE));
		await writeFile(join(sourceRoot, BOUND_SOURCE), "# the source\n");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(
			makeBindingsDocument({
				bindings: [
					{ source: BOUND_SOURCE, destinations: [LINKED_PAYLOAD_RELATIVE], declaredMode: MODE_REGION },
				],
			}),
		);
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "region" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
			}),
		);

		expect(outcome.ok).toBe(false);
		const failure = outcome.ok ? null : outcome.failure;
		expect(failure?.code).toBe("invalid");
		// Nothing was written: the refusal came before the first mutation.
		expect(bindings.save).not.toHaveBeenCalled();
		await expect(readFile(join(outside, "payload.md"))).rejects.toMatchObject({ code: "ENOENT" });
	});

	test("an enrollment whose destination is reached through an inside link completes", async () => {
		await mkdir(join(destinationRoot, INSIDE_RELATIVE), { recursive: true });
		await createJunction(join(destinationRoot, INSIDE_RELATIVE), join(destinationRoot, LINK_RELATIVE));
		await writeFile(join(sourceRoot, BOUND_SOURCE), "# the source\n");
		const bindings = mock<BindingsStore>();
		bindings.load.mockResolvedValue(makeBindingsDocument({ bindings: [] }));
		const clearance = mock<ClearanceStore>();
		clearance.load.mockResolvedValue(makeClearanceLoad({ [BOUND_SOURCE]: { mode: "region" } }));
		const layout = new LocalFilesystemLayout();
		const useCase = new EnrollDestinations({
			bindings,
			clearance,
			layout,
			guard: new LocalWriteTargetGuard(layout),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
		});

		const outcome = await useCase.execute(
			makeEnrollmentRequest({
				editor: "opencode",
				sourceRoot,
				destinationRoot,
				bindingsPath: join(destinationRoot, BINDINGS_RELATIVE),
				bindCleared: true,
			}),
		);

		expect(outcome.ok).toBe(true);
		expect(bindings.save).toHaveBeenCalled();
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
