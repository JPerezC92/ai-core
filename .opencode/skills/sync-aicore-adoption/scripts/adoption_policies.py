"""Runtime identity and configuration policy checks."""

from __future__ import annotations

import json
from typing import Mapping

from adoption_constants import (
    DESTINATION_POLICIES,
    OPENCODE_CONFIG_BASENAME,
    _ADOPTER_ROOT_FORBIDDEN_REFERENCES,
    _ADOPTER_ROOT_REQUIRED_MARKERS,
)
from adoption_contracts import (
    TestRunner,
    _Snapshot,
    _content_projection,
    _need,
    _normalize_destination,
)
from adoption_mapping import _declared_members

def _adopter_root_policy_violation(content: bytes) -> str | None:
    """Return the first adopter-root policy violation, or ``None`` when valid."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return "mapped root must be UTF-8 text"
    folded = text.casefold()
    for forbidden in _ADOPTER_ROOT_FORBIDDEN_REFERENCES:
        if forbidden in folded:
            return f"mapped root contains prohibited reference {forbidden!r}"
    for marker, pattern in _ADOPTER_ROOT_REQUIRED_MARKERS:
        if pattern.search(text) is None:
            return f"mapped root is missing required {marker!r} marker"
    return None


def _destination_policy_violation(
    uid: str,
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    snapshot: _Snapshot,
    test_runner: TestRunner | None,
) -> str | None:
    """Evaluate a catalog unit's closed destination policy against its snapshot.

    The adopter's ``opencode.jsonc`` — the destination of the catalog's
    ``opencode-config`` assertions unit — is evaluated first under the
    declaration's reviewed ``test_runner`` metadata. The guarded root-runtime
    identity policy then runs unchanged for ``guarded_file`` units.
    """
    destination = str(catalog_unit.get("destination") or "")
    if _is_opencode_config_destination(destination):
        entry = snapshot.file_entry(destination)
        if entry is None:
            # A missing config stays governed by the unit's assertions.
            return None
        return _opencode_config_policy_violation(entry.content, test_runner)
    if catalog_unit.get("sync_projection") != "guarded_file":
        return None
    policy = str(catalog_unit.get("destination_policy"))
    _need(
        policy in DESTINATION_POLICIES,
        "invalid_mapping",
        f"{uid}: unsupported destination policy {policy!r}",
    )
    if decl_unit.get("mode") == "replacement":
        replacements = list(decl_unit.get("replacement_members", []) or [])
        if len(replacements) != 1 or _content_projection(
            str(replacements[0].get("projection"))
        ) != "file":
            return "guarded root replacement must map exactly one file"
        destination = str(replacements[0].get("destination"))
    else:
        declared = _declared_members(catalog_unit, decl_unit, uid)
        members = list(catalog_unit.get("members", []) or [])
        if len(members) != 1:
            return "guarded root must declare exactly one catalog member"
        destination = declared[str(members[0].get("id"))]
    entry = snapshot.file_entry(destination)
    content = entry.content if entry is not None else b""
    return _adopter_root_policy_violation(content)


def _is_opencode_config_destination(destination: str) -> bool:
    """Return whether a catalog destination names the adopter's opencode config."""
    return (
        _normalize_destination(destination).rsplit("/", 1)[-1]
        == OPENCODE_CONFIG_BASENAME
    )


def _has_wildcard(pattern: str) -> bool:
    """Return whether a permission pattern contains an OpenCode wildcard."""
    return "*" in pattern or "?" in pattern


def _wildcard_match(pattern: str, command: str) -> bool:
    """Match one OpenCode permission pattern against a parsed command.

    ``*`` matches zero or more of any character, ``?`` matches exactly one
    character, and every other character matches literally (documented in the
    OpenCode granular-rules object syntax). The bounded dynamic-programming
    table keeps adversarial patterns linear rather than exponential.
    """
    previous = [False] * (len(command) + 1)
    previous[0] = True
    for marker in pattern:
        current = [False] * (len(command) + 1)
        if marker == "*":
            current[0] = previous[0]
            for position in range(1, len(command) + 1):
                current[position] = previous[position] or current[position - 1]
        elif marker == "?":
            for position in range(1, len(command) + 1):
                current[position] = previous[position - 1]
        else:
            for position in range(1, len(command) + 1):
                current[position] = (
                    previous[position - 1] and command[position - 1] == marker
                )
        previous = current
    return previous[len(command)]


