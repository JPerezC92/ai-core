/**
 * Top-level JSON object merge: source keys win, `mcp` merges by server name.
 *
 * The destination's content outside replaced or inserted members is preserved
 * verbatim, comments included, because the merge edits spans instead of
 * re-serializing the document. The `qmd` server's `--index` argument is
 * retargeted to the destination project's own name on every `mcp` write path and
 * in the comparison, so a write is never followed by drift.
 */

import type { JsoncMapping, JsoncMember, JsoncObject, JsoncValue } from "./jsonc.ts";
import { parseJsoncObject } from "./jsonc.ts";

const MEMBER_INDENT = "  ";
const INDEX_FLAG = "--index";
const MCP_KEY = "mcp";
const QMD_SERVER_KEY = "qmd";
const SERVERS_KEY = "servers";

/** One span replacement; a zero-width span inserts its text. */
type Edit = {
  readonly start: number;
  readonly end: number;
  readonly text: string;
};

/**
 * Merge the source object's top-level keys into the destination text.
 *
 * Each key already present in the destination has its value span replaced by the
 * source's raw value, except `mcp`: when both sides hold `mcp.servers` as an
 * object the servers merge by name — a same-named server is core-wins, a
 * source-only server is inserted, and every destination-only server and any
 * non-`servers` child of the destination `mcp` survive. Source-only keys are
 * inserted before the destination's closing brace.
 *
 * `null` reports an unreadable source or destination document.
 */
export function mergeTopLevel(
  sourceText: string,
  destinationText: string,
  projectName: string,
): string | null {
  const source = parseJsoncObject(sourceText);
  const destination = parseJsoncObject(destinationText);
  if (source === null || destination === null) {
    return null;
  }
  const destinationSpans = membersByKey(destination.members);

  const edits: Edit[] = [];
  const sourceOnly: string[] = [];
  for (const member of source.members) {
    const existing = destinationSpans.get(member.key);
    if (existing === undefined) {
      sourceOnly.push(
        member.key === MCP_KEY
          ? retargetMcpMemberText(sourceText, member, projectName)
          : sourceText.slice(member.memberStart, member.valueEnd),
      );
      continue;
    }
    if (
      member.key === MCP_KEY &&
      mergeMcpServers(sourceText, member, destinationText, existing, edits, projectName)
    ) {
      continue;
    }
    edits.push({
      start: existing.valueStart,
      end: existing.valueEnd,
      text:
        member.key === MCP_KEY
          ? retargetMcpValueText(sourceText, member, projectName)
          : sourceText.slice(member.valueStart, member.valueEnd),
    });
  }

  const result = applyEdits(destinationText, edits);
  if (sourceOnly.length === 0) {
    return result;
  }
  const inserted = sourceOnly.map((member) => `${MEMBER_INDENT}${member}`).join(",\n");
  const separator = destination.members.length > 0 && !destination.trailingComma ? "," : "";
  const closeIndex = shiftedCloseIndex(destination, edits);
  return (
    result.slice(0, closeIndex) +
    separator +
    "\n" +
    inserted +
    "\n" +
    result.slice(closeIndex)
  );
}

/**
 * Return whether every source top-level key is present with an equal value.
 *
 * Extra destination-only keys are allowed. For `mcp`, when both sides hold
 * `mcp.servers` as an object the destination must contain every source server
 * with an equal value plus any extra servers; otherwise `mcp` is compared exactly
 * like any other key. Comparison is semantic, so formatting and comments in the
 * destination do not affect the result.
 *
 * `null` reports an unreadable source or destination document.
 */
export function isMerged(
  sourceText: string,
  destinationText: string,
  projectName: string,
): boolean | null {
  const source = parseJsoncObject(sourceText);
  const destination = parseJsoncObject(destinationText);
  if (source === null || destination === null) {
    return null;
  }
  const sourceSpans = membersByKey(source.members);
  const destinationSpans = membersByKey(destination.members);
  for (const [key, value] of Object.entries(source.value)) {
    if (!Object.hasOwn(destination.value, key)) {
      return false;
    }
    if (
      key === MCP_KEY &&
      mcpServersContained(sourceSpans.get(key), destinationSpans.get(key), projectName)
    ) {
      continue;
    }
    const expected = key === MCP_KEY ? retargetMcpValue(value, projectName) : value;
    if (!jsoncEquals(destination.value[key], expected)) {
      return false;
    }
  }
  return true;
}

