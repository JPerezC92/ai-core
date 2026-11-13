/**
 * Infrastructure: the YAML spelling of the bindings and report documents.
 *
 * The contract fixes both documents' *schema*, not their serialization, so this
 * adapter owns the small YAML subset they use: block mappings, block sequences,
 * sequences of mappings, plain and quoted scalars, and an empty flow sequence.
 * It reads that subset into plain data for the domain's schema rule and writes
 * the domain's records back out. It reads no other YAML and never guesses: an
 * input outside the subset produces no value, and the domain then reports a
 * malformed document.
 */

import type { BindingsRecord } from "#domain/synchronization/bindings.ts";
import type { ReconciliationEntry } from "#domain/synchronization/reconciliation.ts";
import { SCHEMA_VERSION } from "#domain/synchronization/constants.ts";

type Line = {
  readonly indent: number;
  readonly text: string;
};

type Cursor = {
  readonly lines: readonly Line[];
  index: number;
};

const KEY_PATTERN = /^([A-Za-z_][A-Za-z0-9_]*):(.*)$/u;

/**
 * Read a bindings document's text into plain data.
 *
 * `null` reports text this adapter cannot read at all; the domain then reports a
 * malformed document rather than accepting a guessed shape.
 */
export function readDocumentText(text: string): unknown {
  const lines: Line[] = [];
  for (const raw of text.split(/\r\n|[\n\r]/u)) {
    const trimmed = raw.trim();
    if (trimmed === "" || trimmed.startsWith("#")) {
      continue;
    }
    lines.push({ indent: raw.length - raw.trimStart().length, text: trimmed });
  }
  const first = lines[0];
  if (first === undefined) {
    return null;
  }
  const cursor: Cursor = { lines, index: 0 };
  const value = parseNode(cursor, first.indent);
  return cursor.index === lines.length ? value : null;
}

/** Render a bindings document. */
export function writeBindingsDocument(record: BindingsRecord): string {
  const lines: string[] = [
    `schema: ${String(record.schema)}`,
    `core_revision: ${scalar(record.core_revision)}`,
  ];
  if (record.root !== undefined) {
    lines.push(`root: ${scalar(record.root)}`);
  }
  if (record.bindings.length === 0) {
    lines.push("bindings: []");
  } else {
    lines.push("bindings:");
    for (const entry of record.bindings) {
      lines.push(`- source: ${scalar(entry.source)}`);
      lines.push("  destinations:");
      for (const destination of entry.destinations) {
        lines.push(`  - ${scalar(destination)}`);
      }
    }
  }
  if (record.pending.length === 0) {
    lines.push("pending: []");
  } else {
    lines.push("pending:");
    for (const path of record.pending) {
      lines.push(`- ${scalar(path)}`);
    }
  }
  return `${lines.join("\n")}\n`;
}

/** Render a reconciliation report. */
export function writeReconciliationReport(
  entries: readonly ReconciliationEntry[],
  revision: string,
): string {
  const lines: string[] = [
    `schema: ${String(SCHEMA_VERSION)}`,
    `core_revision: ${scalar(revision)}`,
  ];
  if (entries.length === 0) {
    lines.push("entries: []");
  } else {
    lines.push("entries:");
    for (const entry of entries) {
      lines.push(`- destination: ${scalar(entry.destination)}`);
      lines.push(`  source: ${scalar(entry.source)}`);
      lines.push(`  action: ${scalar(entry.action)}`);
    }
  }
  return `${lines.join("\n")}\n`;
}

function parseNode(cursor: Cursor, indent: number): unknown {
  const line = cursor.lines[cursor.index];
  if (line === undefined) {
    return null;
  }
  if (line.text === "-" || line.text.startsWith("- ")) {
    return parseSequence(cursor, indent);
  }
  return parseMapping(cursor, indent);
}

