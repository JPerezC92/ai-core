import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import {
  makeApostropheFeatureFile,
  makeFeatureFile,
} from "../support/feature-file-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const repositoryRoot = resolve(skillRoot, "../../..");
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

/** Normalizes the platform line terminator so only the diagnostic text is compared. */
function normalizeLineEndings(text: string): string {
  return text.replaceAll("\r\n", "\n");
}

/** The Python baseline names its own script in the usage line; the entry point names its file. */
const PYTHON_USAGE = "usage: validate_feature_file.py <file-or-directory>";
const NODE_USAGE = "usage: validate_feature_file.ts <file-or-directory>";

/** Normalizes only the exact launcher token; every other byte is compared as it stands. */
function normalizeLauncherToken(text: string): string {
  return text.replaceAll(PYTHON_USAGE, NODE_USAGE);
}

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

function runPythonBaseline(args: string[]): ReturnType<typeof spawnSync> {
  const script = relative(repositoryRoot, join(skillRoot, "scripts", "validate_feature_file.py"));
  return spawnSync("uv", ["run", "--frozen", "python3", script, ...args], {
    cwd: repositoryRoot,
    encoding: "utf8",
  });
}

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

function expectPythonParity(
  runtime: string,
  args: string[],
  expectedStatus: number,
): void {
  const python = runPythonBaseline(args);
  const node = runIsolatedNode(runtime, args);

  expect(python.error).toBeUndefined();
  expect(node.error).toBeUndefined();
  expect(python.status).toBe(expectedStatus);
  expect(node.status).toBe(expectedStatus);
  expect(normalizeLineEndings(String(node.stdout))).toBe(
    normalizeLineEndings(normalizeLauncherToken(String(python.stdout))),
  );
  expect(normalizeLineEndings(String(node.stderr))).toBe(
    normalizeLineEndings(String(python.stderr)),
  );
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("validate_feature_file process in an isolated source-only copy", () => {
  it("matches Python success output and the derived status without dependencies", () => {
    const { runtime, fixtures } = createEnvironment();
    const documents = join(fixtures, "valid");
    mkdirSync(documents);
    writeFileSync(join(documents, "_template.md"), makeFeatureFile(), "utf8");
    writeFileSync(join(documents, "feature.md"), makeFeatureFile(), "utf8");

    expectPythonParity(runtime, [documents], 0);
    expect(readdirSync(runtime).sort()).toEqual(["package.json", "scripts"]);
    expect(existsSync(join(runtime, "node_modules"))).toBe(false);
    expect(existsSync(join(runtime, "cli", "aicore"))).toBe(false);
  });

  it("matches Python usage output and nonzero process status", () => {
    const { runtime } = createEnvironment();

    expectPythonParity(runtime, [], 2);
  });

  it("matches Python invalid-document diagnostics and exit status", () => {
    const { runtime, fixtures } = createEnvironment();
    const file = join(fixtures, "invalid.md");
    writeFileSync(file, makeFeatureFile("achieved"), "utf8");

    expectPythonParity(runtime, [file], 1);
  });

  it("matches Python diagnostics for apostrophe-bearing values", () => {
    const { runtime, fixtures } = createEnvironment();
    const file = join(fixtures, "apostrophe.md");
    writeFileSync(file, makeApostropheFeatureFile(), "utf8");

    expectPythonParity(runtime, [file], 1);
  });

  it("matches Python no-files output for a template-only directory", () => {
    const { runtime, fixtures } = createEnvironment();
    const documents = join(fixtures, "template-only");
    mkdirSync(documents);
    writeFileSync(join(documents, "_template.md"), makeFeatureFile(), "utf8");

    expectPythonParity(runtime, [documents], 1);
  });
});
