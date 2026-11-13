"""Parse and query a schema v1 Markdown text-integrity policy document."""

from __future__ import annotations

from markdown_text_pkg.domain.models import (
    CODE_INPUT,
    CODE_POLICY,
    MAX_UNICODE_SCALAR,
    SURROGATE_END,
    SURROGATE_START,
    CodepointSpec,
    Decoding,
    DomainError,
    EditorDriftFinding,
    EditorOverride,
    EditorProjection,
    InvalidSequence,
    Policy,
    RangeSpec,
    Rule,
)

ROOT_KEYS = frozenset(
    {
        "version",
        "id",
        "default_classification",
        "decoding",
        "rules",
        "editor_projection",
    }
)
DECODING_KEYS = frozenset({"encoding", "invalid_sequence"})
INVALID_SEQUENCE_KEYS = frozenset({"id", "severity", "class", "rationale"})
RULE_BASE_KEYS = frozenset({"id", "severity", "class", "rationale"})
CODEPOINT_KEYS = frozenset({"cp", "hex"})
RANGE_KEYS = frozenset({"start", "end", "start_hex", "end_hex"})
EDITOR_KEYS = frozenset({"scope", "setting_key", "overrides"})
OVERRIDE_KEYS = frozenset(
    {"codepoint", "hex", "gremlins_key", "severity", "description"}
)
RULE_SEVERITIES = frozenset({"error", "warning"})


def canonical_hex(codepoint: int) -> str:
    """Return the canonical U+ form: uppercase hex, minimum four digits."""

    return f"U+{codepoint:04X}"


def canonical_gremlins_key(codepoint: int) -> str:
    """Return the lowercase hex Gremlins key, minimum four digits, no U+ prefix."""

    return f"{codepoint:04x}"


def classify_codepoint(policy: Policy, codepoint: int) -> Rule | None:
    """Return the unique covering rule, or None when the scalar is allowed by default."""

    for rule in policy.rules:
        for spec in rule.codepoints:
            if spec.cp == codepoint:
                return rule
        for spec in rule.ranges:
            if spec.start <= codepoint <= spec.end:
                return rule
    return None


def parse_policy(data: object) -> Policy | DomainError:
    """Validate a decoded JSON document against schema v1 and return a Policy."""

    root = _require_object(data, "policy root")
    if isinstance(root, DomainError):
        return root
    keys_error = _require_exact_keys(root, ROOT_KEYS, "policy root")
    if keys_error is not None:
        return keys_error

    version = _require_int(root["version"], "version")
    if isinstance(version, DomainError):
        return version
    if version != 1:
        return DomainError(CODE_POLICY, f"unsupported policy version: {version}")

    policy_id = _require_nonempty_str(root["id"], "id")
    if isinstance(policy_id, DomainError):
        return policy_id

    default_classification = _require_nonempty_str(
        root["default_classification"], "default_classification"
    )
    if isinstance(default_classification, DomainError):
        return default_classification
    if default_classification != "allow":
        return DomainError(
            CODE_POLICY,
            "default_classification must be allow",
        )

    decoding = _parse_decoding(root["decoding"])
    if isinstance(decoding, DomainError):
        return decoding

    rules = _parse_rules(root["rules"], decoding.invalid_sequence.id)
    if isinstance(rules, DomainError):
        return rules

    editor_projection = _parse_editor_projection(root["editor_projection"])
    if isinstance(editor_projection, DomainError):
        return editor_projection

    return Policy(
        version=version,
        id=policy_id,
        default_classification=default_classification,
        decoding=decoding,
        rules=rules,
        editor_projection=editor_projection,
    )


