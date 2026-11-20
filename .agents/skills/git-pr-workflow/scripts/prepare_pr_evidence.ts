/** Compose PR review evidence preparation commands from local files and read-only Git data. */

import { compactJson, isDirectExecution, printError, printOut } from "#scripts/cli_delivery.ts";
import { AssembleReviewSnapshot } from "#scripts/pr_review/application/assemble_review_snapshot.ts";
import { CollectLocalInventory } from "#scripts/pr_review/application/collect_local_inventory.ts";
import { PrepareLocalSnapshot } from "#scripts/pr_review/application/prepare_local_snapshot.ts";
import { VerifyPersistedBody } from "#scripts/pr_review/application/verify_persisted_body.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import { decodeCapture } from "#scripts/pr_review/infrastructure/adapters/pr_capture.ts";
import { publicationTitle } from "#scripts/pr_review/infrastructure/adapters/prepared_receipt.ts";
import {
	decodeExactPaths,
	decodeLocalInventory,
} from "#scripts/pr_review/infrastructure/adapters/snapshot_assembly.ts";
import { createText, readText, InputOutputFailure } from "#scripts/pr_review/infrastructure/filesystem.ts";
import { GitBoundaryError, GitReader } from "#scripts/pr_review/infrastructure/git_reader.ts";
import { decodeSnapshot } from "#scripts/attribution_scan/infrastructure/adapters/snapshot_document.ts";
import { SnapshotValidationError } from "#scripts/attribution_scan/domain/records.ts";

/** The commands this entry point composes. */
const COMMAND_NAMES = ["snapshot", "prepare-snapshot", "prepare-local", "verify"] as const;

/** The options every command requires. */
const COMMAND_OPTIONS = new Map<string, readonly string[]>([
	["snapshot", ["--input", "--paths", "--output"]],
	["prepare-snapshot", ["--receipt", "--body", "--inventory", "--paths", "--output"]],
	["prepare-local", ["--pr", "--base", "--receipt", "--body", "--output"]],
	["verify", ["--baseline", "--current", "--body"]],
]);

/** The name this entry point reports in its own diagnostics. */
const PROGRAM_NAME = "prepare_pr_evidence.ts";

/** A command line that the entry point cannot accept. */
class UsageError extends Error {
	readonly command: string | undefined;

	constructor(message: string, command?: string) {
		super(message);
		this.name = "UsageError";
		this.command = command;
	}
}

/** Report whether a decoded name is one of the composed commands. */
function isCommandName(name: string): name is (typeof COMMAND_NAMES)[number] {
	return (COMMAND_NAMES as readonly string[]).includes(name);
}

/** Convert one command-line value to a positive integer or reject it. */
function positiveInteger(value: string): number | null {
	const trimmed = value.trim();
	if (!/^[+-]?[0-9]+$/u.test(trimmed)) return null;
	const number = Number(trimmed);
	return Number.isSafeInteger(number) && number >= 1 ? number : null;
}

/** Parse the command line into one command and its required option values. */
function parseArguments(argv: readonly string[]): { name: string; options: Map<string, string> } {
	const name = argv[0];
	if (name === undefined) {
		throw new UsageError("the following arguments are required: command");
	}
	if (!isCommandName(name)) {
		throw new UsageError(
			`argument command: invalid choice: '${name}' (choose from 'snapshot', 'prepare-snapshot', 'prepare-local', 'verify')`,
		);
	}
	const allowed = COMMAND_OPTIONS.get(name) ?? [];
	const options = new Map<string, string>();
	const unrecognized: string[] = [];
	for (let index = 1; index < argv.length; index += 1) {
		const argument = argv[index] ?? "";
		if (!allowed.includes(argument)) {
			unrecognized.push(argument);
			continue;
		}
		const value = argv[index + 1];
		if (value === undefined) {
			throw new UsageError(`argument ${argument}: expected one argument`, name);
		}
		options.set(argument, value);
		index += 1;
	}
	if (name === "prepare-local") {
		const value = options.get("--pr");
		if (value !== undefined && positiveInteger(value) === null) {
			throw new UsageError(`argument --pr: a positive integer is required: ${value}`, name);
		}
	}
	const missing = allowed.filter((option) => !options.has(option));
	if (missing.length > 0) {
		throw new UsageError(`the following arguments are required: ${missing.join(", ")}`, name);
	}
	if (unrecognized.length > 0) {
		throw new UsageError(`unrecognized arguments: ${unrecognized.join(" ")}`, name);
	}
	return { name, options };
}

