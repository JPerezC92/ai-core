/** Shared test data for the retirement check: task records and a fake source port. */

import type { RetirementSource } from "#scripts/retirement_check/domain/ports.ts";

/** The completed-but-active finding this suite's sibling rule reports. */
export const COMPLETED_BUT_ACTIVE_FINDING =
  "active record has every task done: close the record or record the open closure prerequisite as a Log entry";

export type TaskRecordOptions = {
  readonly status?: "active" | "closed";
  readonly closedOn?: string | null;
  readonly taskStatus?: "open" | "in progress" | "done";
  readonly closeEntry?: boolean;
};

/** A task record assembled from the fields the retention rules read. */
export function makeTaskRecord(options: TaskRecordOptions = {}): string {
  const status = options.status ?? "closed";
  const closedOn = options.closedOn === undefined ? "2026-11-01" : options.closedOn;
  const taskStatus = options.taskStatus ?? "done";
  const closeEntry = options.closeEntry ?? true;

  const lines = [
    "# Sample record",
    "",
    `> **Status:** ${status}`,
    "> **Owner:** Cipher (Lead Orchestrator)",
    "> **Created:** 2026-10-23",
  ];
  if (closedOn !== null) lines.push(`> **Closed:** ${closedOn}`);
  lines.push(
    "",
    "## Specs",
    "",
    "- S1 — A requirement.",
    "",
    "## Tasks",
    "",
    `- T1 | S1 | route | ${taskStatus} | commit: abc1234`,
    "",
    "## Log",
    "",
    "- L1 — original request",
  );
  if (closeEntry) lines.push("- L2 — Close: delivered");
  lines.push("");
  return lines.join("\n");
}

/** A record directory and the documents behind it. */
export type TaskRecordFixture = {
  readonly references: string[];
  readonly documents: Map<string, string>;
};

/** An in-memory retirement source that records the references it reads. */
export class RetirementSourceFake implements RetirementSource {
  readonly reads: string[] = [];
  private readonly references: string[];
  private readonly documents: Map<string, string>;

  constructor(references: string[], documents: Map<string, string>) {
    this.references = references;
    this.documents = documents;
  }

  discover(_target: string): string[] {
    return [...this.references];
  }

  read(reference: string): string {
    this.reads.push(reference);
    const document = this.documents.get(reference);
    if (document === undefined) throw new Error(`missing fixture: ${reference}`);
    return document;
  }
}
