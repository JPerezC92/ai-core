"""Application layer: close-out postcondition validation use case."""

from __future__ import annotations

from ticket_runbook_pkg.domain.ports import RegisterRowsPort
from ticket_runbook_pkg.domain.rules import (
    check_identification_consistency,
    evaluate_close_out,
    parse_ticket_record,
)
from ticket_runbook_pkg.domain.value_objects import (
    CloseOutSnapshot,
    ModeFindings,
)

__all__ = ["ValidateCloseOut"]


class ValidateCloseOut:
    """Close-out postcondition use case for the collapsed durable ticket set."""

    def execute(
        self,
        snapshot: CloseOutSnapshot,
        load_register_rows: RegisterRowsPort,
    ) -> ModeFindings:
        """Evaluate durable postconditions, loading register rows only when cited."""
        violations = evaluate_close_out(snapshot)

        if len(snapshot["ticket_file_names"]) == 1:
            if snapshot["ticket_content"] is not None:
                try:
                    record = parse_ticket_record(
                        snapshot["ticket_content"],
                        snapshot["ticket_file_names"][0],
                    )
                except ValueError as exc:
                    violations.append(
                        f"CLOSE-7: ticket record cannot be parsed: {exc}"
                    )
                else:
                    violations.extend(
                        check_identification_consistency(
                            record["identification_verdict"],
                            record["known_problem_ids"],
                            load_register_rows(),
                        )
                    )

        return {"violations": violations, "warnings": []}
