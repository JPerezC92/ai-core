import { checkConcurrentSession, checkIdentificationVerdict, checkKillSwitches, checkPhase, checkSlaClock, checkStepSections, STEP_FILES, STEP_NAMES } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import type { AnalysisHeader } from '#scripts/incident_workflow_pkg/domain/rules.ts';

export class ValidateStep {
  private readonly clock: () => Date;
  constructor(clock: () => Date) { this.clock = clock; }
  execute(header: AnalysisHeader, contents: Readonly<Record<string, string>>, step: string, directory: string) {
    const index = STEP_NAMES.findIndex(name => name === step);
    const filename = STEP_FILES[index] ?? `${step}.md`;
    const content = contents[filename];
    if (content === undefined) return { violations: [`STEP-NOT-WRITTEN: step ${step} (${filename}) not yet written in ${directory}`], warnings: [] as string[] };
    const violations = [...checkPhase(header), ...checkIdentificationVerdict(header)];
    for (const [, item] of checkStepSections(content, filename, true)) {
      violations.push(item.startsWith('UNFILLED-TOKEN:') ? `${item} in ${filename}` : `MISSING-SECTION: ${filename} is missing ${item}`);
    }
    violations.push(...checkKillSwitches(header));
    const warnings: string[] = [];
    const now = this.clock();
    const sla = checkSlaClock(header, now);
    const concurrent = checkConcurrentSession(header, now);
    if (sla !== undefined) warnings.push(sla);
    if (concurrent !== undefined) warnings.push(concurrent);
    return { violations, warnings };
  }
}
