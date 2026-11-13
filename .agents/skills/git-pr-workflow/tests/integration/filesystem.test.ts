import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  createText,
  InputOutputFailure,
  readText,
} from "../../scripts/pr_review/infrastructure/filesystem.ts";

const temporaryDirectories: string[] = [];

function makeDirectory(): string {
  const directory = mkdtempSync(join(tmpdir(), "git-pr-workflow-filesystem-"));
  temporaryDirectories.push(directory);
  return directory;
}

afterEach(() => {
  for (const directory of temporaryDirectories.splice(0)) {
    rmSync(directory, { recursive: true, force: true });
  }
});

describe("the filesystem adapter", () => {
  it("reads UTF-8 bytes without newline translation", () => {
    const directory = makeDirectory();
    const file = join(directory, "body.md");
    writeFileSync(file, "first\r\nsecond\r\n", "utf8");

    expect(readText(file)).toBe("first\r\nsecond\r\n");
  });

  it("rejects content that is not valid UTF-8", () => {
    const directory = makeDirectory();
    const file = join(directory, "binary.bin");
    writeFileSync(file, Buffer.from([0xff, 0xfe, 0x00]));

    expect(() => readText(file)).toThrow(InputOutputFailure);
  });

  it("reports a missing file as an input/output failure", () => {
    const directory = makeDirectory();

    expect(() => readText(join(directory, "absent.md"))).toThrow(InputOutputFailure);
  });

  it("creates an artifact exclusively and leaves an existing file untouched", () => {
    const directory = makeDirectory();
    const file = join(directory, "snapshot.json");

    createText(file, "{}\n");

    expect(readFileSync(file, "utf8")).toBe("{}\n");
    expect(() => createText(file, "replaced\n")).toThrow(InputOutputFailure);
    expect(readFileSync(file, "utf8")).toBe("{}\n");
  });
});
