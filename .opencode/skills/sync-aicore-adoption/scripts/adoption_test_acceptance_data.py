"""Mixed-mode and runtime-lineage acceptance payloads.

This module is the single owner of the ``MIXED_*`` payload family, its large
review (transition-adjacent) descriptors, and the complete runtime-lineage
reconciliation cases. Consumers import the constants from here directly; digest
and commit helpers stay in logic modules, never as data constants.

The runtime-lineage cases exist so an independent model review can read every
complete previous-core / target-core / destination-before / result set and
judge ancestor attribution, preservation of the destination's existing local
rule, and the recorded local-version rationale under ``AGENTS.md:75``. Python
only stores and binds these bytes; no test module classifies the meaning of a
result or the correctness of a bump.
"""

from __future__ import annotations

from typing import TypedDict

# ---------------------------------------------------------------------------
# Protected two-section fixtures (G2)
# ---------------------------------------------------------------------------
#
# ``PROTECTED_MANDATORY_CORE`` is copied byte-for-byte into every source and
# destination protected fixture, so a candidate converges while its technical
# framing and Project extensions stay destination-specific. Tests bind these
# bytes; no test classifies their meaning.

PROTECTED_MANDATORY_CORE = """## Mandatory core

MANDATORY_CORE_V1

### Hard Rules
- Never weaken the mandatory core.
"""

PROTECTED_ROOT_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: guarded_file
    destination_policy: adopter_root_rules
    rule_documents:
      - AGENTS.md
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
"""

PROTECTED_ROOT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: root-runtime-spec
    mode: adapted
    members:
      - { id: root, destination: AGENTS.md }
"""

PROTECTED_SOURCE_ROOT = (
    "# Core Runtime\n"
    "> **Spec version:** 3.0.0\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Core-owned environment preferences.\n"
    "\n"
) + PROTECTED_MANDATORY_CORE

PROTECTED_DESTINATION_ROOT = (
    "# Relay Runtime\n"
    "> **Project identity:** Relay\n"
    "> **Spec version:** 3.0.0\n"
    "> **Local version:** 1.0.0\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Destination-local extension rules.\n"
    "\n"
) + PROTECTED_MANDATORY_CORE

PROTECTED_AGENT_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: reviewer-agent
    kind: agent
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    rule_documents:
      - .opencode/agents/reviewer.md
    members:
      - { id: spec, source: .opencode/agents/reviewer.md, destination: .opencode/agents/reviewer.md }
      - { id: profile, source: agents/reviewer/profile.md, destination: agents/reviewer/profile.md }
"""

PROTECTED_AGENT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: reviewer-agent
    mode: adapted
    members:
      - { id: spec, destination: .opencode/agents/reviewer.md }
      - { id: profile, destination: agents/reviewer/profile.md }
"""

PROTECTED_AGENT_MIRROR_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: reviewer-agent
    mode: mirror
    members:
      - { id: spec, destination: .opencode/agents/reviewer.md }
      - { id: profile, destination: agents/reviewer/profile.md }
"""

PROTECTED_AGENT_MANDATORY = """## Mandatory core

MANDATORY_AGENT_CORE

### Hard Rules
- Never edit source.
"""

PROTECTED_SOURCE_AGENT = (
    "---\n"
    "name: reviewer\n"
    "description: Reviews changes.\n"
    "mode: subagent\n"
    "version: 1.0.0\n"
    "---\n"
    "\n"
    "# Reviewer\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "**Persona / personality:** see `agents/reviewer/profile.md` "
    "(source of truth — do not duplicate here).\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Source extension note.\n"
    "\n"
) + PROTECTED_AGENT_MANDATORY

PROTECTED_DESTINATION_AGENT = (
    "---\n"
    "name: reviewer\n"
    "description: Reviews changes.\n"
    "mode: subagent\n"
    "version: 1.0.0\n"
    "---\n"
    "\n"
    "# Reviewer — Destination\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "**Persona / personality:** see `agents/reviewer/profile.md` "
    "(source of truth — do not duplicate here).\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Destination extension note.\n"
    "\n"
) + PROTECTED_AGENT_MANDATORY

PROTECTED_AGENT_PROFILE = "Reviewer persona profile.\n"

MIXED_CATALOG = """schema_version: 2
catalog:
  version: 2.4.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: rulebook
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: rules, source: skills/rules.md, destination: skills/rules.md }
  - id: helper-agent
    kind: agent
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: cv, source: agents/helper/profile.md, destination: agents/helper/profile.md }
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: guarded_file
    destination_policy: adopter_root_runtime
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
  - id: portable-stories-always
    kind: user-story
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: alpha, source: user-stories/alpha.md, destination: user-stories/alpha.md, collision_policy: core_wins }
  - id: portable-stories-ticket
    kind: user-story
    applicability: { requires: [ticket_system] }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: gamma, source: user-stories/gamma.md, destination: user-stories/gamma.md, collision_policy: core_wins }
"""
MIXED_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: true, python_scripts: true, ticket_system: false }
units:
  - id: rulebook
    mode: adapted
    members:
      - { id: rules, destination: skills/rules.md }
  - id: helper-agent
    mode: replacement
    replacement_members:
      - { id: helper-local, destination: agents/helper/profile.md, projection: file }
  - id: root-runtime-spec
    mode: adapted
    members:
      - { id: root, destination: AGENTS.md }
  - id: portable-stories-always
    mode: mirror
    members:
      - { id: alpha, destination: user-stories/alpha.md }
  - id: portable-stories-ticket
    mode: not_applicable
"""
MIXED_REVIEW = """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: root-runtime-spec
    decision: applied
    evidence: "Destination root runtime reviewed with destination-only identity."
    reviewer: test-suite
"""
MIXED_REVIEW_RULEBOOK = MIXED_REVIEW + """  - unit: rulebook
    decision: applied
    evidence: "Destination rulebook adaptation reviewed against the upstream rewrite."
    reviewer: test-suite
"""
MIXED_REVIEW_ALL = MIXED_REVIEW_RULEBOOK + """  - unit: helper-agent
    decision: applied
    evidence: "Destination replacement agent reviewed against the upstream helper."
    reviewer: test-suite
"""
MIXED_CORE_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha | active | ep-a | `a` |
| `gamma` | Gamma | active | ep-g | `g` |
| `aicore-only` | AICore only | active | ep-core | `core` |

## Appendices