def compare_editor_projection(
    policy: Policy, settings: object, path: str
) -> EditorDriftFinding | DomainError | None:
    """Compare only the representable projection; extra cloned defaults are drift."""

    if not isinstance(settings, dict):
        return DomainError(CODE_INPUT, "editor settings must be a JSON object")

    scope_value = settings.get(policy.editor_projection.scope)
    if scope_value is None:
        actual: dict[str, object] = {}
    else:
        if not isinstance(scope_value, dict):
            return DomainError(CODE_INPUT, "editor scope must be an object")
        characters = scope_value.get(policy.editor_projection.setting_key)
        if characters is None:
            actual = {}
        elif not isinstance(characters, dict):
            return DomainError(CODE_INPUT, "editor projection must be an object")
        else:
            actual = characters

    expected = {item.gremlins_key: item for item in policy.editor_projection.overrides}
    missing: list[str] = []
    mismatched: list[str] = []
    extra: list[str] = []

    for key, override in expected.items():
        if key not in actual:
            missing.append(key)
            continue
        value = actual[key]
        if not _override_matches(value, override):
            mismatched.append(key)

    for key in actual:
        if key not in expected:
            extra.append(str(key))

    if not missing and not extra and not mismatched:
        return None
    return EditorDriftFinding(
        path=path.replace("\\", "/"),
        missing=tuple(sorted(missing)),
        extra=tuple(sorted(extra)),
        mismatched=tuple(sorted(mismatched)),
    )


def _override_matches(value: object, override: EditorOverride) -> bool:
    """Return whether a settings entry matches the representable override."""

    if not isinstance(value, dict):
        return False
    return (
        value.get("level") == override.severity
        and value.get("description") == override.description
    )


def _parse_decoding(value: object) -> Decoding | DomainError:
    """Parse the decoding envelope object."""

    payload = _require_object(value, "decoding")
    if isinstance(payload, DomainError):
        return payload
    keys_error = _require_exact_keys(payload, DECODING_KEYS, "decoding")
    if keys_error is not None:
        return keys_error

    encoding = _require_nonempty_str(payload["encoding"], "decoding.encoding")
    if isinstance(encoding, DomainError):
        return encoding
    if encoding != "utf-8":
        return DomainError(CODE_POLICY, "decoding.encoding must be utf-8")

    invalid_sequence = _parse_invalid_sequence(payload["invalid_sequence"])
    if isinstance(invalid_sequence, DomainError):
        return invalid_sequence
    return Decoding(encoding=encoding, invalid_sequence=invalid_sequence)


def _parse_invalid_sequence(value: object) -> InvalidSequence | DomainError:
    """Parse the invalid UTF-8 envelope rule."""

    payload = _require_object(value, "decoding.invalid_sequence")
    if isinstance(payload, DomainError):
        return payload
    keys_error = _require_exact_keys(
        payload, INVALID_SEQUENCE_KEYS, "decoding.invalid_sequence"
    )
    if keys_error is not None:
        return keys_error

    rule_id = _require_nonempty_str(payload["id"], "decoding.invalid_sequence.id")
    if isinstance(rule_id, DomainError):
        return rule_id
    severity = _require_nonempty_str(
        payload["severity"], "decoding.invalid_sequence.severity"
    )
    if isinstance(severity, DomainError):
        return severity
    if severity != "error":
        return DomainError(
            CODE_POLICY, "decoding.invalid_sequence.severity must be error"
        )
    class_name = _require_nonempty_str(
        payload["class"], "decoding.invalid_sequence.class"
    )
    if isinstance(class_name, DomainError):
        return class_name
    rationale = _require_nonempty_str(
        payload["rationale"], "decoding.invalid_sequence.rationale"
    )
    if isinstance(rationale, DomainError):
        return rationale
    return InvalidSequence(
        id=rule_id,
        severity=severity,
        class_name=class_name,
        rationale=rationale,
    )


def _parse_rules(
    value: object, invalid_sequence_id: str
) -> tuple[Rule, ...] | DomainError:
    """Parse the rules array and reject overlapping coverage or duplicate IDs."""

    if not isinstance(value, list):
        return DomainError(CODE_POLICY, "rules must be an array")

    rules: list[Rule] = []
    seen_ids = {invalid_sequence_id}
    intervals: list[tuple[int, int, str]] = []
    for index, item in enumerate(value):
        rule = _parse_rule(item, index)
        if isinstance(rule, DomainError):
            return rule
        if rule.id in seen_ids:
            return DomainError(CODE_POLICY, f"duplicate rule id: {rule.id}")
        seen_ids.add(rule.id)
        for spec in rule.codepoints:
            intervals.append((spec.cp, spec.cp, rule.id))
        for spec in rule.ranges:
            intervals.append((spec.start, spec.end, rule.id))
        rules.append(rule)

    overlap = _first_overlap(intervals)
    if overlap is not None:
        return overlap
    return tuple(rules)


