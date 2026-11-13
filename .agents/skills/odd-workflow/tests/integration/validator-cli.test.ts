import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { main as validateFeatures } from "../../scripts/validate_feature.ts";
import { makeFeature, makeFeatureWithApostropheHeading } from "../support/feature-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "odd-workflow-validator-"));
  temporaryDirectories.push(directory);
  return directory;
}

function invoke(main: (args: string[], print?: (line: string) => void) => number, args: string[]): { code: number; output: string } {
  const lines: string[] = [];
  return { code: main(args, (line: string) => lines.push(line)), output: lines.join("\n") + (lines.length ? "\n" : "") };
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("validate_feature CLI with the real filesystem adapter", () => {
  it("prints ordered success output, excludes the template, and reports usage/no-documents statuses", () => {
    const directory = makeDirectory();
    writeFileSync(join(directory, "_template.md"), makeFeature("Feature name"), "utf8");
    writeFileSync(join(directory, "z.md"), makeFeature(), "utf8");
    writeFileSync(join(directory, "a.md"), makeFeature(), "utf8");

    expect(invoke(validateFeatures, [directory])).toEqual({
      code: 0,
      output: `ok ${join(directory, "a.md")}\nok ${join(directory, "z.md")}\n`,
    });
    expect(invoke(validateFeatures, [])).toEqual({
      code: 2,
      output: "usage: validate_feature.ts <file-or-directory>\n",
    });

    const templateOnly = join(directory, "template-only");
    mkdirSync(templateOnly);
    writeFileSync(join(templateOnly, "_template.md"), makeFeature("Feature name"), "utf8");
    expect(invoke(validateFeatures, [templateOnly])).toEqual({
      code: 1,
      output: "no feature documents found\n",
    });
  });

  it("prints the exact invalid-feature diagnostic and exit status", () => {
    const directory = makeDirectory();
    const file = join(directory, "feature.md");
    writeFileSync(file, makeFeature("Feature name"), "utf8");

    expect(invoke(validateFeatures, [file])).toEqual({
      code: 1,
      output: `FAIL ${file}\n  - title must not be the template placeholder\n`,
    });
  });

  it("ignores an unknown heading and reports the duplicated required heading with the exact quoted text", () => {
    const directory = makeDirectory();
    const file = join(directory, "feature.md");
    writeFileSync(file, makeFeatureWithApostropheHeading(), "utf8");

    expect(invoke(validateFeatures, [file])).toEqual({
      code: 1,
      output: `FAIL ${file}\n  - heading '## Tasks' must appear exactly once; found 2\n`,
    });
  });

  it("preserves earlier output when a later filesystem read fails", () => {
    const directory = makeDirectory();
    const earlier = join(directory, "a.md");
    writeFileSync(earlier, makeFeature(), "utf8");
    writeFileSync(join(directory, "z.md"), Buffer.from([0xff]));
    const lines: string[] = [];

    expect(() => validateFeatures([directory], (line) => lines.push(line))).toThrow();
    expect(lines).toEqual([`ok ${earlier}`]);
  });
});
