/** Prepare one pull-request publication body and its receipt from a JSON publication input. */

import { basename } from "node:path";

import { PreparePublication } from "#scripts/pr_content/application/prepare_publication.ts";
import { isPublicationError } from "#scripts/pr_content/domain/records.ts";
import { renderPublication } from "#scripts/pr_content/domain/rendering.ts";
import { encodePreparationReceipt } from "#scripts/pr_content/infrastructure/adapters/prepared_receipt.ts";
import {
	createArtifact,
	readPublicationInput,
	reserveArtifact,
} from "#scripts/pr_content/infrastructure/filesystem.ts";

interface Options {
	readonly input: string;
	readonly output: string;
}

type ParseResult =
	| { readonly ok: true; readonly help: true }
	| { readonly ok: true; readonly help: false; readonly options: Options }
	| { readonly ok: false; readonly message: string };

/** Serialize the payload with the documented spaced JSON separators. */
function spacedJsonObject(entries: ReadonlyArray<readonly [string, string]>): string {
	const body = entries.map(([key, value]) => `${JSON.stringify(key)}: ${JSON.stringify(value)}`).join(", ");
	return `{${body}}`;
}

function usage(program: string): string {
	return `usage: ${program} [-h] --input <publication.json> --output <body.md>`;
}

function parseCli(args: readonly string[]): ParseResult {
	const values = new Map<string, string>();
	for (let index = 0; index < args.length; index += 1) {
		const arg = args[index]!;
		if (arg === "-h" || arg === "--help") return { ok: true, help: true };
		if (!arg.startsWith("--")) return { ok: false, message: `unrecognized arguments: ${arg}` };
		const value = args[index + 1];
		if (value === undefined) return { ok: false, message: `argument ${arg}: expected one argument` };
		values.set(arg.slice(2), value);
		index += 1;
	}
	for (const field of ["input", "output"]) {
		if (!values.has(field)) return { ok: false, message: `the following arguments are required: --${field}` };
	}
	for (const field of values.keys()) {
		if (field !== "input" && field !== "output")
			return { ok: false, message: `unrecognized arguments: --${field}` };
	}
	return {
		ok: true,
		help: false,
		options: { input: values.get("input")!, output: values.get("output")! },
	};
}

/** Decode supplied files, invoke the operation and serialize results at delivery. */
export function main(argv: readonly string[], program = "prepare_pr_review.ts"): number {
	const parsed = parseCli(argv);
	if (!parsed.ok) {
		process.stderr.write(`${usage(program)}\n${basename(program)}: error: ${parsed.message}\n`);
		return 2;
	}
	if (parsed.help) {
		process.stdout.write(`${usage(program)}\n`);
		return 0;
	}

	try {
		const options = parsed.options;
		const result = new PreparePublication(
			readPublicationInput,
			createArtifact,
			reserveArtifact,
			renderPublication,
			encodePreparationReceipt,
		).execute({
			inputPath: options.input,
			bodyPath: options.output,
			receiptPath: `${options.output}.receipt.json`,
		});
		if (isPublicationError(result)) {
			process.stdout.write(
				`${spacedJsonObject([
					["code", result.code],
					["message", result.message],
				])}\n`,
			);
			return 1;
		}
		process.stdout.write(encodePreparationReceipt(result));
		return 0;
	} catch (error) {
		process.stderr.write(`input/output failure: ${(error as Error).message}\n`);
		return 2;
	}
}

process.exitCode = main(process.argv.slice(2), basename(process.argv[1] ?? "prepare_pr_review.ts"));
