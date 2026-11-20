/** Render the canonical pull-request body from one validated publication record. */

import {
	escapeMarkdownText,
	expectedSectionNames,
	sectionContent,
	sectionHeading,
} from "#scripts/pr_content/domain/body_format.ts";
import type { Publication } from "#scripts/pr_content/domain/records.ts";

/**
 * Render the complete body of one pull request.
 *
 * The rendering is a pure function of the validated record, so the same input always produces
 * the same bytes, and the canonical body format owns every section the body carries.
 */
export function renderPublication(publication: Publication): string {
	const sections = expectedSectionNames(publication).map(
		(name) => `${sectionHeading(name)}\n\n${sectionContent(publication, name).join("\n")}`,
	);
	const body = `${sections.join("\n\n")}\n`;
	const verdict = publication.review?.verdict;
	if (verdict === undefined) return body;
	return `${body}\n[${verdict.kind}] — ${escapeMarkdownText(verdict.basis)}\n`;
}
