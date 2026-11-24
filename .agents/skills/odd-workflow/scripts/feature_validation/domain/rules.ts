/** Pure feature-document rules, path ordering, and an injected path-comparison policy. */

import { basename, normalize, parse, sep } from "node:path";
import { readFenceStructure } from "#scripts/markdown/fences.ts";

const REQUIRED_HEADINGS = ["## Specs", "## Tasks", "## Log"] as const;
const SPEC_RE = /^- (?:\*\*)?S\p{Nd}+ — .+(?:\*\*)?$/u;
const TASK_RE =
	/^- T\p{Nd}+ \| S\p{Nd}+(?:, S\p{Nd}+)* \| .+ \| (?<status>open|in progress|done) \| commit: (?<commit>.*)$/u;
const COMMIT_RE = /^[0-9a-fA-F]{7,64}$/u;
const LOG_RE = /^- L1 — .+$/u;
const LOG_ENTRY_RE = /^- L(\p{Nd}+)/u;
const BLOCKED_LOG_RE = /^- L\p{Nd}+ .*\bBlocked: .+$/u;
const CREATED_DATE_RE = /^> \*\*Created:\*\* (\d{4}-\d{2}-\d{2})$/u;

/**
 * The date the completed-but-active rule took effect.
 *
 * The rule is prospective: it applies to records created on or after this date and
 * never retroactively. A record created earlier is historical, so its status and Log
 * are left exactly as written rather than rewritten to satisfy a later convention.
 */
export const CLOSURE_CONSISTENCY_EFFECTIVE_FROM = "2026-11-14";
const MAX_LOG_IDENTIFIER_DIGITS = 9;
const HEADER_RE = /^> \*\*(Status|Owner|Created):\*\* .+$/u;
const STATUS_RE = /^> \*\*Status:\*\* (active|closed)$/u;
const STATUS_CLOSED_RE = /^> \*\*Status:\*\* closed$/u;
const CLOSED_RE = /^> \*\*Closed:\*\* \S+/u;
const CLOSE_LOG_RE = /^- L\p{Nd}+ — Close: .+$/u;
const CLOSED_DATE_VALUE_RE = /^> \*\*Closed:\*\* (\d{4}-\d{2}-\d{2})$/u;

/**
 * The prospective date from which a closed record states its closure disposition.
 *
 * A record closed before it keeps the pre-disposition shape, so accepted history is never
 * rewritten to satisfy a rule it was not written against.
 */
export const DISPOSITION_EFFECTIVE_FROM = "2026-11-24";
const DISPOSITION_RE = /^> \*\*Disposition:\*\* (completed|cancelled|superseded)$/u;
const SUPERSEDED_BY_RE = /^> \*\*Superseded-by:\*\* \S/u;
const OBSOLESCENCE_RE = /\bobsolet\w*/iu;
const CANCELLATION_AUTHORIZATION_RE = /user[-\s]authori[sz]/iu;

/**
 * Parses a `YYYY-MM-DD` value to its UTC midnight, or `null` when it is not a real calendar date.
 *
 * A shaped but impossible value such as `2026-02-31` is not a readable closure date, so it must
 * not be treated as one: doing so would let a record escape a date-gated obligation.
 */
