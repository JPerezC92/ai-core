/**
 * Diagnostic-knowledge integrity.
 *
 * Two registers hold destination-owned learning: `incidents/diagnostics/symptoms.md`
 * for destination classes and `incidents/diagnostics/problems.md` for problem
 * patterns. AICore's managed catalogs stay separate and are read as the shared
 * baseline. This operation reports every defect it finds and never repairs one.
 *
 * A missing register is not an empty register: emptiness is a valid state a
 * destination reaches through authorized initialization, so absence is reported
 * rather than being read as "nothing known".
 */

import { combineSymptomCatalogs, parseSymptomCatalog } from "#scripts/incident_workflow_pkg/domain/symptom-catalog.ts";
import { BASELINE_SYMPTOM_ID, parseSymptomReferences } from "#scripts/incident_workflow_pkg/domain/symptom-id.ts";
import type { ProblemRow } from "#scripts/incident_workflow_pkg/domain/ports.ts";

/** The documents a diagnostic-knowledge check reads; `null` means absent. */
export interface DiagnosticKnowledgeInput {
	readonly baselineSymptoms: string | null;
	readonly localSymptoms: string | null;
	readonly localProblemRows: readonly ProblemRow[] | null;
	readonly localSymptomsPath: string;
	readonly localProblemsPath: string;
}

/** The findings of one diagnostic-knowledge check. */
export interface DiagnosticKnowledgeFindings {
	readonly violations: readonly string[];
}

export class ValidateDiagnosticKnowledge {
	execute(input: DiagnosticKnowledgeInput): DiagnosticKnowledgeFindings {
		const violations: string[] = [];
		if (input.localSymptoms === null) {
			violations.push(`KNOWLEDGE-1: local symptom register missing: ${input.localSymptomsPath}`);
		}
		if (input.localProblemRows === null) {
			violations.push(`KNOWLEDGE-2: local problem register missing: ${input.localProblemsPath}`);
		}
		if (violations.length > 0) return { violations };

		const baseline = input.baselineSymptoms === null ? null : parseSymptomCatalog(input.baselineSymptoms);
		const local = parseSymptomCatalog(input.localSymptoms ?? "");
		const combined = combineSymptomCatalogs(baseline === null ? [local] : [baseline, local]);

		if (local.duplicates.length > 0) {
			violations.push(`KNOWLEDGE-3: local symptom register defines an id twice: ${local.duplicates.join(", ")}`);
		}
		if (baseline !== null) {
			const repeated = combined.duplicates.filter((id) => !local.duplicates.includes(id));
			if (repeated.length > 0) {
				violations.push(`KNOWLEDGE-4: id defined in both baseline and local registers: ${repeated.join(", ")}`);
			}
		}

		const known = new Set(combined.ids.length === 0 ? [] : combined.ids);
		for (const id of local.ids) {
			if (BASELINE_SYMPTOM_ID.test(id)) {
				violations.push(`KNOWLEDGE-7: local register defines a non-LOCAL symptom id: ${id}`);
			}
		}
		for (const row of input.localProblemRows ?? []) {
			const references = parseSymptomReferences(row.symptom);
			if (references.invalid.length > 0) {
				violations.push(
					`KNOWLEDGE-5: ${row.id} Symptom cell has an invalid token: ${references.invalid.join(", ")}`,
				);
			}
			for (const reference of references.tokens) {
				if (!known.has(reference)) {
					violations.push(`KNOWLEDGE-6: ${row.id} references an unknown symptom: ${reference}`);
				}
			}
		}
		return { violations };
	}
}
