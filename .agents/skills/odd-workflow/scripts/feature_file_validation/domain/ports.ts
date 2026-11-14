/** Domain-owned filesystem capability for durable feature-file validation. */

export interface FeatureFileSource {
  discover(target: string): readonly string[];
  read(reference: string): string;
}