Core appendix notes.
"""
MIXED_DESTINATION_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha | active | ep-a | `a` |
| `dest-own` | Destination owned | active | local | `d` |

## Destination notes

Local trailing section that must survive byte-for-byte.
"""
UPSTREAM_MIXED_ROOT = """# Upstream runtime spec
> **Spec version:** 2.4.0

Upstream agent rules.
"""
ADAPTED_RULEBOOK = "destination-adapted rulebook\n"
REPLACEMENT_AGENT = "destination replacement agent bytes\n"

# ---------------------------------------------------------------------------
# Runtime-lineage reconciliation cases (G5)
# ---------------------------------------------------------------------------
#
# Each case carries a complete previous-core, target-core, destination-before
# and reconciled-result document plus its recorded review reasoning. The local
# business rule exists in ``destination_before`` and survives reconciliation in
# every valid case. Python binds these bytes; the independent model review reads
# every version and judges incorporation/override and the bump rationale. The
# ``intended_verdict``/``intent`` fields are case metadata for that review, not
# an assertion any test performs.

RELAY_PREVIOUS_CORE = """# AICore runtime
> **Spec version:** 2.1.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
"""

RELAY_TARGET_CORE = """# AICore runtime
> **Spec version:** 2.2.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.
"""

RELAY_DESTINATION_BEFORE = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.1.0
> **Local version:** 1.4.2

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
"""

RELAY_RESULT_UPSTREAM_ONLY = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.2.0
> **Local version:** 1.4.2

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
"""

RELAY_REVIEW_UPSTREAM_ONLY = (
    "Incorporated CORE_RULE_TWO from the target core and retained the existing "
    "destination LOCAL_BUSINESS_RULE; the change is upstream-only, so the "
    "destination Local version stays at its non-initial 1.4.2 value."
)

RELAY_RESULT_NEW_ENFORCEMENT = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.2.0
> **Local version:** 1.5.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
- LOCAL_ENFORCEMENT_RULE: Relay production deploys require a two-person review.
"""

RELAY_REVIEW_NEW_ENFORCEMENT = (
    "Incorporated CORE_RULE_TWO and added the destination-local enforceable "
    "LOCAL_ENFORCEMENT_RULE while retaining LOCAL_BUSINESS_RULE; AGENTS.md:75 "
    "gives a new local enforceable rule a minor bump, so the destination Local "
    "version advances 1.4.2 -> 1.5.0."
)

RELAY_DERIVED_PREVIOUS_CORE = """---
name: derived-runtime
---

# AICore derived runtime
> **Spec version:** 2.1.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
"""

RELAY_DERIVED_TARGET_CORE = """---
name: derived-runtime
---

# AICore derived runtime
> **Spec version:** 2.2.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.
"""

RELAY_DERIVED_DESTINATION_BEFORE = """---
name: derived-runtime
local-version: 1.4.2
---

# Relay derived runtime
> **Project identity:** Relay
> **Spec version:** 2.1.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
"""

RELAY_DERIVED_RESULT_UPSTREAM_ONLY = """---
name: derived-runtime
local-version: 1.4.2
---

# Relay derived runtime
> **Project identity:** Relay
> **Spec version:** 2.2.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
"""

RELAY_REVIEW_DERIVED_UPSTREAM_ONLY = (
    "Derived-runtime frontmatter keeps the destination local-version 1.4.2 for "
    "an upstream-only sync while the copied spec version advances to the target "
    "2.2.0 and both the incorporated core rule and the local business rule stay."
)

# Invalid examples: complete payloads the independent model review must reject
# with a case-specific reason. No test classifies them.
RELAY_RESULT_WRONG_ANCESTOR = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.1.0
> **Local version:** 1.4.2

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
"""

RELAY_REVIEW_WRONG_ANCESTOR = (
    "Incorporated CORE_RULE_TWO and retained LOCAL_BUSINESS_RULE, but the "
    "destination spec version was left at the previous core 2.1.0 while the "
    "target core advanced to 2.2.0."
)

RELAY_RESULT_LOCAL_RESET = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.2.0
> **Local version:** 1.0.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
"""

RELAY_REVIEW_LOCAL_RESET = (
    "Incorporated CORE_RULE_TWO and retained LOCAL_BUSINESS_RULE, but reset the "
    "destination Local version to 1.0.0 from its existing 1.4.2 value."
)

RELAY_RESULT_MISSING_RATIONALE = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.2.0
> **Local version:** 1.5.0

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
- LOCAL_ENFORCEMENT_RULE: Relay production deploys require a two-person review.
"""

RELAY_REVIEW_MISSING_RATIONALE = "Runtime updated."

RELAY_RESULT_CONTRADICTORY_BUMP = """# Relay project runtime
> **Project identity:** Relay
> **Spec version:** 2.2.0
> **Local version:** 1.4.3

## Core requirements

- CORE_RULE_ONE: Record every adopted unit at one accepted revision.
- CORE_RULE_TWO: Reconcile every adapted unit against the destination business rule.

## Local rules

- LOCAL_BUSINESS_RULE: Relay billing approval requires finance sign-off.
- LOCAL_ENFORCEMENT_RULE: Relay production deploys require a two-person review.
"""

RELAY_REVIEW_CONTRADICTORY_BUMP = (
    "Added the destination-local enforceable LOCAL_ENFORCEMENT_RULE; recorded a "
    "patch bump 1.4.2 -> 1.4.3 despite the new enforceable rule."
)


class RuntimeLineageCase(TypedDict):
    """One complete runtime reconciliation case for independent model review."""

    case_id: str
    unit: str
    previous_core: str
    target_core: str
    destination_before: str
    result: str
    ancestor_before: str
    ancestor_after: str
    local_version_before: str
    local_version_after: str
    review_reasoning: str
    intended_verdict: str
    intent: str


