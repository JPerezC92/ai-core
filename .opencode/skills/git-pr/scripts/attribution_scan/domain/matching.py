"""Match attribution lines and report policy exclusions in validated snapshots."""

from .records import AttributionPolicy, Exclusion, Match, ScanResult, Snapshot


def _scan_content(
    content: str,
    surface: str,
    source: str | None,
    path: str | None,
    policy: AttributionPolicy,
) -> list[Match]:
    matches: list[Match] = []
    markers = [(item, item.casefold()) for item in policy["markers"]]
    identities = [(item, item.casefold()) for item in policy["identities"]]
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        normalized_line = raw_line.strip().casefold()
        matching_markers = [item for item in markers if normalized_line.startswith(item[1])]
        matching_identities = [item for item in identities if item[1] in normalized_line]
        for marker, _ in matching_markers:
            for identity, _ in matching_identities:
                matches.append(
                    {
                        "surface": surface,
                        "source": source,
                        "path": path,
                        "line": line_number,
                        "marker": marker,
                        "identity": identity,
                    }
                )
    return matches


def scan_validated_snapshot(snapshot: Snapshot, policy: AttributionPolicy) -> ScanResult:
    """Return ordered same-line matches and exclusions without validating inputs."""
    matches: list[Match] = []
    exclusions: list[Exclusion] = []
    for artifact in snapshot["artifacts"]:
        matches.extend(
            _scan_content(
                artifact["content"], artifact["surface"], artifact["source"], None, policy
            )
        )
    for changed_file in snapshot["changed_files"]:
        if changed_file["path"].replace("\\", "/") == policy["self_excluded_file"].replace("\\", "/"):
            exclusions.append(
                {"path": changed_file["path"], "reason": "policy self-exclusion"}
            )
            continue
        matches.extend(
            _scan_content(
                changed_file["content"], "changed-file", None, changed_file["path"], policy
            )
        )
    return {
        "pr_number": snapshot["pr_number"],
        "head_sha": snapshot["head_sha"],
        "base": snapshot["base"],
        "matches": matches,
        "exclusions": exclusions,
    }
