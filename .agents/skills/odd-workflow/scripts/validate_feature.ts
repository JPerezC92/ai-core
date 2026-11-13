/** Native Node.js entry point for validating ODD feature documents. */

import { ValidateFeatures } from "./feature_validation/application/validate_features.ts";
import {
  InvalidFeatureError,
  NoFeatureDocumentsError,
} from "./feature_validation/domain/records.ts";
import { FilesystemFeatureSource } from "./feature_validation/infrastructure/filesystem.ts";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

export { validateFeature as validate_feature } from "./feature_validation/domain/rules.ts";
import type { PathComparisonPolicy } from "./feature_validation/domain/rules.ts";

/** The host path-comparison policy: Windows paths compare case-insensitively. */
const hostPathComparisonPolicy: PathComparisonPolicy = {
  caseSensitive: process.platform !== "win32",
};

export function main(
  args: readonly string[],
  print: (line: string) => void = console.log,
): number {
  if (args.length !== 1) {
    print("usage: validate_feature.ts <file-or-directory>");
    return 2;
  }

  const target = args[0]!;
  let failed = false;
  const operation = new ValidateFeatures(
    new FilesystemFeatureSource(),
    hostPathComparisonPolicy,
  );
  for (const result of operation.execute(target)) {
    if (result instanceof NoFeatureDocumentsError) {
      print(result.message);
      failed = true;
    } else if (result instanceof InvalidFeatureError) {
      failed = true;
      print(`FAIL ${result.path}`);
      for (const finding of result.findings) print(`  - ${finding}`);
    } else {
      print(`ok ${result.path}`);
    }
  }
  return failed ? 1 : 0;
}

function isDirectExecution(): boolean {
  const entry = process.argv[1];
  return entry !== undefined && pathToFileURL(resolve(entry)).href === import.meta.url;
}

if (isDirectExecution()) process.exitCode = main(process.argv.slice(2));