RUNTIME_LINEAGE_CASES: tuple[RuntimeLineageCase, ...] = (
    {
        "case_id": "lineage-root-upstream-only",
        "unit": "root-runtime-spec",
        "previous_core": RELAY_PREVIOUS_CORE,
        "target_core": RELAY_TARGET_CORE,
        "destination_before": RELAY_DESTINATION_BEFORE,
        "result": RELAY_RESULT_UPSTREAM_ONLY,
        "ancestor_before": "2.1.0",
        "ancestor_after": "2.2.0",
        "local_version_before": "1.4.2",
        "local_version_after": "1.4.2",
        "review_reasoning": RELAY_REVIEW_UPSTREAM_ONLY,
        "intended_verdict": "pass",
        "intent": (
            "Root upstream-only sync: adopt target ancestor 2.2.0, preserve the "
            "non-initial Local version 1.4.2, incorporate CORE_RULE_TWO and keep "
            "the existing LOCAL_BUSINESS_RULE."
        ),
    },
    {
        "case_id": "lineage-root-new-enforceable-rule",
        "unit": "root-runtime-spec",
        "previous_core": RELAY_PREVIOUS_CORE,
        "target_core": RELAY_TARGET_CORE,
        "destination_before": RELAY_DESTINATION_BEFORE,
        "result": RELAY_RESULT_NEW_ENFORCEMENT,
        "ancestor_before": "2.1.0",
        "ancestor_after": "2.2.0",
        "local_version_before": "1.4.2",
        "local_version_after": "1.5.0",
        "review_reasoning": RELAY_REVIEW_NEW_ENFORCEMENT,
        "intended_verdict": "pass",
        "intent": (
            "A new destination-local enforceable rule takes a minor bump under "
            "AGENTS.md:75 (1.4.2 -> 1.5.0) while the target ancestor is adopted "
            "and the existing local business rule survives."
        ),
    },
    {
        "case_id": "lineage-derived-upstream-only",
        "unit": "root-runtime-spec",
        "previous_core": RELAY_DERIVED_PREVIOUS_CORE,
        "target_core": RELAY_DERIVED_TARGET_CORE,
        "destination_before": RELAY_DERIVED_DESTINATION_BEFORE,
        "result": RELAY_DERIVED_RESULT_UPSTREAM_ONLY,
        "ancestor_before": "2.1.0",
        "ancestor_after": "2.2.0",
        "local_version_before": "1.4.2",
        "local_version_after": "1.4.2",
        "review_reasoning": RELAY_REVIEW_DERIVED_UPSTREAM_ONLY,
        "intended_verdict": "pass",
        "intent": (
            "Derived runtime upstream-only sync: frontmatter local-version 1.4.2 "
            "is preserved, the copied Spec version advances to 2.2.0, and the "
            "existing local rule survives."
        ),
    },
    {
        "case_id": "lineage-invalid-wrong-ancestor",
        "unit": "root-runtime-spec",
        "previous_core": RELAY_PREVIOUS_CORE,
        "target_core": RELAY_TARGET_CORE,
        "destination_before": RELAY_DESTINATION_BEFORE,
        "result": RELAY_RESULT_WRONG_ANCESTOR,
        "ancestor_before": "2.1.0",
        "ancestor_after": "2.1.0",
        "local_version_before": "1.4.2",
        "local_version_after": "1.4.2",
        "review_reasoning": RELAY_REVIEW_WRONG_ANCESTOR,
        "intended_verdict": "block",
        "intent": "Wrong ancestor: the result never adopts the target 2.2.0 core.",
    },
    {
        "case_id": "lineage-invalid-local-reset",
        "unit": "root-runtime-spec",
        "previous_core": RELAY_PREVIOUS_CORE,
        "target_core": RELAY_TARGET_CORE,
        "destination_before": RELAY_DESTINATION_BEFORE,
        "result": RELAY_RESULT_LOCAL_RESET,
        "ancestor_before": "2.1.0",
        "ancestor_after": "2.2.0",
        "local_version_before": "1.4.2",
        "local_version_after": "1.0.0",
        "review_reasoning": RELAY_REVIEW_LOCAL_RESET,
        "intended_verdict": "block",
        "intent": (
            "Local reset: an upstream-only sync resets the destination Local "
            "version to 1.0.0 instead of preserving the non-initial 1.4.2."
        ),
    },
    {
        "case_id": "lineage-invalid-missing-rationale",
        "unit": "root-runtime-spec",
        "previous_core": RELAY_PREVIOUS_CORE,
        "target_core": RELAY_TARGET_CORE,
        "destination_before": RELAY_DESTINATION_BEFORE,
        "result": RELAY_RESULT_MISSING_RATIONALE,
        "ancestor_before": "2.1.0",
        "ancestor_after": "2.2.0",
        "local_version_before": "1.4.2",
        "local_version_after": "1.5.0",
        "review_reasoning": RELAY_REVIEW_MISSING_RATIONALE,
        "intended_verdict": "block",
        "intent": (
            "Missing rationale: the minor bump has no case-specific reasoning "
            "for the new enforceable rule."
        ),
    },
    {
        "case_id": "lineage-invalid-contradictory-bump",
        "unit": "root-runtime-spec",
        "previous_core": RELAY_PREVIOUS_CORE,
        "target_core": RELAY_TARGET_CORE,
        "destination_before": RELAY_DESTINATION_BEFORE,
        "result": RELAY_RESULT_CONTRADICTORY_BUMP,
        "ancestor_before": "2.1.0",
        "ancestor_after": "2.2.0",
        "local_version_before": "1.4.2",
        "local_version_after": "1.4.3",
        "review_reasoning": RELAY_REVIEW_CONTRADICTORY_BUMP,
        "intended_verdict": "block",
        "intent": (
            "Contradictory bump: a new local enforceable rule takes a patch bump "
            "although AGENTS.md:75 requires a minor bump."
        ),
    },
)


# ---------------------------------------------------------------------------
# Protected collision/notice prepared cases (G3/G4/G5)
# ---------------------------------------------------------------------------
#
# Each case carries every complete previous-source, target-source,
# destination-before, and result surface plus the recorded review notice.
# Python stores these bytes and the engine binds them. No test classifies the
# notice. ``intended_verdict`` and ``intent`` are labels for the independent
# model review only; acceptance tests must not read them as a verdict.
#
# The incoming mandatory sentence is "Every change requires recorded review
# before merge." A compatible preference is unrelated and stays byte-for-byte.
# A pre-existing local exception, "Low-risk changes may merge without review.",
# is corrected so the result no longer authorizes that exception.


class NoticeSurface(TypedDict):
    """One complete previous/target/before/result document for a case path."""

    path: str
    previous_source: str
    target_source: str
    destination_before: str
    result: str


class RuleNoticeCase(TypedDict):
    """One complete protected collision case for independent model review."""

    case_id: str
    unit: str
    catalog: str
    declaration: str
    decision: str
    verified_layout: bool
    omit_paths: tuple[str, ...]
    surfaces: tuple[NoticeSurface, ...]
    review_notice: str
    intended_verdict: str
    intent: str


def _sectioned_document(
    title: str,
    extensions: str,
    mandatory: str,
    *,
    spec: str | None = None,
    identity: str | None = None,
    local_version: str | None = None,
) -> str:
    """Assemble one two-section fixture document from exact section bytes."""
    lines = [f"# {title}"]
    if identity is not None:
        lines.append(f"> **Project identity:** {identity}")
    if spec is not None:
        lines.append(f"> **Spec version:** {spec}")
    if local_version is not None:
        lines.append(f"> **Local version:** {local_version}")
    lines.append("> **Rule layout:** two-section-v1")
    lines.append("")
    mandatory_body = mandatory if mandatory.endswith("\n") else mandatory + "\n"
    return (
        "\n".join(lines)
        + "\n## Project extensions\n\n"
        + extensions.rstrip("\n")
        + "\n\n"
        + mandatory_body
    )


