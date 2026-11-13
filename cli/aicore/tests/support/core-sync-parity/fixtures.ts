/**
 * Synthetic fixtures for the parity corpus.
 *
 * Every fixture is built from scratch inside a disposable temporary root: a
 * synthetic source tree and a synthetic destination tree, never the real
 * checkout and never a real project. The destination root's own directory name
 * is fixed, because the merge mode derives the QMD index from it.
 */

import { link, mkdir, symlink, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";

import {
  createTemporaryRoot,
  disposeTemporaryRoot,
} from "#support/disposable-root.ts";

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
    spec.nestedSourceInsideDestination === true
      ? join(destinationRoot, "source")
      : join(root, "source");

  await mkdir(sourceRoot, { recursive: true });
  await mkdir(destinationRoot, { recursive: true });

  for (const file of spec.sourceFiles ?? []) {
    await writeFile(join(sourceRoot, file.path), file.content, "utf8");
  }
  for (const linkSpec of spec.sourceLinks ?? []) {
    await symlink(linkSpec.target, join(sourceRoot, linkSpec.path));
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
 */
let symlinkSupport: boolean | undefined;

export async function canCreateSymlinks(): Promise<boolean> {
  if (symlinkSupport !== undefined) {
    return symlinkSupport;
  }
  const created = await createTemporaryRoot(FIXTURE_PREFIX);
  try {
    await symlink("target", join(created.root, "link"));
    symlinkSupport = true;
  } catch {
    symlinkSupport = false;
  } finally {
    await disposeTemporaryRoot(created.root, created.prefix);
  }
  return symlinkSupport;
}
