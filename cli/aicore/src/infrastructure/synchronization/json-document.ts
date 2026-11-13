/**
 * Infrastructure: strict JSON reading that keeps every object key.
 *
 * A general-purpose JSON parser collapses a repeated key before any domain rule
 * can see it, so a document that declares one key twice would validate as
 * whatever the last declaration said. This reader applies the same grammar as
 * the platform parser — no comments and no trailing commas — and reports a
 * repeated key at any nesting level instead of silently overwriting it.
 */

/** The result of reading one JSON document. */
export type JsonRead =
  | { readonly kind: "value"; readonly value: unknown }
  | { readonly kind: "duplicate-key"; readonly key: string }
  | { readonly kind: "malformed" };

type Cursor = {
  position: number;
  readonly text: string;
  readonly length: number;
  /** The first failure the reader met, if any. */
  failure: JsonRead | null;
};

const WHITESPACE = " \t\r\n";
const NUMBER_PATTERN =
  /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/u;
const HEX_UNIT_PATTERN = /^[0-9a-fA-F]{4}$/u;
const SIMPLE_ESCAPES: ReadonlyMap<string, string> = new Map([
  ['"', '"'],
  ["\\", "\\"],
  ["/", "/"],
  ["b", "\b"],
  ["f", "\f"],
  ["n", "\n"],
  ["r", "\r"],
  ["t", "\t"],
]);

const MALFORMED: JsonRead = { kind: "malformed" };

/**
 * Read one JSON document.
 *
 * A duplicate key outranks malformed syntax: the duplicate is the reason the
 * document is rejected, and reporting it names the path that was declared twice.
 */
export function readJsonDocument(text: string): JsonRead {
  const cursor: Cursor = {
    position: 0,
    text,
    length: text.length,
    failure: null,
  };
  skipWhitespace(cursor);
  const value = parseValue(cursor);
  skipWhitespace(cursor);
  if (cursor.failure !== null) {
    return cursor.failure;
  }
  if (value === undefined || cursor.position !== cursor.length) {
    return MALFORMED;
  }
  return { kind: "value", value };
}

function parseValue(cursor: Cursor): unknown {
  const character = cursor.text.charAt(cursor.position);
  if (character === "{") {
    return parseObject(cursor);
  }
  if (character === "[") {
    return parseArray(cursor);
  }
  if (character === '"') {
    return parseString(cursor);
  }
  if (character === "t") {
    return parseLiteral(cursor, "true", true);
  }
  if (character === "f") {
    return parseLiteral(cursor, "false", false);
  }
  if (character === "n") {
    return parseLiteral(cursor, "null", null);
  }
  if (character === "-" || (character >= "0" && character <= "9")) {
    return parseNumber(cursor);
  }
  return fail(cursor, MALFORMED);
}

function parseObject(cursor: Cursor): Record<string, unknown> | undefined {
  cursor.position += 1;
  const result: Record<string, unknown> = {};
  skipWhitespace(cursor);
  if (cursor.text.charAt(cursor.position) === "}") {
    cursor.position += 1;
    return result;
  }
  while (true) {
    skipWhitespace(cursor);
    if (cursor.text.charAt(cursor.position) !== '"') {
      return fail(cursor, MALFORMED);
    }
    const key = parseString(cursor);
    if (key === undefined) {
      return undefined;
    }
    if (Object.hasOwn(result, key)) {
      cursor.failure = { kind: "duplicate-key", key };
      return undefined;
    }
    skipWhitespace(cursor);
    if (cursor.text.charAt(cursor.position) !== ":") {
      return fail(cursor, MALFORMED);
    }
    cursor.position += 1;
    skipWhitespace(cursor);
    const value = parseValue(cursor);
    if (value === undefined) {
      return undefined;
    }
    result[key] = value;
    skipWhitespace(cursor);
    const separator = cursor.text.charAt(cursor.position);
    if (separator === ",") {
      cursor.position += 1;
      continue;
    }
    if (separator === "}") {
      cursor.position += 1;
      return result;
    }
    return fail(cursor, MALFORMED);
  }
}

function parseArray(cursor: Cursor): unknown[] | undefined {
  cursor.position += 1;
  const items: unknown[] = [];
  skipWhitespace(cursor);
  if (cursor.text.charAt(cursor.position) === "]") {
    cursor.position += 1;
    return items;
  }
  while (true) {
    skipWhitespace(cursor);
    const item = parseValue(cursor);
    if (item === undefined) {
      return undefined;
    }
    items.push(item);
    skipWhitespace(cursor);
    const separator = cursor.text.charAt(cursor.position);
    if (separator === ",") {
      cursor.position += 1;
      continue;
    }
    if (separator === "]") {
      cursor.position += 1;
      return items;
    }
    return fail(cursor, MALFORMED);
  }
}

function parseString(cursor: Cursor): string | undefined {
  cursor.position += 1;
  let value = "";
  while (cursor.position < cursor.length) {
    const character = cursor.text.charAt(cursor.position);
    if (character === '"') {
      cursor.position += 1;
      return value;
    }
    if (character === "\\") {
      const escaped = parseEscape(cursor);
      if (escaped === undefined) {
        return undefined;
      }
      value += escaped;
      continue;
    }
    if (character < " ") {
      return fail(cursor, MALFORMED);
    }
    value += character;
    cursor.position += 1;
  }
  return fail(cursor, MALFORMED);
}

function parseEscape(cursor: Cursor): string | undefined {
  cursor.position += 1;
  const character = cursor.text.charAt(cursor.position);
  if (character === "u") {
    cursor.position += 1;
    const digits = cursor.text.slice(cursor.position, cursor.position + 4);
    if (!HEX_UNIT_PATTERN.test(digits)) {
      return fail(cursor, MALFORMED);
    }
    cursor.position += 4;
    return String.fromCharCode(Number.parseInt(digits, 16));
  }
  const escaped = SIMPLE_ESCAPES.get(character);
  if (escaped === undefined) {
    return fail(cursor, MALFORMED);
  }
  cursor.position += 1;
  return escaped;
}

function parseLiteral<T>(cursor: Cursor, word: string, value: T): T | undefined {
  if (!cursor.text.startsWith(word, cursor.position)) {
    return fail(cursor, MALFORMED);
  }
  cursor.position += word.length;
  return value;
}

function parseNumber(cursor: Cursor): number | undefined {
  const match = NUMBER_PATTERN.exec(cursor.text.slice(cursor.position));
  if (match === null) {
    return fail(cursor, MALFORMED);
  }
  cursor.position += match[0].length;
  return Number(match[0]);
}

function skipWhitespace(cursor: Cursor): void {
  while (
    cursor.position < cursor.length &&
    WHITESPACE.includes(cursor.text.charAt(cursor.position))
  ) {
    cursor.position += 1;
  }
}

/** Record the first failure and report the absence of a value. */
function fail(cursor: Cursor, failure: JsonRead): undefined {
  if (cursor.failure === null) {
    cursor.failure = failure;
  }
  return undefined;
}
