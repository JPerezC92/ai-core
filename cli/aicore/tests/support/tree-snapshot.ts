/**
 * Shared destination-tree snapshot for the end-to-end suite.
 *
 * A workflow that must leave a tree untouched is asserted by comparing the
 * tree's exact bytes before and after the run, not by the absence of an obvious
 * edit. Contract T15: the helper lives under the test root instead of being
 * restated in each module that needs it.
 */

import { readFile, readdir } from "node:fs/promises";
import { join, relative, sep } from "node:path";

/** Every entry under `root`, by POSIX-relative path, with its exact bytes. */
export async function snapshotTree(root: string): Promise<[string, string][]> {
	const entries: [string, string][] = [];
	const walk = async (directory: string): Promise<void> => {
		for (const entry of await readdir(directory, { withFileTypes: true })) {
			const absolute = join(directory, entry.name);
			const path = relative(root, absolute).split(sep).join("/");
			if (entry.isDirectory()) {
				entries.push([`${path}/`, "directory"]);
				await walk(absolute);
			} else {
				entries.push([path, (await readFile(absolute)).toString("base64")]);
			}
		}
	};
	await walk(root);
	return entries.sort(([left], [right]) => (left < right ? -1 : left > right ? 1 : 0));
}
