/** Compose the attribution scan CLI from input decoding, the operation, and output. */

import { ScanAttribution } from "./attribution_scan/application/scan_attribution.ts";
import {
  PolicyValidationError,
  SnapshotValidationError,
} from "./attribution_scan/domain/records.ts";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

// Explicit re-export surface: every typed record stays reachable by name.
export type {
  Artifact,
  AttributionPolicy,
  ChangedFile,
  Exclusion,
  Match,
  ScanInput,
  ScanResult,
  Snapshot,
} from "./attribution_scan/domain/records.ts";
export { PolicyValidationError, SnapshotValidationError } from "./attribution_scan/domain/records.ts";

/** The name this entry point reports in its own diagnostics. */
const PROGRAM_NAME = "scan_attribution.ts";

/** The options this entry point requires. */
const REQUIRED_OPTIONS = ["--policy", "--snapshot"];

/** Report that one input file cannot be read. */
class InputUnavailable extends Error {}

/** Report that one input file does not carry valid UTF-8. */
class InvalidEncoding extends Error {}

/** A command line that the entry point cannot accept. */
class UsageError extends Error {}

/** Parse the command line into the required option values. */
function parseArguments(argv: readonly string[]): Map<string, string> {
  const options = new Map<string, string>();
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index] ?? "";
    if (!REQUIRED_OPTIONS.includes(argument)) {
      throw new UsageError(`unrecognized arguments: ${argument}`);
    }
    const value = argv[index + 1];
    if (value === undefined) {
      throw new UsageError(`argument ${argument}: expected one argument`);
    }
    options.set(argument, value);
    index += 1;
  }
  const missing = REQUIRED_OPTIONS.filter((option) => !options.has(option));
  if (missing.length > 0) {
    throw new UsageError(`the following arguments are required: ${missing.join(", ")}`);
  }
  return options;
}

/** Read one input file as UTF-8 text with universal line endings. */
function readInput(path: string): string {
  let raw: Buffer;
  try {
    raw = readFileSync(path);
  } catch {
    throw new InputUnavailable("unable to read input file");
  }
  try {
    return new TextDecoder("utf-8", { fatal: true, ignoreBOM: true })
      .decode(raw)
      .replace(/\r\n?/gu, "\n");
  } catch {
    throw new InvalidEncoding("input is not valid UTF-8");
  }
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

/** Serialize one decoded value with sorted object keys and two-space indentation. */
function toSortedJson(value: unknown): string {
  const render = (item: unknown, depth: number): string => {
    if (Array.isArray(item)) {
      if (item.length === 0) return "[]";
      const pad = "  ".repeat(depth + 1);
      const entries = item.map((entry) => `${pad}${render(entry, depth + 1)}`);
      return `[\n${entries.join(",\n")}\n${"  ".repeat(depth)}]`;
    }
    if (item !== null && typeof item === "object") {
      const record = item as Record<string, unknown>;
      const keys = Object.keys(record).sort();
      if (keys.length === 0) return "{}";
      const pad = "  ".repeat(depth + 1);
      const entries = keys.map(
        (key) => `${pad}${JSON.stringify(key)}: ${render(record[key], depth + 1)}`,
      );
      return `{\n${entries.join(",\n")}\n${"  ".repeat(depth)}}`;
    }
    return JSON.stringify(item) ?? "null";
  };
  return render(value, 0);
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
  printError(`usage: ${PROGRAM_NAME} --policy POLICY --snapshot SNAPSHOT\n`);
  printError(`${PROGRAM_NAME}: error: ${error.message}\n`);
  return 2;
}

export function main(argv: readonly string[]): number {
  let options: Map<string, string>;
  try {
    options = parseArguments(argv);
  } catch (error) {
    if (error instanceof UsageError) return reportUsage(error);
    throw error;
  }
  let policyValue: unknown;
  let snapshotValue: unknown;
  try {
    policyValue = JSON.parse(readInput(options.get("--policy") ?? ""));
    snapshotValue = JSON.parse(readInput(options.get("--snapshot") ?? ""));
  } catch (error) {
    if (error instanceof InputUnavailable) {
      printOut(`${compactJson({ error: "unable to read input file" })}\n`);
      return 2;
    }
    if (error instanceof InvalidEncoding) {
      printOut(`${compactJson({ error: "input is not valid UTF-8" })}\n`);
      return 2;
    }
    printOut(`${compactJson({ error: "input is not valid JSON" })}\n`);
    return 2;
  }
  const result = new ScanAttribution().execute({ snapshotValue, policyValue });
  if (result instanceof PolicyValidationError || result instanceof SnapshotValidationError) {
    printOut(`${compactJson({ error: result.message })}\n`);
    return 2;
  }
  printOut(`${toSortedJson(result)}\n`);
  return result.matches.length > 0 ? 1 : 0;
}

function isDirectExecution(): boolean {
  const entry = process.argv[1];
  return entry !== undefined && pathToFileURL(resolve(entry)).href === import.meta.url;
}

if (isDirectExecution()) process.exitCode = main(process.argv.slice(2));
