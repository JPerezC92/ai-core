/** Shared test data for the durable feature-file validator: documents and a fake source port. */

import type { FeatureFileSource } from "../../scripts/feature_file_validation/domain/ports.ts";

/** A durable feature file that satisfies every anatomy rule. */
export function makeFeatureFile(status = "partial"): string {
  return [
    "# Sample feature",
    "",
    "The feature states what it is in one paragraph.",
    "",
    `**Status:** ${status}`,
    "",
    "## Requirements",
    "",
    "- [x] R1 — the requirement remains true.",
    "- [ ] R2 — another requirement remains true.",
    "",
  ].join("\n");
}

/**
 * A durable feature file whose declared status and requirement mark carry an
 * apostrophe, so both are reported wrapped in double quotes.
 */
export function makeApostropheFeatureFile(): string {
  return [
    "# Sample feature",
    "",
    "The feature states what it is in one paragraph.",
    "",
    "**Status:** achieved's",
    "",
    "## Requirements",
    "",
    "- [ ] R1 `owner's mark` — the requirement remains true.",
    "- [ ] R2 — another requirement remains true.",
    "",
  ].join("\n");
}

/** The candidate references of a fixture and the documents behind them. */
export type FeatureFileFixture = {
  readonly references: string[];
  readonly documents: Map<string, string>;
};

/** A directory holding a template and two files. */
export function featureFileDirectoryFixture(): FeatureFileFixture {
  return {
    references: ["features/z.md", "features/_template.md", "features/a.md"],
    documents: new Map([
      ["features/a.md", makeFeatureFile()],
      ["features/z.md", makeFeatureFile()],
    ]),
  };
}

/** A directory holding only the template. */
export function featureFileTemplateOnlyFixture(): FeatureFileFixture {
  return { references: ["features/_template.md"], documents: new Map() };
}

/** A single file with the given declared status. */
export function featureFileSingleFixture(status = "partial"): FeatureFileFixture {
  return {
    references: ["features/a.md"],
    documents: new Map([["features/a.md", makeFeatureFile(status)]]),
  };
}

/** Two files whose case-sensitive order differs from their case-insensitive order. */
export function featureFileCaseOrderFixture(): FeatureFileFixture {
  return {
    references: ["features/B.md", "features/a.md"],
    documents: new Map([
      ["features/B.md", makeFeatureFile()],
      ["features/a.md", makeFeatureFile()],
    ]),
  };
}

/** Two files where reading the later one fails. */
export function featureFileFailingFixture(): FeatureFileFixture {
  return {
    references: ["features/z.md", "features/a.md"],
    documents: new Map([["features/a.md", makeFeatureFile()]]),
  };
}

/** The reference whose read fails when a source carries a read failure. */
const FAILING_REFERENCE = "features/z.md";

/** An in-memory feature-file source that records the references it reads. */
export class FeatureFileSourceFake implements FeatureFileSource {
  readonly reads: string[] = [];
  private readonly references: string[];
  private readonly documents: Map<string, string>;
  private readonly readFailure: Error | undefined;

  constructor(
    references: string[],
    documents: Map<string, string>,
    readFailure?: Error,
  ) {
    this.references = references;
    this.documents = documents;
    this.readFailure = readFailure;
  }

  discover(_target: string): string[] {
    return [...this.references];
  }

  read(reference: string): string {
    this.reads.push(reference);
    if (reference === FAILING_REFERENCE && this.readFailure) throw this.readFailure;
    const document = this.documents.get(reference);
    if (document === undefined) throw new Error(`missing fixture: ${reference}`);
    return document;
  }
}
