/**
 * Infrastructure: the persisted bindings document and its reconciliation report.
 *
 * The adapter reads the file, hands the YAML text to the document reader, and
 * asks the domain's schema rule whether it is a valid document. Nothing here
 * decides what a valid document is.
 */

import { dirname, join } from "node:path";

import { bindingsRecord, parseBindingsDocument } from "#domain/synchronization/bindings.ts";
import {
  RECONCILIATION_DIRECTORY,
  RECONCILIATION_FILENAME,
} from "#domain/synchronization/constants.ts";
import type { BindingsDocument } from "#domain/synchronization/bindings.ts";
import type { ReconciliationEntry } from "#domain/synchronization/reconciliation.ts";
import type { BindingsStore } from "#domain/synchronization/ports.ts";

import { readTextFile, writeTextFile } from "./local-files.ts";
import {
  readDocumentText,
  writeBindingsDocument,
  writeReconciliationReport,
} from "./yaml-document.ts";

export class YamlBindingsStore implements BindingsStore {
  async load(path: string): Promise<BindingsDocument | null> {
    const text = await readTextFile(path);
    if (text === null) {
      return null;
    }
    return parseBindingsDocument(readDocumentText(text));
  }

  async save(path: string, document: BindingsDocument): Promise<void> {
    await writeTextFile(path, writeBindingsDocument(bindingsRecord(document)));
  }

  async writeReport(
    bindingsPath: string,
    entries: readonly ReconciliationEntry[],
    revision: string,
  ): Promise<void> {
    const reportPath = join(dirname(bindingsPath), RECONCILIATION_DIRECTORY, RECONCILIATION_FILENAME);
    await writeTextFile(reportPath, writeReconciliationReport(entries, revision));
  }
}
