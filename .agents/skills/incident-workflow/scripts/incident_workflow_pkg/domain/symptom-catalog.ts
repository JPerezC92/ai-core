/**
 * Symptom catalog reading.
 *
 * A catalog is a Markdown table whose first column holds symptom identifiers.
 * AICore's managed catalog and a destination's own catalog share this reader,
 * so both are validated by one rule set. The reader reports duplicate
 * definitions rather than picking a winner.
 */

import { isSymptomId } from "./symptom-id.ts";

/** The identifiers a catalog defines, and any identifier it defines twice. */
export interface SymptomCatalog {
	readonly ids: readonly string[];
	readonly duplicates: readonly string[];
}

/** Read the symptom identifiers defined by one catalog document. */
export function parseSymptomCatalog(content: string): SymptomCatalog {
	const seen = new Set<string>();
	const duplicates = new Set<string>();
	for (const line of content.split(/\r\n|\n|\r/)) {
		const trimmed = line.trim();
		if (!trimmed.startsWith("|")) continue;
		const cells = trimmed
			.replace(/^\|+|\|+$/g, "")
			.split("|")
			.map((cell) => cell.trim());
		const id = cells[0] ?? "";
		if (!isSymptomId(id)) continue;
		if (seen.has(id)) duplicates.add(id);
		else seen.add(id);
	}
	return { ids: [...seen], duplicates: [...duplicates] };
}

/** Combine catalogs, reporting identifiers defined in more than one place. */
export function combineSymptomCatalogs(catalogs: readonly SymptomCatalog[]): SymptomCatalog {
	const seen = new Set<string>();
	const duplicates = new Set<string>();
	for (const catalog of catalogs) {
		for (const id of catalog.duplicates) duplicates.add(id);
		for (const id of catalog.ids) {
			if (seen.has(id)) duplicates.add(id);
			else seen.add(id);
		}
	}
	return { ids: [...seen], duplicates: [...duplicates] };
}