function mergeMcpServers(
  sourceText: string,
  sourceSpan: JsoncMember,
  destinationText: string,
  destinationSpan: JsoncMember,
  edits: Edit[],
  projectName: string,
): boolean {
  const sourceServers = serversObject(sourceSpan);
  const destinationServers = serversObject(destinationSpan);
  if (sourceServers === null || destinationServers === null) {
    return false;
  }
  const destinationMembers = membersByKey(destinationServers.members);
  const inserted: string[] = [];
  for (const member of sourceServers.members) {
    const existing = destinationMembers.get(member.key);
    let rawValue = sourceText.slice(member.valueStart, member.valueEnd);
    if (member.key === QMD_SERVER_KEY) {
      rawValue = retargetIndexLiteral(rawValue, member.value, projectName);
    }
    if (existing === undefined) {
      inserted.push(sourceText.slice(member.memberStart, member.valueStart) + rawValue);
      continue;
    }
    edits.push({ start: existing.valueStart, end: existing.valueEnd, text: rawValue });
  }
  if (inserted.length > 0) {
    const indent = memberIndent(destinationText, destinationServers);
    const closeIndent = closeLineIndent(destinationText, destinationServers);
    const body = inserted.map((member) => `${indent}${member}`).join(",\n");
    const separator =
      destinationServers.members.length > 0 && !destinationServers.trailingComma ? "," : "";
    const closeIndex = destinationServers.closeIndex;
    edits.push({ start: closeIndex, end: closeIndex, text: `${separator}\n${body}\n${closeIndent}` });
  }
  return true;
}

/** Return the `servers` object body nested under an `mcp` value, if any. */
function serversObject(span: JsoncMember | undefined): JsoncObject | null {
  const mcpBody = span?.members ?? null;
  if (mcpBody === null) {
    return null;
  }
  return membersByKey(mcpBody.members).get(SERVERS_KEY)?.members ?? null;
}

/** Return whether the destination `mcp.servers` holds every source server. */
function mcpServersContained(
  sourceSpan: JsoncMember | undefined,
  destinationSpan: JsoncMember | undefined,
  projectName: string,
): boolean {
  const sourceServers = serversObject(sourceSpan);
  const destinationServers = serversObject(destinationSpan);
  if (sourceServers === null || destinationServers === null) {
    return false;
  }
  for (const [name, value] of Object.entries(sourceServers.value)) {
    if (!Object.hasOwn(destinationServers.value, name)) {
      return false;
    }
    if (!jsoncEquals(destinationServers.value[name], retargetServerValue(name, value, projectName))) {
      return false;
    }
  }
  return true;
}

/** Return a source server value with its `--index` argument retargeted. */
function retargetServerValue(name: string, value: JsoncValue, projectName: string): JsoncValue {
  return name === QMD_SERVER_KEY ? retargetQmdServer(value, projectName) : value;
}

/** Return an `mcp` value whose `qmd` server index is retargeted. */
function retargetMcpValue(value: JsoncValue, projectName: string): JsoncValue {
  if (projectName === "" || !isMapping(value)) {
    return value;
  }
  const servers = value[SERVERS_KEY];
  if (!isMapping(servers)) {
    return value;
  }
  const qmd = servers[QMD_SERVER_KEY];
  if (qmd === undefined) {
    return value;
  }
  const retargeted = retargetQmdServer(qmd, projectName);
  if (retargeted === qmd) {
    return value;
  }
  return { ...value, [SERVERS_KEY]: { ...servers, [QMD_SERVER_KEY]: retargeted } };
}

/** Return a server value with the argument following `--index` replaced. */
function retargetQmdServer(value: JsoncValue, projectName: string): JsoncValue {
  if (projectName === "" || !isMapping(value)) {
    return value;
  }
  const command = value["command"];
  if (!Array.isArray(command)) {
    return value;
  }
  const position = indexArgumentPosition(command);
  if (position === null) {
    return value;
  }
  const retargeted = [...command];
  retargeted[position] = projectName;
  return { ...value, command: retargeted };
}

/** Return the command position holding the index name after `--index`. */
function indexArgumentPosition(command: readonly JsoncValue[]): number | null {
  for (const [position, item] of command.entries()) {
    if (position === command.length - 1) {
      return null;
    }
    if (item === INDEX_FLAG && typeof command[position + 1] === "string") {
      return position + 1;
    }
  }
  return null;
}

/** Return the `--index` value of a parsed server value, if it has one. */
function qmdIndexName(value: JsoncValue): string | null {
  if (!isMapping(value)) {
    return null;
  }
  const command = value["command"];
  if (!Array.isArray(command)) {
    return null;
  }
  const position = indexArgumentPosition(command);
  if (position === null) {
    return null;
  }
  const indexName = command[position];
  return typeof indexName === "string" ? indexName : null;
}

