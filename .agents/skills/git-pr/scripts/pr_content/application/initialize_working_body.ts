/** Decide whether a creation draft becomes the working body and create it exclusively. */

import { extractBody, validateCreationBody } from "#scripts/pr_content/domain/body_validation.ts";
import type { ExclusiveArtifactWriter, SuppliedTextReader } from "#scripts/pr_content/domain/ports.ts";
import type { PreparedBody, ReviewPreparationError } from "#scripts/pr_content/domain/records.ts";

/** The supplied draft and the artifact the operation may create. */
export interface InitializeWorkingBodyInput {
	readonly draftPath: string;
	readonly workingBodyPath: string;
}

/** Extract the creation body from the supplied draft, then create the working body. */
export class InitializeWorkingBody {
	readonly #readSuppliedText: SuppliedTextReader;
	readonly #createArtifact: ExclusiveArtifactWriter;

	constructor(readSuppliedText: SuppliedTextReader, createArtifact: ExclusiveArtifactWriter) {
		this.#readSuppliedText = readSuppliedText;
		this.#createArtifact = createArtifact;
	}

	/** Return the extracted body, or the refusal reached before anything is created. */
	execute(input: InitializeWorkingBodyInput): PreparedBody | ReviewPreparationError {
		const extracted = extractBody(this.#readSuppliedText(input.draftPath));
		if (typeof extracted !== "string") return extracted;
		const invalid = validateCreationBody(extracted);
		if (invalid !== undefined) return invalid;
		this.#createArtifact(input.workingBodyPath, extracted);
		return { body: extracted };
	}
}
