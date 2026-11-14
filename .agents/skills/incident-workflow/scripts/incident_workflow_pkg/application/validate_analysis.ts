import { checkConcurrentSession, checkIdentificationVerdict, checkKillSwitches, checkPhase, checkSlaClock, checkStepFilesExist, checkStepSections, STEP_FILES, STEP_NAMES } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import type { AnalysisHeader } from '#scripts/incident_workflow_pkg/domain/rules.ts';

export class ValidateAnalysis {
  private readonly clock: () => Date;
  constructor(clock: () => Date) { this.clock = clock; }
  execute(header: AnalysisHeader, contents: Readonly<Record<string, string>>, directory: string) {
    const violations = [...checkPhase(header), ...checkIdentificationVerdict(header)];
    const rank = STEP_NAMES.findIndex(name => name === header.Phase.trim()) + 1;
    const existence = rank ? checkStepFilesExist(contents, directory, rank) : { violations: [], warnings: [] };
    violations.push(...existence.violations);
    for (const [index, filename] of STEP_FILES.entries()) {
      const content = contents[filename];
      if (content === undefined) continue;
      for (const [, item] of checkStepSections(content, filename, index + 1 <= rank)) {
        violations.push(item.startsWith('UNFILLED-TOKEN:') ? `${item} in ${filename}` : `MISSING-SECTION: ${filename} is missing ${item}`);
      }
    }
    violations.push(...checkKillSwitches(header));
    const now = this.clock();
    const warnings = [...existence.warnings];
    const sla = checkSlaClock(header, now);
    const concurrent = checkConcurrentSession(header, now);
    if (sla !== undefined) warnings.push(sla);
    if (concurrent !== undefined) warnings.push(concurrent);
    return { violations, warnings };
  }
}
