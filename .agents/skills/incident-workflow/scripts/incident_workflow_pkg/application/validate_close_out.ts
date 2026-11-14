import type { Problem } from '#scripts/incident_workflow_pkg/domain/problem.ts';
import type { CloseOutSnapshot } from '#scripts/incident_workflow_pkg/domain/ports.ts';
import { checkIdentificationConsistency, evaluateCloseOut } from '#scripts/incident_workflow_pkg/domain/rules.ts';
import type { ParsedRecord, TicketIdentification } from '#scripts/incident_workflow_pkg/domain/rules.ts';

export class ValidateCloseOut {
  execute(snapshot: CloseOutSnapshot, ticket: ParsedRecord<TicketIdentification> | null, registerRows: readonly Problem[]) {
    const violations = evaluateCloseOut(snapshot);
    if (ticket !== null) {
      if ('error' in ticket) violations.push(`CLOSE-7: ticket record cannot be parsed: ${ticket.error}`);
      else violations.push(...checkIdentificationConsistency(ticket.value.identification_verdict, ticket.value.known_problem_ids, registerRows));
    }
    return { violations, warnings: [] as string[] };
  }
}
