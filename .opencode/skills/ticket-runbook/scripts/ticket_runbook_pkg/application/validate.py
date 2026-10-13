"""Application layer: named ticket-runbook validation use cases exposing ``execute()``."""

from __future__ import annotations

from ticket_runbook_pkg.domain.rules import (
    STEP_FILE_BY_NAME,
    STEP_FILES,
    AnalysisHeader,
    CloseOutSnapshot,
    ModeFindings,
    ProblemRow,
    RegisterRowsPort,
    _current_step_rank,
    check_concurrent_session,
    check_identification_consistency,
    check_identification_verdict,
    check_kill_switches,
    check_phase,
    check_single_step_file_exists,
    check_single_step_sections,
    check_sla_clock,
    check_step_files_exist,
    check_step_files_have_required_sections,
    evaluate_close_out,
    evaluate_pre_close,
    parse_ticket_record,
)


class ValidateAnalysis:
    """Full working-analysis validation use case for the default CLI mode."""

    def execute(
        self,
        header: AnalysisHeader,
        step_contents: dict[str, str],
        analysis_dir: str,
    ) -> ModeFindings:
        """Validate the header and every present step through the header's phase rank."""
        violations: list[str] = []
        warnings: list[str] = []

        violations.extend(check_phase(header))
        violations.extend(check_identification_verdict(header))

        current_rank = _current_step_rank(header)
        if current_rank is not None:
            step_violations, step_warnings = check_step_files_exist(
                step_contents, analysis_dir, current_rank
            )
            violations.extend(step_violations)
            warnings.extend(step_warnings)

        for fname, item in check_step_files_have_required_sections(
            step_contents,
            fill_token_rank_limit=current_rank if current_rank is not None else 0,
        ):
            if item.startswith("UNFILLED-TOKEN:"):
                violations.append(f"{item} in {fname}")
            else:
                violations.append(f"MISSING-SECTION: {fname} is missing {item}")

        violations.extend(check_kill_switches(header))

        sla_warn = check_sla_clock(header)
        if sla_warn:
            warnings.append(sla_warn)
        concurrent_warn = check_concurrent_session(header)
        if concurrent_warn:
            warnings.append(concurrent_warn)

        return {"violations": violations, "warnings": warnings}


class ValidateScaffold:
    """Structural scaffold-validation use case for a freshly copied analysis set."""

    def execute(
        self,
        header: AnalysisHeader,
        step_contents: dict[str, str],
        analysis_dir: str,
    ) -> ModeFindings:
        """Validate the header and all four scaffold files without fill-token checks."""
        violations: list[str] = []
        warnings: list[str] = []

        violations.extend(check_phase(header))
        violations.extend(check_identification_verdict(header))

        step_violations, step_warnings = check_step_files_exist(
            step_contents, analysis_dir, len(STEP_FILES)
        )
        violations.extend(step_violations)
        warnings.extend(step_warnings)

        for fname, item in check_step_files_have_required_sections(
            step_contents, fill_token_rank_limit=0
        ):
            violations.append(f"MISSING-SECTION: {fname} is missing {item}")

        violations.extend(check_kill_switches(header))

        sla_warn = check_sla_clock(header)
        if sla_warn:
            warnings.append(sla_warn)
        concurrent_warn = check_concurrent_session(header)
        if concurrent_warn:
            warnings.append(concurrent_warn)

        return {"violations": violations, "warnings": warnings}


class ValidateStep:
    """Strict single-step validation use case for the explicitly selected step."""

    def execute(
        self,
        header: AnalysisHeader,
        step_contents: dict[str, str],
        step_name: str,
        analysis_dir: str,
    ) -> ModeFindings:
        """Validate the header and the one named step; a missing step is the sole finding."""
        violations: list[str] = []
        warnings: list[str] = []

        violations.extend(check_phase(header))
        violations.extend(check_identification_verdict(header))

        fname = check_single_step_file_exists(step_contents, step_name)
        if fname is None:
            expected = STEP_FILE_BY_NAME.get(step_name, f"{step_name}.md")
            return {
                "violations": [
                    f"STEP-NOT-WRITTEN: step {step_name} ({expected}) "
                    f"not yet written in {analysis_dir}"
                ],
                "warnings": [],
            }

        for _fname, item in check_single_step_sections(step_contents, step_name):
            if item.startswith("UNFILLED-TOKEN:"):
                violations.append(f"{item} in {_fname}")
            else:
                violations.append(f"MISSING-SECTION: {_fname} is missing {item}")

        violations.extend(check_kill_switches(header))

        sla_warn = check_sla_clock(header)
        if sla_warn:
            warnings.append(sla_warn)
        concurrent_warn = check_concurrent_session(header)
        if concurrent_warn:
            warnings.append(concurrent_warn)

        return {"violations": violations, "warnings": warnings}


class ValidatePreClose:
    """Pre-close readiness use case for the working and durable ticket set."""

    def execute(
        self,
        snapshot: CloseOutSnapshot,
        register_rows: list[ProblemRow],
    ) -> ModeFindings:
        """Evaluate pre-collapse readiness from an already-loaded snapshot."""
        return {
            "violations": evaluate_pre_close(snapshot, register_rows),
            "warnings": [],
        }


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
                record = parse_ticket_record(
                    snapshot["ticket_content"],
                    snapshot["ticket_file_names"][0],
                )
                violations.extend(
                    check_identification_consistency(
                        record["identification_verdict"],
                        record["known_problem_ids"],
                        load_register_rows(),
                    )
                )

        return {"violations": violations, "warnings": []}
