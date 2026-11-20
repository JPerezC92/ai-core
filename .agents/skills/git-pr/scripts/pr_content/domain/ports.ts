/** Domain-owned capability contracts for supplied input and exclusive artifact creation. */

import type { PreparationReceipt, Publication, PublicationError } from "#scripts/pr_content/domain/records.ts";

/**
 * Read the publication input supplied at a caller-named path.
 *
 * The implementation decodes and maps the supplied bytes; a missing or unreadable path is a
 * boundary failure, so it is thrown, while an invalid document is returned as a business refusal.
 */
export type PublicationReader = (path: string) => Publication | PublicationError;

/**
 * Create a new artifact at the caller-named path without overwriting an existing artifact.
 *
 * The capability owns exclusive creation only; deciding whether an artifact may be created is the
 * application's rule. An existing artifact or an unusable parent directory is a boundary failure,
 * so it is thrown rather than returned as a business rejection.
 */
export type ExclusiveArtifactWriter = (path: string, content: string) => void;

/**
 * Reserve an artifact path exclusively before its content is known.
 *
 * The reservation is committed with its final content or released, so an artifact is never
 * published without the artifact that describes it.
 */
export type ArtifactReserver = (path: string) => ReservedArtifact;

/** One reserved artifact path awaiting its final content. */
export interface ReservedArtifact {
	/** Write the reserved artifact's content and finish it. */
	commit(content: string): void;
	/** Finish the reservation without leaving an artifact behind. */
	release(): void;
}

/** Render one validated publication record as the canonical body. */
export type PublicationRenderer = (publication: Publication) => string;

/**
 * Encode one prepared receipt as the content of its receipt artifact.
 *
 * The application owns the receipt's typed fields; the encoding of that record for the artifact
 * belongs to the boundary that owns the artifact representation.
 */
export type PreparationReceiptEncoder = (receipt: PreparationReceipt) => string;
