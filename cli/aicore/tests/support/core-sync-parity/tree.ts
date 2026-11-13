/**
 * Filesystem tree comparison for the parity corpus.
 *
 * A case states the whole expected destination tree: every file, directory and
 * symbolic link that must exist afterwards, and nothing else. A file the engine
 * wrote that the case did not expect, or a file the case expected that the
 * engine did not write, is a difference — so a command that writes more than
 * the contract allows fails, not passes.
 */

import { readFile, readdir, readlink } from "node:fs/promises";
import { join, relative, sep } from "node:path";

import { readBindingsDocument, readReportDocument } from "./document.ts";
import type { TreeEntry } from "./types.ts";

/** One observed entry of a filesystem tree. */
export type ObservedEntry = {
  readonly path: string;
  readonly kind: "file" | "directory" | "symlink";
  readonly content?: string;
  readonly target?: string;
};

/** Read a directory tree into a flat, comparable list. */
export async function snapshotTree(root: string): Promise<ObservedEntry[]> {
  const observed: ObservedEntry[] = [];
  await walk(root, root, observed);
  observed.sort((left, right) => (left.path < right.path ? -1 : left.path > right.path ? 1 : 0));
  return observed;
}

async function walk(root: string, current: string, collected: ObservedEntry[]): Promise<void> {
  const entries = await readdir(current, { withFileTypes: true });
  for (const entry of entries) {
    const absolute = join(current, entry.name);
    const path = relative(root, absolute).split(sep).join("/");
    if (entry.isSymbolicLink()) {
      collected.push({ path, kind: "symlink", target: await readlink(absolute) });
      continue;
    }
    if (entry.isDirectory()) {
      collected.push({ path, kind: "directory" });
      await walk(root, absolute, collected);
      continue;
    }
    collected.push({ path, kind: "file", content: await readFile(absolute, "utf8") });
  }
}

/**
 * Compare an observed tree with a case's expected tree.
 *
 * Returns one message per difference; an empty array means the trees agree.
 */
export function compareTree(
  root: string,
  observed: readonly ObservedEntry[],
  expected: readonly TreeEntry[],
): string[] {
  const differences: string[] = [];
  const observedByPath = new Map(observed.map((entry) => [entry.path, entry]));
  const expectedPaths = new Set(expected.map((entry) => entry.path));

  for (const entry of observed) {
    if (!expectedPaths.has(entry.path)) {
      differences.push(`${root}: unexpected entry ${entry.path} (${entry.kind})`);
    }
  }

  for (const expectation of expected) {
    const actual = observedByPath.get(expectation.path);
    if (actual === undefined) {
      differences.push(`${root}: missing entry ${expectation.path}`);
      continue;
    }
    differences.push(...compareEntry(root, expectation, actual));
  }
  return differences;
}

function compareEntry(root: string, expectation: TreeEntry, actual: ObservedEntry): string[] {
  const differences: string[] = [];
  switch (expectation.kind) {
    case "directory":
      if (actual.kind !== "directory") {
        differences.push(`${root}: ${expectation.path} is ${actual.kind}, expected a directory`);
      }
      return differences;
    case "symlink":
      if (actual.kind !== "symlink") {
        differences.push(`${root}: ${expectation.path} is ${actual.kind}, expected a symbolic link`);
        return differences;
      }
      if (actual.target !== expectation.target) {
        differences.push(
          `${root}: ${expectation.path} links to ${JSON.stringify(actual.target)}, expected ${JSON.stringify(expectation.target)}`,
        );
      }
      return differences;
    case "file":
      if (actual.kind !== "file") {
        differences.push(`${root}: ${expectation.path} is ${actual.kind}, expected a file`);
        return differences;
      }
      if (actual.content !== expectation.content) {
        differences.push(
          `${root}: ${expectation.path} content differs\n${describeDifference(expectation.content, actual.content ?? "")}`,
        );
      }
      return differences;
    case "blocker": {
      if (actual.kind !== "file") {
        differences.push(`${root}: ${expectation.path} is ${actual.kind}, expected a file`);
        return differences;
      }
      const content = actual.content ?? "";
      if (!content.startsWith(expectation.prefix)) {
        differences.push(
          `${root}: ${expectation.path} does not start with the expected blocker prefix\n--- expected prefix ---\n${expectation.prefix}\n--- actual ---\n${content}\n--- end ---`,
        );
        return differences;
      }
      if (!content.endsWith(expectation.suffix)) {
        differences.push(
          `${root}: ${expectation.path} does not end with the expected blocker suffix\n--- expected suffix ---\n${expectation.suffix}\n--- actual ---\n${content}\n--- end ---`,
        );
        return differences;
      }
      const body = content.slice(
        expectation.prefix.length,
        content.length - expectation.suffix.length,
      );
      for (const required of expectation.bodyContains) {
        if (!body.includes(required)) {
          differences.push(`${root}: ${expectation.path} blocker body does not mention ${JSON.stringify(required)}`);
        }
      }
      return differences;
    }
    case "jsonc": {
      if (actual.kind !== "file") {
        differences.push(`${root}: ${expectation.path} is ${actual.kind}, expected a file`);
        return differences;
      }
      const content = actual.content ?? "";
      const normalizedActual = normalizeJsonc(content);
      const normalizedExpected = normalizeJsonc(expectation.content);
      if (normalizedActual !== normalizedExpected) {
        differences.push(
          `${root}: ${expectation.path} content differs\n--- expected ---\n${expectation.content}\n--- actual ---\n${content}\n--- end ---`,
        );
      }
      for (const required of expectation.mustContain ?? []) {
        if (!content.includes(required)) {
          differences.push(`${root}: ${expectation.path} does not keep ${JSON.stringify(required)}`);
        }
      }
      return differences;
    }
    case "bindings": {
      if (actual.kind !== "file") {
        differences.push(`${root}: ${expectation.path} is ${actual.kind}, expected a file`);
        return differences;
      }
      const document = readBindingsDocument(actual.content ?? "");
      differences.push(...compareDocuments(root, expectation.path, document, expectation.document));
      return differences;
    }
    case "report": {
      if (actual.kind !== "file") {
        differences.push(`${root}: ${expectation.path} is ${actual.kind}, expected a file`);
        return differences;
      }
      const document = readReportDocument(actual.content ?? "");
      differences.push(...compareDocuments(root, expectation.path, document, expectation.document));
      return differences;
    }
  }
}

