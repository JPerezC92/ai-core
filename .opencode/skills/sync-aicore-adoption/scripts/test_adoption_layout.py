"""Two-section rule-layout parser contract tests.

The layout parser is a single owner: this module covers corpus partitions and
distinct boundary attacks. Parser cases do not inherit the repository fixture.
One scan supplies both the layout and the diagnostic.
"""

from __future__ import annotations

import pytest

from adoption_content import (
    _rule_layout,
    _rule_layout_violation,
    _scan_rule_layout,
)
from adoption_loaders import load_catalog
from adoption_test_repos import repository_root

VALID_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
)

VALID_FRONTMATTER_LAYOUT = (
    "---\n"
    "name: reviewer\n"
    "mode: subagent\n"
    "version: 1.0.0\n"
    "---\n"
    "\n"
    "# Reviewer\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "**Persona / personality:** see `agents/reviewer/profile.md`.\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

QUOTED_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Inline quotation `> **Rule layout:** two-section-v1` is a syntax example.\n"
    "\n"
    "| field | value |\n"
    "|---|---|\n"
    "| marker | `> **Rule layout:** two-section-v1` |\n"
    "\n"
    "```markdown\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "## Mandatory core\n"
    "```\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
)

MISSING_MARKER_LAYOUT = (
    "# Reviewer\n\n## Project extensions\n\nExtension.\n\n## Mandatory core\n\nCore.\n"
)

DUPLICATE_MARKER_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

MISPLACED_MARKER_LAYOUT = (
    "# Reviewer\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

OPERATIONAL_INTRO_LAYOUT = (
    "# Reviewer\n"
    "\n"
    "This operational sentence must not be framing.\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

BLOCKQUOTED_INTRO_LAYOUT = (
    "# Reviewer\n"
    "> **Note:** an operational blockquote is not version metadata.\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

OUT_OF_ORDER_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
)

ORPHAN_REGION_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Orphan\n"
    "\n"
    "Orphan.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

# A leading ``---`` whose only exact close lies at/after the first ownership
# heading must not open frontmatter and hide operational prose.
FAKE_FRONTMATTER_CLOSE_LAYOUT = (
    "---\n"
    "name: x\n"
    "> **Rule layout:** two-section-v1\n"
    "OPERATIONAL PROSE THAT MUST BE REJECTED\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
    "---\n"
)

FENCED_FAKE_FRONTMATTER_CLOSE_LAYOUT = (
    "---\n"
    "name: x\n"
    "> **Rule layout:** two-section-v1\n"
    "OPERATIONAL PROSE THAT MUST BE REJECTED\n"
    "## Project extensions\n"
    "ext\n"
    "```markdown\n"
    "---\n"
    "```\n"
    "## Mandatory core\n"
    "CORE\n"
)

# A real ``--- ... ---`` block can still hide non-YAML operational prose.
HIDDEN_INTRO_IN_FRONTMATTER_LAYOUT = (
    "---\n"
    "name: x\n"
    "> ## Project extensions\n"
    "OPERATIONAL PROSE\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
)

# Indented prose inside a real block is not a YAML continuation of a key with a
# value, and an orphan indented list item has no preceding key/block opener.
INDENTED_HIDDEN_INTRO_LAYOUT = (
    "---\n"
    "name: x\n"
    "  > ## Project extensions\n"
    "  OPERATIONAL PROSE\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
)

ORPHAN_INDENTED_PROSE_LAYOUT = (
    "---\n"
    "  - OPERATIONAL PROSE\n"
    "name: x\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
)

TAB_H2_LAYOUT = VALID_LAYOUT.replace(
    "## Mandatory core\n",
    "##\tHidden region\n\n## Mandatory core\n",
)
INDENTED_H2_LAYOUT = VALID_LAYOUT.replace(
    "## Mandatory core\n",
    " ## Hidden region\n\n   ## Also hidden\n\n## Mandatory core\n",
)
INVALID_FENCE_INFO_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "```bad`info\n"
    "## Extra ownership\n"
    "```\n"
)
INVALID_CLOSER_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "```\n"
    "example\n"
    "``` trailing\n"
    "## Extra ownership\n"
)
SHORT_BACKTICK_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "`\n"
    "## Extra ownership\n"
)
SHORT_TILDE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "~~\n"
    "## Extra ownership\n"
)
INDENTED_CODE_FENCE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "    ```\n"
    "## Extra ownership\n"
    "    ```\n"
)
FRAMING_FENCE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "```markdown\n"
    "hidden operational prose\n"
    "```\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)