NOTICE_MANDATORY_SENTENCE = "Every change requires recorded review before merge."
NOTICE_EXCEPTION_BEFORE = "Low-risk changes may merge without review."
NOTICE_EXCEPTION_AFTER = "Low-risk changes require recorded review before merge."
NOTICE_PREFERENCE_SENTENCE = "Relay release notes use the project name Relay."
NOTICE_SOURCE_FAST_TRACK_EXTENSION = (
    "Core fast-track notes are not destination rules."
)
NOTICE_SOURCE_ROOT_EXTENSION = "Core-owned preferences."
NOTICE_MANDATORY_PREVIOUS = (
    "## Mandatory core\n\n"
    "Every reconciliation is reported at one accepted revision.\n"
)
NOTICE_MANDATORY_TARGET = (
    "## Mandatory core\n\n"
    "Every reconciliation is reported at one accepted revision.\n"
    f"{NOTICE_MANDATORY_SENTENCE}\n"
)
NOTICE_MANDATORY_DIVERGED = (
    "## Mandatory core\n\n"
    "Every reconciliation is reported at one accepted revision.\n"
    f"{NOTICE_EXCEPTION_BEFORE}\n"
)
NOTICE_POLICY_BASELINE_SENTENCE = (
    "Fast-track notes do not waive a recorded review requirement."
)
NOTICE_POLICY_MANDATORY = (
    "## Mandatory core\n\n"
    f"{NOTICE_POLICY_BASELINE_SENTENCE}\n"
)
NOTICE_COMPATIBLE_EXTENSIONS = f"{NOTICE_PREFERENCE_SENTENCE}\n"
NOTICE_CONTRADICTION_EXTENSIONS_BEFORE = (
    f"{NOTICE_PREFERENCE_SENTENCE}\n{NOTICE_EXCEPTION_BEFORE}\n"
)
NOTICE_CONTRADICTION_EXTENSIONS_AFTER = (
    f"{NOTICE_PREFERENCE_SENTENCE}\n{NOTICE_EXCEPTION_AFTER}\n"
)

NOTICE_PREVIOUS_ROOT = _sectioned_document(
    "Core Runtime",
    NOTICE_SOURCE_ROOT_EXTENSION,
    NOTICE_MANDATORY_PREVIOUS,
    spec="3.0.0",
)
NOTICE_TARGET_ROOT = _sectioned_document(
    "Core Runtime",
    NOTICE_SOURCE_ROOT_EXTENSION,
    NOTICE_MANDATORY_TARGET,
    spec="3.1.0",
)
NOTICE_COMPATIBLE_BEFORE = _sectioned_document(
    "Relay Runtime",
    NOTICE_COMPATIBLE_EXTENSIONS,
    NOTICE_MANDATORY_PREVIOUS,
    spec="3.0.0",
    identity="Relay",
    local_version="1.2.0",
)
NOTICE_COMPATIBLE_RESULT = _sectioned_document(
    "Relay Runtime",
    NOTICE_COMPATIBLE_EXTENSIONS,
    NOTICE_MANDATORY_TARGET,
    spec="3.1.0",
    identity="Relay",
    local_version="1.2.0",
)
NOTICE_CONTRADICTION_BEFORE = _sectioned_document(
    "Relay Runtime",
    NOTICE_CONTRADICTION_EXTENSIONS_BEFORE,
    NOTICE_MANDATORY_PREVIOUS,
    spec="3.0.0",
    identity="Relay",
    local_version="1.2.0",
)
NOTICE_CONTRADICTION_RESULT = _sectioned_document(
    "Relay Runtime",
    NOTICE_CONTRADICTION_EXTENSIONS_AFTER,
    NOTICE_MANDATORY_TARGET,
    spec="3.1.0",
    identity="Relay",
    local_version="2.0.0",
)
NOTICE_CONTRADICTION_RESULT_INVALID_PATCH = _sectioned_document(
    "Relay Runtime",
    NOTICE_CONTRADICTION_EXTENSIONS_AFTER,
    NOTICE_MANDATORY_TARGET,
    spec="3.1.0",
    identity="Relay",
    local_version="1.2.1",
)
NOTICE_DIVERGED_RESULT = _sectioned_document(
    "Relay Runtime",
    NOTICE_COMPATIBLE_EXTENSIONS,
    NOTICE_MANDATORY_DIVERGED,
    spec="3.1.0",
    identity="Relay",
    local_version="1.2.0",
)
NOTICE_POLICY_SOURCE = _sectioned_document(
    "Core fast-track policy",
    NOTICE_SOURCE_FAST_TRACK_EXTENSION,
    NOTICE_POLICY_MANDATORY,
)
NOTICE_POLICY_BEFORE = _sectioned_document(
    "Relay fast-track policy",
    NOTICE_EXCEPTION_BEFORE,
    NOTICE_POLICY_MANDATORY,
)
NOTICE_POLICY_RESULT = _sectioned_document(
    "Relay fast-track policy",
    NOTICE_EXCEPTION_AFTER,
    NOTICE_POLICY_MANDATORY,
)
NOTICE_CROSS_FILE_ROOT_BEFORE = _sectioned_document(
    "Relay Runtime",
    NOTICE_COMPATIBLE_EXTENSIONS,
    NOTICE_MANDATORY_PREVIOUS,
    spec="3.0.0",
    identity="Relay",
    local_version="1.2.0",
)
NOTICE_CROSS_FILE_ROOT_RESULT = _sectioned_document(
    "Relay Runtime",
    NOTICE_COMPATIBLE_EXTENSIONS,
    NOTICE_MANDATORY_TARGET,
    spec="3.1.0",
    identity="Relay",
    local_version="1.2.0",
)
NOTICE_CROSS_FILE_ROOT_RESULT_INVALID_BUMP = _sectioned_document(
    "Relay Runtime",
    NOTICE_COMPATIBLE_EXTENSIONS,
    NOTICE_MANDATORY_TARGET,
    spec="3.1.0",
    identity="Relay",
    local_version="1.2.1",
)

NOTICE_CROSS_FILE_CATALOG = """schema_version: 2
catalog:
  version: 2.5.1
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: file
    rule_documents:
      - AGENTS.md
      - policies/fast-track.md
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
      - { id: fast-track, source: policies/fast-track.md, destination: policies/fast-track.md }
"""