def _parse_rule(value: object, index: int) -> Rule | DomainError:
    """Parse one rules[] object with exactly one of codepoints or ranges."""

    label = f"rules[{index}]"
    payload = _require_object(value, label)
    if isinstance(payload, DomainError):
        return payload

    has_codepoints = "codepoints" in payload
    has_ranges = "ranges" in payload
    if has_codepoints == has_ranges:
        return DomainError(
            CODE_POLICY,
            f"{label} must have exactly one of codepoints or ranges",
        )
    expected = RULE_BASE_KEYS | (
        frozenset({"codepoints"}) if has_codepoints else frozenset({"ranges"})
    )
    keys_error = _require_exact_keys(payload, expected, label)
    if keys_error is not None:
        return keys_error

    rule_id = _require_nonempty_str(payload["id"], f"{label}.id")
    if isinstance(rule_id, DomainError):
        return rule_id
    severity = _require_nonempty_str(payload["severity"], f"{label}.severity")
    if isinstance(severity, DomainError):
        return severity
    if severity not in RULE_SEVERITIES:
        return DomainError(
            CODE_POLICY, f"{label}.severity must be error or warning"
        )
    class_name = _require_nonempty_str(payload["class"], f"{label}.class")
    if isinstance(class_name, DomainError):
        return class_name
    rationale = _require_nonempty_str(payload["rationale"], f"{label}.rationale")
    if isinstance(rationale, DomainError):
        return rationale

    if has_codepoints:
        codepoints = _parse_codepoints(payload["codepoints"], f"{label}.codepoints")
        if isinstance(codepoints, DomainError):
            return codepoints
        ranges: tuple[RangeSpec, ...] = ()
    else:
        codepoints = ()
        parsed_ranges = _parse_ranges(payload["ranges"], f"{label}.ranges")
        if isinstance(parsed_ranges, DomainError):
            return parsed_ranges
        ranges = parsed_ranges

    return Rule(
        id=rule_id,
        severity=severity,
        class_name=class_name,
        rationale=rationale,
        codepoints=codepoints,
        ranges=ranges,
    )


def _parse_codepoints(
    value: object, label: str
) -> tuple[CodepointSpec, ...] | DomainError:
    """Parse a non-empty codepoints array."""

    if not isinstance(value, list):
        return DomainError(CODE_POLICY, f"{label} must be an array")
    if len(value) == 0:
        return DomainError(CODE_POLICY, f"{label} must not be empty")
    items: list[CodepointSpec] = []
    for index, item in enumerate(value):
        parsed = _parse_codepoint_item(item, f"{label}[{index}]")
        if isinstance(parsed, DomainError):
            return parsed
        items.append(parsed)
    return tuple(items)


def _parse_codepoint_item(value: object, label: str) -> CodepointSpec | DomainError:
    """Parse one codepoints[] object."""

    payload = _require_object(value, label)
    if isinstance(payload, DomainError):
        return payload
    keys_error = _require_exact_keys(payload, CODEPOINT_KEYS, label)
    if keys_error is not None:
        return keys_error
    codepoint = _require_scalar_int(payload["cp"], f"{label}.cp")
    if isinstance(codepoint, DomainError):
        return codepoint
    hex_value = _require_nonempty_str(payload["hex"], f"{label}.hex")
    if isinstance(hex_value, DomainError):
        return hex_value
    expected = canonical_hex(codepoint)
    if hex_value != expected:
        return DomainError(
            CODE_POLICY, f"{label}.hex must be {expected}"
        )
    return CodepointSpec(cp=codepoint, hex=hex_value)


