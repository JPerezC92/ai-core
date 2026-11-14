/** Domain-owned filesystem capability needed by the retirement check. */

export interface RetirementSource {
  discover(target: string): readonly string[];
  read(reference: string): string;
}
