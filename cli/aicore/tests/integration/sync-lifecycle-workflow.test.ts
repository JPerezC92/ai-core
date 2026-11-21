/**
 * Integration: the managed-source lifecycle as one workflow over real filesystems.
 *
 * One behavioral concern — a destination whose source tree lost two managed
 * sources is reconciled by one real `apply` run. The fully Core-owned raw
 * destination is retired and its binding dropped, the shared region-managed
 * destination is preserved with its project-owned region intact and stays
 * registered as outstanding, and the unrelated changed source is still
 * delivered.
 */

import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { ApplyCoreRevision } from "#application/synchronization/apply-core-revision.ts";
import { CLEARANCE_FILENAME, RECONCILE_BEGIN, RECONCILE_END } from "#domain/synchronization/constants.ts";
import { YamlBindingsStore } from "#infrastructure/synchronization/bindings-store.ts";
import { JsonClearanceStore } from "#infrastructure/synchronization/clearance-store.ts";
import { LocalDestinationFiles } from "#infrastructure/synchronization/local-destination-files.ts";
import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import { LocalSourceFiles } from "#infrastructure/synchronization/local-source-files.ts";
import { LocalWriteTargetGuard } from "#infrastructure/synchronization/write-target-guard.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";
import { makeBindingsDocument, makeSynchronizationRequest } from "#support/synchronization.factory.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-sync-lifecycle-";

/** The fully Core-owned raw source, and the destination it owned. */
const RETIRED_SOURCE = ".agents/skills/retired-skill/SKILL.md";
const RETIRED_DESTINATION = ".agents/skills/retired-skill/SKILL.md";

/** The shared region-managed source, and the destination it landed at. */
const SHARED_SOURCE = ".agents/skills/shared-skill/SKILL.md";
const SHARED_DESTINATION = ".opencode/skills/shared-skill/SKILL.md";

/** The unrelated source whose change still lands, and the destination it owns. */
const LIVE_SOURCE = ".agents/skills/live-skill/SKILL.md";
const LIVE_DESTINATION = ".agents/skills/live-skill/SKILL.md";

/**
 * The registry the source tree holds.
 *
 * The retired and shared sources are gone from the tree, so their directory
 * roots clear nothing for this editor; the registry still declares their
 * ownership, which is what tells a retired destination from a preserved one.
 */
const CLEARANCE = {
	schema: 1,
	cleared: {
		".agents/skills/retired-skill/": { mode: "raw" },
		".agents/skills/shared-skill/": {
			mode: "raw",
			region_files: ["SKILL.md"],
			editors: {
				opencode: { destination: ".opencode/skills/shared-skill/" },
				cursor: { destination: ".cursor/skills/shared-skill/" },
			},
		},
		".agents/skills/live-skill/": { mode: "raw" },
	},
};

/** The destination's own root runtime file, which carries the blocker. */
const ROOT_FILE = "AGENTS.md";

/** The text the destination's root runtime file holds outside the blocker. */
const ROOT_TEXT = "# Destination project\n";

/** The blocker a previous run left in the destination's root runtime file. */
const PREVIOUS_BLOCK = "> **A previous run's blocker.**\n";

/** The shared destination's own text, core region and project region alike. */
const SHARED_DESTINATION_TEXT = [
	"<!-- core:begin -->",
	"stale core body",
	"<!-- core:end -->",
	"",
	"<!-- project:begin -->",
	"destination owned rules",
	"<!-- project:end -->",
	"",
].join("\n");

/** The project-owned region inside the shared destination. */
const PROJECT_REGION_TEXT = "<!-- project:begin -->\ndestination owned rules\n<!-- project:end -->\n";

/** The source the unrelated destination still holds, before the update. */
const STALE_LIVE_TEXT = "stale live body\n";

/** The source's current bytes, which the update must deliver. */
const CURRENT_LIVE_TEXT = "current live body\n";

let root = "";
let prefix = "";
let sourceRoot = "";
let destinationRoot = "";
let bindingsPath = "";

/** Write a file under one root, creating its parent directory. */
async function writeUnder(base: string, relativePath: string, content: string): Promise<string> {
	const path = join(base, relativePath);
	await mkdir(dirname(path), { recursive: true });
	await writeFile(path, content, "utf8");
	return path;
}

/** Report whether a path is there. */
async function isThere(path: string): Promise<boolean> {
	try {
		await access(path);
		return true;
	} catch {
		return false;
	}
}