def _parse_ranges(value: object, label: str) -> tuple[RangeSpec, ...] | DomainError:
    """Parse a non-empty ranges array."""

    if not isinstance(value, list):
        return DomainError(CODE_POLICY, f"{label} must be an array")
    if len(value) == 0:
        return DomainError(CODE_POLICY, f"{label} must not be empty")
    items: list[RangeSpec] = []
    for index, item in enumerate(value):
        parsed = _parse_range_item(item, f"{label}[{index}]")
        if isinstance(parsed, DomainError):
            return parsed
        items.append(parsed)
    return tuple(items)


def _parse_range_item(value: object, label: str) -> RangeSpec | DomainError:
    """Parse one ranges[] object with inclusive scalar bounds."""

    payload = _require_object(value, label)
    if isinstance(payload, DomainError):
        return payload
    keys_error = _require_exact_keys(payload, RANGE_KEYS, label)
    if keys_error is not None:
        return keys_error
    start = _require_scalar_int(payload["start"], f"{label}.start")
    if isinstance(start, DomainError):
        return start
    end = _require_scalar_int(payload["end"], f"{label}.end")
    if isinstance(end, DomainError):
        return end
    if start > end:
        return DomainError(CODE_POLICY, f"{label} start must be <= end")
    start_hex = _require_nonempty_str(payload["start_hex"], f"{label}.start_hex")
    if isinstance(start_hex, DomainError):
        return start_hex
    end_hex = _require_nonempty_str(payload["end_hex"], f"{label}.end_hex")
    if isinstance(end_hex, DomainError):
        return end_hex
    expected_start = canonical_hex(start)
    expected_end = canonical_hex(end)
    if start_hex != expected_start:
        return DomainError(
            CODE_POLICY, f"{label}.start_hex must be {expected_start}"
        )
    if end_hex != expected_end:
        return DomainError(
            CODE_POLICY, f"{label}.end_hex must be {expected_end}"
        )
    return RangeSpec(start=start, end=end, start_hex=start_hex, end_hex=end_hex)


def _parse_editor_projection(value: object) -> EditorProjection | DomainError:
    """Parse editor_projection; overrides are not mixed into scan rules."""

    payload = _require_object(value, "editor_projection")
    if isinstance(payload, DomainError):
        return payload
    keys_error = _require_exact_keys(payload, EDITOR_KEYS, "editor_projection")
    if keys_error is not None:
        return keys_error
    scope = _require_nonempty_str(payload["scope"], "editor_projection.scope")
    if isinstance(scope, DomainError):
        return scope
    setting_key = _require_nonempty_str(
        payload["setting_key"], "editor_projection.setting_key"
    )
    if isinstance(setting_key, DomainError):
        return setting_key
    if not isinstance(payload["overrides"], list):
        return DomainError(CODE_POLICY, "editor_projection.overrides must be an array")

    overrides: list[EditorOverride] = []
    seen_codepoints: set[int] = set()
    seen_keys: set[str] = set()
    for index, item in enumerate(payload["overrides"]):
        parsed = _parse_override(item, index)
        if isinstance(parsed, DomainError):
            return parsed
        if parsed.codepoint in seen_codepoints:
            return DomainError(
                CODE_POLICY,
                f"duplicate editor_projection codepoint: {canonical_hex(parsed.codepoint)}",
            )
        if parsed.gremlins_key in seen_keys:
            return DomainError(
                CODE_POLICY,
                f"duplicate editor_projection gremlins_key: {parsed.gremlins_key}",
            )
        seen_codepoints.add(parsed.codepoint)
        seen_keys.add(parsed.gremlins_key)
        overrides.append(parsed)
    return EditorProjection(
        scope=scope, setting_key=setting_key, overrides=tuple(overrides)
    )