function compareDocuments(
  root: string,
  path: string,
  actual: unknown,
  expected: unknown,
): string[] {
  const actualText = JSON.stringify(actual, null, 2);
  const expectedText = JSON.stringify(expected, null, 2);
  if (actualText === expectedText) {
    return [];
  }
  return [
    `${root}: ${path} document differs\n--- expected ---\n${expectedText}\n--- actual ---\n${actualText}\n--- end ---`,
  ];
}

/**
 * Describe where two texts first differ.
 *
 * A byte-level expectation can fail on a single invisible character, so the
 * report names the offset and the code points around it instead of printing
 * two long texts that look alike.
 */
export function describeDifference(expected: string, actual: string): string {
  const limit = Math.min(expected.length, actual.length);
  let offset = 0;
  while (offset < limit && expected[offset] === actual[offset]) {
    offset += 1;
  }
  const window = 30;
  const from = Math.max(0, offset - window);
  return [
    `first difference at offset ${offset}`,
    `--- expected around --- ${JSON.stringify(expected.slice(from, offset + window))}`,
    `--- actual around ---   ${JSON.stringify(actual.slice(from, offset + window))}`,
    `--- expected code points --- ${codePoints(expected.slice(offset, offset + 4))}`,
    `--- actual code points ---   ${codePoints(actual.slice(offset, offset + 4))}`,
  ].join("\n");
}

function codePoints(text: string): string {
  return [...text]
    .map((character) => `${character} (U+${character.codePointAt(0)?.toString(16).toUpperCase().padStart(4, "0")})`)
    .join(" ");
}

/**
 * Remove the layout whitespace of a JSONC document.
 *
 * The contract fixes what a merge preserves — keys, values, comments — but not
 * how the result is laid out: it says the destination's content is preserved
 * "by content, not byte-for-byte". Comparing a merged payload with its layout
 * whitespace removed therefore states the contract's requirement without
 * over-constraining the engine's formatting choices. String literals and
 * comments are kept verbatim, so a value or a comment can never be lost.
 */
export function normalizeJsonc(text: string): string {
  let output = "";
  let index = 0;
  while (index < text.length) {
    const char = text.charAt(index);
    if (char === '"') {
      const end = readStringLiteral(text, index);
      output += text.slice(index, end);
      index = end;
      continue;
    }
    if (char === "/" && text[index + 1] === "/") {
      const newline = text.indexOf("\n", index);
      const stop = newline === -1 ? text.length : newline;
      output += text.slice(index, stop);
      index = stop;
      continue;
    }
    if (char === "/" && text[index + 1] === "*") {
      const close = text.indexOf("*/", index + 2);
      const stop = close === -1 ? text.length : close + 2;
      output += text.slice(index, stop);
      index = stop;
      continue;
    }
    if (/\s/u.test(char)) {
      index += 1;
      continue;
    }
    output += char;
    index += 1;
  }
  return output;
}

function readStringLiteral(text: string, start: number): number {
  let index = start + 1;
  while (index < text.length) {
    const char = text[index];
    if (char === "\\") {
      index += 2;
      continue;
    }
    if (char === '"') {
      return index + 1;
    }
    index += 1;
  }
  return text.length;
}
