import { describe, expect, it } from "vitest";
import { ValidateFeatureFiles } from "#scripts/feature_file_validation/application/validate_feature_files.ts";
import {
  InvalidFeatureFileError,
  NoFeatureFileDocumentsError,
  ValidFeatureFile,
} from "#scripts/feature_file_validation/domain/records.ts";
import type { PathComparisonPolicy } from "#scripts/feature_file_validation/domain/rules.ts";
import {
  FeatureFileSourceFake,
  featureFileCaseOrderFixture,
  featureFileDirectoryFixture,
  featureFileFailingFixture,
  featureFileSingleFixture,
  featureFileTemplateOnlyFixture,
} from "#tests/support/feature-file-fixtures.ts";

const caseSensitivePolicy: PathComparisonPolicy = { caseSensitive: true };
const caseInsensitivePolicy: PathComparisonPolicy = { caseSensitive: false };

describe("ValidateFeatureFiles.execute", () => {
  it("sorts candidates, skips the template, and returns the derived status", () => {
    const fixture = featureFileDirectoryFixture();
    const source = new FeatureFileSourceFake(fixture.references, fixture.documents);

    const results = [...new ValidateFeatureFiles(source, caseSensitivePolicy).execute("features")];

    expect(source.reads).toEqual(["features/a.md", "features/z.md"]);
    expect(results).toEqual([
      new ValidFeatureFile("features/a.md", "partial"),
      new ValidFeatureFile("features/z.md", "partial"),
    ]);
  });

  it("returns typed no-files and invalid outcomes", () => {
    const emptyFixture = featureFileTemplateOnlyFixture();
    const empty = new FeatureFileSourceFake(emptyFixture.references, emptyFixture.documents);
    const invalidFixture = featureFileSingleFixture("achieved");
    const invalid = new FeatureFileSourceFake(invalidFixture.references, invalidFixture.documents);

    expect([...new ValidateFeatureFiles(empty, caseSensitivePolicy).execute("features")]).toEqual([
      new NoFeatureFileDocumentsError(),
    ]);
    const [rejected] = [...new ValidateFeatureFiles(invalid, caseSensitivePolicy).execute("features")];
    expect(rejected).toBeInstanceOf(InvalidFeatureFileError);
    expect(rejected).toMatchObject({
      path: "features/a.md",
      findings: [
        "feature-file-status-derivation: declared status 'achieved' does not match the status derived from the ticks 'partial'",
      ],
    });
  });

  it("yields earlier results before a later read exception", () => {
    const failure = new Error("later feature file cannot be read");
    const fixture = featureFileFailingFixture();
    const source = new FeatureFileSourceFake(fixture.references, fixture.documents, failure);
    const iterator = new ValidateFeatureFiles(source, caseSensitivePolicy).execute("features");

    expect(iterator.next().value).toEqual(new ValidFeatureFile("features/a.md", "partial"));
    expect(() => iterator.next()).toThrow(failure);
  });

  it("orders references by the injected path case-sensitivity policy", () => {
    const fixture = featureFileCaseOrderFixture();

    const insensitive = new FeatureFileSourceFake(fixture.references, fixture.documents);
    const insensitiveResults = [
      ...new ValidateFeatureFiles(insensitive, caseInsensitivePolicy).execute("features"),
    ];
    expect(insensitiveResults).toHaveLength(2);
    expect(insensitive.reads).toEqual(["features/a.md", "features/B.md"]);

    const sensitive = new FeatureFileSourceFake(fixture.references, fixture.documents);
    const sensitiveResults = [
      ...new ValidateFeatureFiles(sensitive, caseSensitivePolicy).execute("features"),
    ];
    expect(sensitiveResults).toHaveLength(2);
    expect(sensitive.reads).toEqual(["features/B.md", "features/a.md"]);
  });
});
