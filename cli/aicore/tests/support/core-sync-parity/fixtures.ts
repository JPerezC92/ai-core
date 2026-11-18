/**
 * Synthetic fixtures for the parity corpus.
 *
 * Every fixture is built from scratch inside a disposable temporary root: a
 * synthetic source tree and a synthetic destination tree, never the real
 * checkout and never a real project. The destination root's own directory name
 * is fixed, because the merge mode derives the QMD index from it.
 */

import { link, mkdir, symlink, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";

import type { FixtureSpec } from "./types.ts";

/** Prefix that identifies a fixture root this corpus owns. */
export const FIXTURE_PREFIX = "aicore-parity-";

/** The destination root's directory name; the merge mode derives its index from it. */
export const PROJECT_NAME = "project-under-test";

/** The name of the source clearance registry inside the source root. */
export const CLEARANCE_FILE = "distribution-clearance.json";

/** A valid 40-character lowercase hex revision. */
export const REVISION = "0123456789abcdef0123456789abcdef01234567";

/** A second valid revision, for the drift cases. */
export const OTHER_REVISION = "fedcba9876543210fedcba9876543210fedcba98";

/**
 * The error codes that mean "this platform refuses the link", never "our call is wrong".
 *
 * `EINVAL` is deliberately absent: it reports a malformed link argument, which
 * is a defect in this fixture, not a missing platform capability.
 */
const LINK_CAPABILITY_REFUSALS: ReadonlySet<string> = new Set(["EPERM", "EACCES", "ENOSYS"]);

/**
 * Return `true` only when `error` reports a platform refusal to create a link.
 *
 * The capability probes use this so a genuine filesystem fault is rethrown and
 * fails the case instead of quietly skipping it as an unsupported platform.
 */
export function isLinkCapabilityRefusal(error: unknown): boolean {
	const code = (error as { readonly code?: unknown } | null | undefined)?.code;
	return typeof code === "string" && LINK_CAPABILITY_REFUSALS.has(code);
}

/** A materialised fixture: the two roots, the bindings path, and its cleanup. */
export type MaterialisedFixture = {
	readonly root: string;
	readonly sourceRoot: string;
	readonly destinationRoot: string;
	readonly bindingsPath: string;
	dispose(): Promise<void>;
};

/** Materialise a fixture's source tree, destination tree and documents. */
export async function materialiseFixture(spec: FixtureSpec): Promise<MaterialisedFixture> {
	const created = await createTemporaryRoot(FIXTURE_PREFIX);
	const root = created.root;
	const destinationRoot = join(root, PROJECT_NAME);
	const sourceRoot =
		spec.nestedSourceInsideDestination === true ? join(destinationRoot, "source") : join(root, "source");

	await mkdir(sourceRoot, { recursive: true });
	await mkdir(destinationRoot, { recursive: true });

	for (const file of spec.sourceFiles ?? []) {
		const absolute = join(sourceRoot, file.path);
		await mkdir(dirname(absolute), { recursive: true });
		await writeFile(absolute, file.content, "utf8");
	}
	for (const linkSpec of spec.sourceLinks ?? []) {
		await symlink(linkSpec.target, join(sourceRoot, linkSpec.path));
	}
	for (const directoryLink of spec.sourceDirectoryLinks ?? []) {
		const absolute = join(sourceRoot, directoryLink.path);
		await mkdir(dirname(absolute), { recursive: true });
		await createDirectoryLink(directoryLink.target, absolute);
	}
	for (const hardLink of spec.sourceHardLinks ?? []) {
		await link(join(sourceRoot, hardLink.target), join(sourceRoot, hardLink.path));
	}
	if (spec.clearance !== null && spec.clearance !== undefined) {
		await writeFile(join(sourceRoot, CLEARANCE_FILE), spec.clearance, "utf8");
	}

	for (const directory of spec.destinationDirectories ?? []) {
		await mkdir(join(destinationRoot, directory), { recursive: true });
	}
	for (const file of spec.destinationFiles ?? []) {
		const absolute = join(destinationRoot, file.path);
		await mkdir(dirname(absolute), { recursive: true });
		await writeFile(absolute, file.content, "utf8");
	}
	for (const linkSpec of spec.destinationLinks ?? []) {
		const absolute = join(destinationRoot, linkSpec.path);
		await mkdir(dirname(absolute), { recursive: true });
		await symlink(linkSpec.target, absolute);
	}
	for (const hardLink of spec.destinationHardLinks ?? []) {
		const absolute = join(destinationRoot, hardLink.path);
		await mkdir(dirname(absolute), { recursive: true });
		await link(join(destinationRoot, hardLink.target), absolute);
	}
	if (spec.bindings !== null && spec.bindings !== undefined) {
		const bindingsPath = join(destinationRoot, ".aicore", "core.yaml");
		await mkdir(dirname(bindingsPath), { recursive: true });
		await writeFile(bindingsPath, spec.bindings, "utf8");
	}

	return {
		root,
		sourceRoot,
		destinationRoot,
		bindingsPath: join(destinationRoot, ".aicore", "core.yaml"),
		async dispose(): Promise<void> {
			await disposeTemporaryRoot(root, created.prefix);
		},
	};
}

/**
 * Return `true` when this platform lets the fixture create a symbolic link.
 *
 * Windows refuses symbolic links without an elevated privilege, so the
 * corpus's link cases are skipped there rather than silently reported as
 * covered. The probe runs once per process and never touches a real path.
 * Only a capability refusal is recorded as `false`; any other failure — and any
 * failure creating or disposing the probe root — propagates and fails the case.
 */
let symlinkSupport: boolean | undefined;

export async function canCreateSymlinks(): Promise<boolean> {
	if (symlinkSupport !== undefined) {
		return symlinkSupport;
	}
	const created = await createTemporaryRoot(FIXTURE_PREFIX);
	try {
		try {
			await symlink("target", join(created.root, "link"));
			symlinkSupport = true;
		} catch (error) {
			if (!isLinkCapabilityRefusal(error)) {
				throw error;
			}
			symlinkSupport = false;
		}
	} finally {
		await disposeTemporaryRoot(created.root, created.prefix);
	}
	return symlinkSupport;
}

/**
 * Create a link at `path` that points at the directory `target`.
 *
 * Windows refuses a directory symbolic link without an elevated privilege but
 * creates a junction without elevation, and a junction is the same non-regular
 * entry the distribution rule must skip; POSIX creates a directory symbolic
 * link. Both are created here so a case expresses the platform-independent rule.
 */
export async function createDirectoryLink(target: string, path: string): Promise<void> {
	const absoluteTarget = resolve(dirname(path), target);
	await symlink(absoluteTarget, path, process.platform === "win32" ? "junction" : "dir");
}

/**
 * Return `true` when this platform lets the fixture create a directory link.
 *
 * The probe creates a real directory link inside a disposable root and records
 * `false` only for a capability refusal, so a directory-link case is reported as
 * skipped only where the platform actually refuses one — never unconditionally.
 * Any other link-creation failure, and any failure creating or disposing the
 * probe root, propagates and fails the case.
 */
let directoryLinkSupport: boolean | undefined;

export async function canCreateDirectoryLinks(): Promise<boolean> {
	if (directoryLinkSupport !== undefined) {
		return directoryLinkSupport;
	}
	const created = await createTemporaryRoot(FIXTURE_PREFIX);
	try {
		await mkdir(join(created.root, "target"), { recursive: true });
		try {
			await createDirectoryLink("target", join(created.root, "link"));
			directoryLinkSupport = true;
		} catch (error) {
			if (!isLinkCapabilityRefusal(error)) {
				throw error;
			}
			directoryLinkSupport = false;
		}
	} finally {
		await disposeTemporaryRoot(created.root, created.prefix);
	}
	return directoryLinkSupport;
}
