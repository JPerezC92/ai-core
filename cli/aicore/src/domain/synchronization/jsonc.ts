/**
 * A pure JSON/JSONC object reader with member spans (pure).
 *
 * Merge mode edits a destination document by replacing value spans and inserting
 * members, so it needs both the parsed value and the exact offsets a splice uses.
 * Comments and trailing commas are tolerated; a non-object top level, a duplicate
 * key, an unterminated comment, or malformed syntax is reported as unreadable
 * rather than half-parsed.
 */

/** A parsed JSON value. */
export type JsoncValue =
  | string
  | number
  | boolean
  | null
  | readonly JsoncValue[]
  | JsoncMapping;

/** A parsed JSON object body. */
export type JsoncMapping = { readonly [key: string]: JsoncValue };

/** One object member: its key, parsed value, raw offsets, and nested body. */
export type JsoncMember = {
  readonly key: string;
  readonly value: JsoncValue;
  /** Offset of the member's opening quote. */
  readonly memberStart: number;
  readonly valueStart: number;
  readonly valueEnd: number;
  /** The value's own object body when the value is an object. */
  readonly members: JsoncObject | null;
};

/** A parsed object plus the offsets a merge splices at. */
export type JsoncObject = {
  readonly value: JsoncMapping;
  readonly members: readonly JsoncMember[];
  readonly closeIndex: number;
  readonly trailingComma: boolean;
};

type Cursor = {
  position: number;
  readonly text: string;
  readonly length: number;
  /** Set when a block comment was opened and never closed. */
  unterminatedComment: boolean;
};

const NUMBER_PATTERN = /-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/u;
const WHITESPACE = " \t\r\n";
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

/**
 * Parse a JSON/JSONC document whose top level is an object.
 *
 * `null` reports an unreadable document.
 */
export function parseJsoncObject(text: string): JsoncObject | null {
  const cursor: Cursor = {
    position: 0,
    text,
    length: text.length,
    unterminatedComment: false,
  };
  skipTrivia(cursor);
  if (cursor.text.charAt(cursor.position) !== "{") {
    return null;
  }
  const object = parseObjectBody(cursor);
  if (object === null) {
    return null;
  }
  skipTrivia(cursor);
  if (cursor.unterminatedComment || cursor.position !== cursor.length) {
    return null;
  }
  return object;
}

function parseObjectBody(cursor: Cursor): JsoncObject | null {
  if (cursor.text.charAt(cursor.position) !== "{") {
    return null;
  }
  cursor.position += 1;
  const value: Record<string, JsoncValue> = {};
  const members: JsoncMember[] = [];
  let trailingComma = false;
  skipTrivia(cursor);
  if (cursor.text.charAt(cursor.position) === "}") {
    cursor.position += 1;
    return { value, members, closeIndex: cursor.position - 1, trailingComma };
  }
  while (true) {
    skipTrivia(cursor);
    if (cursor.text.charAt(cursor.position) !== '"') {
      return null;
    }
    const memberStart = cursor.position;
    const key = parseString(cursor);
    if (key === undefined || Object.hasOwn(value, key)) {
      return null;
    }
    skipTrivia(cursor);
    if (cursor.text.charAt(cursor.position) !== ":") {
      return null;
    }
    cursor.position += 1;
    skipTrivia(cursor);
    const valueStart = cursor.position;
    let nested: JsoncObject | null = null;
    let parsed: JsoncValue | undefined;
    if (cursor.text.charAt(cursor.position) === "{") {
      nested = parseObjectBody(cursor);
      if (nested === null) {
        return null;
      }
      parsed = nested.value;
    } else {
      parsed = parseValue(cursor);
    }
    if (parsed === undefined) {
      return null;
    }
    const valueEnd = cursor.position;
    value[key] = parsed;
    members.push({ key, value: parsed, memberStart, valueStart, valueEnd, members: nested });
    skipTrivia(cursor);
    if (cursor.text.charAt(cursor.position) === ",") {
      cursor.position += 1;
      skipTrivia(cursor);
      if (cursor.text.charAt(cursor.position) === "}") {
        cursor.position += 1;
        return { value, members, closeIndex: cursor.position - 1, trailingComma: true };
      }
      continue;
    }
    if (cursor.text.charAt(cursor.position) === "}") {
      cursor.position += 1;
      return { value, members, closeIndex: cursor.position - 1, trailingComma };
    }
    return null;
  }
}

