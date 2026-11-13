/** Native Node.js entry point for validating durable feature files. */

import { ValidateFeatureFiles } from "./feature_file_validation/application/validate_feature_files.ts";
import {
  InvalidFeatureFileError,
  NoFeatureFileDocumentsError,
} from "./feature_file_validation/domain/records.ts";
import { FilesystemFeatureFileSource } from "./feature_file_validation/infrastructure/filesystem.ts";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

export {
  assessFeatureFile as assess_feature_file,
  validateFeatureFile as validate_feature_file,
} from "./feature_file_validation/domain/rules.ts";
import type { PathComparisonPolicy } from "./feature_file_validation/domain/rules.ts";

/** The host path-comparison policy: Windows paths compare case-insensitively. */
const hostPathComparisonPolicy: PathComparisonPolicy = {
  caseSensitive: process.platform !== "win32",
};

export function main(
  args: readonly string[],
  print: (line: string) => void = console.log,
): number {
  if (args.length !== 1) {
    print("usage: validate_feature_file.ts <file-or-directory>");
    return 2;
  }

  const target = args[0]!;
  let failed = false;
  const operation = new ValidateFeatureFiles(
    new FilesystemFeatureFileSource(),
    hostPathComparisonPolicy,
  );
  for (const result of operation.execute(target)) {
    if (result instanceof NoFeatureFileDocumentsError) {
      print(result.message);
      failed = true;
    } else if (result instanceof InvalidFeatureFileError) {
      failed = true;
      print(`FAIL ${result.path}`);
      for (const finding of result.findings) print(`  - ${finding}`);
    } else {
      print(`ok ${result.path} — status: ${result.status}`);
    }
  }
  return failed ? 1 : 0;
}

function isDirectExecution(): boolean {
  const entry = process.argv[1];
  return entry !== undefined && pathToFileURL(resolve(entry)).href === import.meta.url;
}

if (isDirectExecution()) process.exitCode = main(process.argv.slice(2));