INTERNAL_TILDE_FENCE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "~~~markdown\n"
    "## Project extensions\n"
    "## Mandatory core\n"
    "~~~\n"
    "\n"
    "   ```\n"
    "   ## Not an ownership heading\n"
    "   ```\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
)
RICH_FRONTMATTER_LAYOUT = (
    "---\n"
    "# reviewer metadata\n"
    "name: reviewer\n"
    "description: |\n"
    "  reviews changes\n"
    "  across lines\n"
    "metadata:\n"
    "  owner: core\n"
    "  tags:\n"
    "    - layout\n"
    "---\n"
    "\n"
    "# Reviewer\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)
MALFORMED_SCALAR_LAYOUT = (
    "---\n"
    "name: \"unterminated\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "ext\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "CORE\n"
)
UNSAFE_TAG_LAYOUT = (
    "---\n"
    "name: !!python/object/apply:os.system [\"true\"]\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "ext\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "CORE\n"
)
LIST_FRONTMATTER_LAYOUT = (
    "---\n"
    "- not-a-mapping\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "ext\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "CORE\n"
)


_MARKER = "> **Rule layout:** two-section-v1\n"
_EXTENSIONS = _MARKER + "## Project extensions\n"
_CORE = "## Mandatory core\nCORE\n"
_VALID = _EXTENSIONS + _CORE
_ORPHAN = "orphan region: expected exactly two ownership headings"
_UNSUPPORTED = "orphan region: unsupported Markdown block context"
_SEPARATORS = (
    "\u000b",
    "\u000c",
    "\u001c",
    "\u001d",
    "\u001e",
    "\u0085",
    "\u2028",
    "\u2029",
)
_YAML_FORBIDDEN = ("\u000b", "\u000c", "\u001c", "\u001d", "\u001e")
_YAML_QUOTED_SEPARATORS = ("\u0085", "\u2028", "\u2029")


def _assert_valid(document: str) -> None:
    layout, violation = _scan_rule_layout(document)
    assert layout is not None, violation
    assert violation is None
    assert layout.framing + layout.extensions + layout.mandatory == document.encode("utf-8")


class LayoutContractTests:
    """Single layout owner: corpus partitions and distinct boundary attacks.

    Parser cases do not inherit the repository fixture. One scan supplies both
    the layout and the diagnostic.
    """

    def test_valid_framing_with_quotations_accepts(self) -> None:
        layout = _rule_layout(QUOTED_LAYOUT)
        assert layout is not None
        assert layout.mandatory.endswith(b"Core rule.\n")
        assert b"Inline quotation" in layout.extensions
        assert _rule_layout_violation(QUOTED_LAYOUT) is None
        # The quoted fenced headings are not ownership boundaries: only the two
        # real headings are extracted, so the mandatory core matches exactly.
        quoted = _rule_layout(QUOTED_LAYOUT)
        plain = _rule_layout(VALID_LAYOUT)
        assert quoted is not None and plain is not None
        assert quoted.mandatory == plain.mandatory
        assert quoted.framing == plain.framing
        assert quoted.extensions != plain.extensions

    @pytest.mark.parametrize(
        ("document", "fragment"),
        (
            (MISSING_MARKER_LAYOUT, "missing"),
            (DUPLICATE_MARKER_LAYOUT, "duplicate"),
            (MISPLACED_MARKER_LAYOUT, "precede"),
            (OPERATIONAL_INTRO_LAYOUT, "operational prose"),
            (BLOCKQUOTED_INTRO_LAYOUT, "operational prose"),
            (FAKE_FRONTMATTER_CLOSE_LAYOUT, "operational prose"),
            (FENCED_FAKE_FRONTMATTER_CLOSE_LAYOUT, "operational prose"),
            (HIDDEN_INTRO_IN_FRONTMATTER_LAYOUT, "operational prose"),
            (INDENTED_HIDDEN_INTRO_LAYOUT, "operational prose"),
            (ORPHAN_INDENTED_PROSE_LAYOUT, "operational prose"),
            (OUT_OF_ORDER_LAYOUT, "first ownership heading"),
            (ORPHAN_REGION_LAYOUT, "orphan region"),
        ),
    )
    def test_marker_contract_rejections(self, document: str, fragment: str) -> None:
        layout, violation = _scan_rule_layout(document)
        assert layout is None
        assert violation is not None
        assert fragment in violation

    def test_bounded_frontmatter_close_accepts_valid_frontmatter(self) -> None:
        assert _rule_layout_violation(VALID_FRONTMATTER_LAYOUT) is None
        layout = _rule_layout(VALID_FRONTMATTER_LAYOUT)
        assert layout is not None
        assert b"Persona / personality" in layout.framing
        assert layout.mandatory.endswith(b"Core.\n")

    def test_mandatory_bytes_ignore_framing_and_extension_differences(self) -> None:
        source = _rule_layout(VALID_LAYOUT)
        destination = _rule_layout(
            VALID_LAYOUT.replace("# Reviewer", "# Relay").replace(
                "Extension note.", "Destination extension note."
            )
        )
        assert source is not None and destination is not None
        assert source.mandatory == destination.mandatory
        assert source.extensions != destination.extensions
        assert source.framing != destination.framing

    def test_noncanonical_headings_and_invalid_fences_reject(self) -> None:
        for document, fragment in (
            (TAB_H2_LAYOUT, "orphan region"),
            (INDENTED_H2_LAYOUT, "orphan region"),
            (INVALID_FENCE_INFO_LAYOUT, "orphan region"),
            (INDENTED_CODE_FENCE_LAYOUT, "orphan region"),
            (SHORT_BACKTICK_LAYOUT, "orphan region"),
            (SHORT_TILDE_LAYOUT, "orphan region"),
            (FRAMING_FENCE_LAYOUT, "operational prose"),
        ):
            violation = _rule_layout_violation(document)
            assert violation is not None, document
            assert fragment in violation, (fragment, violation)
        layout = _rule_layout(INVALID_CLOSER_LAYOUT)
        assert layout is not None
        assert _rule_layout_violation(INVALID_CLOSER_LAYOUT) is None
        assert b"``` trailing\n## Extra ownership\n" in layout.mandatory

    def test_internal_fences_do_not_create_ownership_regions(self) -> None:
        layout = _rule_layout(INTERNAL_TILDE_FENCE_LAYOUT)
        assert layout is not None
        assert layout.mandatory == _rule_layout(VALID_LAYOUT).mandatory
        assert b"## Project extensions" in layout.extensions
        assert _rule_layout_violation(INTERNAL_TILDE_FENCE_LAYOUT) is None

    def test_yaml_mapping_frontmatter_accepts_comments_blocks_and_nesting(self) -> None:
        layout = _rule_layout(RICH_FRONTMATTER_LAYOUT)
        assert layout is not None
        assert _rule_layout_violation(RICH_FRONTMATTER_LAYOUT) is None
        assert layout.mandatory.endswith(b"Core.\n")
        assert b"reviews changes" in layout.framing

    def test_malformed_frontmatter_rejects_without_inferring_prose(self) -> None:
        for document in (
            MALFORMED_SCALAR_LAYOUT,
            UNSAFE_TAG_LAYOUT,
            LIST_FRONTMATTER_LAYOUT,
        ):
            violation = _rule_layout_violation(document)
            assert violation is not None, document
            assert "operational prose" in violation
            assert "YAML" in violation or "mapping" in violation

    def test_mandatory_slice_is_the_unnormalized_byte_suffix(self) -> None:
        document = VALID_LAYOUT.replace("Core rule.\n", "Core rule.  \n")
        layout = _rule_layout(document)
        assert layout is not None
        start = document.index("## Mandatory core\n")
        assert layout.mandatory == document[start:].encode("utf-8")
        assert layout.mandatory.endswith(b"Core rule.  \n")

    def test_every_catalog_rule_document_has_a_valid_layout(self) -> None:
        root = repository_root()
        catalog = load_catalog(str(root / ".aicore" / "core-catalog-v2.yaml"))
        paths = [
            str(document)
            for unit in catalog["units"]
            for document in (unit.get("rule_documents") or [])
        ]
        distinct = sorted(set(paths))
        assert len(distinct) == 27, distinct
        for document in distinct:
            raw = (root / document).read_bytes()
            text = raw.decode("utf-8")
            layout, violation = _scan_rule_layout(text)
            assert layout is not None, (document, violation)
            assert layout.framing + layout.extensions + layout.mandatory == raw

    def test_p01_valid_document_keeps_exact_mandatory_bytes(self) -> None:
        _assert_valid(_VALID)
        layout = _rule_layout(_VALID)
        assert layout is not None
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p02_trailing_info_before_mandatory_is_orphan(self) -> None:
        document = _EXTENSIONS + "~~~text\n~~~not-a-close\n" + _CORE
        assert _rule_layout(document) is None
        assert _rule_layout_violation(document) == _ORPHAN
        assert document.endswith(_CORE)

    def test_p03_later_valid_closer_keeps_example_fenced(self) -> None:
        document = _EXTENSIONS + "~~~text\n~~~not-a-close\n## Example\n~~~\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p04_shorter_closer_is_literal(self) -> None:
        document = _EXTENSIONS + "````\n```\n## Example\n````\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions

    def test_p05_other_delimiter_is_literal(self) -> None:
        document = _EXTENSIONS + "```\n~~~\n## Example\n```\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions

    def test_p06_indented_closer_is_literal(self) -> None:
        document = _EXTENSIONS + "```\n    ```\n## Example\n```\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions

    def test_p07_unclosed_trailing_info_is_valid_mandatory_drift(self) -> None:
        document = _VALID + "```\n``` trailing\n## Example\n"
        _assert_valid(document)
        base = _rule_layout(_VALID)
        drifted = _rule_layout(document)
        assert base is not None and drifted is not None
        assert drifted.mandatory != base.mandatory
        assert b"## Example\n" in drifted.mandatory

    def test_p08_invalid_openers_do_not_hide_extra_headings(self) -> None:
        for document in (
            _VALID + "```bad`info\n## Extra\n",
            _VALID + "`\n## Extra\n",
            _VALID + "~~\n## Extra\n",
        ):
            assert _rule_layout_violation(document) == _ORPHAN

    def test_p09_dash_setext_underlines_are_extra_headings(self) -> None:
        for underline in ("---", "-", "--"):
            document = _EXTENSIONS + "Extra\n" + underline + "\n" + _CORE
            assert _rule_layout_violation(document) == _ORPHAN

    def test_container_shaped_setext_underline_is_orphan(self) -> None:
        document = _EXTENSIONS + "Extra ownership\n- \n" + _CORE
        assert _rule_layout_violation(document) == _ORPHAN
        _assert_valid(_EXTENSIONS + "- item\n" + _CORE)

    def test_p10_multiline_paragraph_setext_is_extra_heading(self) -> None:
        document = _EXTENSIONS + "First line\nsecond line\n---\n" + _CORE
        assert _rule_layout_violation(document) == _ORPHAN

    def test_p11_blank_line_resets_setext_paragraph(self) -> None:
        _assert_valid(_EXTENSIONS + "Extra\n\n---\n" + _CORE)

    def test_p12_atx_does_not_seed_setext(self) -> None:
        for heading in ("### Example", "# Example"):
            _assert_valid(_EXTENSIONS + heading + "\n---\n" + _CORE)

    def test_p13_thematic_break_and_equals_setext_are_not_h2(self) -> None:
        _assert_valid(_EXTENSIONS + "Extra\n- - -\n" + _CORE)
        _assert_valid(_EXTENSIONS + "Extra\n===\n---\n" + _CORE)

    def test_p14_fenced_and_indented_setext_examples_are_literal(self) -> None:
        _assert_valid(_EXTENSIONS + "```\nExtra\n---\n```\n" + _CORE)
        _assert_valid(_EXTENSIONS + "\n    Extra\n    ---\n" + _CORE)

    def test_p15_setext_is_not_a_canonical_ownership_spelling(self) -> None:
        document = _MARKER + "Project extensions\n---\n" + _CORE
        violation = _rule_layout_violation(document)
        assert violation == "first ownership heading must be '## Project extensions'"

    def test_p16_indented_continuation_before_setext_is_unsupported(self) -> None:
        document = _EXTENSIONS + "Extra\n    continuation\n---\n" + _CORE
        assert _rule_layout_violation(document) == _UNSUPPORTED

    def test_p17_block_and_folded_scalars_do_not_enter_markdown_state(self) -> None:
        for indicator in ("|", ">"):
            document = (
                "---\n"
                f"description: {indicator}\n"
                "  ## Fake\n"
                "  ```\n"
                "  Extra\n"
                "  ---\n"
                "  > **Rule layout:** two-section-v1\n"
                "---\n"
                + _VALID
            )
            _assert_valid(document)
            layout = _rule_layout(document)
            assert layout is not None
            assert layout.mandatory == _CORE.encode("utf-8")
            assert b"## Fake\n" in layout.framing

    def test_p18_quoted_scalar_example_does_not_enter_markdown_state(self) -> None:
        document = (
            "---\n"
            'description: "text\n'
            "## Fake\n"
            "```\n"
            "> **Rule layout:** two-section-v1\n"
            '"\n'
            "---\n"
            + _VALID
        )
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Fake\n" in layout.framing
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p19_mapping_accepts_and_nonmapping_malformed_and_unsafe_reject(self) -> None:
        mapping = (
            "---\n"
            "# reviewer metadata\n"
            "name: reviewer\n"
            "metadata:\n"
            "  owner: core\n"
            "---\n"
            + _VALID
        )
        _assert_valid(mapping)
        sequence = "---\n- not-a-mapping\n---\n" + _VALID
        unterminated = '---\nname: "unterminated\n---\n' + _VALID
        unsafe = '---\nname: !!python/object/apply:os.system ["true"]\n---\n' + _VALID
        for document in (sequence, unterminated, unsafe):
            violation = _rule_layout_violation(document)
            assert violation is not None
            assert violation.startswith("operational prose outside ownership sections: ")
            assert "invalid YAML framing" in violation or "YAML mapping" in violation

    def test_p20_missing_late_and_heading_frontmatter_never_accept(self) -> None:
        missing = "---\nname: x\n" + _VALID
        assert _rule_layout_violation(missing) == (
            "operational prose outside ownership sections: "
            "missing bounded YAML frontmatter close"
        )
        late = missing + "---\n"
        late_violation = _rule_layout_violation(late)
        assert late_violation is not None
        assert late_violation.startswith("operational prose outside ownership sections: ")
        hidden = (
            "---\n"
            "name: x\n"
            "## Project extensions\n"
            "## Mandatory core\n"
            "---\n"
            + _VALID
        )
        assert _rule_layout_violation(hidden) == (
            "operational prose outside ownership sections: "
            "frontmatter close must precede ownership headings"
        )

    def test_p21_crlf_trailing_spaces_and_missing_newline_partition_exactly(self) -> None:
        document = (
            "# Reviewer café\r\n"
            "> **Rule layout:** two-section-v1\r\n"
            "\r\n"
            "## Project extensions\r\n"
            "\r\n"
            "Extension note.  \r\n"
            "## Mandatory core\r\n"
            "Core rule.  "
        )
        layout = _rule_layout(document)
        assert layout is not None
        raw = document.encode("utf-8")
        assert layout.framing + layout.extensions + layout.mandatory == raw
        assert layout.framing == document[: document.index("## Project extensions")].encode("utf-8")
        assert layout.extensions == document[
            document.index("## Project extensions") : document.index("## Mandatory core")
        ].encode("utf-8")
        assert layout.mandatory == document[document.index("## Mandatory core") :].encode("utf-8")
        assert b"\r\n" in layout.mandatory
        assert b"\n" not in layout.mandatory.replace(b"\r\n", b"")

    def test_p23_quote_list_and_table_examples_do_not_seed_headings(self) -> None:
        document = (
            _EXTENSIONS
            + "> ## Quoted example\n"
            + "\n"
            + "- List item\n"
            + "\n"
            + "| A | B |\n"
            + "| --- | --- |\n"
            + "| ## Literal | row |\n"
            + "\n"
            + _CORE
        )
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"> ## Quoted example\n" in layout.extensions
        assert b"| ## Literal | row |\n" in layout.extensions
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p24_lazy_container_continuation_is_unsupported(self) -> None:
        document = _EXTENSIONS + "- Item\ncontinuation\n---\n" + _CORE
        assert _rule_layout_violation(document) == _UNSUPPORTED

    def test_p25_standalone_html_opener_is_unsupported(self) -> None:
        document = _EXTENSIONS + "<div>\n## Hidden\n</div>\n" + _CORE
        assert _rule_layout_violation(document) == _UNSUPPORTED

    def test_p26_inline_and_fenced_html_remain_literal(self) -> None:
        document = (
            _EXTENSIONS
            + "Use <span>inline</span> text.\n"
            + "\n"
            + "```html\n"
            + "<div>\n"
            + "## Example\n"
            + "</div>\n"
            + "```\n"
            + _CORE
        )
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"<div>\n" in layout.extensions
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p27_cr_only_partitions_are_not_normalized(self) -> None:
        document = _VALID.replace("\n", "\r")
        layout = _rule_layout(document)
        assert layout is not None
        raw = document.encode("utf-8")
        assert layout.framing + layout.extensions + layout.mandatory == raw
        assert b"\n" not in raw
        assert layout.mandatory == _CORE.replace("\n", "\r").encode("utf-8")

    def test_p28_separator_fence_and_yaml_controls_follow_reader_rules(self) -> None:
        for separator in _SEPARATORS:
            body = _EXTENSIONS + "text" + separator + "## Extra\n" + _CORE
            assert _rule_layout_violation(body) == _UNSUPPORTED, repr(separator)
            fenced = _EXTENSIONS + "```text\nA" + separator + "B\n```\n" + _CORE
            _assert_valid(fenced)
            layout = _rule_layout(fenced)
            assert layout is not None
            assert separator.encode("utf-8") in (
                layout.framing + layout.extensions + layout.mandatory
            )
        for control in _YAML_FORBIDDEN:
            document = '---\ndescription: "A' + control + 'B"\n---\n' + _VALID
            violation = _rule_layout_violation(document)
            assert violation is not None
            assert violation.startswith(
                "operational prose outside ownership sections: invalid YAML framing"
            )
        for separator in _YAML_QUOTED_SEPARATORS:
            document = '---\ndescription: "A' + separator + 'B"\n---\n' + _VALID
            _assert_valid(document)
            layout = _rule_layout(document)
            assert layout is not None
            assert separator.encode("utf-8") in layout.framing
        for escape in ("\\x0B", "\\x0C", "\\x1C", "\\x1D", "\\x1E"):
            document = '---\ndescription: "A' + escape + 'B"\n---\n' + _VALID
            _assert_valid(document)
            assert escape in document
            assert "\u000b" not in document
            assert "\u000c" not in document
            assert "\u001c" not in document
            assert "\u001d" not in document
            assert "\u001e" not in document
