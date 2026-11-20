/**
 * Integration: removing a managed destination file through the real adapter.
 *
 * One behavioral concern — deleting the file a retired source used to own —
 * exercised over a real disposable root, because the primitive's contract is the
 * filesystem's answer, not a double's.
 */

import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { LocalDestinationFiles } from "#infrastructure/synchronization/local-destination-files.ts";
import { createTemporaryRoot, disposeTemporaryRoot } from "#support/disposable-root.ts";

describe("removing a managed destination file", () => {
	let root = "";
	let prefix = "";
	const destinations = new LocalDestinationFiles();

	beforeEach(async () => {
		const created = await createTemporaryRoot("managed-file-removal");
		root = created.root;
		prefix = created.prefix;
	});

	afterEach(async () => {
		await disposeTemporaryRoot(root, prefix);
	});

	test("an existing managed file is deleted from disk", async () => {
		const path = join(root, "skills", "a.ts");
		await destinations.writeBytes(path, new TextEncoder().encode("payload\n"));
		expect(await destinations.readBytes(path)).not.toBeNull();

		await destinations.remove(path);

		expect(await destinations.readBytes(path)).toBeNull();
	});

	test("an already absent path is not an error", async () => {
		const path = join(root, "skills", "gone.ts");

		await expect(destinations.remove(path)).resolves.toBeUndefined();
	});
});
