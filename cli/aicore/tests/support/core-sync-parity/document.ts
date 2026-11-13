/**
 * The two synchronization documents, projected from their YAML text.
 *
 * The bindings file and the reconciliation report are compared as documents,
 * not as bytes: the contract fixes their schema and their content, but not the
 * YAML dialect a writer uses. Projecting them here keeps that choice in one
 * place instead of spreading it across the corpus.
 */

import { readYaml, type YamlMapping, type YamlValue } from "./mini-yaml.ts";

/** One `source` → `destinations` mapping of the bindings document. */
export type BindingMapping = {
  readonly source: string;
  readonly destinations: readonly string[];
};

/** The bindings document, as the contract's schema describes it. */
export type BindingsDocument = {
  readonly schema: number | null;
  readonly coreRevision: string | null;
  readonly root: string | null;
  readonly bindings: readonly BindingMapping[];
  readonly pending: readonly string[];
};

/** One entry of the reconciliation report. */
export type ReportEntry = {
  readonly destination: string;
  readonly source: string;
  readonly action: string;
};

/** The reconciliation report, as the contract describes it. */
export type ReportDocument = {
  readonly schema: number | null;
  readonly coreRevision: string | null;
  readonly entries: readonly ReportEntry[];
};

/** Project a bindings file's text into its documented shape. */
export function readBindingsDocument(text: string): BindingsDocument {
  const root = asMapping(readYaml(text));
  const entries: BindingMapping[] = [];
  const rawBindings = root?.["bindings"];
  if (Array.isArray(rawBindings)) {
    for (const item of rawBindings) {
      const mapping = asMapping(item);
      if (mapping === null) {
        continue;
      }
      const destinations = mapping["destinations"];
      entries.push({
        source: asText(mapping["source"]) ?? "",
        destinations: Array.isArray(destinations)
          ? destinations.map((entry) => asText(entry) ?? "")
          : [],
      });
    }
  }
  const rawPending = root?.["pending"];
  return {
    schema: asNumber(root?.["schema"]),
    coreRevision: asText(root?.["core_revision"]),
    root: asText(root?.["root"]),
    bindings: entries,
    pending: Array.isArray(rawPending)
      ? rawPending.map((entry) => asText(entry) ?? "")
      : [],
  };
}

/** Project a reconciliation report's text into its documented shape. */
export function readReportDocument(text: string): ReportDocument {
  const root = asMapping(readYaml(text));
  const entries: ReportEntry[] = [];
  const rawEntries = root?.["entries"];
  if (Array.isArray(rawEntries)) {
    for (const item of rawEntries) {
      const mapping = asMapping(item);
      if (mapping === null) {
        continue;
      }
      entries.push({
        destination: asText(mapping["destination"]) ?? "",
        source: asText(mapping["source"]) ?? "",
        action: asText(mapping["action"]) ?? "",
      });
    }
  }
  return {
    schema: asNumber(root?.["schema"]),
    coreRevision: asText(root?.["core_revision"]),
    entries,
  };
}

function asMapping(value: YamlValue | undefined): YamlMapping | null {
  if (value === null || value === undefined || Array.isArray(value) || typeof value !== "object") {
    return null;
  }
  return value;
}

function asText(value: YamlValue | undefined): string | null {
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return null;
}

function asNumber(value: YamlValue | undefined): number | null {
  return typeof value === "number" ? value : null;
}