NOTICE_CROSS_FILE_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: root-runtime-spec
    mode: adapted
    members:
      - { id: root, destination: AGENTS.md }
      - { id: fast-track, destination: policies/fast-track.md }
"""

NOTICE_REVIEW_COMPATIBLE = (
    f'Target AGENTS.md adds the mandatory sentence "{NOTICE_MANDATORY_SENTENCE}" '
    f'The destination preference "{NOTICE_PREFERENCE_SENTENCE}" is unrelated and '
    "is preserved byte-for-byte. The sentences do not conflict. Local version "
    "stays 1.2.0 because no destination-local rule changed."
)
NOTICE_REVIEW_CONTRADICTION = (
    f'AGENTS.md mandatory core says "{NOTICE_MANDATORY_SENTENCE}" The '
    f'pre-existing destination extension said "{NOTICE_EXCEPTION_BEFORE}" Those '
    "sentences conflict. The mandatory sentence wins. The prepared AGENTS.md "
    f'replaces the local sentence with "{NOTICE_EXCEPTION_AFTER}" so the file '
    "no longer authorizes merge without review. The unrelated preference "
    f'"{NOTICE_PREFERENCE_SENTENCE}" is unchanged byte-for-byte. Withdrawing '
    "the local authorization to merge without review is an incompatible local "
    "authority change. The AGENTS.md local-version clause gives an incompatible "
    "local authority change a major bump, so Local version advances from "
    "1.2.0 to 2.0.0. This is not a compatible patch."
)
NOTICE_REVIEW_CONTRADICTION_INVALID_PATCH = (
    f'AGENTS.md mandatory core says "{NOTICE_MANDATORY_SENTENCE}" The '
    f'pre-existing destination extension said "{NOTICE_EXCEPTION_BEFORE}" Those '
    "sentences conflict. The mandatory sentence wins. The prepared AGENTS.md "
    f'replaces the local sentence with "{NOTICE_EXCEPTION_AFTER}" so the file '
    "no longer authorizes merge without review. The unrelated preference "
    f'"{NOTICE_PREFERENCE_SENTENCE}" is unchanged byte-for-byte. Local version '
    "advances from 1.2.0 to 1.2.1 because correcting that destination exception "
    "is a compatible correction of a local rule, not a new capability."
)
NOTICE_REVIEW_CROSS_FILE = (
    f'AGENTS.md mandatory core says "{NOTICE_MANDATORY_SENTENCE}" '
    "policies/fast-track.md project extensions said "
    f'"{NOTICE_EXCEPTION_BEFORE}" Those sentences conflict. The mandatory '
    "sentence in AGENTS.md wins. The prepared policies/fast-track.md replaces "
    f'that sentence with "{NOTICE_EXCEPTION_AFTER}" The root preference '
    f'"{NOTICE_PREFERENCE_SENTENCE}" is unchanged byte-for-byte. '
    f'The policy mandatory core already said "{NOTICE_POLICY_BASELINE_SENTENCE}" '
    "before this synchronization, so the local exception already contradicted "
    "that policy sentence. This synchronization did not first create that "
    "policy-file conflict. The incoming root sentence is a separate "
    "contradiction and is the winner cited above. policies/fast-track.md has "
    "no Local version marker. The AGENTS.md local-version clause applies to "
    "the destination root runtime and derived agent specs, not to an "
    "unversioned policy file, so the root Local version stays 1.2.0. The "
    "policy edit is not transferred onto the root version, and no version "
    "marker is added to policies/fast-track.md."
)
NOTICE_REVIEW_CROSS_FILE_INVALID_ROOT_BUMP = (
    f'AGENTS.md mandatory core says "{NOTICE_MANDATORY_SENTENCE}" '
    "policies/fast-track.md project extensions said "
    f'"{NOTICE_EXCEPTION_BEFORE}" Those sentences conflict. The mandatory '
    "sentence in AGENTS.md wins. The prepared policies/fast-track.md replaces "
    f'that sentence with "{NOTICE_EXCEPTION_AFTER}" The root preference '
    f'"{NOTICE_PREFERENCE_SENTENCE}" is unchanged byte-for-byte. Local version '
    "advances from 1.2.0 to 1.2.1 because correcting the destination exception "
    "in policies/fast-track.md is a compatible correction of a local rule."
)
NOTICE_REVIEW_SEMANTIC_OMISSION = (
    "Complete cross-file review of every affected rule surface.\n"
    "Root before:\n"
    f"{NOTICE_CROSS_FILE_ROOT_BEFORE}"
    "Root result:\n"
    f"{NOTICE_CROSS_FILE_ROOT_RESULT}"
    "The review attestation is complete."
)
NOTICE_REVIEW_DECLINED = (
    "The prepared AGENTS.md mandatory core contains "
    f'"{NOTICE_EXCEPTION_BEFORE}" while the target mandatory core says '
    f'"{NOTICE_MANDATORY_SENTENCE}" The recorded decision is declined. A '
    "declined decision cannot authorize that mandatory-byte divergence."
)
NOTICE_REVIEW_COUNTERFEIT = (
    "The review records applied verified_layout while the prepared AGENTS.md "
    f'mandatory core contains "{NOTICE_EXCEPTION_BEFORE}" instead of the target '
    f'sentence "{NOTICE_MANDATORY_SENTENCE}" The attestation does not authorize '
    "that divergence."
)
NOTICE_REVIEW_MISSING_FILE = (
    "policies/fast-track.md is an affected destination rule surface whose "
    f'before text says "{NOTICE_EXCEPTION_BEFORE}" A snapshot that omits '
    "policies/fast-track.md is missing the affected file and cannot be accepted."
)


def _root_surface(before: str, result: str) -> NoticeSurface:
    return {
        "path": "AGENTS.md",
        "previous_source": NOTICE_PREVIOUS_ROOT,
        "target_source": NOTICE_TARGET_ROOT,
        "destination_before": before,
        "result": result,
    }


def _policy_surface(before: str, result: str) -> NoticeSurface:
    return {
        "path": "policies/fast-track.md",
        "previous_source": NOTICE_POLICY_SOURCE,
        "target_source": NOTICE_POLICY_SOURCE,
        "destination_before": before,
        "result": result,
    }


RULE_NOTICE_ACCEPT_CASES: tuple[RuleNoticeCase, ...] = (
    {
        "case_id": "notice-compatible-extension",
        "unit": "root-runtime-spec",
        "catalog": PROTECTED_ROOT_CATALOG,
        "declaration": PROTECTED_ROOT_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": (),
        "surfaces": (_root_surface(NOTICE_COMPATIBLE_BEFORE, NOTICE_COMPATIBLE_RESULT),),
        "review_notice": NOTICE_REVIEW_COMPATIBLE,
        "intended_verdict": "pass",
        "intent": (
            "The incoming review-before-merge requirement does not conflict "
            "with the unrelated release-note preference, which stays byte-for-byte."
        ),
    },
    {
        "case_id": "notice-contradicted-exception",
        "unit": "root-runtime-spec",
        "catalog": PROTECTED_ROOT_CATALOG,
        "declaration": PROTECTED_ROOT_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": (),
        "surfaces": (
            _root_surface(NOTICE_CONTRADICTION_BEFORE, NOTICE_CONTRADICTION_RESULT),
        ),
        "review_notice": NOTICE_REVIEW_CONTRADICTION,
        "intended_verdict": "pass",
        "intent": (
            "The incoming mandatory review sentence contradicts the pre-existing "
            "unchanged merge-without-review exception. The result removes that "
            "authorization, keeps the unrelated preference, and records the "
            "local-version bump rationale."
        ),
    },
    {
        "case_id": "notice-cross-file-collision",
        "unit": "root-runtime-spec",
        "catalog": NOTICE_CROSS_FILE_CATALOG,
        "declaration": NOTICE_CROSS_FILE_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": (),
        "surfaces": (
            _root_surface(
                NOTICE_CROSS_FILE_ROOT_BEFORE, NOTICE_CROSS_FILE_ROOT_RESULT
            ),
            _policy_surface(NOTICE_POLICY_BEFORE, NOTICE_POLICY_RESULT),
        ),
        "review_notice": NOTICE_REVIEW_CROSS_FILE,
        "intended_verdict": "pass",
        "intent": (
            "The conflicting exception lives in policies/fast-track.md. The "
            "notice quotes both sentences, names both paths, states the "
            "mandatory winner, and states the concrete edit."
        ),
    },
)

RULE_NOTICE_REJECT_CASES: tuple[RuleNoticeCase, ...] = (
    {
        "case_id": "notice-core-divergence-declined",
        "unit": "root-runtime-spec",
        "catalog": PROTECTED_ROOT_CATALOG,
        "declaration": PROTECTED_ROOT_DECLARATION,
        "decision": "declined",
        "verified_layout": False,
        "omit_paths": (),
        "surfaces": (
            _root_surface(NOTICE_CONTRADICTION_BEFORE, NOTICE_DIVERGED_RESULT),
        ),
        "review_notice": NOTICE_REVIEW_DECLINED,
        "intended_verdict": "block",
        "intent": (
            "A declined decision cannot authorize mandatory-byte divergence."
        ),
    },
    {
        "case_id": "notice-counterfeit-attestation",
        "unit": "root-runtime-spec",
        "catalog": PROTECTED_ROOT_CATALOG,
        "declaration": PROTECTED_ROOT_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": (),
        "surfaces": (
            _root_surface(NOTICE_CONTRADICTION_BEFORE, NOTICE_DIVERGED_RESULT),
        ),
        "review_notice": NOTICE_REVIEW_COUNTERFEIT,
        "intended_verdict": "block",
        "intent": (
            "An applied verified_layout attestation cannot authorize mandatory "
            "bytes that differ from the target."
        ),
    },
    {
        "case_id": "notice-missing-affected-file",
        "unit": "root-runtime-spec",
        "catalog": NOTICE_CROSS_FILE_CATALOG,
        "declaration": NOTICE_CROSS_FILE_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": ("policies/fast-track.md",),
        "surfaces": (
            _root_surface(
                NOTICE_CROSS_FILE_ROOT_BEFORE, NOTICE_CROSS_FILE_ROOT_RESULT
            ),
            _policy_surface(NOTICE_POLICY_BEFORE, NOTICE_POLICY_RESULT),
        ),
        "review_notice": NOTICE_REVIEW_MISSING_FILE,
        "intended_verdict": "block",
        "intent": (
            "The affected policies/fast-track.md surface is complete in the "
            "case and absent from the reviewed snapshot, so acceptance rejects."
        ),
    },
)

RULE_NOTICE_CASES: tuple[RuleNoticeCase, ...] = (
    *RULE_NOTICE_ACCEPT_CASES,
    *RULE_NOTICE_REJECT_CASES,
)

# N04: the old 1.2.1 rationales are explicit invalid semantic variants. Tests
# may bind these bytes. They must not treat an engine round-trip as acceptance
# of the version class, and no Python code classifies the bump.
RULE_NOTICE_SEMANTIC_BLOCK_CASES: tuple[RuleNoticeCase, ...] = (
    {
        "case_id": "notice-invalid-patch-rationale",
        "unit": "root-runtime-spec",
        "catalog": PROTECTED_ROOT_CATALOG,
        "declaration": PROTECTED_ROOT_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": (),
        "surfaces": (
            _root_surface(
                NOTICE_CONTRADICTION_BEFORE,
                NOTICE_CONTRADICTION_RESULT_INVALID_PATCH,
            ),
        ),
        "review_notice": NOTICE_REVIEW_CONTRADICTION_INVALID_PATCH,
        "intended_verdict": "block",
        "intent": (
            "Invalid semantic variant: the authorization withdrawal is recorded "
            "as a compatible patch 1.2.1 instead of an incompatible authority "
            "major. Python does not classify this version class."
        ),
    },
    {
        "case_id": "notice-invalid-root-bump",
        "unit": "root-runtime-spec",
        "catalog": NOTICE_CROSS_FILE_CATALOG,
        "declaration": NOTICE_CROSS_FILE_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": (),
        "surfaces": (
            _root_surface(
                NOTICE_CROSS_FILE_ROOT_BEFORE,
                NOTICE_CROSS_FILE_ROOT_RESULT_INVALID_BUMP,
            ),
            _policy_surface(NOTICE_POLICY_BEFORE, NOTICE_POLICY_RESULT),
        ),
        "review_notice": NOTICE_REVIEW_CROSS_FILE_INVALID_ROOT_BUMP,
        "intended_verdict": "block",
        "intent": (
            "Invalid semantic variant: an unversioned policy edit is transferred "
            "onto a root Local version bump to 1.2.1. Python does not classify "
            "this version class."
        ),
    },
)

# N07: mapped bytes and digests stay valid. The review payload omits the policy
# before/result. The engine may succeed; the model BLOCK is not an engine gate.
RULE_NOTICE_SEMANTIC_OMISSION_CASES: tuple[RuleNoticeCase, ...] = (
    {
        "case_id": "notice-semantic-omission",
        "unit": "root-runtime-spec",
        "catalog": NOTICE_CROSS_FILE_CATALOG,
        "declaration": NOTICE_CROSS_FILE_DECLARATION,
        "decision": "applied",
        "verified_layout": True,
        "omit_paths": (),
        "surfaces": (
            _root_surface(
                NOTICE_CROSS_FILE_ROOT_BEFORE, NOTICE_CROSS_FILE_ROOT_RESULT
            ),
            _policy_surface(NOTICE_POLICY_BEFORE, NOTICE_POLICY_RESULT),
        ),
        "review_notice": NOTICE_REVIEW_SEMANTIC_OMISSION,
        "intended_verdict": "block",
        "intent": (
            "Semantic-only omission: the review payload quotes the root "
            "documents and claims a complete cross-file review, but it omits "
            "the policy before/result. Record the engine outcome separately."
        ),
    },
)


# ---------------------------------------------------------------------------
# Hermetic bootstrap prepared results (G3)
# ---------------------------------------------------------------------------
#
# Fresh enrollment creates absent debt/problem registers from structural
# headers and does not copy source rows. An existing project keeps its
# register, preserve member, and manifest bytes. The symptom catalog text is
# retained in both. Production code gains no writer; tests prepare these
# bytes with ordinary file operations and the existing temp-repo helpers.

BOOTSTRAP_DEBT_HEADER = """# Accepted Debt Register