function parseSequence(cursor: Cursor, indent: number): unknown[] {
  const items: unknown[] = [];
  while (cursor.index < cursor.lines.length) {
    const line = cursor.lines[cursor.index];
    if (line === undefined || line.indent !== indent) {
      break;
    }
    if (line.text !== "-" && !line.text.startsWith("- ")) {
      break;
    }
    const rest = line.text === "-" ? "" : line.text.slice(1).trimStart();
    const restOffset = line.text.length - rest.length;
    cursor.index += 1;
    if (rest === "") {
      const child = cursor.lines[cursor.index];
      items.push(
        child !== undefined && child.indent > indent ? parseNode(cursor, child.indent) : null,
      );
      continue;
    }
    const match = KEY_PATTERN.exec(rest);
    if (match === null) {
      items.push(readScalar(rest));
      continue;
    }
    items.push(
      parseMappingItem(cursor, indent + restOffset, match[1] ?? "", (match[2] ?? "").trim()),
    );
  }
  return items;
}

function parseMappingItem(
  cursor: Cursor,
  itemIndent: number,
  firstKey: string,
  firstInline: string,
): Record<string, unknown> {
  const mapping: Record<string, unknown> = {};
  assignKey(cursor, mapping, itemIndent, firstKey, firstInline);
  while (cursor.index < cursor.lines.length) {
    const line = cursor.lines[cursor.index];
    if (line === undefined || line.indent !== itemIndent) {
      break;
    }
    if (line.text === "-" || line.text.startsWith("- ")) {
      break;
    }
    const match = KEY_PATTERN.exec(line.text);
    if (match === null) {
      break;
    }
    cursor.index += 1;
    assignKey(cursor, mapping, itemIndent, match[1] ?? "", (match[2] ?? "").trim());
  }
  return mapping;
}

function parseMapping(cursor: Cursor, indent: number): Record<string, unknown> {
  const mapping: Record<string, unknown> = {};
  while (cursor.index < cursor.lines.length) {
    const line = cursor.lines[cursor.index];
    if (line === undefined || line.indent !== indent) {
      break;
    }
    const match = KEY_PATTERN.exec(line.text);
    if (match === null) {
      break;
    }
    cursor.index += 1;
    assignKey(cursor, mapping, indent, match[1] ?? "", (match[2] ?? "").trim());
  }
  return mapping;
}

function assignKey(
  cursor: Cursor,
  mapping: Record<string, unknown>,
  indent: number,
  key: string,
  inline: string,
): void {
  if (Object.hasOwn(mapping, key)) {
    return;
  }
  if (inline !== "") {
    mapping[key] = readScalar(inline);
    return;
  }
  const child = cursor.lines[cursor.index];
  const continues =
    child !== undefined &&
    (child.indent > indent ||
      (child.indent === indent && (child.text === "-" || child.text.startsWith("- "))));
  mapping[key] = continues && child !== undefined ? parseNode(cursor, child.indent) : null;
}

function readScalar(text: string): unknown {
  if (text === "" || text === "null" || text === "~") {
    return null;
  }
  if (text === "[]") {
    return [];
  }
  if (text.startsWith("[") && text.endsWith("]")) {
    const inner = text.slice(1, -1).trim();
    return inner === "" ? [] : inner.split(",").map((item) => readScalar(item.trim()));
  }
  const quoted = readQuoted(text);
  if (quoted !== null) {
    return quoted;
  }
  if (text === "true") {
    return true;
  }
  if (text === "false") {
    return false;
  }
  if (/^-?\d+$/u.test(text)) {
    return Number(text);
  }
  return text;
}

function readQuoted(text: string): string | null {
  if (text.length < 2) {
    return null;
  }
  const first = text.charAt(0);
  const last = text.charAt(text.length - 1);
  if (first === '"' && last === '"') {
    return text.slice(1, -1).replaceAll('\\"', '"').replaceAll("\\\\", "\\");
  }
  if (first === "'" && last === "'") {
    return text.slice(1, -1).replaceAll("''", "'");
  }
  return null;
}

/**
 * Render one scalar.
 *
 * A value that is safe as a plain scalar stays plain, so the documents read like
 * the contract's own examples; anything else is double-quoted so a colon, a
 * bracket or a leading indicator character cannot change what it means. A
 * revision is always quoted: an all-digit hexadecimal value would otherwise read
 * as a number.
 */
function scalar(value: string | null): string {
  if (value === null) {
    return "null";
  }
  if (/^[0-9a-f]{40}$/u.test(value)) {
    return `"${value}"`;
  }
  if (/^[A-Za-z0-9._/-]+$/u.test(value) && !value.startsWith("-")) {
    return value;
  }
  return `"${value.replaceAll("\\", "\\\\").replaceAll('"', '\\"')}"`;
}
