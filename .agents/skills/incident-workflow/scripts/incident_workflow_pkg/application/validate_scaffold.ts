import { checkConcurrentSession, checkIdentificationVerdict, checkKillSwitches, checkPhase, checkSlaClock, checkStepFilesExist, checkStepSections, STEP_FILES } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import type { AnalysisHeader } from '#scripts/incident_workflow_pkg/domain/rules.ts';

export class ValidateScaffold {
  private readonly clock: () => Date;
  constructor(clock: () => Date) { this.clock = clock; }
  execute(header: AnalysisHeader, contents: Readonly<Record<string, string>>, directory: string) {
    const existence = checkStepFilesExist(contents, directory, STEP_FILES.length);
    const violations = [...checkPhase(header), ...checkIdentificationVerdict(header), ...existence.violations];
    for (const filename of STEP_FILES) {
      const content = contents[filename];
      if (content === undefined) continue;
      for (const [, item] of checkStepSections(content, filename, false)) violations.push(`MISSING-SECTION: ${filename} is missing ${item}`);
    }
    violations.push(...checkKillSwitches(header));
    const warnings = [...existence.warnings];
    const now = this.clock();
    const sla = checkSlaClock(header, now);
    const concurrent = checkConcurrentSession(header, now);
    if (sla !== undefined) warnings.push(sla);
    if (concurrent !== undefined) warnings.push(concurrent);
    return { violations, warnings };
  }
}
