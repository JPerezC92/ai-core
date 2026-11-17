/**
 * Symptom identifier grammar.
 *
 * Two namespaces share one `S-` shape: AICore's shared baseline (`S-01`) and a
 * destination's own classes (`LOCAL:S-01`). A reference is valid only as a
 * complete token, so `LOCAL:S-01` never matches as a bare baseline id and a
 * substring such as `XS-01` never passes. Digit width is open-ended so neither
 * namespace has a forced capacity.
 */

/** AICore-managed baseline class identifier. */
export const BASELINE_SYMPTOM_ID = /^S-\d{2,}$/;

/** Destination-owned class identifier, scoped to the destination's own register. */
export const LOCAL_SYMPTOM_ID = /^LOCAL:S-\d{2,}$/;

/** Either namespace, as one complete token. */
export const SYMPTOM_ID = /^(?:LOCAL:)?S-\d{2,}$/;

/** Return whether `token` is one complete symptom identifier. */
export function isSymptomId(token: string): boolean {
	return SYMPTOM_ID.test(token);
}

/** Return whether `token` names a destination-owned class. */
export function isLocalSymptomId(token: string): boolean {
	return LOCAL_SYMPTOM_ID.test(token);
}

/** A parsed symptom-reference cell. */
export interface SymptomReferences {
	readonly tokens: readonly string[];
	readonly invalid: readonly string[];
}

/**
 * Split a register `Symptom` cell into complete tokens.
 *
 * The cell is a comma-separated list, primary class first. Empty segments are
 * ignored; every remaining segment must be a whole identifier.
 */
export function parseSymptomReferences(cell: string): SymptomReferences {
	const tokens: string[] = [];
	const invalid: string[] = [];
	for (const segment of cell.split(",")) {
		const token = segment.trim();
		if (token === "") continue;
		if (isSymptomId(token)) tokens.push(token);
		else invalid.push(token);
	}
	return { tokens, invalid };
}
