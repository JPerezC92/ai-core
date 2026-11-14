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

export interface IncidentFiles {
  readText(path: string): string;
  isFile(path: string): boolean;
  loadStepFiles(analysisDir: string): Record<string, string>;
  loadCloseOutSnapshot(ticketDir: string): CloseOutSnapshot;
}