function parseCalendarDay(value: string): number | null {
	const year = Number(value.slice(0, 4));
	const month = Number(value.slice(5, 7));
	const day = Number(value.slice(8, 10));
	const time = Date.UTC(year, month - 1, day);
	const parsed = new Date(time);
	if (parsed.getUTCFullYear() !== year || parsed.getUTCMonth() !== month - 1 || parsed.getUTCDate() !== day) {
		return null;
	}
	return time;
}
const PLACEHOLDER_RE = /<[^>]+>/u;
const CODE_SPAN_RE = /`[^`]*`/gu;
// Deliberate: the validator must treat every Unicode line terminator as a break.
// oxlint-disable-next-line no-control-regex
const LINE_BREAK_RE = /\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/u;
// oxlint-disable-next-line no-control-regex
const LINE_BREAK_AT_END_RE = /(?:\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029])$/u;

const DECIMAL_ZERO_CODE_POINTS = [
	0x0030, 0x0660, 0x06f0, 0x07c0, 0x0966, 0x09e6, 0x0a66, 0x0ae6, 0x0b66, 0x0be6, 0x0c66, 0x0ce6, 0x0d66, 0x0de6,
	0x0e50, 0x0ed0, 0x0f20, 0x1040, 0x1090, 0x17e0, 0x1810, 0x1946, 0x19d0, 0x1a80, 0x1a90, 0x1b50, 0x1bb0, 0x1c40,
	0x1c50, 0xa620, 0xa8d0, 0xa900, 0xa9d0, 0xa9f0, 0xaa50, 0xabf0, 0xff10, 0x104a0, 0x10d30, 0x11066, 0x110f0, 0x11136,
	0x111d0, 0x112f0, 0x11450, 0x114d0, 0x11650, 0x116c0, 0x11730, 0x118e0, 0x11950, 0x11c50, 0x11d50, 0x11da0, 0x11f50,
	0x16a60, 0x16ac0, 0x16b50, 0x1d7ce, 0x1d7d8, 0x1d7e2, 0x1d7ec, 0x1d7f6, 0x1e140, 0x1e2f0, 0x1e4f0, 0x1e950, 0x1fbf0,
];

export function splitLines(text: string): string[] {
	if (text.length === 0) return [];
	const lines = text.split(LINE_BREAK_RE);
	if (LINE_BREAK_AT_END_RE.test(text)) lines.pop();
	return lines;
}

/** Maps non-ASCII decimal digits onto their ASCII digits and leaves every other character unchanged. */
function decimalDigitsToAscii(value: string): string {
	return Array.from(value)
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

export function isTemplateReference(reference: string): boolean {
	return basename(reference) === "_template.md";
}

export function sortFeatureReferences(references: readonly string[], policy: PathComparisonPolicy): string[] {
	return [...references].sort((left, right) => comparePath(left, right, policy));
}

export function section(lines: readonly string[], heading: string): string[] {
	const start = lines.findIndex((line) => line.trim() === heading);
	if (start < 0) return [];
	let end = lines.length;
	const logBody = heading === "## Log";
	for (let index = start + 1; index < lines.length; index += 1) {
		const candidate = lines[index]!;
		if (logBody) {
			const trimmed = candidate.trim();
			if (trimmed !== heading && REQUIRED_HEADINGS.some((required) => required === trimmed)) {
				end = index;
				break;
			}
			continue;
		}
		if (candidate.startsWith("## ")) {
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
 * Format a diagnostic value as a quoted literal.
 *
 * Single quotes are the default. The value is wrapped in double quotes only
 * when it contains a single quote and no double quote. Backslashes, the
 * chosen delimiter and control characters are escaped; every other character
 * stays literal.
 */
export function quoteDiagnosticValue(value: string): string {
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

/**
 * Whether the completed-but-active rule applies to a record.
 *
 * The rule is prospective, so a record created before the effective date is exempt
 * and its history is never rewritten. A record that declares no readable creation
 * date is treated as in scope, so a new record cannot escape the rule by omitting
 * the field.
 */
function closureConsistencyApplies(lines: readonly string[]): boolean {
	const headerEnd = lines.findIndex((line) => line.startsWith("## "));
	const header = headerEnd < 0 ? lines : lines.slice(0, headerEnd);
	const created = header.map((line) => CREATED_DATE_RE.exec(line.trim())).filter((match) => match !== null);
	if (created.length !== 1) return true;
	return created[0]![1]! >= CLOSURE_CONSISTENCY_EFFECTIVE_FROM;
}

/**
 * Whether the record's most recent Log entry names an open closure prerequisite.
 *
 * The exemption tracks the record's current state: a prerequisite recorded once and
 * later resolved stops suppressing the finding, because the finding asks for the
 * prerequisite that is open now.
 */
function namesOpenClosurePrerequisite(logLines: readonly string[]): boolean {
	let latestIdentifier: bigint | null = null;
	let latestLine = "";
	for (const line of logLines) {
		const match = LOG_ENTRY_RE.exec(line);
		const digits = match?.[1];
		if (digits === undefined) continue;
		if (Array.from(digits).length > MAX_LOG_IDENTIFIER_DIGITS) continue;
		const identifier = BigInt(decimalDigitsToAscii(digits));
		if (latestIdentifier === null || identifier > latestIdentifier) {
			latestIdentifier = identifier;
			latestLine = line;
		}
	}
	return latestIdentifier !== null && BLOCKED_LOG_RE.test(latestLine);
}

/**
 * Groups the `## Specs` section into entries.
 *
 * An entry begins at a top-level bullet and owns the indented lines that follow it,
 * so a specification may carry its heading, its verbatim requirement quotation and
 * its acceptance criteria as separate readable lines without becoming several
 * entries.
 */
