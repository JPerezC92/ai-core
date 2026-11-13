import { describe, expect, it } from "vitest";
import { ValidateFeatures } from "../../scripts/feature_validation/application/validate_features.ts";
import {
  InvalidFeatureError,
  NoFeatureDocumentsError,
  ValidFeature,
} from "../../scripts/feature_validation/domain/records.ts";
import type { PathComparisonPolicy } from "../../scripts/feature_validation/domain/rules.ts";
import {
  FeatureSourceFake,
  featureCaseOrderFixture,
  featureDirectoryFixture,
  featureEmptyFixture,
  featureFailingFixture,
  featureSingleFixture,
  featureTemplateOnlyFixture,
} from "../support/feature-fixtures.ts";

const caseSensitivePolicy: PathComparisonPolicy = { caseSensitive: true };
const caseInsensitivePolicy: PathComparisonPolicy = { caseSensitive: false };

describe("ValidateFeatures.execute", () => {
  it("sorts candidates, skips the template, and returns typed results", () => {
    const fixture = featureDirectoryFixture();
    const source = new FeatureSourceFake(fixture.references, fixture.documents);

    const results = [...new ValidateFeatures(source, caseSensitivePolicy).execute("features")];

    expect(source.reads).toEqual(["features/a.md", "features/z.md"]);
    expect(results).toEqual([
      new ValidFeature("features/a.md"),
      new ValidFeature("features/z.md"),
    ]);
  });

  it("returns a typed no-documents result when selection is empty or template-only", () => {
    const emptyFixture = featureEmptyFixture();
    const empty = new FeatureSourceFake(emptyFixture.references, emptyFixture.documents);
    const templateFixture = featureTemplateOnlyFixture();
    const template = new FeatureSourceFake(templateFixture.references, templateFixture.documents);

    expect([...new ValidateFeatures(empty, caseSensitivePolicy).execute("features")]).toEqual([
      new NoFeatureDocumentsError(),
    ]);
    expect([...new ValidateFeatures(template, caseSensitivePolicy).execute("features")]).toEqual([
      new NoFeatureDocumentsError(),
    ]);
    expect(template.reads).toEqual([]);
  });

  it("returns invalid outcomes with the original ordered findings", () => {
    const fixture = featureSingleFixture("Feature name");
    const source = new FeatureSourceFake(fixture.references, fixture.documents);

    const [result] = [...new ValidateFeatures(source, caseSensitivePolicy).execute("features")];

    expect(result).toBeInstanceOf(InvalidFeatureError);
    expect(result).toMatchObject({
      path: "features/a.md",
      findings: ["title must not be the template placeholder"],
    });
  });

  it("yields earlier results before a later read exception", () => {
    const failure = new Error("later document cannot be read");
    const fixture = featureFailingFixture();
    const source = new FeatureSourceFake(fixture.references, fixture.documents, failure);
    const iterator = new ValidateFeatures(source, caseSensitivePolicy).execute("features");

    expect(iterator.next().value).toEqual(new ValidFeature("features/a.md"));
    expect(source.reads).toEqual(["features/a.md"]);
    expect(() => iterator.next()).toThrow(failure);
    expect(source.reads).toEqual(["features/a.md", "features/z.md"]);
  });

  it("orders references by the injected path case-sensitivity policy", () => {
    const fixture = featureCaseOrderFixture();

    const insensitive = new FeatureSourceFake(fixture.references, fixture.documents);
    const insensitiveResults = [
      ...new ValidateFeatures(insensitive, caseInsensitivePolicy).execute("features"),
    ];
    expect(insensitiveResults).toHaveLength(2);
    expect(insensitive.reads).toEqual(["features/a.md", "features/B.md"]);

    const sensitive = new FeatureSourceFake(fixture.references, fixture.documents);
    const sensitiveResults = [
      ...new ValidateFeatures(sensitive, caseSensitivePolicy).execute("features"),
    ];
    expect(sensitiveResults).toHaveLength(2);
    expect(sensitive.reads).toEqual(["features/B.md", "features/a.md"]);
  });
});
