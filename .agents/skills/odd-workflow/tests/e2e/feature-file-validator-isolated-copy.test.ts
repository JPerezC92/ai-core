import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import {
  makeApostropheFeatureFile,
  makeFeatureFile,
} from "#tests/support/feature-file-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const runtimeFiles = [
  "scripts/validate_feature_file.ts",
  "scripts/feature_file_validation/domain/records.ts",
  "scripts/feature_file_validation/domain/ports.ts",
  "scripts/feature_file_validation/domain/rules.ts",
  "scripts/feature_file_validation/application/validate_feature_files.ts",
  "scripts/feature_file_validation/infrastructure/filesystem.ts",
];
/** The copy carries the runtime modules and the ESM boundary that makes them modules. */
const copyFiles = ["package.json", ...runtimeFiles];
const temporaryDirectories: string[] = [];

function createEnvironment(): { runtime: string; fixtures: string } {
  const root = mkdtempSync(join(tmpdir(), "odd-workflow-feature-file-e2e-"));
  temporaryDirectories.push(root);
  const runtime = join(root, "isolated-skill");
  const fixtures = join(root, "fixtures");
  for (const file of copyFiles) {
    const destination = join(runtime, file);
    mkdirSync(dirname(destination), { recursive: true });
    cpSync(join(skillRoot, file), destination);
  }
  mkdirSync(fixtures, { recursive: true });
  return { runtime, fixtures };
}

/** Runs the copied entry point with the environment's Node binary and no dependency paths. */
function runIsolatedNode(runtime: string, args: string[]): ReturnType<typeof spawnSync> {
  const environment = { ...process.env };
  delete environment.NODE_PATH;
  delete environment.NODE_OPTIONS;
  return spawnSync(
    process.execPath,
    [join(runtime, "scripts", "validate_feature_file.ts"), ...args],
    { cwd: runtime, encoding: "utf8", env: environment },
  );
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("validate_feature_file process in an isolated source-only copy", () => {
  it("pins the ok line with the derived status and skips the template of a directory that holds both", () => {
    const { runtime, fixtures } = createEnvironment();
    const documents = join(fixtures, "valid");
    mkdirSync(documents);
    writeFileSync(join(documents, "_template.md"), makeFeatureFile(), "utf8");
    writeFileSync(join(documents, "feature.md"), makeFeatureFile(), "utf8");

    const run = runIsolatedNode(runtime, [documents]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(0);
    expect(String(run.stdout)).toBe(`ok ${join(documents, "feature.md")} — status: partial\n`);
    expect(String(run.stderr)).toBe("");
    expect(readdirSync(runtime).sort()).toEqual(["package.json", "scripts"]);
    expect(existsSync(join(runtime, "node_modules"))).toBe(false);
    expect(existsSync(join(runtime, "cli", "aicore"))).toBe(false);
  });

  it("pins the usage error, its message and its exit status", () => {
    const { runtime } = createEnvironment();

    const run = runIsolatedNode(runtime, []);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(2);
    expect(String(run.stdout)).toBe("usage: validate_feature_file.ts <file-or-directory>\n");
    expect(String(run.stderr)).toBe("");
  });

  it("pins the status-derivation diagnostic and its exit status", () => {
    const { runtime, fixtures } = createEnvironment();
    const file = join(fixtures, "invalid.md");
    writeFileSync(file, makeFeatureFile("achieved"), "utf8");

    const run = runIsolatedNode(runtime, [file]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(1);
    expect(String(run.stdout)).toBe(
      `FAIL ${file}\n  - feature-file-status-derivation: declared status 'achieved' does not match the status derived from the ticks 'partial'\n`,
    );
    expect(String(run.stderr)).toBe("");
  });

  it("pins the double-quoted diagnostics for apostrophe-bearing values and their exit status", () => {
    const { runtime, fixtures } = createEnvironment();
    const file = join(fixtures, "apostrophe.md");
    writeFileSync(file, makeApostropheFeatureFile(), "utf8");

    const run = runIsolatedNode(runtime, [file]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(1);
    expect(String(run.stdout)).toBe(
      `FAIL ${file}\n` +
        `  - feature-file-status: status must be one of 'achieved', 'partial' or 'not started'; found "achieved's"\n` +
        `  - feature-file-requirement-mark: requirement 1 carries an unknown mark "owner's mark"; marks are 'upstream', 'upstream · local detail', 'upstream · narrowed', 'local' or 'local · conflicts'\n`,
    );
    expect(String(run.stderr)).toBe("");
  });

  it("pins the no-files output and its exit status for a template-only directory", () => {
    const { runtime, fixtures } = createEnvironment();
    const documents = join(fixtures, "template-only");
    mkdirSync(documents);
    writeFileSync(join(documents, "_template.md"), makeFeatureFile(), "utf8");

    const run = runIsolatedNode(runtime, [documents]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(1);
    expect(String(run.stdout)).toBe("no feature files found\n");
    expect(String(run.stderr)).toBe("");
  });
});
