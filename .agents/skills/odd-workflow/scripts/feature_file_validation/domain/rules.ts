/** Pure durable feature-file rules, status derivation, and path ordering. */

import { basename, normalize, parse, sep } from "node:path";
import {
  FeatureFileAssessment,
  FeatureRequirement,
} from "./records.ts";
import type { FeatureStatus } from "./records.ts";

const TEMPLATE_NAME = "_template.md";
const REQUIREMENTS_HEADING = "## Requirements";
const GUIDANCE_HEADING = "## Guidance";
const COMPLETION_HEADING = "## Completion";
const ACHIEVED: FeatureStatus = "achieved";
const PARTIAL: FeatureStatus = "partial";
const NOT_STARTED: FeatureStatus = "not started";
const STATUSES: readonly FeatureStatus[] = [ACHIEVED, PARTIAL, NOT_STARTED];
const MARKS = [
  "upstream",
  "upstream · local detail",
  "upstream · narrowed",
  "local",
  "local · conflicts",
] as const;

const TITLE_RE = /^# (?<title>\S.*)$/u;
const STATUS_RE = /^\*\*Status:\*\*[ \t]*(?<value>.*)$/u;
const REQUIREMENT_RE =
  /^- \[(?<tick>[x ])\] R(?<number>\p{Nd}+) (?:`(?<mark>[^`]*)` )?— (?<wording>.+)$/u;
const STATE_FIELD_RE = /(?:\*\*|__)?[ \t]*State[ \t]*(?:\*\*|__)?[ \t]*:/u;
const PLACEHOLDER_RE = /<[^>]+>/u;
const CODE_SPAN_RE = /`[^`]*`/gu;
const FENCED_BLOCK_RE = /```[\s\S]*?```/gu;
const LINE_BREAK_RE = /\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/u;
const LINE_BREAK_AT_END_RE = /(?:\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029])$/u;
const DECIMAL_ZERO_CODE_POINTS = [
  0x0030, 0x0660, 0x06f0, 0x07c0, 0x0966, 0x09e6, 0x0a66, 0x0ae6,
  0x0b66, 0x0be6, 0x0c66, 0x0ce6, 0x0d66, 0x0de6, 0x0e50, 0x0ed0,
  0x0f20, 0x1040, 0x1090, 0x17e0, 0x1810, 0x1946, 0x19d0, 0x1a80,
  0x1a90, 0x1b50, 0x1bb0, 0x1c40, 0x1c50, 0xa620, 0xa8d0, 0xa900,
  0xa9d0, 0xa9f0, 0xaa50, 0xabf0, 0xff10, 0x104a0, 0x10d30, 0x11066,
  0x110f0, 0x11136, 0x111d0, 0x112f0, 0x11450, 0x114d0, 0x11650,
  0x116c0, 0x11730, 0x118e0, 0x11950, 0x11c50, 0x11d50, 0x11da0,
  0x11f50, 0x16a60, 0x16ac0, 0x16b50, 0x1d7ce, 0x1d7d8, 0x1d7e2,
  0x1d7ec, 0x1d7f6, 0x1e140, 0x1e2f0, 0x1e4f0, 0x1e950, 0x1fbf0,
];

function splitLines(text: string): string[] {
  if (text.length === 0) return [];
  const lines = text.split(LINE_BREAK_RE);
  if (LINE_BREAK_AT_END_RE.test(text)) lines.pop();
  return lines;
}

function pythonDecimalToAscii(value: string): string {
  return [...value]
    .map((character) => {
      const codePoint = character.codePointAt(0);
      if (codePoint === undefined) return character;
      const zero = DECIMAL_ZERO_CODE_POINTS.find(
        (candidate) => codePoint >= candidate && codePoint < candidate + 10,
      );
      return zero === undefined ? character : String(codePoint - zero);
    })
    .join("");
}

function pathParts(reference: string): string[] {
  const normalized = normalize(reference);
  const root = parse(normalized).root;
  const parts = normalized.slice(root.length).split(sep).filter(Boolean);
  return root ? [root, ...parts] : parts;
}

/** The comparison policy that decides whether path parts compare case-sensitively. */
export type PathComparisonPolicy = {
  readonly caseSensitive: boolean;
};

function comparePathPart(left: string, right: string, policy: PathComparisonPolicy): number {
  const leftKey = policy.caseSensitive ? left : left.toLowerCase();
  const rightKey = policy.caseSensitive ? right : right.toLowerCase();
  return leftKey < rightKey ? -1 : leftKey > rightKey ? 1 : 0;
}

function comparePath(left: string, right: string, policy: PathComparisonPolicy): number {
  const leftParts = pathParts(left);
  const rightParts = pathParts(right);
  const sharedLength = Math.min(leftParts.length, rightParts.length);
  for (let index = 0; index < sharedLength; index += 1) {
    const comparison = comparePathPart(leftParts[index]!, rightParts[index]!, policy);
    if (comparison !== 0) return comparison;
  }
  return leftParts.length - rightParts.length;
}

