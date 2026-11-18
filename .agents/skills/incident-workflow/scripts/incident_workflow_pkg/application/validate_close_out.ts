import type { Problem } from "#scripts/incident_workflow_pkg/domain/problem.ts";
import type { CloseOutSnapshot } from "#scripts/incident_workflow_pkg/domain/ports.ts";
import { checkIdentificationConsistency, evaluateCloseOut } from "#scripts/incident_workflow_pkg/domain/rules.ts";
import type { ParsedRecord, TicketIdentification } from "#scripts/incident_workflow_pkg/domain/rules.ts";

/**
 * The outcome of one close-out validation: the close is skipped because no
 * durable ticket record exists, or the durable set was checked and the
 * postconditions it breaks are reported.
 */
export type CloseOutOutcome =
	| { readonly kind: "skipped"; readonly code: string; readonly reason: string }
	| { readonly kind: "checked"; readonly violations: string[]; readonly warnings: string[] };

export class ValidateCloseOut {
	execute(
		snapshot: CloseOutSnapshot,
		ticket: ParsedRecord<TicketIdentification> | null,
		registerRows: readonly Problem[],
	): CloseOutOutcome {
		const evaluation = evaluateCloseOut(snapshot);
		if (evaluation.kind === "skipped") return evaluation;
		const violations = [...evaluation.violations];
		if (ticket !== null) {
			if ("error" in ticket) violations.push(`CLOSE-7: ticket record cannot be parsed: ${ticket.error}`);
			else
				violations.push(
					...checkIdentificationConsistency(
						ticket.value.identification_verdict,
						ticket.value.known_problem_ids,
						registerRows,
					),
				);
		}
		return { kind: "checked", violations, warnings: [] as string[] };
	}
}