## Entry format

Each entry includes an ID, a date, and a deferral decision.

## Register
"""
BOOTSTRAP_PROBLEM_HEADER = """# Known Problem Pattern Register

## Entry format

One row per record. Source history is not an entry.

## Register
"""
BOOTSTRAP_SOURCE_DEBT = """# Accepted Debt Register

## Register

DEBT-001 source history row must not be copied.
"""
BOOTSTRAP_SOURCE_PROBLEMS = """# Known Problem Pattern Register

## Register

P-001 source history row must not be copied.
"""
BOOTSTRAP_EXISTING_DEBT = """# Accepted Debt Register

## Register

DEBT-014 Relay keeps this local deferral.
"""
BOOTSTRAP_EXISTING_PROBLEMS = """# Known Problem Pattern Register

## Register

P-014 Relay keeps this local problem row.
"""
BOOTSTRAP_SYMPTOMS = """# Diagnostic Symptom Catalog

SYMPTOM_CATALOG_TEXT: durable class S-01 stays in the destination catalog.
"""
BOOTSTRAP_SOURCE_GITKEEP = "source scaffold marker\n"
BOOTSTRAP_FRESH_GITKEEP = "\n"
BOOTSTRAP_EXISTING_GITKEEP = "local plan scaffold\n"
BOOTSTRAP_SOURCE_MANIFEST = """[project]
name = "core-upstream"
version = "2.5.1"
dependencies = ["core-history==9.9.9"]
"""
BOOTSTRAP_FRESH_MANIFEST_BEFORE = """[project]
name = "relay"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.relay]
notes = "destination"
"""
BOOTSTRAP_EXISTING_MANIFEST = """[project]
name = "relay"
version = "1.4.2"
requires-python = ">=3.11"
dependencies = ["owner-lib==1.2.3"]

