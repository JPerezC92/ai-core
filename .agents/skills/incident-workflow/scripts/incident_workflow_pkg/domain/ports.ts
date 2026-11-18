import type { Problem } from "./problem.ts";

export interface CloseOutSnapshot {
	readonly ticketFileNames: string[];
	readonly ticketContent: string | null;
	readonly citedPaths: string[];
	readonly workingAnalysisFiles: string[];
	readonly analysisContents: Record<string, string>;
	readonly responseDraftPresent: boolean;
	readonly screenshotsDirPresent: boolean;
	readonly validationsDirPresent: boolean;
	readonly missingImagePaths: string[];
	readonly missingTicketPaths: string[];
	readonly unsafeTicketPaths: string[];
	readonly leftoverDownloadFiles: string[];
}

/**
 * A problem-register row as the register declares it, before any field is
 * validated: a row that breaks an invariant is still a row the register
 * declares, so the diagnostic-knowledge check reports it instead of losing it.
 */
export interface ProblemRow {
	readonly id: string;
	readonly symptom: string;
}

export interface IncidentFiles {
	readText(path: string): string;
	isFile(path: string): boolean;
	loadStepFiles(analysisDir: string): Record<string, string>;
	loadCloseOutSnapshot(ticketDir: string): CloseOutSnapshot;
	/** The incident rows the register declares; an absent register declares none. */
	loadProblemRegister(path: string): Problem[];
	/** The declared rows of the register, or `null` when the register is absent. */
	loadProblemRows(path: string): ProblemRow[] | null;
}
