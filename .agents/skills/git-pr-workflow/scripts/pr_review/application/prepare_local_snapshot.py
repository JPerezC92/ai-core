"""Prepare scanner input using local authored title/body and supplied immutable data."""

from attribution_scan.domain.records import Snapshot

from pr_review.domain.records import ReviewPreparationError
from pr_review.domain.snapshot_assembly import assemble_snapshot, validate_local_inventory


def execute(*, draft: str, body: str, inventory: object, exact_paths: object) -> Snapshot | ReviewPreparationError:
    """Assemble local artifacts without fetching remote prose or collecting Git state."""
    lines = draft.splitlines()
    if not lines or not lines[0].startswith("Title: "):
        return ReviewPreparationError("DRAFT_INVALID", "creation draft must begin with a Title: line")
    validated = validate_local_inventory(inventory)
    if isinstance(validated, ReviewPreparationError):
        return validated
    if not isinstance(body, str):
        return ReviewPreparationError("SNAPSHOT_INVALID", "local working body must be text")
    title = lines[0][len("Title: "):]
    candidate: Snapshot = {
        "schema": validated["schema"], "pr_number": validated["pr_number"],
        "head_sha": validated["head_sha"], "base": validated["base"],
        "artifacts": [
            {"surface": "pr-title", "source": f"PR #{validated['pr_number']} title", "content": title},
            {"surface": "pr-body", "source": f"PR #{validated['pr_number']} body", "content": body},
            *validated["commit_messages"],
        ],
        "changed_files": validated["changed_files"],
    }
    return assemble_snapshot(candidate, exact_paths)