function isTemplateReference(reference: string): boolean {
  return basename(reference) === TEMPLATE_NAME;
}

function sortFeatureFileReferences(
  references: readonly string[],
  policy: PathComparisonPolicy,
): string[] {
  return [...references].sort((left, right) => comparePath(left, right, policy));
}

function section(lines: readonly string[], heading: string): string[] {
  const start = lines.findIndex((line) => line.trim() === heading);
  if (start < 0) return [];
  let end = lines.length;
  for (let index = start + 1; index < lines.length; index += 1) {
    if (lines[index]!.startsWith("## ")) {
      end = index;
      break;
    }
  }
  return lines.slice(start + 1, end);
}

function stripCode(line: string): string {
  return line.replace(CODE_SPAN_RE, "");
}

/**
 * Format a value with Python `repr` semantics for strings.
 *
 * Python prefers single quotes and switches to double quotes only when the
 * value contains a single quote and no double quote. Backslashes, the chosen
 * delimiter and control characters are escaped; every other character stays
 * literal.
 */
export function pythonRepr(value: string): string {
  const delimiter = value.includes("'") && !value.includes('"') ? '"' : "'";
  let rendered = "";
  for (const character of value) {
    if (character === "\\") {
      rendered += "\\\\";
      continue;
    }
    if (character === delimiter) {
      rendered += `\\${delimiter}`;
      continue;
    }
    if (character === "\n") {
      rendered += "\\n";
      continue;
    }
    if (character === "\r") {
      rendered += "\\r";
      continue;
    }
    if (character === "\t") {
      rendered += "\\t";
      continue;
    }
    const codePoint = character.codePointAt(0) ?? 0;
    if (codePoint < 0x20 || codePoint === 0x7f) {
      rendered += `\\x${codePoint.toString(16).padStart(2, "0")}`;
      continue;
    }
    rendered += character;
  }
  return `${delimiter}${rendered}${delimiter}`;
}

function titleIndex(lines: readonly string[]): number | null {
  for (let index = 0; index < lines.length; index += 1) {
    if (TITLE_RE.test(lines[index]!)) return index;
  }
  return null;
}

function titleFindings(lines: readonly string[]): string[] {
  if (titleIndex(lines) !== null) return [];
  return [
    "feature-file-title: the file must open with an H1 title line '# <feature name>'",
  ];
}

function descriptionFindings(lines: readonly string[]): string[] {
  const title = titleIndex(lines);
  if (title === null) return [];
  const paragraph: string[] = [];
  for (const line of lines.slice(title + 1)) {
    if (line.startsWith("#") || STATUS_RE.test(line)) break;
    if (line.trim()) paragraph.push(line);
  }
  if (paragraph.length > 0) return [];
  return [
    "feature-file-description: the title needs one paragraph saying what the feature is",
  ];
}

function statusValues(lines: readonly string[]): string[] {
  const values: string[] = [];
  for (const line of lines) {
    const value = STATUS_RE.exec(line)?.groups?.value;
    if (value !== undefined) values.push(value.trim());
  }
  return values;
}

function statusFindings(lines: readonly string[]): string[] {
  const values = statusValues(lines);
  if (values.length === 0) {
    return [
      "feature-file-status: the file must carry exactly one '**Status:** achieved|partial|not started' line; found none",
    ];
  }
  if (values.length > 1) {
    return [
      `feature-file-status: the file must carry exactly one status line; found ${values.length}`,
    ];
  }
  const value = values[0]!;
  if (!STATUSES.includes(value as FeatureStatus)) {
    return [
      `feature-file-status: status must be one of 'achieved', 'partial' or 'not started'; found ${pythonRepr(value)}`,
    ];
  }
  return [];
}

function requirementCandidates(lines: readonly string[]): string[] {
  return section(lines, REQUIREMENTS_HEADING).filter((line) => line.startsWith("- ["));
}

function requirementLines(lines: readonly string[]): string[] {
  return requirementCandidates(lines).filter((line) => REQUIREMENT_RE.test(line));
}

function requirementsFindings(lines: readonly string[]): string[] {
  const count = lines.filter((line) => line.trim() === REQUIREMENTS_HEADING).length;
  if (count !== 1) {
    return [
      `feature-file-requirements: heading '${REQUIREMENTS_HEADING}' must appear exactly once; found ${count}`,
    ];
  }
  if (requirementLines(lines).length === 0) {
    return [
      "feature-file-requirements: '## Requirements' needs at least one '- [ ] R<n> — <requirement>' line",
    ];
  }
  return [];
}