/** Report the usage line and the diagnostic of one rejected command line. */
function reportUsage(error: UsageError): number {
	if (error.command === undefined) {
		printError(`usage: ${PROGRAM_NAME} <command> [options]\n`);
		printError(`${PROGRAM_NAME}: error: ${error.message}\n`);
		return 2;
	}
	const allowed = COMMAND_OPTIONS.get(error.command) ?? [];
	const usage = allowed.map((option) => `${option} ${option.slice(2).toUpperCase()}`).join(" ");
	printError(`usage: ${PROGRAM_NAME} ${error.command}${usage === "" ? "" : ` ${usage}`}\n`);
	printError(`${PROGRAM_NAME} ${error.command}: error: ${error.message}\n`);
	return 2;
}

/** Report one refused preparation and end the command with the refusal status. */
function reportRefusal(error: ReviewPreparationError): number {
	printOut(`${compactJson({ code: error.code, message: error.message })}\n`);
	return 1;
}

export function main(argv: readonly string[]): number {
	let parsed: { name: string; options: Map<string, string> };
	try {
		parsed = parseArguments(argv);
	} catch (error) {
		if (error instanceof UsageError) return reportUsage(error);
		throw error;
	}
	const options = parsed.options;
	try {
		if (parsed.name === "snapshot") {
			const collected = decodeSnapshot(JSON.parse(readText(options.get("--input") ?? "")));
			if (collected instanceof SnapshotValidationError) {
				return reportRefusal(new ReviewPreparationError("SNAPSHOT_INVALID", collected.message));
			}
			const paths = decodeExactPaths(JSON.parse(readText(options.get("--paths") ?? "")));
			if (paths instanceof ReviewPreparationError) return reportRefusal(paths);
			const result = new AssembleReviewSnapshot().execute(collected, paths);
			if (result instanceof ReviewPreparationError) return reportRefusal(result);
			createText(options.get("--output") ?? "", `${JSON.stringify(result, null, 2)}\n`);
		} else if (parsed.name === "prepare-snapshot") {
			const receipt: unknown = JSON.parse(readText(options.get("--receipt") ?? ""));
			const body = readText(options.get("--body") ?? "");
			const inventoryValue = JSON.parse(readText(options.get("--inventory") ?? ""));
			const pathsValue = JSON.parse(readText(options.get("--paths") ?? ""));
			const title = publicationTitle(receipt);
			if (title instanceof ReviewPreparationError) return reportRefusal(title);
			const inventory = decodeLocalInventory(inventoryValue);
			if (inventory instanceof ReviewPreparationError) return reportRefusal(inventory);
			const exactPaths = decodeExactPaths(pathsValue);
			if (exactPaths instanceof ReviewPreparationError) return reportRefusal(exactPaths);
			const result = new PrepareLocalSnapshot().execute(title, body, inventory, exactPaths);
			if (result instanceof ReviewPreparationError) return reportRefusal(result);
			createText(options.get("--output") ?? "", `${JSON.stringify(result, null, 2)}\n`);
		} else if (parsed.name === "prepare-local") {
			const prValue = options.get("--pr") ?? "";
			const prNumber = positiveInteger(prValue);
			if (prNumber === null) {
				throw new UsageError(`argument --pr: a positive integer is required: ${prValue}`, parsed.name);
			}
			const receipt: unknown = JSON.parse(readText(options.get("--receipt") ?? ""));
			const body = readText(options.get("--body") ?? "");
			const collected = new CollectLocalInventory(new GitReader()).execute(prNumber, options.get("--base") ?? "");
			if (collected instanceof ReviewPreparationError) return reportRefusal(collected);
			const title = publicationTitle(receipt);
			if (title instanceof ReviewPreparationError) return reportRefusal(title);
			const result = new PrepareLocalSnapshot().execute(title, body, collected.inventory, collected.paths);
			if (result instanceof ReviewPreparationError) return reportRefusal(result);
			createText(options.get("--output") ?? "", `${JSON.stringify(result, null, 2)}\n`);
		} else {
			const baseline = decodeCapture(JSON.parse(readText(options.get("--baseline") ?? "")));
			if (baseline instanceof ReviewPreparationError) return reportRefusal(baseline);
			const current = decodeCapture(JSON.parse(readText(options.get("--current") ?? "")));
			if (current instanceof ReviewPreparationError) return reportRefusal(current);
			const candidate = readText(options.get("--body") ?? "");
			const outcome = new VerifyPersistedBody().execute(baseline, current, candidate);
			if (outcome instanceof ReviewPreparationError) return reportRefusal(outcome);
		}
		printOut(`${compactJson({ status: "prepared", command: parsed.name })}\n`);
		return 0;
	} catch (error) {
		if (error instanceof UsageError) return reportUsage(error);
		if (error instanceof GitBoundaryError) {
			printError(`git read failure: ${error.message}\n`);
			return 2;
		}
		if (error instanceof SyntaxError || error instanceof InputOutputFailure) {
			printError(`input/output failure: ${error.message}\n`);
			return 2;
		}
		throw error;
	}
}

if (isDirectExecution(import.meta.url)) process.exitCode = main(process.argv.slice(2));