/** Return an `mcp` member's raw text with its `qmd` index retargeted. */
function retargetMcpMemberText(
  sourceText: string,
  member: JsoncMember,
  projectName: string,
): string {
  return (
    sourceText.slice(member.memberStart, member.valueStart) +
    retargetMcpValueText(sourceText, member, projectName)
  );
}

/**
 * Return an `mcp` value's raw text with its `qmd` index retargeted.
 *
 * Only the `qmd` server's own span is rewritten, so an equal literal held by
 * another server is never touched.
 */
function retargetMcpValueText(
  sourceText: string,
  member: JsoncMember,
  projectName: string,
): string {
  const valueText = sourceText.slice(member.valueStart, member.valueEnd);
  const server = serverMember(member, QMD_SERVER_KEY);
  if (server === null) {
    return valueText;
  }
  const start = server.valueStart - member.valueStart;
  const end = server.valueEnd - member.valueStart;
  const serverText = retargetIndexLiteral(valueText.slice(start, end), server.value, projectName);
  return valueText.slice(0, start) + serverText + valueText.slice(end);
}

/** Return a `qmd` server's raw text with its `--index` literal replaced. */
function retargetIndexLiteral(
  serverText: string,
  serverValue: JsoncValue,
  projectName: string,
): string {
  if (projectName === "") {
    return serverText;
  }
  const indexName = qmdIndexName(serverValue);
  if (indexName === null || indexName === projectName) {
    return serverText;
  }
  const literal = JSON.stringify(indexName);
  const replacement = JSON.stringify(projectName);
  const at = serverText.indexOf(literal);
  if (at === -1) {
    return serverText;
  }
  return serverText.slice(0, at) + replacement + serverText.slice(at + literal.length);
}

/** Return one named server member under an `mcp` value, if present. */
function serverMember(span: JsoncMember, name: string): JsoncMember | null {
  const servers = serversObject(span);
  if (servers === null) {
    return null;
  }
  return servers.members.find((member) => member.key === name) ?? null;
}

function membersByKey(members: readonly JsoncMember[]): Map<string, JsoncMember> {
  return new Map(members.map((member) => [member.key, member]));
}

function applyEdits(text: string, edits: readonly Edit[]): string {
  if (edits.length === 0) {
    return text;
  }
  let cursor = 0;
  let output = "";
  for (const edit of [...edits].sort((left, right) =>
    left.start === right.start ? left.end - right.end : left.start - right.start,
  )) {
    output += text.slice(cursor, edit.start) + edit.text;
    cursor = edit.end;
  }
  return output + text.slice(cursor);
}

/** Return the indentation an object's inserted members should use. */
function memberIndent(text: string, object: JsoncObject): string {
  const last = object.members[object.members.length - 1];
  if (last !== undefined) {
    const prefix = linePrefix(text, last.memberStart);
    if (prefix.trim() === "") {
      return prefix;
    }
  }
  const closePrefix = linePrefix(text, object.closeIndex);
  if (closePrefix.trim() === "") {
    return closePrefix + MEMBER_INDENT;
  }
  return MEMBER_INDENT + MEMBER_INDENT;
}

/** Return the whitespace an object's closing brace is indented with. */
function closeLineIndent(text: string, object: JsoncObject): string {
  const prefix = linePrefix(text, object.closeIndex);
  return prefix.trim() === "" ? prefix : "";
}

/** Return the text between the previous newline and `index`. */
function linePrefix(text: string, index: number): string {
  return text.slice(text.lastIndexOf("\n", index - 1) + 1, index);
}

/** Return the destination's closing-brace offset after the edits. */
function shiftedCloseIndex(destination: JsoncObject, edits: readonly Edit[]): number {
  let shift = 0;
  for (const edit of edits) {
    if (edit.end <= destination.closeIndex) {
      shift += edit.text.length - (edit.end - edit.start);
    }
  }
  return destination.closeIndex + shift;
}

function isMapping(value: JsoncValue | undefined): value is JsoncMapping {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function jsoncEquals(left: JsoncValue | undefined, right: JsoncValue | undefined): boolean {
  if (left === right) {
    return true;
  }
  if (Array.isArray(left) || Array.isArray(right)) {
    if (!Array.isArray(left) || !Array.isArray(right) || left.length !== right.length) {
      return false;
    }
    return left.every((item, index) => jsoncEquals(item, right[index]));
  }
  if (!isMapping(left) || !isMapping(right)) {
    return false;
  }
  const leftKeys = Object.keys(left);
  const rightKeys = Object.keys(right);
  if (leftKeys.length !== rightKeys.length) {
    return false;
  }
  return leftKeys.every(
    (key) => Object.hasOwn(right, key) && jsoncEquals(left[key], right[key]),
  );
}