function specSectionBlocks(specLines: readonly string[]): string[][] {
	const blocks: string[][] = [];
	for (const line of specLines) {
		if (line.startsWith("- ")) {
			blocks.push([line]);
			continue;
		}
		if (blocks.length > 0 && line.trim().length > 0) {
			blocks[blocks.length - 1]!.push(line);
		}
	}
	return blocks;
}

/** The effective date of the closure-evidence rules, separate from the closure-consistency date. */
export const CLOSURE_EVIDENCE_EFFECTIVE_FROM = "2026-11-19";

const FIRST_FAILURE_RE = /\bfirst fail(?:ure|ing|ed)\b/iu;
const NO_EXECUTABLE_FAILURE_RE =
	/\b(?:no applicable executable failure|executable failure cannot apply|no executable failure applies)\b/iu;

/** Whether the closure-evidence rules govern a record, by its created date. */
function closureEvidenceApplies(lines: readonly string[]): boolean {
	const created = lines.map((line) => CREATED_DATE_RE.exec(line.trim())?.[1]).filter((value) => value !== undefined);
	if (created.length === 0) return false;
	// A present but unreadable date fails closed, like the closure-consistency sibling, so a
	// malformed record cannot escape the rule by carrying a date the parser rejects.
	const declared = created[0]!;
	if (!/^\d{4}-\d{2}-\d{2}$/u.test(declared)) return true;
	return declared >= CLOSURE_EVIDENCE_EFFECTIVE_FROM;
}

/**
 * The closure-evidence findings for a closed record the rules govern.
 *
 * The per-spec reviewer-verdict requirement and the commit-binding of those verdict entries were
 * retired with the multi-agent acceptance model: a record is no longer closed by a second agent's
 * verdict, so requiring one would be an obligation with no owner. The first-failure rule survives
 * because it is an evidence-honesty obligation about the delivered work, not about a reviewer.
 */
function closureEvidenceFindings(logLines: readonly string[]): string[] {
	const findings: string[] = [];
	const logText = logLines.join("\n");
	if (!FIRST_FAILURE_RE.test(logText) && !NO_EXECUTABLE_FAILURE_RE.test(logText)) {
		findings.push(
			"closed feature needs the first failure recorded or the reason an executable failure cannot apply",
		);
	}
	return findings;
}