function parseValue(cursor: Cursor): JsoncValue | undefined {
  if (cursor.position >= cursor.length) {
    return undefined;
  }
  const character = cursor.text.charAt(cursor.position);
  if (character === "{") {
    return parseObjectBody(cursor)?.value;
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
  return undefined;
}

function parseArray(cursor: Cursor): readonly JsoncValue[] | undefined {
  cursor.position += 1;
  const items: JsoncValue[] = [];
  skipTrivia(cursor);
  if (cursor.text.charAt(cursor.position) === "]") {
    cursor.position += 1;
    return items;
  }
  while (true) {
    skipTrivia(cursor);
    const item = parseValue(cursor);
    if (item === undefined) {
      return undefined;
    }
    items.push(item);
    skipTrivia(cursor);
    if (cursor.text.charAt(cursor.position) === ",") {
      cursor.position += 1;
      skipTrivia(cursor);
      if (cursor.text.charAt(cursor.position) === "]") {
        cursor.position += 1;
        return items;
      }
      continue;
    }
    if (cursor.text.charAt(cursor.position) === "]") {
      cursor.position += 1;
      return items;
    }
    return undefined;
  }
}

function parseLiteral<T>(cursor: Cursor, word: string, value: T): T | undefined {
  if (!cursor.text.startsWith(word, cursor.position)) {
    return undefined;
  }
  cursor.position += word.length;
  return value;
}

function parseNumber(cursor: Cursor): number | undefined {
  const match = NUMBER_PATTERN.exec(cursor.text.slice(cursor.position));
  if (match === null) {
    return undefined;
  }
  cursor.position += match[0].length;
  return Number(match[0]);
}

function parseString(cursor: Cursor): string | undefined {
  cursor.position += 1;
  const characters: string[] = [];
  while (cursor.position < cursor.length) {
    const character = cursor.text.charAt(cursor.position);
    if (character === '"') {
      cursor.position += 1;
      return characters.join("");
    }
    if (character === "\\") {
      const escape = parseEscape(cursor);
      if (escape === undefined) {
        return undefined;
      }
      characters.push(escape);
      continue;
    }
    if (character < " ") {
      return undefined;
    }
    characters.push(character);
    cursor.position += 1;
  }
  return undefined;
}

function parseEscape(cursor: Cursor): string | undefined {
  cursor.position += 1;
  if (cursor.position >= cursor.length) {
    return undefined;
  }
  const character = cursor.text.charAt(cursor.position);
  if (character === "u") {
    cursor.position += 1;
    return parseUnicodeEscape(cursor);
  }
  const simple = SIMPLE_ESCAPES.get(character);
  if (simple === undefined) {
    return undefined;
  }
  cursor.position += 1;
  return simple;
}

function parseUnicodeEscape(cursor: Cursor): string | undefined {
  const high = readHexUnit(cursor);
  if (high === undefined) {
    return undefined;
  }
  if (high >= 0xd800 && high <= 0xdbff && cursor.text.startsWith("\\u", cursor.position)) {
    cursor.position += 2;
    const low = readHexUnit(cursor);
    if (low === undefined || low < 0xdc00 || low > 0xdfff) {
      return undefined;
    }
    return String.fromCodePoint(0x10000 + ((high - 0xd800) << 10) + (low - 0xdc00));
  }
  return String.fromCodePoint(high);
}

function readHexUnit(cursor: Cursor): number | undefined {
  const digits = cursor.text.slice(cursor.position, cursor.position + 4);
  if (digits.length !== 4 || !/^[0-9a-fA-F]{4}$/u.test(digits)) {
    return undefined;
  }
  cursor.position += 4;
  return Number.parseInt(digits, 16);
}

function skipTrivia(cursor: Cursor): void {
  while (cursor.position < cursor.length) {
    const character = cursor.text.charAt(cursor.position);
    if (WHITESPACE.includes(character)) {
      cursor.position += 1;
      continue;
    }
    if (character === "/" && cursor.text.startsWith("//", cursor.position)) {
      const newline = cursor.text.indexOf("\n", cursor.position);
      cursor.position = newline === -1 ? cursor.length : newline;
      continue;
    }
    if (character === "/" && cursor.text.startsWith("/*", cursor.position)) {
      const close = cursor.text.indexOf("*/", cursor.position + 2);
      if (close === -1) {
        cursor.unterminatedComment = true;
        cursor.position = cursor.length;
        return;
      }
      cursor.position = close + 2;
      continue;
    }
    return;
  }
}