describe("the managed-source lifecycle as one workflow", () => {
	beforeEach(async () => {
		const created = await createTemporaryRoot(ROOT_PREFIX);
		root = created.root;
		prefix = created.prefix;
		sourceRoot = join(root, "source");
		destinationRoot = join(root, "destination");
		bindingsPath = join(destinationRoot, ".aicore", "core.yaml");

		await mkdir(sourceRoot, { recursive: true });
		await mkdir(destinationRoot, { recursive: true });

		// The source tree: the registry, the two empty directories whose sources
		// were removed, and the one source that still exists.
		await writeUnder(sourceRoot, CLEARANCE_FILENAME, `${JSON.stringify(CLEARANCE, null, 2)}\n`);
		await mkdir(join(sourceRoot, ".agents", "skills", "retired-skill"), { recursive: true });
		await mkdir(join(sourceRoot, ".agents", "skills", "shared-skill"), { recursive: true });
		await writeUnder(sourceRoot, LIVE_SOURCE, CURRENT_LIVE_TEXT);

		// The destination tree: the obsolete raw copy, the shared region-managed
		// copy, the stale copy of the live source, and the root runtime file with
		// the blocker a previous run left in it.
		await writeUnder(destinationRoot, RETIRED_DESTINATION, "obsolete raw body\n");
		await writeUnder(destinationRoot, SHARED_DESTINATION, SHARED_DESTINATION_TEXT);
		await writeUnder(destinationRoot, LIVE_DESTINATION, STALE_LIVE_TEXT);
		await writeUnder(
			destinationRoot,
			ROOT_FILE,
			`${ROOT_TEXT}\n${RECONCILE_BEGIN}\n${PREVIOUS_BLOCK}${RECONCILE_END}\n`,
		);

		const bindings = new YamlBindingsStore();
		await bindings.save(
			bindingsPath,
			makeBindingsDocument({
				bindings: [
					{ source: RETIRED_SOURCE, destinations: [RETIRED_DESTINATION], declaredMode: "raw" },
					{ source: SHARED_SOURCE, destinations: [SHARED_DESTINATION], declaredMode: "region" },
					{ source: LIVE_SOURCE, destinations: [LIVE_DESTINATION], declaredMode: "raw" },
				],
				pending: [],
			}),
		);
	});

	afterEach(async () => {
		await disposeTemporaryRoot(root, prefix);
	});

	test("one apply retires the Core-owned destination, preserves the shared region destination and still delivers the unrelated change", async () => {
		const layout = new LocalFilesystemLayout();
		const bindings = new YamlBindingsStore();
		const useCase = new ApplyCoreRevision({
			bindings,
			clearance: new JsonClearanceStore(),
			sources: new LocalSourceFiles(),
			destinations: new LocalDestinationFiles(),
			layout,
			guard: new LocalWriteTargetGuard(layout),
		});

		const outcome = await useCase.execute(
			makeSynchronizationRequest({
				sourceRoot,
				destinationRoot,
				bindingsPath,
				editor: "opencode",
			}),
		);

		expect(outcome.ok).toBe(true);
		expect(outcome.ok && outcome.message).toContain(`retired: ${RETIRED_DESTINATION}`);

		// The fully Core-owned raw destination is gone from disk.
		expect(await isThere(join(destinationRoot, RETIRED_DESTINATION))).toBe(false);

		// Its binding is gone with it; the other two bindings remain registered.
		const saved = await bindings.load(bindingsPath);
		expect(saved?.bindings.map((entry) => entry.source)).toEqual([SHARED_SOURCE, LIVE_SOURCE]);

		// The shared region-managed destination is still there, byte for byte, so
		// its project-owned region is untouched.
		const sharedText = await readFile(join(destinationRoot, SHARED_DESTINATION), "utf8");
		expect(sharedText).toBe(SHARED_DESTINATION_TEXT);
		expect(sharedText).toContain(PROJECT_REGION_TEXT);

		// Only the shared destination is outstanding.
		expect(saved?.pending).toEqual([SHARED_DESTINATION]);

		// The blocker that already existed is replaced in place, and it names both
		// the missing shared source and its destination. Its markers are counted as
		// exact lines, because the block's own prose quotes them.
		const rootText = await readFile(join(destinationRoot, ROOT_FILE), "utf8");
		const rootLines = rootText.split("\n");
		expect(rootLines.filter((line) => line.trim() === RECONCILE_BEGIN)).toHaveLength(1);
		expect(rootLines.filter((line) => line.trim() === RECONCILE_END)).toHaveLength(1);
		expect(rootText.startsWith(ROOT_TEXT)).toBe(true);
		expect(rootText).toContain(`Source: \`${SHARED_SOURCE}\``);
		expect(rootText).toContain(`Destination: \`${SHARED_DESTINATION}\``);
		expect(rootText).toContain("no longer exists at its registered source path");
		expect(rootText).not.toContain(PREVIOUS_BLOCK);

		// The unrelated safe update still landed.
		expect(await readFile(join(destinationRoot, LIVE_DESTINATION), "utf8")).toBe(CURRENT_LIVE_TEXT);
	});
});