export function validateFeature(text: string): string[] {
	const findings: string[] = [];
	// One structural view serves every rule below: the unfenced projection is the document with
	// fenced lines removed, so a quoted example can never stand in for record structure — not a
	// heading or section boundary, not header metadata, not a Specs, Tasks or Log entry, not a
	// Close entry, an identifier, a cancellation authorization or a placeholder.
	const fenceStructure = readFenceStructure(splitLines(text));
	const lines = fenceStructure.unfencedLines;
	const log = section(lines, "## Log");

	for (const fence of fenceStructure.unclosed) {
		findings.push(
			`unclosed Markdown code fence opened at line ${fence.line} with ${fence.length} ${fence.marker === "`" ? "backtick" : "tilde"} character(s); add the closing fence`,
		);
	}

	const headings = lines.filter((line) => line.startsWith("## ")).map((line) => line.trim());
	for (const heading of REQUIRED_HEADINGS) {
		const count = headings.filter((candidate) => candidate === heading).length;
		if (count !== 1) {
			findings.push(`heading ${quoteDiagnosticValue(heading)} must appear exactly once; found ${count}`);
		}
	}

	if (!lines.some((line) => line.startsWith("# ") && line.trim() !== "# Feature name")) {
		findings.push("title must not be the template placeholder");
	}

	const headerFields = new Set<string>();
	for (const line of lines) {
		const match = HEADER_RE.exec(line);
		if (match?.[1] !== undefined) headerFields.add(match[1]);
	}
	for (const field of ["Status", "Owner", "Created"]) {
		if (!headerFields.has(field)) findings.push(`header must include ${field}`);
	}
	if (text.includes("> **Created:** date")) {
		findings.push("Created must be a real date, not the template placeholder");
	}
	const createdFields = lines.filter((line) => line.trim().startsWith("> **Created:**")).length;
	if (createdFields !== 1) {
		findings.push(`header must include exactly one Created line; found ${createdFields}`);
	}

	const statusLines = lines.map((line) => line.trim()).filter((line) => line.startsWith("> **Status:**"));
	if (statusLines.length !== 1) {
		findings.push("header must include exactly one Status line");
	} else if (!STATUS_RE.test(statusLines[0]!)) {
		findings.push("Status must be active or closed");
	}

	const isClosed = lines.some((line) => STATUS_CLOSED_RE.test(line));
	if (isClosed && !lines.some((line) => CLOSED_RE.test(line.trim()))) {
		findings.push("closed feature needs a Closed date");
	}

	const closedLine = lines.map((line) => line.trim()).find((line) => line.startsWith("> **Closed:**"));
	const closedValue = CLOSED_DATE_VALUE_RE.exec(closedLine ?? "")?.[1];
	// A closed record whose closure date is absent or is not a real calendar date is treated as
	// in scope, so a shaped but impossible value such as `2026-02-31` cannot escape the
	// disposition obligation either.
	const dispositionApplies =
		isClosed &&
		(closedValue === undefined ||
			parseCalendarDay(closedValue) === null ||
			closedValue >= DISPOSITION_EFFECTIVE_FROM);
	const dispositionLines = lines.map((line) => line.trim()).filter((line) => line.startsWith("> **Disposition:**"));
	let disposition: string | undefined;
	if (dispositionApplies) {
		if (dispositionLines.length !== 1) {
			findings.push("closed feature needs exactly one Disposition line: completed, cancelled or superseded");
		} else {
			const match = DISPOSITION_RE.exec(dispositionLines[0] ?? "");
			if (match === null) {
				findings.push("Disposition must be completed, cancelled or superseded");
			} else {
				disposition = match[1];
			}
		}
		if (disposition === "superseded") {
			const hasReplacement = lines.some((line) => SUPERSEDED_BY_RE.test(line.trim()));
			const hasObsolescenceExplanation = log.some(
				(line) => CLOSE_LOG_RE.test(line) && OBSOLESCENCE_RE.test(line),
			);
			if (!hasReplacement && !hasObsolescenceExplanation) {
				findings.push(
					"superseded feature needs a Superseded-by delivery reference or a Close entry explaining why its requirements are obsolete",
				);
			}
		}
		if (disposition === "cancelled" && !CANCELLATION_AUTHORIZATION_RE.test(log.join("\n"))) {
			findings.push(
				"cancelled feature needs a Log entry recording explicit user authorization for the cancellation",
			);
		}
	}
	const claimsCompletion = disposition === undefined || disposition === "completed";

	const hasCloseEntry = log.some((line) => CLOSE_LOG_RE.test(line));
	if (isClosed && !hasCloseEntry) {
		findings.push("closed feature needs a Log 'Close:' entry");
	}
	if (!isClosed && hasCloseEntry) {
		findings.push("active feature has a Log 'Close:' entry; set Status: closed");
	}

	const specs = section(lines, "## Specs");
	const tasks = section(lines, "## Tasks");
	const specBlocks = specSectionBlocks(specs);
	const taskEntries = tasks.filter((line) => line.startsWith("- "));

	if (specBlocks.length === 0) {
		findings.push("Specs needs at least one '- S# — ...' entry");
	}
	for (const block of specBlocks) {
		const heading = block[0]!;
		if (!SPEC_RE.test(heading)) {
			findings.push(`Specs entry must match '- S# — ...': ${heading.trim()}`);
		}
	}

	if (taskEntries.length === 0) {
		findings.push("Tasks needs at least one '- T# | S# | ... | status | commit: ...' entry");
	}
	for (const line of taskEntries) {
		if (!TASK_RE.test(line)) {
			findings.push(
				`Tasks entry must match '- T# | S# | ... | open|in progress|done | commit: ...': ${line.trim()}`,
			);
		}
	}

	for (const line of taskEntries) {
		const match = TASK_RE.exec(line);
		if (match === null) continue;
		const status = match.groups?.status;
		const commit = match.groups?.commit?.trim() ?? "";
		const hasCommitReference = COMMIT_RE.test(commit);
		if (!commit) findings.push(`task commit must not be blank: ${line.trim()}`);
		if (status === "done" && !hasCommitReference) {
			findings.push(`done task must have a 7-64 character hexadecimal commit identifier: ${line.trim()}`);
		} else if (commit !== "pending" && !hasCommitReference) {
			findings.push(
				`task commit must be 'pending' or a 7-64 character hexadecimal commit identifier: ${line.trim()}`,
			);
		}
		if (isClosed && claimsCompletion) {
			if (status !== "done") findings.push(`closed feature has a ${status} task: ${line.trim()}`);
			if (status !== "done" && !hasCommitReference) {
				findings.push(
					`closed feature task must have a 7-64 character hexadecimal commit identifier: ${line.trim()}`,
				);
			}
		}
	}

	if (!log.some((line) => LOG_RE.test(line))) findings.push("Log needs an L1 entry");

	const taskStatuses = taskEntries
		.map((line) => TASK_RE.exec(line)?.groups?.status)
		.filter((status) => status !== undefined);
	if (
		closureConsistencyApplies(lines) &&
		!isClosed &&
		taskEntries.length > 0 &&
		taskStatuses.length === taskEntries.length &&
		taskStatuses.every((status) => status === "done") &&
		!namesOpenClosurePrerequisite(log)
	) {
		findings.push(
			"active record has every task done: close the record or record the open closure prerequisite as a Log entry",
		);
	}

	if (isClosed && claimsCompletion && closureEvidenceApplies(lines)) {
		findings.push(...closureEvidenceFindings(log));
	}

	const logIdentifiers: bigint[] = [];
	for (const line of log) {
		const match = LOG_ENTRY_RE.exec(line);
		const digits = match?.[1];
		if (digits === undefined) continue;
		if (/[^\u0030-\u0039]/u.test(digits)) {
			findings.push(`Log entry identifier must use ASCII digits: ${line.trim()}`);
			continue;
		}
		if (Array.from(digits).length > MAX_LOG_IDENTIFIER_DIGITS) {
			findings.push(`Log entry identifier is not a valid L number: ${line.trim()}`);
			continue;
		}
		logIdentifiers.push(BigInt(decimalDigitsToAscii(digits)));
	}

	for (let index = 1; index < logIdentifiers.length; index += 1) {
		const previous = logIdentifiers[index - 1]!;
		const current = logIdentifiers[index]!;
		if (current <= previous) {
			findings.push(`Log entry identifiers must ascend strictly: L${current} follows L${previous}`);
			break;
		}
	}

	const counts = new Map<bigint, number>();
	for (const identifier of logIdentifiers) {
		counts.set(identifier, (counts.get(identifier) ?? 0) + 1);
	}
	for (const identifier of [...counts.keys()].sort((left, right) => (left < right ? -1 : left > right ? 1 : 0))) {
		if (counts.get(identifier)! > 1) {
			findings.push(`Log entry identifier must be unique: L${identifier} appears more than once`);
		}
	}

	if (logIdentifiers.length > 0 && logIdentifiers[0] !== 1n) {
		findings.push(`first Log entry must be L1: L${logIdentifiers[0]}`);
	}

	for (const line of lines) {
		if (PLACEHOLDER_RE.test(stripCode(line))) {
			findings.push(`unfilled placeholder: ${line.trim()}`);
		}
	}

	return findings;
}
