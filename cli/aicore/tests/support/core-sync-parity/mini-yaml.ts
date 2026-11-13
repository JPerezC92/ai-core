/**
 * A minimal reader for the YAML subset the two synchronization documents use.
 *
 * The bindings file and the reconciliation report have a contract-defined
 * *schema* but no contract-defined *serialization*: the reference emits one
 * YAML dialect, and a different engine may emit another. Comparing the two
 * documents therefore means comparing what they say, not how they spell it.
 *
 * This reader understands block mappings, block sequences, sequences of
 * mappings, plain and quoted scalars, and flow sequences. It is deliberately
 * narrow: it reads the corpus's two document shapes and nothing else.
 */

/** A parsed YAML value: a scalar, a sequence, or a mapping. */
export type YamlValue = string | number | boolean | null | YamlValue[] | YamlMapping;

/** A parsed YAML mapping. */
export type YamlMapping = { [key: string]: YamlValue };

type Line = {
  readonly indent: number;
  readonly text: string;
};

const KEY_PATTERN = /^([A-Za-z_][A-Za-z0-9_]*):(.*)$/;
const INTEGER_PATTERN = /^-?\d+$/;

/** Parse a YAML document into plain values. */
export function readYaml(text: string): YamlValue {
  const lines: Line[] = [];
  for (const raw of text.split("\n")) {
    const trimmed = raw.trim();
    if (trimmed === "") {
      continue;
    }
    lines.push({ indent: raw.length - raw.trimStart().length, text: trimmed });
  }
  const cursor = { lines, index: 0 };
  if (lines.length === 0) {
    return null;
  }
  const first = lines[0];
  if (first === undefined) {
    return null;
  }
  return parseNode(cursor, first.indent);
}

type Cursor = { readonly lines: readonly Line[]; index: number };

function peek(cursor: Cursor): Line | undefined {
  return cursor.lines[cursor.index];
}

function parseNode(cursor: Cursor, indent: number): YamlValue {
  const line = peek(cursor);
  if (line === undefined) {
    return null;
  }
  if (line.text === "-" || line.text.startsWith("- ")) {
    return parseSequence(cursor, indent);
  }
  return parseMapping(cursor, indent);
}

function parseSequence(cursor: Cursor, indent: number): YamlValue[] {
  const items: YamlValue[] = [];
  while (cursor.index < cursor.lines.length) {
    const line = peek(cursor);
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
      const child = peek(cursor);
      items.push(child !== undefined && child.indent > indent ? parseNode(cursor, child.indent) : null);
      continue;
    }
    const match = KEY_PATTERN.exec(rest);
    if (match === null) {
      items.push(scalar(rest));
      continue;
    }
    items.push(parseMappingItem(cursor, indent + restOffset, match[1] ?? "", (match[2] ?? "").trim()));
  }
  return items;
}

function parseMappingItem(
  cursor: Cursor,
  itemIndent: number,
  firstKey: string,
  firstInline: string,
): YamlMapping {
  const mapping: YamlMapping = {};
  assignKey(cursor, mapping, itemIndent, firstKey, firstInline);
  while (cursor.index < cursor.lines.length) {
    const line = peek(cursor);
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

function parseMapping(cursor: Cursor, indent: number): YamlMapping {
  const mapping: YamlMapping = {};
  while (cursor.index < cursor.lines.length) {
    const line = peek(cursor);
    if (line === undefined || line.indent !== indent) {
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
    assignKey(cursor, mapping, indent, match[1] ?? "", (match[2] ?? "").trim());
  }
  return mapping;
}

function assignKey(
  cursor: Cursor,
  mapping: YamlMapping,
  indent: number,
  key: string,
  inline: string,
): void {
  if (inline !== "") {
    mapping[key] = scalar(inline);
    return;
  }
  const child = peek(cursor);
  const continues =
    child !== undefined &&
    (child.indent > indent || (child.indent === indent && (child.text === "-" || child.text.startsWith("- "))));
  mapping[key] = continues && child !== undefined ? parseNode(cursor, child.indent) : null;
}

function scalar(text: string): YamlValue {
  if (text === "" || text === "null" || text === "~") {
    return null;
  }
  if (text === "[]") {
    return [];
  }
  if (text.startsWith("[") && text.endsWith("]")) {
    const inner = text.slice(1, -1).trim();
    if (inner === "") {
      return [];
    }
    return inner.split(",").map((item) => scalar(item.trim()));
  }
  if (text.length >= 2 && text.startsWith('"') && text.endsWith('"')) {
    return text.slice(1, -1);
  }
  if (text.length >= 2 && text.startsWith("'") && text.endsWith("'")) {
    return text.slice(1, -1);
  }
  if (text === "true") {
    return true;
  }
  if (text === "false") {
    return false;
  }
  if (INTEGER_PATTERN.test(text)) {
    return Number(text);
  }
  return text;
}
