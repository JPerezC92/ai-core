/** Compose PR review evidence preparation commands from local files and read-only Git data. */

import { AssembleReviewSnapshot } from "./pr_review/application/assemble_review_snapshot.ts";
import { CollectLocalInventory } from "./pr_review/application/collect_local_inventory.ts";
import { PrepareLocalSnapshot } from "./pr_review/application/prepare_local_snapshot.ts";
import { VerifyPersistedBody } from "./pr_review/application/verify_persisted_body.ts";
import { ReviewPreparationError } from "./pr_review/domain/records.ts";
import { createText, readText, InputOutputFailure } from "./pr_review/infrastructure/filesystem.ts";
import { GitBoundaryError, GitReader } from "./pr_review/infrastructure/git_reader.ts";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

/** The commands this entry point composes. */
const COMMAND_NAMES = ["snapshot", "prepare-snapshot", "prepare-local", "verify"] as const;

/** The options every command requires. */
const COMMAND_OPTIONS = new Map<string, readonly string[]>([
  ["snapshot", ["--input", "--paths", "--output"]],
  ["prepare-snapshot", ["--draft", "--working-body", "--input", "--paths", "--output"]],
  ["prepare-local", ["--pr", "--base", "--draft", "--working-body", "--output"]],
  ["verify", ["--baseline", "--current", "--working-body"]],
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

/** Escape every character outside printable ASCII as a hexadecimal escape. */
function escapeNonAscii(text: string): string {
  return text.replace(/[\u007f-\uffff]/gu, (character) => {
    const code = character.codePointAt(0) ?? 0;
    if (code <= 0xffff) return `\\u${code.toString(16).padStart(4, "0")}`;
    const adjusted = code - 0x10000;
    const high = 0xd800 + (adjusted >> 10);
    const low = 0xdc00 + (adjusted & 0x3ff);
    return `\\u${high.toString(16).padStart(4, "0")}\\u${low.toString(16).padStart(4, "0")}`;
  });
}

/** Serialize one flat payload the way the documented output is serialized. */
function compactJson(record: Readonly<Record<string, string>>): string {
  const entries = Object.entries(record).map(
    ([key, value]) => `${JSON.stringify(key)}: ${escapeNonAscii(JSON.stringify(value))}`,
  );
  return `{${entries.join(", ")}}`;
}

/** Write one line to the standard output stream. */
function printOut(text: string): void {
  process.stdout.write(text);
}

/** Write one line to the standard error stream. */
function printError(text: string): void {
  process.stderr.write(text);
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
    if (parsed.name === "snapshot" || parsed.name === "prepare-snapshot") {
      const inventory = JSON.parse(readText(options.get("--input") ?? ""));
      const paths = JSON.parse(readText(options.get("--paths") ?? ""));
      const result =
        parsed.name === "prepare-snapshot"
          ? new PrepareLocalSnapshot().execute(
              readText(options.get("--draft") ?? ""),
              readText(options.get("--working-body") ?? ""),
              inventory,
              paths,
            )
          : new AssembleReviewSnapshot().execute(inventory, paths);
      if (result instanceof ReviewPreparationError) {
        printOut(`${compactJson({ code: result.code, message: result.message })}\n`);
        return 1;
      }
      createText(options.get("--output") ?? "", `${JSON.stringify(result, null, 2)}\n`);
    } else if (parsed.name === "prepare-local") {
      const prValue = options.get("--pr") ?? "";
      const prNumber = positiveInteger(prValue);
      if (prNumber === null) {
        throw new UsageError(`argument --pr: a positive integer is required: ${prValue}`, parsed.name);
      }
      const result = new CollectLocalInventory(
        new GitReader(),
        new PrepareLocalSnapshot(),
      ).execute(
        prNumber,
        options.get("--base") ?? "",
        readText(options.get("--draft") ?? ""),
        readText(options.get("--working-body") ?? ""),
      );
      if (result instanceof ReviewPreparationError) {
        printOut(`${compactJson({ code: result.code, message: result.message })}\n`);
        return 1;
      }
      createText(options.get("--output") ?? "", `${JSON.stringify(result, null, 2)}\n`);
    } else {
      const baseline = JSON.parse(readText(options.get("--baseline") ?? ""));
      const current = JSON.parse(readText(options.get("--current") ?? ""));
      const candidate = readText(options.get("--working-body") ?? "");
      const outcome = new VerifyPersistedBody().execute(baseline, current, candidate);
      if (outcome instanceof ReviewPreparationError) {
        printOut(`${compactJson({ code: outcome.code, message: outcome.message })}\n`);
        return 1;
      }
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

function isDirectExecution(): boolean {
  const entry = process.argv[1];
  return entry !== undefined && pathToFileURL(resolve(entry)).href === import.meta.url;
}

if (isDirectExecution()) process.exitCode = main(process.argv.slice(2));
