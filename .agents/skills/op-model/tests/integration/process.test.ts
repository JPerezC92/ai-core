import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";

import { ModelSourceFailure } from "#scripts/op_model_lookup/domain/catalog.ts";
import { OpencodeModelSource } from "#scripts/op_model_lookup/infrastructure/process.ts";
import { create, listingOf } from "#tests/support/model.factory.ts";

/**
 * Integration: the child-process adapter across its real boundary.
 *
 * The external program is a controlled substitute the test owns — this file's
 * own interpreter running a generated script — so the adapter's real spawn,
 * real status classification and real parse-to-domain mapping are exercised
 * without depending on any installed `opencode` binary (T4, T18).
 */
const temporaryDirectories: string[] = [];

afterEach(() => {
	for (const directory of temporaryDirectories.splice(0)) {
		rmSync(directory, { recursive: true, force: true });
	}
});

/** Run `body` as the adapter's external command. */
function sourceRunning(body: string): OpencodeModelSource {
	const directory = mkdtempSync(join(tmpdir(), "op-model-source-"));
	temporaryDirectories.push(directory);
	const script = join(directory, "command.mjs");
	writeFileSync(script, body, "utf8");
	return new OpencodeModelSource({ executable: process.execPath, args: [script] });
}

/** A command that prints `stdout` and succeeds. */
function sourcePrinting(stdout: string): OpencodeModelSource {
	return sourceRunning(`process.stdout.write(${JSON.stringify(stdout)});`);
}

describe("catalog mapping", () => {
	it("maps selector output to models, including a final line without a newline", () => {
		const expected = [
			create(),
			create({ config: "openai/gpt-5.1", id: "gpt-5.1", provider: "openai", name: "gpt-5.1" }),
		];

		expect(sourcePrinting(`${listingOf(expected).trimEnd()}`).fetch()).toEqual(expected);
	});

	it("returns the valid models when the output also carries a non-selector line", () => {
		const model = create({ config: "openai/gpt-5.1", id: "gpt-5.1", provider: "openai", name: "gpt-5.1" });

		expect(sourcePrinting(`not a selector\n${listingOf([model])}`).fetch()).toEqual([model]);
	});

	it("returns an empty selection when the command reports no models", () => {
		expect(sourcePrinting("").fetch()).toEqual([]);
	});
});

describe("failure classification", () => {
	it("maps a non-zero exit to a boundary failure naming the status and stderr", () => {
		const source = sourceRunning('process.stderr.write("boom\\n"); process.exit(3);');

		expect(() => source.fetch()).toThrow(ModelSourceFailure);
		expect(() => source.fetch()).toThrow("ERROR: `opencode models` failed (exit 3):\nboom\n");
	});

	it("reports a missing executable as the documented boundary failure", () => {
		const source = new OpencodeModelSource({ executable: "opencode-absent-from-path", args: ["models"] });

		expect(() => source.fetch()).toThrow("ERROR: `opencode` not found on PATH. Cannot list models.");
	});
});
