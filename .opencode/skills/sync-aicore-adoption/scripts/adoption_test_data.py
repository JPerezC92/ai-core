"""Shared neutral document fixtures and digest helpers for adoption tests."""

from __future__ import annotations

import hashlib
from typing import TypedDict

from adoption_digests import (
    _snapshot_digest,
    assertion_list_digest,
    assertion_status_digest,
    declaration_unit_digest,
    member_digest,
    unit_digest,
)
from adoption_contracts import ProjectedEntry
from adoption_test_runner_data import AICORE_RUNNER

UPSTREAM_ID = "example/upstream"
CATALOG_REL = ".aicore/core-catalog-v2.yaml"



PLACEHOLDER_DIGEST = "sha256:" + "0" * 64

def review_with_transition(
    review_text: str,
    target_commit: str,
    declaration_text: str,
    baseline_lock_digest: str | None = None,
    decision_digests: dict[str, tuple[str, str]] | None = None,
) -> str:
    """Inject transition bindings and optional decision digests via text insertion."""
    baseline_val = "null" if baseline_lock_digest is None else baseline_lock_digest
    decl_digest = sha256_text(declaration_text)
    transition_block = (
        f"transition:\n"
        f"  baseline_lock_digest: {baseline_val}\n"
        f"  target_source_commit: {target_commit}\n"
        f"  declaration_digest: {decl_digest}\n"
    )
    lines = review_text.split("\n")
    result = []
    inserted = False
    for line in lines:
        result.append(line)
        if not inserted and line.startswith("upstream_repository:"):
            result.append(transition_block.rstrip("\n"))
            inserted = True
    text = "\n".join(result)
    # Add decision digests if requested and transition is present
    if decision_digests:
        out_lines = []
        current_unit = None
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("- unit:"):
                current_unit = stripped.split(":", 1)[1].strip()
            out_lines.append(line)
            if (current_unit and stripped.startswith("reviewer:")
                    and current_unit in decision_digests):
                up_d, dst_d = decision_digests[current_unit]
                indent = " " * (len(line) - len(line.lstrip()))
                out_lines.append(f"{indent}reviewed_upstream_digest: {up_d}")
                out_lines.append(f"{indent}reviewed_destination_digest: {dst_d}")
        text = "\n".join(out_lines)
    return text

class LockMemberRow(TypedDict):
    """One member's accepted source and adopter snapshot digests."""

    id: str
    destination: str
    accepted_upstream_digest: str
    accepted_destination_digest: str


class LockUnitRow(TypedDict):
    """One adoption unit and the digests for its mapped members."""

    id: str
    mode: str
    declaration_unit_digest: str
    accepted_upstream_digest: str
    members: list[LockMemberRow]


class LockDocument(TypedDict):
    """A complete schema-v2 adoption lock document."""

    schema_version: int
    upstream_repository: str
    accepted_source_commit: str
    accepted_catalog_digest: str
    declaration_digest: str
    review_digest: str
    accepted_snapshot_digest: str
    units: list[LockUnitRow]


class AssertionSpec(TypedDict):
    """One fixed-shape configuration assertion fixture."""

    id: str
    contains: str


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def member_file(text: str) -> str:
    return member_digest(
        [ProjectedEntry(path="", mode="100644", content=text.encode("utf-8"))]
    )


def placeholder_digest(seed: str) -> str:
    return sha256_text("placeholder:" + seed)


def snapshot_digest(
    declaration: str, review: str, rows: list[LockUnitRow]
) -> str:
    return _snapshot_digest(sha256_text(declaration), sha256_text(review), rows)


GREETING_CATALOG = """schema_version: 2
catalog:
  version: 2.0.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: greeting
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/greeting.txt, destination: content/greeting.txt }
"""
GREETING_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: mirror
    members:
      - { id: file, destination: content/greeting.txt }
"""
EMPTY_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions: []
"""
GREETING_DECISION_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: greeting
    decision: applied
    evidence: "Destination-owned fork re-based on the upstream change."
    reviewer: test-suite
"""
TWO_UNIT_CATALOG = """schema_version: 2
catalog:
  version: 2.0.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: greeting
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/greeting.txt, destination: content/greeting.txt }
  - id: note
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: content/note.txt, destination: content/note.txt }
"""
TWO_UNIT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: mirror
    members:
      - { id: file, destination: content/greeting.txt }
  - id: note
    mode: adapted
    members:
      - { id: file, destination: content/note-local.txt }
"""
TWO_UNIT_DECISION_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: note
    decision: applied
    evidence: "Local note reconciled with the upstream rewrite."
    reviewer: test-suite
