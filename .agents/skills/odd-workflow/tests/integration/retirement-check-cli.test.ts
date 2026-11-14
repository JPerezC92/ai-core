import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { main as checkRetirements } from "#scripts/retirement_check.ts";
import { makeTaskRecord } from "#tests/support/retirement-fixtures.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "odd-workflow-retirement-"));
  temporaryDirectories.push(directory);
  return directory;
}

function invoke(
  args: string[],
): { code: number; output: string } {
  const lines: string[] = [];
  const code = checkRetirements(args, (line: string) => lines.push(line));
  return { code, output: lines.join("\n") + (lines.length ? "\n" : "") };
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("retirement_check CLI with the real filesystem adapter", () => {
  it("reports candidates and exclusion reasons, and exits zero", () => {
    const directory = makeDirectory();
    const candidate = join(directory, "a.md");
    const young = join(directory, "b.md");
    writeFileSync(candidate, makeTaskRecord({ closedOn: "2026-11-01" }), "utf8");
    writeFileSync(young, makeTaskRecord({ closedOn: "2026-11-12" }), "utf8");

    expect(invoke([directory, "--as-of", "2026-11-14"])).toEqual({
      code: 0,
      output:
        `candidate ${candidate} - closed 2026-11-01; 13 complete calendar days\n` +
        `excluded ${young} - 2 complete calendar days since closure; 7 required\n` +
        "1 candidates of 2 records\n",
    });
  });

  it("excludes the template and reports when no records are found", () => {
    const directory = makeDirectory();
    writeFileSync(join(directory, "_template.md"), makeTaskRecord(), "utf8");

    expect(invoke([directory, "--as-of", "2026-11-14"])).toEqual({
      code: 1,
      output: "no task records found\n",
    });
  });

  it("reports a usage error and exits two", () => {
    expect(invoke([])).toEqual({
      code: 2,
      output: "usage: retirement_check.ts <tasks-directory> [--as-of YYYY-MM-DD]\n",
    });
    expect(invoke(["one", "two"])).toEqual({
      code: 2,
      output: "usage: retirement_check.ts <tasks-directory> [--as-of YYYY-MM-DD]\n",
    });
    expect(invoke(["one", "--as-of"])).toEqual({
      code: 2,
      output: "usage: retirement_check.ts <tasks-directory> [--as-of YYYY-MM-DD]\n",
    });
    expect(invoke(["one", "--unknown"])).toEqual({
      code: 2,
      output: "usage: retirement_check.ts <tasks-directory> [--as-of YYYY-MM-DD]\n",
    });
  });

  it("leaves every record byte-unchanged", () => {
    const directory = makeDirectory();
    const first = join(directory, "a.md");
    const second = join(directory, "b.md");
    const firstText = makeTaskRecord({ closedOn: "2026-11-01" });
    const secondText = makeTaskRecord({ closedOn: "2026-11-12" });
    writeFileSync(first, firstText, "utf8");
    writeFileSync(second, secondText, "utf8");

    invoke([directory, "--as-of", "2026-11-14"]);

    expect(readFileSync(first, "utf8")).toBe(firstText);
    expect(readFileSync(second, "utf8")).toBe(secondText);
  });

  it("reports an unreadable record as an exclusion and still reports the rest", () => {
    const directory = makeDirectory();
    const candidate = join(directory, "a.md");
    writeFileSync(candidate, makeTaskRecord({ closedOn: "2026-11-01" }), "utf8");
    writeFileSync(join(directory, "b.md"), Buffer.from([0xff]));

    const result = invoke([directory, "--as-of", "2026-11-14"]);

    expect(result.code).toBe(0);
    expect(result.output).toContain(`candidate ${candidate} - closed 2026-11-01; 13 complete calendar days`);
    expect(result.output).toMatch(/^excluded .*b\.md - cannot be read: /mu);
    expect(result.output.trimEnd().endsWith("1 candidates of 2 records")).toBe(true);
  });

  it("rejects an as-of operand that is not a calendar date", () => {
    const directory = makeDirectory();

    expect(invoke([directory, "--as-of", "2026-13-01"])).toEqual({
      code: 2,
      output: "usage: retirement_check.ts <tasks-directory> [--as-of YYYY-MM-DD]\n",
    });
  });
});
