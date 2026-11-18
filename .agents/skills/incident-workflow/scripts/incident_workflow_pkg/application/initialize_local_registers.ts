/**
 * Authorized initialization of a project's diagnostic registers.
 *
 * This is the only operation that creates `incidents/diagnostics/symptoms.md`
 * and `incidents/diagnostics/problems.md`. It creates a missing register from
 * its shipped template and never rewrites one that exists: an existing register
 * is validated instead, and a malformed or incompatible one is reported as a
 * defect rather than repaired. Ordinary reads never call this operation, and
 * synchronization never writes these paths at all.
 */

import { ValidateDiagnosticKnowledge } from "./validate_diagnostic_knowledge.ts";
import type { ProblemRow } from "#scripts/incident_workflow_pkg/domain/ports.ts";

/** The filesystem facts this operation needs, so it stays testable. */
export interface RegisterInitializationPorts {
	readonly isFile: (path: string) => boolean;
	readonly readText: (path: string) => string;
	readonly writeText: (path: string, content: string) => void;
	readonly ensureDirectory: (path: string) => void;
	readonly loadProblemRows: (path: string) => readonly ProblemRow[] | null;
}

/** Where the registers live and which template seeds each one. */
export interface RegisterInitializationRequest {
	readonly localSymptomsPath: string;
	readonly localProblemsPath: string;
	readonly localSymptomsTemplate: string;
	readonly localProblemsTemplate: string;
	readonly baselineSymptomsPath: string;
}

/** What initialization did, per register. */
export interface RegisterInitializationResult {
	readonly created: readonly string[];
	readonly kept: readonly string[];
	readonly violations: readonly string[];
}

export class InitializeLocalRegisters {
	private readonly ports: RegisterInitializationPorts;
	private readonly knowledge: ValidateDiagnosticKnowledge;

	constructor(ports: RegisterInitializationPorts, knowledge: ValidateDiagnosticKnowledge) {
		this.ports = ports;
		this.knowledge = knowledge;
	}

	execute(request: RegisterInitializationRequest): RegisterInitializationResult {
		const created: string[] = [];
		const kept: string[] = [];

		for (const [path, template] of [
			[request.localSymptomsPath, request.localSymptomsTemplate],
			[request.localProblemsPath, request.localProblemsTemplate],
		] as const) {
			if (this.ports.isFile(path)) {
				kept.push(path);
				continue;
			}
			this.ports.ensureDirectory(path.slice(0, path.lastIndexOf("/")));
			this.ports.writeText(path, this.ports.readText(template));
			created.push(path);
		}

		// An existing register is validated after the create-only pass, so a
		// malformed file is reported rather than overwritten by a template.
		const knowledge = this.knowledge.execute({
			baselineSymptoms: this.ports.isFile(request.baselineSymptomsPath)
				? this.ports.readText(request.baselineSymptomsPath)
				: null,
			localSymptoms: this.ports.isFile(request.localSymptomsPath)
				? this.ports.readText(request.localSymptomsPath)
				: null,
			localProblemRows: this.ports.loadProblemRows(request.localProblemsPath),
			localSymptomsPath: request.localSymptomsPath,
			localProblemsPath: request.localProblemsPath,
		});

		return { created, kept, violations: knowledge.violations };
	}
}
