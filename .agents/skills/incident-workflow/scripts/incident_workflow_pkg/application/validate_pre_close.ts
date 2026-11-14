import type { Problem } from '#scripts/incident_workflow_pkg/domain/problem.ts';
import type { CloseOutSnapshot } from '#scripts/incident_workflow_pkg/domain/ports.ts';
import { evaluatePreClose } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import type { AnalysisHeader, ParsedRecord, TicketIdentification } from '#scripts/incident_workflow_pkg/domain/rules.ts';

export class ValidatePreClose {
  execute(snapshot: CloseOutSnapshot, ticket: ParsedRecord<TicketIdentification> | null, header: ParsedRecord<AnalysisHeader> | null, registerRows: readonly Problem[]) {
    return { violations: evaluatePreClose(snapshot, ticket, header, registerRows), warnings: [] as string[] };
  }
}
