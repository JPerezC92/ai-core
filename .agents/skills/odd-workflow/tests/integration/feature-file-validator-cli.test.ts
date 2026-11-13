import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { main as validateFeatureFiles } from "../../scripts/validate_feature_file.ts";
import {
  makeApostropheFeatureFile,
  makeFeatureFile,
} from "../support/feature-file-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "odd-workflow-feature-file-cli-"));
  temporaryDirectories.push(directory);
  return directory;
}

function invoke(args: string[]): { code: number; output: string } {
  const lines: string[] = [];
  const code = validateFeatureFiles(args, (line: string) => lines.push(line));
  return {
    code,
    output: lines.join("\n") + (lines.length ? "\n" : ""),
  };
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("validate_feature_file CLI with the real filesystem adapter", () => {
  it("prints derived status, skips the template, and returns usage/no-files statuses", () => {
    const directory = makeDirectory();
    writeFileSync(join(directory, "_template.md"), makeFeatureFile(), "utf8");
    const file = join(directory, "feature.md");
    writeFileSync(file, makeFeatureFile(), "utf8");

    expect(invoke([directory])).toEqual({
      code: 0,
      output: `ok ${file} — status: partial\n`,
    });
    expect(invoke([])).toEqual({
      code: 2,
      output: "usage: validate_feature_file.ts <file-or-directory>\n",
    });

    const templateOnly = join(directory, "template-only");
    mkdirSync(templateOnly);
    writeFileSync(join(templateOnly, "_template.md"), makeFeatureFile(), "utf8");
    expect(invoke([templateOnly])).toEqual({
      code: 1,
      output: "no feature files found\n",
    });
  });

  it("prints the Python-compatible invalid-document diagnostic and exit status", () => {
    const directory = makeDirectory();
    const file = join(directory, "invalid.md");
    writeFileSync(file, makeFeatureFile("achieved"), "utf8");

    expect(invoke([file])).toEqual({
      code: 1,
      output: `FAIL ${file}\n  - feature-file-status-derivation: declared status 'achieved' does not match the status derived from the ticks 'partial'\n`,
    });
  });

  it("prints the Python repr quoting for an apostrophe-bearing status and mark", () => {
    const directory = makeDirectory();
    const file = join(directory, "apostrophe.md");
    writeFileSync(file, makeApostropheFeatureFile(), "utf8");

    expect(invoke([file])).toEqual({
      code: 1,
      output:
        `FAIL ${file}\n` +
        `  - feature-file-status: status must be one of 'achieved', 'partial' or 'not started'; found "achieved's"\n` +
        `  - feature-file-requirement-mark: requirement 1 carries an unknown mark "owner's mark"; marks are 'upstream', 'upstream · local detail', 'upstream · narrowed', 'local' or 'local · conflicts'\n`,
    });
  });

  it("preserves earlier output when a later UTF-8 read fails", () => {
    const directory = makeDirectory();
    const earlier = join(directory, "a.md");
    writeFileSync(earlier, makeFeatureFile(), "utf8");
    writeFileSync(join(directory, "z.md"), Buffer.from([0xff]));
    const lines: string[] = [];

    expect(() => validateFeatureFiles([directory], (line) => lines.push(line))).toThrow();
    expect(lines).toEqual([`ok ${earlier} — status: partial`]);
  });
});