def _parse_override(value: object, index: int) -> EditorOverride | DomainError:
    """Parse one representable editor override."""

    label = f"editor_projection.overrides[{index}]"
    payload = _require_object(value, label)
    if isinstance(payload, DomainError):
        return payload
    keys_error = _require_exact_keys(payload, OVERRIDE_KEYS, label)
    if keys_error is not None:
        return keys_error
    codepoint = _require_scalar_int(payload["codepoint"], f"{label}.codepoint")
    if isinstance(codepoint, DomainError):
        return codepoint
    hex_value = _require_nonempty_str(payload["hex"], f"{label}.hex")
    if isinstance(hex_value, DomainError):
        return hex_value
    expected_hex = canonical_hex(codepoint)
    if hex_value != expected_hex:
        return DomainError(CODE_POLICY, f"{label}.hex must be {expected_hex}")
    gremlins_key = _require_nonempty_str(
        payload["gremlins_key"], f"{label}.gremlins_key"
    )
    if isinstance(gremlins_key, DomainError):
        return gremlins_key
    expected_key = canonical_gremlins_key(codepoint)
    if gremlins_key != expected_key:
        return DomainError(
            CODE_POLICY, f"{label}.gremlins_key must be {expected_key}"
        )
    severity = _require_nonempty_str(payload["severity"], f"{label}.severity")
    if isinstance(severity, DomainError):
        return severity
    if severity != "none":
        return DomainError(CODE_POLICY, f"{label}.severity must be none")
    description = _require_nonempty_str(
        payload["description"], f"{label}.description"
    )
    if isinstance(description, DomainError):
        return description
    return EditorOverride(
        codepoint=codepoint,
        hex=hex_value,
        gremlins_key=gremlins_key,
        severity=severity,
        description=description,
    )


def _first_overlap(intervals: list[tuple[int, int, str]]) -> DomainError | None:
    """Return a policy error when inclusive coverage overlaps, including duplicates."""

    ordered = sorted(intervals, key=lambda item: (item[0], item[1], item[2]))
    for index in range(len(ordered) - 1):
        start_a, end_a, id_a = ordered[index]
        start_b, end_b, id_b = ordered[index + 1]
        if end_a >= start_b:
            return DomainError(
                CODE_POLICY,
                f"overlapping coverage between {id_a} and {id_b}",
            )
    return None


def _require_object(value: object, label: str) -> dict[str, object] | DomainError:
    """Require a JSON object."""

    if not isinstance(value, dict):
        return DomainError(CODE_POLICY, f"{label} must be an object")
    return value


def _require_exact_keys(
    payload: dict[str, object], expected: frozenset[str], label: str
) -> DomainError | None:
    """Reject missing and unknown fields on a closed object."""

    keys = frozenset(payload)
    missing = expected - keys
    extra = keys - expected
    if not missing and not extra:
        return None
    parts: list[str] = []
    if missing:
        parts.append("missing " + ", ".join(sorted(missing)))
    if extra:
        parts.append("unknown " + ", ".join(sorted(extra)))
    return DomainError(CODE_POLICY, f"{label}: {'; '.join(parts)}")


def _require_int(value: object, label: str) -> int | DomainError:
    """Require a true integer; bool is not an integer and floats are rejected."""

    if type(value) is not int:
        return DomainError(CODE_POLICY, f"{label} must be an integer")
    return value


def _require_scalar_int(value: object, label: str) -> int | DomainError:
    """Require a Unicode scalar integer, excluding surrogates."""

    number = _require_int(value, label)
    if isinstance(number, DomainError):
        return number
    if number < 0 or number > MAX_UNICODE_SCALAR:
        return DomainError(
            CODE_POLICY, f"{label} must be a Unicode scalar 0..{MAX_UNICODE_SCALAR}"
        )
    if SURROGATE_START <= number <= SURROGATE_END:
        return DomainError(CODE_POLICY, f"{label} must not be a surrogate")
    return number


def _require_nonempty_str(value: object, label: str) -> str | DomainError:
    """Require a non-empty string."""

    if type(value) is not str:
        return DomainError(CODE_POLICY, f"{label} must be a string")
    if value == "":
        return DomainError(CODE_POLICY, f"{label} must be non-empty")
    return value