def _effective_bash_action(
    bash: Mapping[str, object], command: str
) -> str | None:
    """Return the last matching OpenCode action for ``command``, or ``None``.

    OpenCode evaluates granular rules in document order and the last matching
    rule wins, so the mapping's insertion order is authoritative. A later
    matching ``deny`` or ``ask`` therefore makes an earlier literal ``allow``
    ineffective. The matched rule's value is taken verbatim rather than
    filtered: a non-canonical value (``Deny``, ``true``, an object) never
    resolves to ``allow``, so the ordered-effect path fails closed instead of
    silently skipping an unrecognized action.
    """
    action: str | None = None
    for pattern, candidate in bash.items():
        if not isinstance(pattern, str):
            continue
        if _wildcard_match(pattern, command):
            action = str(candidate)
    return action


def _broad_grant_violation(pattern: str, commands: set[str]) -> str | None:
    """Return the broad-grant violation for an ``allow`` pattern, or ``None``.

    A wildcard pattern that is not itself one of the approved command literals
    can match arbitrary command text and is rejected structurally. Neither the
    number of tokens in the pattern head nor any runner name list is treated as
    proof of scope, so ``uv run *`` and ``python3 -c *`` fail exactly like a
    bare ``uv *``.
    """
    if pattern not in commands and _has_wildcard(pattern):
        return f"allow {pattern!r} grants arbitrary commands"
    return None


class _JsoncCommentError(ValueError):
    """Raised when comment stripping cannot preserve JSONC token boundaries."""


def _strip_jsonc_comments(text: str) -> str:
    """Remove ``//`` line and ``/* ... */`` block comments from JSONC text.

    Comment removal never manufactures valid JSON: a block comment is replaced
    by one space so adjacent tokens stay separate, and an unterminated block
    comment raises ``_JsoncCommentError`` instead of silently swallowing the
    rest of the document. A ``//`` comment terminates at the first of ``\\n``,
    ``\\r``, ``\\u2028``, or ``\\u2029`` — a ``\\r\\n`` pair is one line
    terminator whose two characters are copied through verbatim, and an
    ECMAScript-only ``\\u2028``/``\\u2029`` terminator is normalized to
    ``\\n`` so it remains valid JSON whitespace — so a terminated comment can
    never hide following JSON from the parser. The checker never accepts a
    document whose comment structure a conformant JSONC parse sees
    differently: comment removal preserves exactly the token separation a
    conformant parse performs, and for bare ECMAScript-only whitespace
    outside comments the checker is stricter — never looser — than a
    conformant parse. ``#`` is never a JSONC comment, so a ``#`` line
    survives to the JSON parser and fails there. String literals are
    preserved verbatim, including escapes and comment-like characters
    inside a value.
    """
    result: list[str] = []
    index = 0
    length = len(text)
    in_string = False
    while index < length:
        char = text[index]
        if in_string:
            result.append(char)
            if char == "\\" and index + 1 < length:
                result.append(text[index + 1])
                index += 2
                continue
            if char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            result.append(char)
            index += 1
            continue
        if char == "/" and index + 1 < length and text[index + 1] == "/":
            end = index + 2
            while end < length and text[end] not in "\r\n\u2028\u2029":
                end += 1
            if end < length and text[end] in "\u2028\u2029":
                # Normalize an ECMAScript-only line terminator to "\n": the
                # comment still ends at exactly this position, and the
                # replacement is whitespace Python's JSON parser accepts, so
                # the stripped text parses exactly like the conformant
                # JSONC parse of the original.
                result.append("\n")
                end += 1
            # Any other terminator (and the "\n" of a "\r\n" pair) is copied
            # through by the main loop as ordinary JSON whitespace; only the
            # comment body between "//" and the terminator is removed.
            index = end
            continue
        if char == "/" and index + 1 < length and text[index + 1] == "*":
            terminator = text.find("*/", index + 2)
            if terminator == -1:
                raise _JsoncCommentError("unterminated block comment")
            result.append(" ")
            index = terminator + 2
            continue
        result.append(char)
        index += 1
    return "".join(result)