function entryFindings(lines: readonly string[]): string[] {
  return requirementCandidates(lines)
    .filter((line) => !REQUIREMENT_RE.test(line))
    .map(
      (line) =>
        "feature-file-requirement-entry: requirement line must match '- [x] R<n> — <requirement>' or '- [x] R<n> `<mark>` — <requirement>': " +
        line.trim(),
    );
}

function requirementNumbers(lines: readonly string[]): bigint[] {
  return requirementLines(lines).flatMap((line) => {
    const number = REQUIREMENT_RE.exec(line)?.groups?.number;
    return number === undefined ? [] : [BigInt(pythonDecimalToAscii(number))];
  });
}

function numberingFindings(lines: readonly string[]): string[] {
  const numbers = requirementNumbers(lines);
  let expected = 1n;
  for (const number of numbers) {
    if (number !== expected) {
      return [
        `feature-file-requirement-numbering: requirement numbers must be consecutive from 1 with no gaps or duplicates; found [${numbers.join(", ")}]`,
      ];
    }
    expected += 1n;
  }
  return [];
}

export function readRequirements(text: string): FeatureRequirement[] {
  const requirements: FeatureRequirement[] = [];
  for (const line of requirementLines(splitLines(text))) {
    const groups = REQUIREMENT_RE.exec(line)?.groups;
    if (groups === undefined) continue;
    requirements.push(
      new FeatureRequirement(
        groups.number!,
        groups.mark ?? "",
        groups.wording!,
        groups.tick === "x",
      ),
    );
  }
  return requirements;
}

function markFindings(text: string): string[] {
  return readRequirements(text)
    .filter((requirement) => requirement.mark !== "" && !MARKS.includes(requirement.mark as (typeof MARKS)[number]))
    .map(
      (requirement) =>
        `feature-file-requirement-mark: requirement ${requirement.number} carries an unknown mark ${pythonRepr(requirement.mark)}; marks are 'upstream', 'upstream · local detail', 'upstream · narrowed', 'local' or 'local · conflicts'`,
    );
}

function supersededFindings(lines: readonly string[]): string[] {
  const findings: string[] = [];
  if (lines.some((line) => line.trim() === COMPLETION_HEADING)) {
    findings.push(
      `feature-file-superseded-section: '${COMPLETION_HEADING}' is a superseded completion-sheet section; the feature file records its requirements instead`,
    );
  }
  for (const line of requirementCandidates(lines)) {
    if (STATE_FIELD_RE.test(line)) {
      findings.push(
        `feature-file-superseded-state: requirement line carries the superseded 'State:' field: ${line.trim()}`,
      );
    }
  }
  return findings;
}

function placeholderFindings(text: string): string[] {
  return splitLines(text.replace(FENCED_BLOCK_RE, ""))
    .filter((line) => PLACEHOLDER_RE.test(stripCode(line)))
    .map((line) => `feature-file-unfilled-placeholder: unfilled placeholder: ${line.trim()}`);
}

function guidanceFindings(lines: readonly string[]): string[] {
  if (!lines.some((line) => line.trim() === GUIDANCE_HEADING)) return [];
  return [
    `feature-file-template-guidance: '${GUIDANCE_HEADING}' is template-only; a real feature file carries no Guidance section`,
  ];
}

export function deriveFeatureStatus(
  requirements: readonly FeatureRequirement[],
): FeatureStatus | null {
  if (requirements.length === 0) return null;
  const ticked = requirements.filter((requirement) => requirement.ticked).length;
  if (ticked === requirements.length) return ACHIEVED;
  if (ticked > 0) return PARTIAL;
  return NOT_STARTED;
}

function derivationFindings(text: string): string[] {
  const values = statusValues(splitLines(text));
  if (values.length !== 1 || !STATUSES.includes(values[0] as FeatureStatus)) return [];
  const derived = deriveFeatureStatus(readRequirements(text));
  if (derived === null || derived === values[0]) return [];
  return [
    `feature-file-status-derivation: declared status ${pythonRepr(values[0]!)} does not match the status derived from the ticks ${pythonRepr(derived)}`,
  ];
}

function findings(text: string): string[] {
  const lines = splitLines(text);
  return [
    ...titleFindings(lines),
    ...descriptionFindings(lines),
    ...statusFindings(lines),
    ...requirementsFindings(lines),
    ...entryFindings(lines),
    ...numberingFindings(lines),
    ...markFindings(text),
    ...derivationFindings(text),
    ...supersededFindings(lines),
    ...placeholderFindings(text),
    ...guidanceFindings(lines),
  ];
}

export function assessFeatureFile(text: string): FeatureFileAssessment {
  return new FeatureFileAssessment(findings(text), deriveFeatureStatus(readRequirements(text)));
}

export function validateFeatureFile(text: string): string[] {
  return findings(text);
}

export { isTemplateReference as isTemplateFeatureFileReference };
export { sortFeatureFileReferences };
