/** Decode supplied local preparation documents into typed domain records. */

import { z } from "zod";

import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import type { LocalInventory } from "#scripts/pr_review/domain/records.ts";

/** The message every rejected local inventory document is reported with. */
const INVENTORY_REQUIRED = "local immutable inventory required";

/**
 * The local inventory document's shape.
 *
 * The decoded document is the only outside representation of the inventory, so this adapter owns
 * its exact field set and element shapes; the typed record's own content rules stay in the
 * domain. Nested entries accept their documented fields only, so an extra nested value is
 * dropped rather than becoming part of the typed record.
 */
const commitMessageSchema = z.object({
	surface: z.literal("commit-message"),
	source: z.string(),
	content: z.string(),
});

const changedFileSchema = z.object({
	path: z.string(),
	content: z.string(),
});

const localInventoryDocumentSchema = z.strictObject({
	schema: z.number(),
	pr_number: z.number(),
	head_sha: z.string(),
	base: z.string(),
	commit_messages: z.array(commitMessageSchema),
	changed_files: z.array(changedFileSchema),
});

/** The exact diff path inventory's shape. */
const exactPathsSchema = z.array(z.string());

type LocalInventoryDocument = z.infer<typeof localInventoryDocumentSchema>;

/** Map a decoded inventory document into the typed immutable inventory. */
function toInventory(document: LocalInventoryDocument): LocalInventory {
	return {
		schema: document.schema,
		pr_number: document.pr_number,
		head_sha: document.head_sha,
		base: document.base,
		commit_messages: document.commit_messages.map((message) => ({
			surface: message.surface,
			source: message.source,
			content: message.content,
		})),
		changed_files: document.changed_files.map((file) => ({ path: file.path, content: file.content })),
	};
}

/** Decode one supplied local inventory document into typed data or a business rejection. */
export function decodeLocalInventory(value: unknown): LocalInventory | ReviewPreparationError {
	const parsed = localInventoryDocumentSchema.safeParse(value);
	if (!parsed.success) return new ReviewPreparationError("SNAPSHOT_INVALID", INVENTORY_REQUIRED);
	return toInventory(parsed.data);
}

/** Decode one supplied path inventory into the exact diff path list. */
export function decodeExactPaths(value: unknown): readonly string[] | ReviewPreparationError {
	const parsed = exactPathsSchema.safeParse(value);
	if (!parsed.success) {
		return new ReviewPreparationError("SNAPSHOT_PATHS_MISMATCH", "path inventory must be a string list");
	}
	return parsed.data;
}
