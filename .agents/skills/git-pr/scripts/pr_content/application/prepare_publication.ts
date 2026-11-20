/** Prepare one publication body and its receipt from a supplied JSON publication input. */

import { validateGeneratedBody } from "#scripts/pr_content/domain/body_format.ts";
import { isPublicationError } from "#scripts/pr_content/domain/records.ts";
import type { PreparationReceipt, PublicationError } from "#scripts/pr_content/domain/records.ts";
import type {
	ArtifactReserver,
	ExclusiveArtifactWriter,
	PreparationReceiptEncoder,
	PublicationReader,
	PublicationRenderer,
} from "#scripts/pr_content/domain/ports.ts";
import { validatePublication } from "#scripts/pr_content/domain/validation.ts";

/**
 * Prepare the publication artifacts of one pull request.
 *
 * The operation reads the supplied input, validates it, renders the canonical body, checks that
 * body against the canonical body format and creates the body and its receipt exclusively. It
 * never compares the generated body with an earlier body, a capture or a published state.
 */
export class PreparePublication {
	readonly #read: PublicationReader;
	readonly #write: ExclusiveArtifactWriter;
	readonly #reserve: ArtifactReserver;
	readonly #render: PublicationRenderer;
	readonly #encode: PreparationReceiptEncoder;

	constructor(
		read: PublicationReader,
		write: ExclusiveArtifactWriter,
		reserve: ArtifactReserver,
		render: PublicationRenderer,
		encode: PreparationReceiptEncoder,
	) {
		this.#read = read;
		this.#write = write;
		this.#reserve = reserve;
		this.#render = render;
		this.#encode = encode;
	}

	execute(input: {
		readonly inputPath: string;
		readonly bodyPath: string;
		readonly receiptPath: string;
	}): PreparationReceipt | PublicationError {
		const supplied = this.#read(input.inputPath);
		if (isPublicationError(supplied)) return supplied;
		const publication = validatePublication(supplied);
		if (isPublicationError(publication)) return publication;

		const body = this.#render(publication);
		const malformed = validateGeneratedBody(body, publication);
		if (malformed !== undefined) return malformed;

		const reservation = this.#reserve(input.receiptPath);
		try {
			this.#write(input.bodyPath, body);
		} catch (error) {
			reservation.release();
			throw error;
		}
		const receipt: PreparationReceipt = { status: "prepared", title: publication.title };
		reservation.commit(this.#encode(receipt));
		return receipt;
	}
}
