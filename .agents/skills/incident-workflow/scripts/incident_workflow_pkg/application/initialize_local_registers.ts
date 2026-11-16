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
import type { DiagnosticKnowledgeFindings } from "./validate_diagnostic_knowledge.ts";

/** Read-only validation of one destination's diagnostic knowledge. */
export function validateDiagnosticKnowledge(input: {
	readonly baselineSymptoms: string | null;
	readonly localSymptoms: string | null;
	readonly localProblems: string | null;
	readonly localSymptomsPath: string;
	readonly localProblemsPath: string;
}): DiagnosticKnowledgeFindings {
	return new ValidateDiagnosticKnowledge().execute(input);
}

/** The filesystem facts this operation needs, so it stays testable. */
export interface RegisterInitializationPorts {
	readonly isFile: (path: string) => boolean;
	readonly readText: (path: string) => string;
	readonly writeText: (path: string, content: string) => void;
	readonly ensureDirectory: (path: string) => void;
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

	constructor(ports: RegisterInitializationPorts) {
		this.ports = ports;
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
		const knowledge = validateDiagnosticKnowledge({
			baselineSymptoms: this.ports.isFile(request.baselineSymptomsPath)
				? this.ports.readText(request.baselineSymptomsPath)
				: null,
			localSymptoms: this.ports.isFile(request.localSymptomsPath)
				? this.ports.readText(request.localSymptomsPath)
				: null,
			localProblems: this.ports.isFile(request.localProblemsPath)
				? this.ports.readText(request.localProblemsPath)
				: null,
			localSymptomsPath: request.localSymptomsPath,
			localProblemsPath: request.localProblemsPath,
		});

		return { created, kept, violations: knowledge.violations };
	}
}
