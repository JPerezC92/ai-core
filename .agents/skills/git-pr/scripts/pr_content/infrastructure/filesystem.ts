/** Read supplied publication inputs and exclusively create publication artifacts. */

import { closeSync, openSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";

import { publicationError } from "#scripts/pr_content/domain/records.ts";
import type { Publication, PublicationError } from "#scripts/pr_content/domain/records.ts";
import type { ReservedArtifact } from "#scripts/pr_content/domain/ports.ts";
import { mapPublication } from "#scripts/pr_content/infrastructure/adapters/publication_record.ts";

/** Create a new artifact exclusively, leaving existing files untouched. */
export function createArtifact(path: string, content: string): void {
	writeFileSync(path, content, { encoding: "utf8", flag: "wx" });
}

/** Reserve an artifact path exclusively before its content is known. */
export function reserveArtifact(path: string): ReservedArtifact {
	const descriptor = openSync(path, "wx");
	let finished = false;
	return {
		commit(content: string): void {
			if (finished) return;
			finished = true;
			try {
				writeFileSync(descriptor, content, "utf8");
			} finally {
				closeSync(descriptor);
			}
		},
		release(): void {
			if (finished) return;
			finished = true;
			closeSync(descriptor);
			try {
				unlinkSync(path);
			} catch {
				// The reserved artifact is already gone; there is nothing left to release.
			}
		},
	};
}

/**
 * Read the supplied publication input and map it to typed records.
 *
 * An unreadable path is a boundary failure and throws; an invalid document is a business
 * refusal and is returned as a value.
 */
export function readPublicationInput(path: string): Publication | PublicationError {
	const bytes = readFileSync(path);
	let value: unknown;
	try {
		value = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
	} catch {
		return publicationError("INPUT_INVALID", "valid JSON publication required");
	}
	return mapPublication(value);
}
