"""Build typed offline review content inputs and deliberately invalid variants."""

from __future__ import annotations

from typing import Literal, TypedDict

from .domain.records import ReviewMetadata

BodyDefect = Literal["missing-row", "duplicate-row", "unchecked", "wrong-head", "changed-item"]
RemoteField = Literal["number", "headRefOid", "body"]


def create_body(**overrides: str) -> str:
    """Create a canonical passing body; overrides target named textual fields."""
    item = overrides.get("item", "Inspect the change and confirm the intended result")
    return (
        "## Summary\n- Preserve this unrelated explanation exactly.\n\n"
        f"## Test plan\n- [x] {item}\n"
        "- [x] Inspect the regression and confirm it is absent\n\n"
        "## Findings / blockers\nNo findings.\n\n"
        "## Test evidence\n- PR: `#80`\n"
        f"- Immutable head SHA: `{overrides.get('head', 'a' * 40)}`\n"
        "- Base: `origin/main`\n"
        f"- Scope command: `git diff \"origin/main\"...{'a' * 40}`\n\n"
        "| Test-plan item | Literal action/input | Observed result | Executor |\n"
        "|---|---|---|---|\n"
        f"| {item} | Inspect the change | Expected result observed | Reviewer |\n"
        "| Inspect the regression and confirm it is absent | Inspect regression | Absent | Reviewer |\n\n"
        "[PASS] — Required checks are recorded and no findings remain.\n"
    )


def create_metadata(*, number: int = 80, head: str = "a" * 40, body: str | None = None) -> ReviewMetadata:
    """Create externally supplied metadata with explicit typed overrides."""
    return {
        "number": number, "headRefOid": head, "baseRefName": "main",
        "headRefName": "feat/release/body", "state": "OPEN",
        "title": "feat(release): prepare review", "body": create_body() if body is None else body,
    }


def create_draft() -> str:
    """Create the existing title-wrapped creation artifact."""
    return "Title: feat(release): prepare review\n\n---\n\n" + create_body()


def create_divergence(field: RemoteField) -> ReviewMetadata:
    """Create a remote identity, head, or body change."""
    if field == "number":
        return create_metadata(number=81)
    if field == "headRefOid":
        return create_metadata(head="b" * 40)
    return create_metadata(body="Changed remotely")


MetadataDefect = Literal[
    "non-object", "zero-number", "negative-number", "string-number",
    "short-head", "non-hex-head", "long-head", "not-open-state",
    "blank-base", "blank-head-ref", "blank-title",
    "non-string-title", "non-string-base", "non-string-head-ref",
    "non-string-state", "non-string-body",
    "missing-field",
]


def create_invalid_metadata(defect: MetadataDefect) -> object:
    """Create one named metadata rejection variant, including non-object input."""
    if defect == "non-object":
        return tuple(create_metadata().items())
    if defect == "missing-field":
        incomplete = dict(create_metadata())
        del incomplete["body"]
        return incomplete
    rejections: dict[str, tuple[str, object]] = {
        "zero-number": ("number", 0),
        "negative-number": ("number", -1),
        "string-number": ("number", "80"),
        "short-head": ("headRefOid", "a" * 6),
        "non-hex-head": ("headRefOid", "z" * 40),
        "long-head": ("headRefOid", "a" * 65),
        "not-open-state": ("state", "MERGED"),
        "blank-base": ("baseRefName", "   "),
        "blank-head-ref": ("headRefName", ""),
        "blank-title": ("title", " "),
        "non-string-title": ("title", 7),
        "non-string-base": ("baseRefName", None),
        "non-string-head-ref": ("headRefName", ["feat/release/body"]),
        "non-string-state": ("state", True),
        "non-string-body": ("body", 0),
    }
    field, invalid = rejections[defect]
    metadata: dict[str, object] = dict(create_metadata())
    metadata[field] = invalid
    return metadata


def create_invalid_body(defect: BodyDefect) -> str:
    """Create one named structural evidence defect without implying semantic truth."""
    body = create_body()
    row = next(line for line in body.splitlines() if line.startswith("| Inspect the change"))
    if defect == "missing-row":
        return body.replace(row + "\n", "")
    if defect == "duplicate-row":
        return body.replace(row, row + "\n" + row)
    if defect == "unchecked":
        return body.replace("- [x]", "- [ ]", 1)
    if defect == "wrong-head":
        return create_body(head="b" * 40)
    return body.replace("- [x] Inspect the change", "- [x] Recheck the change", 1)


FindingStatus = Literal["FIXED", "REJECTED", "OPEN", "IN PROGRESS", "DEFERRED"]
ProtectedChange = Literal["summary", "item"]
HistoryChange = Literal["removed", "renumbered", "severity"]


def create_truncated_evidence_body() -> str:
    """Keep the expected section names but end at a heading without a newline."""
    return create_body().split("## Test evidence", 1)[0] + "## Test evidence"


def create_findings_body(status: FindingStatus = "FIXED") -> str:
    """Create canonical finding rows with explicit resolution or refutation text."""
    evidence = "output/audits/fix.md — corrected result verified"
    resolution = "Implementer — parser corrected; verified by Reviewer"
    if status == "REJECTED":
        evidence = "output/audits/refutation.md — exact comparison returned equal"
        resolution = "Reviewer — mechanically refuted by exact comparison"
    elif status in ("OPEN", "IN PROGRESS"):
        resolution = "Implementer — correct parser and request verification"
    elif status == "DEFERRED":
        resolution = ".aicore/core/knowledge/debt.md#fixture — user authorized deferral on 2026-10-31"
    findings = (
        "| ID | Severity | Status | Evidence | Owner / resolution |\n"
        "|---|---|---|---|---|\n"
        f"| F1 | `ADVISORY` | `{status}` | {evidence} | {resolution} |"
    )
    body = create_body().replace("No findings.", findings)
    if status == "DEFERRED":
        body = body.replace(
            "[PASS] —", "## Open debt\n- F1 — .aicore/core/knowledge/debt.md#fixture, authorized by user on 2026-10-31\n\n[PASS] —",
        )
    return body