[tool.relay]
notes = "local tool table"
"""
BOOTSTRAP_CONFLICT_MANIFEST = """[project]
name = "relay"
version = "1.4.2"
requires-python = ">=3.11"
dependencies = ["owner-lib==1.2.3", "PyYAML==6.0.2"]

[tool.relay]
notes = "local tool table"
"""
BOOTSTRAP_SKILL_REQUIREMENT = "PyYAML==6.0.3"
BOOTSTRAP_EXPECTED_FRESH_DEPENDENCIES: tuple[str, ...] = (BOOTSTRAP_SKILL_REQUIREMENT,)
BOOTSTRAP_EXPECTED_EXISTING_DEPENDENCIES: tuple[str, ...] = (
    "owner-lib==1.2.3",
    BOOTSTRAP_SKILL_REQUIREMENT,
)
BOOTSTRAP_SKILL = """---
name: enrolled-skill
metadata:
  dependencies:
    - PyYAML==6.0.3
---
Enrolled skill body. The dependency pin above is the prepared metadata.
"""
BOOTSTRAP_SKILL_NO_DEPENDENCIES = """---
name: enrolled-skill
metadata:
  dependencies: []
---
Enrolled skill body with an empty dependency list.
"""
BOOTSTRAP_ASSERTION_CONTAINS = '"sudo *": "deny"'
BOOTSTRAP_FRESH_CONFIG = """{
  "local": "fresh-custom",
  "permission": {"bash": {"sudo *": "deny"}}
}
"""
BOOTSTRAP_EXISTING_CONFIG_BEFORE = """{
  "local": "existing-custom"
}
"""
BOOTSTRAP_MIRROR_NOTE = """# Mirror note
> **Rule layout:** two-section-v1

## Project extensions

Mirror extension stays identical.

## Mandatory core

MIRROR_NOTE_MANDATORY
"""
BOOTSTRAP_STORY_FILE = "alpha v1\n"
BOOTSTRAP_SOURCE_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha | active | ep-a | `a` |

## Appendices

Core appendix notes.
"""
BOOTSTRAP_EXISTING_INDEX = """# User Stories

| Slug | Title | Status | Epic | Affected areas |
|---|---|---|---|---|
| `alpha` | Alpha local edit | active | ep-a | `a` |
| `relay-own` | Relay owned | active | local | `r` |

## Destination notes

Local trailing section that must survive byte-for-byte.
"""
BOOTSTRAP_LEGACY_MANDATORY = """## Mandatory core

LEGACY_MANDATORY_NOT_SOURCE
"""
BOOTSTRAP_LEGACY_ROOT = _sectioned_document(
    "Relay Runtime",
    "Destination-local extension rules.",
    BOOTSTRAP_LEGACY_MANDATORY,
    spec="2.0.0",
    identity="Relay",
    local_version="1.0.0",
)
BOOTSTRAP_AGENT_EXTENSION = "Relay reviewer notes for Relay.\n"
BOOTSTRAP_LEGACY_AGENT = (
    "---\n"
    "name: reviewer\n"
    "description: Reviews changes.\n"
    "mode: subagent\n"
    "version: 1.0.0\n"
    "---\n"
    "\n"
    "# Reviewer — Destination\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "**Persona / personality:** see `agents/reviewer/profile.md` "
    "(source of truth — do not duplicate here).\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Legacy reviewer note without the destination identity sentence.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "LEGACY_AGENT_MANDATORY\n"
)
BOOTSTRAP_REVIEW_EVIDENCE = "Reviewed the prepared bootstrap snapshot."
BOOTSTRAP_FORBIDDEN_COMMANDS: tuple[str, ...] = (
    "pnpm approve-builds",
    "pnpm install",
    "pnpm build",
    "npm install",
    "npm run build",
    "uv sync",
    "uv add",
    "pip install",
    "yarn install",
    "cargo build",
)
BOOTSTRAP_ADOPTED_PATHS: tuple[str, ...] = (
    "AGENTS.md",
    ".opencode/agents/reviewer.md",
    "agents/reviewer/profile.md",
    "skills/mirror-note.md",
    "knowledge/debt.md",
    "knowledge/symptoms.md",
    "knowledge/problems.md",
    "plans/.gitkeep",
    "pyproject.toml",
    ".opencode/skills/enrolled/SKILL.md",
    "opencode.jsonc",
    "user-stories/alpha.md",
    "user-stories/index.md",
)
BOOTSTRAP_RETAINED_PATHS: tuple[str, ...] = (
    "knowledge/debt.md",
    "knowledge/problems.md",
    "knowledge/symptoms.md",
    "plans/.gitkeep",
)

