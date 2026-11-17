import { InputError } from "#scripts/incident_workflow_pkg/domain/errors.ts";
import { Problem } from "#scripts/incident_workflow_pkg/domain/problem.ts";
import type { ProblemFields } from "#scripts/incident_workflow_pkg/domain/problem.ts";
import type { AnalysisHeader, TicketIdentification } from "#scripts/incident_workflow_pkg/domain/rules.ts";
import { loadFrontMatter } from "./frontmatter.ts";

/**
 * Name what actually arrived, so a writer can act on it. The YAML 1.1 schema this skill parses
 * with turns an unquoted timestamp into a `Date`, which is neither a mapping nor a scalar and must
 * not be reported as one.
 */
function describeKind(value: unknown): string {
	if (Array.isArray(value)) return "a list";
	if (typeof value !== "object") return `a value of type ${typeof value}`;
	const prototype = Object.getPrototypeOf(value) as { constructor?: { name?: string } } | null;
	if (prototype === null || prototype === Object.prototype) return "a mapping";
	const name = prototype.constructor?.name;
	return name === undefined ? "a non-scalar object" : `a ${name} value`;
}

function scalarText(value: unknown, field: string, source: string): string {
	if (value === null) return "None";
	if (typeof value === "boolean") return value ? "True" : "False";
	if (typeof value === "string") return value;
	if (typeof value === "number" || typeof value === "bigint") return String(value);
	throw new InputError(`Field '${field}' in ${source} must be a scalar value, found ${describeKind(value)}`);
}

function stringList(value: unknown, field: string, source: string): string[] {
	if (value === null || value === undefined) return [];
	if (Array.isArray(value))
		return value
			.map((item) => scalarText(item, field, source))
			.map((item) => item.trim())
			.filter(Boolean);
	const text = scalarText(value, field, source).trim();
	if (!text || text === "[]") return [];
	return text
		.split(",")
		.map((item) => item.trim())
		.filter(Boolean);
}

export function parseStateHeader(content: string, source: string): AnalysisHeader {
	const data = loadFrontMatter(content, source);
	const fields = [
		"Phase",
		"SLA-due",
		"Updated",
		"Hypotheses-outstanding",
		"Query-budget",
		"identification_verdict",
		"Same-query-reruns",
	];
	const missing = fields.filter((field) => !Object.hasOwn(data, field)).sort();
	if (missing.length)
		throw new InputError(
			`Missing header fields in ${source}: [${missing.map((field) => `'${field}'`).join(", ")}]`,
		);
	return {
		Phase: scalarText(data.Phase, "Phase", source),
		SLA_due: scalarText(data["SLA-due"], "SLA-due", source),
		Updated: scalarText(data.Updated, "Updated", source),
		Hypotheses_outstanding: scalarText(data["Hypotheses-outstanding"], "Hypotheses-outstanding", source),
		Query_budget: scalarText(data["Query-budget"], "Query-budget", source),
		Identification_verdict: scalarText(data.identification_verdict, "identification_verdict", source),
		Same_query_reruns: scalarText(data["Same-query-reruns"], "Same-query-reruns", source),
	};
}

export function parseTicketRecord(content: string, source: string): TicketIdentification {
	const data = loadFrontMatter(content, source);
	return {
		symptom_ids: stringList(data.symptom_ids, "symptom_ids", source),
		known_problem_ids: stringList(data.known_problem_ids, "known_problem_ids", source),
		identification_verdict: scalarText(
			Object.hasOwn(data, "identification_verdict") ? data.identification_verdict : "pending",
			"identification_verdict",
			source,
		).trim(),
	};
}

