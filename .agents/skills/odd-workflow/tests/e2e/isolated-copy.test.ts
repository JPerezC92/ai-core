import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import { makeFeature } from "#tests/support/feature-fixtures.ts";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const runtimeFiles = [
  "scripts/validate_feature.ts",
  "scripts/feature_validation/domain/records.ts",
  "scripts/feature_validation/domain/ports.ts",
  "scripts/feature_validation/domain/rules.ts",
  "scripts/feature_validation/application/validate_features.ts",
  "scripts/feature_validation/infrastructure/filesystem.ts",
];
/** The copy carries the runtime modules and the ESM boundary that makes them modules. */
const copyFiles = ["package.json", ...runtimeFiles];
const temporaryDirectories: string[] = [];

function createEnvironment(): { root: string; runtime: string; fixtures: string } {
  const root = mkdtempSync(join(tmpdir(), "odd-workflow-feature-e2e-"));
  temporaryDirectories.push(root);
  const runtime = join(root, "isolated-skill");
  const fixtures = join(root, "fixtures");
  for (const file of copyFiles) {
    const destination = join(runtime, file);
    mkdirSync(dirname(destination), { recursive: true });
    cpSync(join(skillRoot, file), destination);
  }
  mkdirSync(fixtures, { recursive: true });
  return { root, runtime, fixtures };
}

/** Runs the copied entry point with the environment's Node binary and no dependency paths. */
function runIsolatedNode(runtime: string, args: string[]): ReturnType<typeof spawnSync> {
  const environment = { ...process.env };
  delete environment.NODE_PATH;
  delete environment.NODE_OPTIONS;
  return spawnSync(
    process.execPath,
    [join(runtime, "scripts", "validate_feature.ts"), ...args],
    { cwd: runtime, encoding: "utf8", env: environment },
  );
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("validate_feature process in an isolated source-only copy", () => {
  it("pins one ok line per document and skips the template of a directory that holds both", () => {
    const { runtime, fixtures } = createEnvironment();
    const documents = join(fixtures, "valid");
    mkdirSync(documents);
    writeFileSync(join(documents, "_template.md"), makeFeature("Feature name"), "utf8");
    writeFileSync(join(documents, "feature.md"), makeFeature(), "utf8");

    const run = runIsolatedNode(runtime, [documents]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(0);
    expect(String(run.stdout)).toBe(`ok ${join(documents, "feature.md")}\n`);
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
    expect(String(run.stdout)).toBe("usage: validate_feature.ts <file-or-directory>\n");
    expect(String(run.stderr)).toBe("");
  });

  it("pins the invalid-document diagnostic and its exit status", () => {
    const { runtime, fixtures } = createEnvironment();
    const file = join(fixtures, "invalid.md");
    writeFileSync(file, makeFeature("Feature name"), "utf8");

    const run = runIsolatedNode(runtime, [file]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(1);
    expect(String(run.stdout)).toBe(`FAIL ${file}\n  - title must not be the template placeholder\n`);
    expect(String(run.stderr)).toBe("");
  });

  it("pins the no-documents output and its exit status for a template-only directory", () => {
    const { runtime, fixtures } = createEnvironment();
    const documents = join(fixtures, "template-only");
    mkdirSync(documents);
    writeFileSync(join(documents, "_template.md"), makeFeature("Feature name"), "utf8");

    const run = runIsolatedNode(runtime, [documents]);

    expect(run.error).toBeUndefined();
    expect(run.status).toBe(1);
    expect(String(run.stdout)).toBe("no feature documents found\n");
    expect(String(run.stderr)).toBe("");
  });
});