BOOTSTRAP_CATALOG = """schema_version: 2
catalog:
  version: 2.5.1
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: guarded_file
    destination_policy: adopter_root_rules
    rule_documents:
      - AGENTS.md
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
  - id: reviewer-agent
    kind: agent
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    rule_documents:
      - .opencode/agents/reviewer.md
    members:
      - { id: spec, source: .opencode/agents/reviewer.md, destination: .opencode/agents/reviewer.md }
      - { id: profile, source: agents/reviewer/profile.md, destination: agents/reviewer/profile.md }
  - id: mirror-note
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    rule_documents:
      - skills/mirror-note.md
    members:
      - { id: note, source: skills/mirror-note.md, destination: skills/mirror-note.md }
  - id: enrolled-skill
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: skill, source: .opencode/skills/enrolled/SKILL.md, destination: .opencode/skills/enrolled/SKILL.md }
  - id: opencode-config
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: assertions
    destination: opencode.jsonc
    assertions:
      - { id: sudo-deny, contains: '"sudo *": "deny"' }
  - id: portable-stories
    kind: user-story
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: alpha, source: user-stories/alpha.md, destination: user-stories/alpha.md, collision_policy: core_wins }
  - id: knowledge-debt
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: file, source: knowledge/debt.md, destination: knowledge/debt.md }
  - id: symptom-problem-register
    kind: infra
    applicability: { always: true }
    install_strategy: copy
    sync_projection: file
    members:
      - { id: symptoms, source: knowledge/symptoms.md, destination: knowledge/symptoms.md }
      - { id: problems, source: knowledge/problems.md, destination: knowledge/problems.md }
  - id: plans
    kind: infra
    applicability: { always: true }
    install_strategy: preserve
    sync_projection: file
    members:
      - { id: gitkeep, source: plans/.gitkeep, destination: plans/.gitkeep }
  - id: project-manifest
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: file
    members:
      - { id: manifest, source: pyproject.toml, destination: pyproject.toml }
"""

BOOTSTRAP_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
test_runner:
  no_tests: true
  reviewer: reviewer
  evidence: Relay has no enrolled suite in this fixture.
units:
  - id: root-runtime-spec
    mode: adapted
    members:
      - { id: root, destination: AGENTS.md }
  - id: reviewer-agent
    mode: adapted
    members:
      - { id: spec, destination: .opencode/agents/reviewer.md }
      - { id: profile, destination: agents/reviewer/profile.md }
  - id: mirror-note
    mode: mirror
    members:
      - { id: note, destination: skills/mirror-note.md }
  - id: enrolled-skill
    mode: mirror
    members:
      - { id: skill, destination: .opencode/skills/enrolled/SKILL.md }
  - id: opencode-config
    mode: mirror
  - id: portable-stories
    mode: mirror
    members:
      - { id: alpha, destination: user-stories/alpha.md }
  - id: knowledge-debt
    mode: adapted
    members:
      - { id: file, destination: knowledge/debt.md }
  - id: symptom-problem-register
    mode: adapted
    members:
      - { id: symptoms, destination: knowledge/symptoms.md }
      - { id: problems, destination: knowledge/problems.md }
  - id: plans
    mode: adapted
    members:
      - { id: gitkeep, destination: plans/.gitkeep }
  - id: project-manifest
    mode: adapted
    members:
      - { id: manifest, destination: pyproject.toml }
"""

BOOTSTRAP_SOURCE_FILES: dict[str, str] = {
    "AGENTS.md": PROTECTED_SOURCE_ROOT,
    ".opencode/agents/reviewer.md": PROTECTED_SOURCE_AGENT,
    "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
    "skills/mirror-note.md": BOOTSTRAP_MIRROR_NOTE,
    ".opencode/skills/enrolled/SKILL.md": BOOTSTRAP_SKILL,
    "knowledge/debt.md": BOOTSTRAP_SOURCE_DEBT,
    "knowledge/symptoms.md": BOOTSTRAP_SYMPTOMS,
    "knowledge/problems.md": BOOTSTRAP_SOURCE_PROBLEMS,
    "plans/.gitkeep": BOOTSTRAP_SOURCE_GITKEEP,
    "pyproject.toml": BOOTSTRAP_SOURCE_MANIFEST,
    "user-stories/alpha.md": BOOTSTRAP_STORY_FILE,
    "user-stories/index.md": BOOTSTRAP_SOURCE_INDEX,
}
BOOTSTRAP_EXISTING_FILES: dict[str, str] = {
    "AGENTS.md": BOOTSTRAP_LEGACY_ROOT,
    ".opencode/agents/reviewer.md": BOOTSTRAP_LEGACY_AGENT,
    "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
    "skills/mirror-note.md": BOOTSTRAP_MIRROR_NOTE,
    ".opencode/skills/enrolled/SKILL.md": BOOTSTRAP_SKILL,
    "knowledge/debt.md": BOOTSTRAP_EXISTING_DEBT,
    "knowledge/symptoms.md": BOOTSTRAP_SYMPTOMS,
    "knowledge/problems.md": BOOTSTRAP_EXISTING_PROBLEMS,
    "plans/.gitkeep": BOOTSTRAP_EXISTING_GITKEEP,
    "pyproject.toml": BOOTSTRAP_EXISTING_MANIFEST,
    "opencode.jsonc": BOOTSTRAP_EXISTING_CONFIG_BEFORE,
    "user-stories/alpha.md": BOOTSTRAP_STORY_FILE,
    "user-stories/index.md": BOOTSTRAP_EXISTING_INDEX,
}