export function parseProblemRegister(content: string): Problem[] {
	const rows: Problem[] = [];
	for (const line of content.split(/\r\n|\n|\r/)) {
		const trimmed = line.trim();
		if (!trimmed.startsWith("|")) continue;
		const cells = trimmed
			.replace(/^\|+|\|+$/g, "")
			.split("|")
			.map((cell) => cell.trim());
		if (cells.length !== 14 || !/^P-\d+$/.test(cells[0] ?? "")) continue;
		const [
			id,
			date,
			team,
			symptom,
			system,
			module,
			problem,
			discriminators,
			exclusions,
			evidence,
			rootCause,
			lifecycle,
			allowExact,
			status,
		] = cells;
		const fields: ProblemFields = {
			id: id!,
			date: date!,
			team: team!,
			symptom: symptom!,
			system: system!,
			module: module!,
			problem: problem!,
			discriminators: discriminators!,
			exclusions: exclusions!,
			evidence: evidence!,
			rootCause: rootCause!,
			lifecycle: lifecycle!,
			allowExact: allowExact!,
			status: status!,
		};
		const result = Problem.create(fields);
		if (result instanceof Problem) rows.push(result);
	}
	return rows;
}

/** A register row read as declared cells, before any field validation. */
export interface RawProblemRow {
	readonly id: string;
	readonly symptom: string;
}

/**
 * Read every declared problem row without validating its fields.
 *
 * A row that fails an invariant is still a row the register declares, so the
 * diagnostic-knowledge check reports it instead of losing it to a filter.
 */
export function readProblemRows(content: string): RawProblemRow[] {
	const rows: RawProblemRow[] = [];
	for (const line of content.split(/\r\n|\n|\r/)) {
		const trimmed = line.trim();
		if (!trimmed.startsWith("|")) continue;
		const cells = trimmed
			.replace(/^\|+|\|+$/g, "")
			.split("|")
			.map((cell) => cell.trim());
		if (!/^P-\d+$/.test(cells[0] ?? "")) continue;
		rows.push({ id: cells[0] ?? "", symptom: cells[3] ?? "" });
	}
	return rows;
}

export function checkRegisterRows(content: string): string[] {
	const violations: string[] = [];
	const lines = content.split(/\r\n|\n|\r/);
	for (const [index, line] of lines.entries()) {
		const trimmed = line.trim();
		if (!trimmed.startsWith("|")) continue;
		const cells = trimmed
			.replace(/^\|+|\|+$/g, "")
			.split("|")
			.map((cell) => cell.trim());
		const id = cells[0] ?? "";
		if (!/^P-\d+$/.test(id)) continue;
		if (cells.length !== 14) {
			violations.push(`REGISTER-1: ${id} (line ${index + 1}) has ${cells.length} columns, expected 14`);
			continue;
		}
		const [
			problemId,
			date,
			team,
			symptom,
			system,
			module,
			problem,
			discriminators,
			exclusions,
			evidence,
			rootCause,
			lifecycle,
			allowExact,
			status,
		] = cells;
		const result = Problem.create({
			id: problemId!,
			date: date!,
			team: team!,
			symptom: symptom!,
			system: system!,
			module: module!,
			problem: problem!,
			discriminators: discriminators!,
			exclusions: exclusions!,
			evidence: evidence!,
			rootCause: rootCause!,
			lifecycle: lifecycle!,
			allowExact: allowExact!,
			status: status!,
		});
		if (result instanceof Problem) continue;
		const quoted = `'${result.message}'`;
		switch (result.code) {
			case "invalid_team":
				violations.push(`REGISTER-2: ${id} Team ${quoted} not in (dev, incident)`);
				break;
			case "invalid_lifecycle":
				violations.push(
					`REGISTER-3: ${id} Lifecycle ${quoted} not in (active, candidate, mitigated, resolved, retired)`,
				);
				break;
			case "invalid_allow_exact":
				violations.push(`REGISTER-4: ${id} Allow_exact ${quoted} not in (no, yes)`);
				break;
			case "invalid_status":
				violations.push(`REGISTER-5: ${id} Status ${quoted} not in (closed, open)`);
				break;
			case "missing_symptom_reference":
				violations.push(`REGISTER-6: ${id} Symptom ${quoted} references no S-xx`);
				break;
			default:
				violations.push(`${result.code}: ${id} ${result.message}`);
		}
	}
	return violations;
}
