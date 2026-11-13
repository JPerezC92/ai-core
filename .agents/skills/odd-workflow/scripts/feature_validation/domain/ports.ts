/** Domain-owned filesystem capability needed by feature validation. */

export interface FeatureSource {
  discover(target: string): readonly string[];
  read(reference: string): string;
}