"""
ASSERTION_CATALOG = """schema_version: 2
catalog:
  version: 2.0.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: opencode-config
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: assertions
    destination: opencode.jsonc
    assertions:
      - { id: sudo-deny, contains: '"sudo *": "deny"' }
  - id: gitignore-config
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: assertions
    destination: .gitignore
    assertions:
      - { id: output-ignored, contains: 'output/' }
"""
ASSERTION_DECLARATION = f"""schema_version: 2
upstream_repository: example/upstream
profile: {{ backend_stack: false, python_scripts: false, ticket_system: false }}
units:
  - id: opencode-config
    mode: mirror
  - id: gitignore-config
    mode: mirror
test_runner:
  commands:
    - {AICORE_RUNNER['commands'][0]}
  executor: {AICORE_RUNNER['executor']}
  scope: {AICORE_RUNNER['scope']}
  reviewer: {AICORE_RUNNER['reviewer']}
  evidence: {AICORE_RUNNER['evidence']}
"""
GUARDED_ROOT_CATALOG = """schema_version: 2
catalog:
  version: 2.1.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: guarded_file
    destination_policy: adopter_root_runtime
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
"""
GUARDED_ROOT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: root-runtime-spec
    mode: adapted
    members:
      - { id: root, destination: AGENTS.md }
"""
UPSTREAM_ROOT = """# Cipher — AICore
> **Spec version:** 2.1.0

## Reuse guide (adopting this core)
Run migrate-core-to-project to adopt AICore.
"""
CLEAN_DESTINATION_ROOT = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.1.0
> **Local version:** 1.0.0

## Identity & Role
Project-local orchestration rules.
"""
ORIGINAL_REUSE_GUIDE_ROOT = CLEAN_DESTINATION_ROOT + """
## Reuse guide (adopting this core)
Run migrate-core-to-project to install AICore and retain its operator guidance.
"""
VERBOSE_UPSTREAM_LINEAGE_ROOT = CLEAN_DESTINATION_ROOT + """
## Upstream lineage
Use migrate-core-to-project and sync-aicore-adoption for future updates.
Retain upstream stack, token, and registry guidance in this runtime.
"""
MINIMAL_UPSTREAM_LINEAGE_ROOT = CLEAN_DESTINATION_ROOT + """
> **Upstream provenance:** AICore (`JPerezC92/ai-core`)

AICore (`JPerezC92/ai-core`) is upstream provenance only.
"""
INCOMPLETE_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units: []
"""
NOT_APPLICABLE_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: not_applicable
"""
DESTINATION_OWNED_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: greeting
    mode: destination_owned
    members:
      - { id: file, destination: content/greeting.txt }
"""

STORY_CATALOG = """schema_version: 2
catalog:
  version: 2.4.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: portable-stories-always
    kind: user-story
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: alpha, source: user-stories/alpha.md, destination: user-stories/alpha.md, collision_policy: core_wins }
      - { id: beta, source: user-stories/beta.md, destination: user-stories/beta.md }
  - id: portable-stories-ticket
    kind: user-story
    applicability: { requires: [ticket_system] }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: gamma, source: user-stories/gamma.md, destination: user-stories/gamma.md, collision_policy: core_wins }
"""
STORY_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: true }
units:
  - id: portable-stories-always
    mode: mirror
    members:
      - { id: alpha, destination: user-stories/alpha.md }
      - { id: beta, destination: user-stories/beta.md }
  - id: portable-stories-ticket
    mode: mirror
    members:
      - { id: gamma, destination: user-stories/gamma.md }
"""
STORY_DECLARATION_NO_TICKET = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: portable-stories-always
    mode: mirror
    members:
      - { id: alpha, destination: user-stories/alpha.md }
      - { id: beta, destination: user-stories/beta.md }
  - id: portable-stories-ticket
    mode: not_applicable
"""
STORY_CORE_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha | active | ep-a | `a` |
| `beta` | Beta | active | ep-b | `b` |
| `gamma` | Gamma | active | ep-g | `g` |
| `aicore-only` | AICore only | active | ep-core | `core` |

## Appendices

Core appendix notes.
"""
STORY_DESTINATION_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha local edit | active | ep-a | `a` |
| `beta` | Beta | active | ep-b | `b` |
| `dest-own` | Destination owned | active | local | `d` |
| `gamma` | Gamma | active | ep-g | `g` |

## Destination notes

Local trailing section that must survive byte-for-byte.
"""


