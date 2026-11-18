import { join } from "node:path";

import { ValidateAnalysis } from "#scripts/incident_workflow_pkg/application/validate_analysis.ts";
import { ValidateScaffold } from "#scripts/incident_workflow_pkg/application/validate_scaffold.ts";
import { ValidateStep } from "#scripts/incident_workflow_pkg/application/validate_step.ts";
import { ValidatePreClose } from "#scripts/incident_workflow_pkg/application/validate_pre_close.ts";
import { ValidateCloseOut } from "#scripts/incident_workflow_pkg/application/validate_close_out.ts";
import { ValidateDiagnosticKnowledge } from "#scripts/incident_workflow_pkg/application/validate_diagnostic_knowledge.ts";
import { REQUIRED_ANALYSIS_FILES, STEP_FILES, STEP_NAMES } from "#scripts/incident_workflow_pkg/domain/rules.ts";
import type { AnalysisHeader, ParsedRecord } from "#scripts/incident_workflow_pkg/domain/rules.ts";
import type { ValidatorArguments } from "#scripts/incident_workflow_pkg/infrastructure/arguments.ts";
import { Filesystem } from "#scripts/incident_workflow_pkg/infrastructure/filesystem.ts";
import { parseStateHeader, parseTicketRecord } from "#scripts/incident_workflow_pkg/infrastructure/records.ts";

/** An operating-system failure raised at the filesystem boundary. */
function isFilesystemError(error: unknown): error is Error & { code: unknown } {
	return error instanceof Error && "code" in error && "syscall" in error;
}

export function runValidator(args: ValidatorArguments, clock: () => Date = () => new Date()): number {
	const files = new Filesystem();
	const writeFindings = (findings: { violations: string[]; warnings: string[] }): boolean => {
		for (const warning of findings.warnings) console.error(`WARN: ${warning}`);
		for (const violation of findings.violations) console.error(violation);
		return findings.violations.length === 0;
	};
	const registerPath = join(args.repoRoot, "incidents", "diagnostics", "problems.md");
	const localSymptomPath = join(args.repoRoot, "incidents", "diagnostics", "symptoms.md");
	const baselineSymptomPath = join(args.repoRoot, ".aicore", "core", "knowledge", "diagnostics", "symptoms.md");
	const knowledge = new ValidateDiagnosticKnowledge();
	/** The diagnostic-knowledge check's input, read at the moment the check runs. */
	const knowledgeInput = () => ({
		baselineSymptoms: files.isFile(baselineSymptomPath) ? files.readText(baselineSymptomPath) : null,
		localSymptoms: files.isFile(localSymptomPath) ? files.readText(localSymptomPath) : null,
		localProblemRows: files.loadProblemRows(registerPath),
		localSymptomsPath: localSymptomPath,
		localProblemsPath: registerPath,
	});

	if (args.mode.kind === "pre-close" || args.mode.kind === "close-out") {
		let snapshot;
		let preCloseRegister;
		try {
			snapshot = files.loadCloseOutSnapshot(args.analysisDir);
			if (args.mode.kind === "pre-close") preCloseRegister = files.loadProblemRegister(registerPath);
		} catch (error) {
			if (args.mode.kind !== "pre-close" || !isFilesystemError(error)) throw error;
			console.error(`PRE-CLOSE-IO: ${error.message}`);
			return 1;
		}
		const ticket =
			snapshot.ticketContent !== null && snapshot.ticketFileNames.length === 1
				? parseTicketRecord(snapshot.ticketContent!, snapshot.ticketFileNames[0]!)
				: null;
		const stateContent = snapshot.analysisContents["state.md"];
		const header = stateContent === undefined ? null : parseStateHeader(stateContent, "state.md");

		if (args.mode.kind === "pre-close") {
			const findings = new ValidatePreClose().execute(snapshot, ticket, header, preCloseRegister!);
			const known = knowledge.execute(knowledgeInput());
			if (
				!writeFindings({
					violations: [...known.violations, ...findings.violations],
					warnings: findings.warnings,
				})
			)
				return 1;
			console.log(`ok  ${args.mode.kind}: ${args.analysisDir}  (${snapshot.ticketFileNames[0]})`);
			return 0;
		}

		// The register is consulted only for a parsed durable ticket record: an
		// unparsed record carries no identification to check against it.
		const register = ticket !== null && "value" in ticket ? files.loadProblemRegister(registerPath) : [];
		const outcome = new ValidateCloseOut().execute(snapshot, ticket, register);
		if (outcome.kind === "skipped") {
			console.error(`CLOSE-SKIPPED: ${outcome.reason} at ${args.analysisDir}`);
			return 2;
		}
		const known = knowledge.execute(knowledgeInput());
		if (
			!writeFindings({
				violations: [...known.violations, ...outcome.violations],
				warnings: outcome.warnings,
			})
		)
			return 1;
		console.log(`ok  ${args.mode.kind}: ${args.analysisDir}  (${snapshot.ticketFileNames[0]})`);
		return 0;
	}

	const statePath = join(args.analysisDir, "state.md");
	let header: ParsedRecord<AnalysisHeader>;
	try {
		header = parseStateHeader(files.readText(statePath), statePath);
	} catch (error) {
		if (!isFilesystemError(error)) throw error;
		console.error(`HEADER-ERROR: ${error.message}`);
		return 1;
	}
	if ("error" in header) {
		console.error(`HEADER-ERROR: ${header.error}`);
		return 1;
	}
	const contents = files.loadStepFiles(args.analysisDir);
	if (args.mode.kind === "scaffold") {
		if (!writeFindings(new ValidateScaffold(clock).execute(header.value, contents, args.analysisDir))) return 1;
		console.log(`ok  scaffold: ${args.analysisDir}`);
		return 0;
	}
	if (args.mode.kind === "step") {
		if (!writeFindings(new ValidateStep(clock).execute(header.value, contents, args.mode.step, args.analysisDir)))
			return 1;
		const filename = STEP_FILES[STEP_NAMES.indexOf(args.mode.step)];
		console.log(`ok  step ${args.mode.step} (${filename})  [analysis: ${args.analysisDir}]`);
		return 0;
	}
	if (!writeFindings(new ValidateAnalysis(clock).execute(header.value, contents, args.analysisDir))) return 1;
	console.log(`\nAnalysis: ${args.analysisDir}  Phase: ${header.value.Phase}\n`);
	console.log(`${"Analysis file".padEnd(35)} Status`);
	console.log("-".repeat(45));
	for (const name of REQUIRED_ANALYSIS_FILES) {
		console.log(
			`  ${name.padEnd(33)} ${files.isFile(join(args.analysisDir, name)) ? "ok" : "absent (not yet written)"}`,
		);
	}
	console.log();
	return 0;
}