def _opencode_config_policy_violation(
    content: bytes, test_runner: TestRunner | None
) -> str | None:
    """Validate the designated test executor's grants against reviewed metadata.

    The declaration names one reviewed ``test_runner``: either an explicit
    ``no_tests`` disposition or the whole-project ``commands`` and the
    ``executor`` that runs them. Only that executor's
    ``agent.<executor>.permission.bash`` mapping is inspected. Approved
    commands are literals: a declared command carrying ``*`` or ``?`` is
    rejected, so the broad-grant membership exemption can never launder a
    wildcard grant. Each approved command is evaluated against the ordered
    wildcard rules, where the last matching rule wins, so a later
    ``deny``/``ask`` cannot pass as executable approval. An entry whose value
    is not exactly ``allow``/``ask``/``deny`` is a config violation in both
    the broad-grant scan and the ordered-effect resolution rather than a
    silently skipped rule. A wildcard ``allow`` that is not itself an
    approved command is a broad arbitrary-execution grant and fails.
    Unrelated agents, top-level grants, and unrelated literal allows are
    never inspected. Malformed or non-object JSONC, including an unterminated
    block comment, is a violation rather than a silent pass.
    """
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return "opencode config is not a valid JSONC object"
    try:
        stripped = _strip_jsonc_comments(text)
    except _JsoncCommentError:
        return "opencode config is not a valid JSONC object"
    try:
        document = json.loads(stripped)
    except json.JSONDecodeError:
        return "opencode config is not a valid JSONC object"
    if not isinstance(document, dict):
        return "opencode config is not a valid JSONC object"
    if test_runner is None:
        return "adopter declares no reviewed test_runner metadata"
    if test_runner.get("no_tests") is True:
        return None
    executor = test_runner.get("executor")
    commands = {
        str(command)
        for command in test_runner.get("commands", []) or []
        if isinstance(command, str) and command
    }
    for command in sorted(commands):
        if _has_wildcard(command):
            return (
                f"designated test executor {str(executor)!r} approved command "
                f"{command!r} must be a literal without wildcard metacharacters"
            )
    agents = document.get("agent")
    agent = agents.get(str(executor)) if isinstance(agents, Mapping) else None
    if not isinstance(agent, Mapping):
        return (
            f"designated test executor {executor!r} has no "
            "agent.<executor>.permission.bash grant"
        )
    permission = agent.get("permission")
    if not isinstance(permission, Mapping) or "bash" not in permission:
        return (
            f"designated test executor {executor!r} has no "
            "agent.<executor>.permission.bash grant"
        )
    bash = permission.get("bash")
    if isinstance(bash, str):
        if bash == "allow":
            return f"agent {str(executor)!r}: blanket string 'allow' grants every command"
        return f"designated test executor {str(executor)!r} permission.bash must be a mapping"
    if not isinstance(bash, Mapping):
        return f"designated test executor {str(executor)!r} permission.bash must be a mapping"
    for pattern, action in bash.items():
        if not isinstance(pattern, str):
            continue
        if action not in ("allow", "ask", "deny"):
            # Fail closed: a non-canonical action is a config violation in
            # the broad-grant scan, never a silently skipped rule that lets
            # an earlier matching allow stand.
            return (
                f"agent {str(executor)!r} permission.bash: {pattern!r} has "
                f"unrecognized action {action!r}"
            )
        if action != "allow":
            continue
        broad = _broad_grant_violation(pattern, commands)
        if broad is not None:
            return f"agent {str(executor)!r} permission.bash: {broad}"
    ineffective = sorted(
        command
        for command in commands
        if _effective_bash_action(bash, command) != "allow"
    )
    if ineffective:
        return (
            f"designated test executor {str(executor)!r} is missing approved "
            f"test-runner grant(s): {ineffective}"
        )
    return None