def greeting_lock_document(
    accepted: str,
    accepted_text: str,
    destination_text: str,
    catalog: str = GREETING_CATALOG,
    declaration: str = GREETING_DECLARATION,
    review: str = EMPTY_REVIEW,
    mode: str = "mirror",
) -> LockDocument:
    upstream_member = member_file(accepted_text)
    destination_member = member_file(destination_text)
    rows: list[LockUnitRow] = [{
        "id": "greeting",
        "mode": mode,
        "declaration_unit_digest": declaration_unit_digest(
            mode, [{"id": "file", "destination": "content/greeting.txt"}], []
        ),
        "accepted_upstream_digest": unit_digest([("file", upstream_member)]),
        "members": [{
            "id": "file",
            "destination": "content/greeting.txt",
            "accepted_upstream_digest": upstream_member,
            "accepted_destination_digest": destination_member,
        }],
    }]
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(review),
        "accepted_snapshot_digest": snapshot_digest(declaration, review, rows),
        "units": rows,
    }


def two_unit_lock_document(
    accepted: str,
    greeting_committed: str,
    note_committed: str,
    greeting_destination: str,
    note_destination: str,
    catalog: str = TWO_UNIT_CATALOG,
    declaration: str = TWO_UNIT_DECLARATION,
    review: str = EMPTY_REVIEW,
) -> LockDocument:
    greeting_upstream = member_file(greeting_committed)
    note_upstream = member_file(note_committed)
    rows: list[LockUnitRow] = []
    for unit_id, mode, destination, upstream in (
        ("greeting", "mirror", "content/greeting.txt", greeting_upstream),
        ("note", "adapted", "content/note-local.txt", note_upstream),
    ):
        rows.append({
            "id": unit_id,
            "mode": mode,
            "declaration_unit_digest": declaration_unit_digest(
                mode, [{"id": "file", "destination": destination}], []
            ),
            "accepted_upstream_digest": unit_digest([("file", upstream)]),
            "members": [{
                "id": "file",
                "destination": destination,
                "accepted_upstream_digest": upstream,
                "accepted_destination_digest": member_file(
                    greeting_destination if unit_id == "greeting" else note_destination
                ),
            }],
        })
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(review),
        "accepted_snapshot_digest": snapshot_digest(declaration, review, rows),
        "units": rows,
    }


def opencode_assertions() -> list[AssertionSpec]:
    return [{"id": "sudo-deny", "contains": '"sudo *": "deny"'}]


def gitignore_assertions() -> list[AssertionSpec]:
    return [{"id": "output-ignored", "contains": "output/"}]


def assertion_lock_document(
    accepted: str,
    opencode_present: bool = True,
    gitignore_present: bool = True,
    catalog: str = ASSERTION_CATALOG,
    declaration: str = ASSERTION_DECLARATION,
    review: str = EMPTY_REVIEW,
) -> LockDocument:
    values = (
        ("opencode-config", "opencode.jsonc", "sudo-deny", opencode_assertions(), opencode_present),
        ("gitignore-config", ".gitignore", "output-ignored", gitignore_assertions(), gitignore_present),
    )
    rows: list[LockUnitRow] = []
    unit_digest = declaration_unit_digest("mirror", [], [])
    for unit_id, destination, assertion_id, assertions, present in values:
        list_digest = assertion_list_digest(assertions)
        status_digest = assertion_status_digest([(assertion_id, present)])
        rows.append({
            "id": unit_id,
            "mode": "mirror",
            "declaration_unit_digest": unit_digest,
            "accepted_upstream_digest": list_digest,
            "members": [{
                "id": "assertions",
                "destination": destination,
                "accepted_upstream_digest": list_digest,
                "accepted_destination_digest": status_digest,
            }],
        })
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(review),
        "accepted_snapshot_digest": snapshot_digest(declaration, review, rows),
        "units": rows,
    }


def guarded_root_lock_document(
    accepted: str,
    destination_root: str,
    catalog: str = GUARDED_ROOT_CATALOG,
    declaration: str = GUARDED_ROOT_DECLARATION,
    review: str = EMPTY_REVIEW,
    upstream_root: str = UPSTREAM_ROOT,
) -> LockDocument:
    upstream_member = member_file(upstream_root)
    destination_member = member_file(destination_root)
    rows: list[LockUnitRow] = [{
        "id": "root-runtime-spec",
        "mode": "adapted",
        "declaration_unit_digest": declaration_unit_digest(
            "adapted", [{"id": "root", "destination": "AGENTS.md"}], []
        ),
        "accepted_upstream_digest": unit_digest([("root", upstream_member)]),
        "members": [{
            "id": "root",
            "destination": "AGENTS.md",
            "accepted_upstream_digest": upstream_member,
            "accepted_destination_digest": destination_member,
        }],
    }]
    return {
        "schema_version": 2,
        "upstream_repository": UPSTREAM_ID,
        "accepted_source_commit": accepted,
        "accepted_catalog_digest": sha256_text(catalog),
        "declaration_digest": sha256_text(declaration),
        "review_digest": sha256_text(review),
        "accepted_snapshot_digest": snapshot_digest(declaration, review, rows),
        "units": rows,
    }