def create_initial_review_body() -> str:
    """Create an unchecked remote baseline before the canonical review join."""
    prefix = create_body().split("## Test evidence", 1)[0]
    return prefix.replace("- [x]", "- [ ]").replace("No findings.", "No review findings yet.")


def create_protected_content_change(change: ProtectedChange) -> str:
    """Create a candidate that changes protected prose or an exact test-item key."""
    if change == "summary":
        return create_body().replace("Preserve this unrelated explanation exactly.", "Unauthorized replacement.")
    return create_body(item="Inspect a different change and confirm its result")


def create_changed_history(change: HistoryChange) -> str:
    """Create a candidate that loses or changes an existing finding identity."""
    body = create_findings_body()
    if change == "removed":
        return create_body()
    if change == "renumbered":
        return body.replace("| F1 |", "| F2 |")
    return body.replace("`ADVISORY`", "`BLOCK`")


class DecisionEvidence(TypedDict):
    """Carry supplied decision provenance without certifying its authenticity."""

    target: str
    actor: str
    date: str
    statement: str
    evidence: str
    destination: str


class ReviewDecisions(TypedDict):
    """Bind supplied N/A, acceptance and debt decisions to one review context."""

    pr_number: int
    head_sha: str
    not_applicable: list[DecisionEvidence]
    acceptance: list[DecisionEvidence]
    debt: list[DecisionEvidence]


OutcomeKind = Literal["na", "advisory", "debt"]
DecisionDefect = Literal["head", "provenance"]


def create_decision(target: str, *, destination: str = "") -> DecisionEvidence:
    """Create explicit supplied provenance for a fixture decision."""
    return {"target": target, "actor": "user", "date": "2026-10-31",
            "statement": "approved", "evidence": "feature Log L15", "destination": destination}


def create_review_decisions(kind: Literal["none", "na", "advisory", "debt"] = "none") -> ReviewDecisions:
    """Create typed decision inputs separately from the rendered body."""
    value: ReviewDecisions = {"pr_number": 80, "head_sha": "a" * 40,
                              "not_applicable": [], "acceptance": [], "debt": []}
    if kind == "na":
        value["not_applicable"] = [create_decision("Inspect the regression and confirm it is absent")]
    if kind in ("advisory", "debt"):
        value["acceptance"] = [create_decision("F1")]
    if kind == "debt":
        value["debt"] = [create_decision("F1", destination=".aicore/core/knowledge/debt.md#fixture")]
    return value


def create_invalid_decisions(defect: DecisionDefect) -> ReviewDecisions:
    """Create deliberately invalid supplied decision binding or provenance."""
    value = create_review_decisions("na")
    if defect == "head":
        value["head_sha"] = "b" * 40
    else:
        value["not_applicable"][0]["evidence"] = ""
    return value


def create_outcome_body(kind: OutcomeKind) -> str:
    """Render canonical outcomes with exact item keys and the existing columns."""
    if kind == "na":
        body = create_body().replace("- [x] Inspect the regression", "- [ ] Inspect the regression")
        row = next(line for line in body.splitlines() if line.startswith("| Inspect the regression"))
        return body.replace(row + "\n", "")
    body = create_findings_body("DEFERRED" if kind == "debt" else "OPEN")
    return body.replace("[PASS] — Required checks are recorded and no findings remain.",
                        "[ADVISORY] — user accepted F1 on 2026-10-31; required checks are recorded.")


FollowupDefect = Literal["missing", "target", "destination", "provenance"]


def create_pipe_item_body(*, mismatched: bool = False) -> str:
    """Keep the checkbox literal while escaping its table-cell pipe for Markdown."""
    item = "Inspect A | B and confirm equality"
    body = create_body(item=item)
    table_item = "Inspect A \\| C and confirm equality" if mismatched else "Inspect A \\| B and confirm equality"
    return body.replace(f"| {item} |", f"| {table_item} |")


def create_followup_decisions(*, advisory: bool = False) -> ReviewDecisions:
    """Authorize a separate follow-up without manufacturing a deferred finding."""
    decisions = create_review_decisions("advisory" if advisory else "none")
    decisions["debt"] = [create_decision("Follow-up: improve diagnostics", destination=".aicore/core/knowledge/debt.md#diagnostics")]
    return decisions


def create_followup_body(*, advisory: bool = False) -> str:
    """Render an independently authorized follow-up using canonical debt syntax."""
    body = create_outcome_body("advisory") if advisory else create_body()
    marker = "[ADVISORY] —" if advisory else "[PASS] —"
    debt = ("## Open debt\n"
            "- Follow-up: improve diagnostics — .aicore/core/knowledge/debt.md#diagnostics, authorized by user on 2026-10-31\n\n")
    return body.replace(marker, debt + marker)


def create_invalid_followup_decisions(defect: FollowupDefect) -> ReviewDecisions:
    """Create missing or inconsistent supplied follow-up authority."""
    decisions = create_followup_decisions()
    if defect == "missing":
        decisions["debt"] = []
    elif defect == "target":
        decisions["debt"][0]["target"] = "Follow-up: different work"
    elif defect == "destination":
        decisions["debt"][0]["destination"] = ".aicore/core/knowledge/debt.md#different"
    else:
        decisions["debt"][0]["evidence"] = ""
    return decisions
