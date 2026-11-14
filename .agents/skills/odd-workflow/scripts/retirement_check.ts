/**
 * Native Node.js entry point reporting ODD task records eligible for retirement.
 *
 * The check is a read-only report. It never deletes, writes or mutates anything:
 * the first actual deletion requires the user's authorization and is executed by
 * the release manager.
 */

import { CheckRetirements } from "#scripts/retirement_check/application/check_retirements.ts";
import { NoTaskRecordsError } from "#scripts/retirement_check/domain/records.ts";
import { parseCalendarDate } from "#scripts/retirement_check/domain/rules.ts";
import { FilesystemRetirementSource } from "#scripts/retirement_check/infrastructure/filesystem.ts";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const USAGE = "usage: retirement_check.ts <tasks-directory> [--as-of YYYY-MM-DD]";
const AS_OF_FLAG = "--as-of";

export { evaluateRetirement as retirement_eligibility } from "#scripts/retirement_check/domain/rules.ts";

/** The report date, as a `YYYY-MM-DD` calendar date in UTC. */
export function currentUtcDate(now: Date = new Date()): string {
  return now.toISOString().slice(0, 10);
}

export function main(
  args: readonly string[],
  print: (line: string) => void = console.log,
): number {
  const positional: string[] = [];
  let asOfDate = currentUtcDate();

  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index]!;
    if (argument === AS_OF_FLAG) {
      const value = args[index + 1];
      if (value === undefined) {
        print(USAGE);
        return 2;
      }
      asOfDate = value;
      index += 1;
      continue;
    }
    if (argument.startsWith("--")) {
      print(USAGE);
      return 2;
    }
    positional.push(argument);
  }

  if (positional.length !== 1) {
    print(USAGE);
    return 2;
  }

  if (parseCalendarDate(asOfDate) === null) {
    print(USAGE);
    return 2;
  }

  let candidates = 0;
  let records = 0;
  try {
    for (const result of new CheckRetirements(new FilesystemRetirementSource()).execute(
      positional[0]!,
      asOfDate,
    )) {
      if (result instanceof NoTaskRecordsError) {
        print(result.message);
        return 1;
      }
      records += 1;
      if (result.decision.kind === "candidate") {
        candidates += 1;
        print(
          `candidate ${result.path} - closed ${result.decision.closedOn}; ${result.decision.ageDays} complete calendar days`,
        );
      } else {
        print(`excluded ${result.path} - ${result.decision.reason}`);
      }
    }
  } catch (error) {
    print(`retirement check failed: ${error instanceof Error ? error.message : String(error)}`);
    return 1;
  }

  print(`${candidates} candidates of ${records} records`);
  return 0;
}

function isDirectExecution(): boolean {
  const entry = process.argv[1];
  return entry !== undefined && pathToFileURL(resolve(entry)).href === import.meta.url;
}

if (isDirectExecution()) process.exitCode = main(process.argv.slice(2));
