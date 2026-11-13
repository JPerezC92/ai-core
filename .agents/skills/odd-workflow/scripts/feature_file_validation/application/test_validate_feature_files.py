"""Test feature-file validation orchestration through a deterministic source fake."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from feature_file_validation.application.validate_feature_files import execute  # noqa: E402
from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_malformed_requirement,
)
from feature_file_validation.domain.records import (  # noqa: E402
    InvalidFeatureFileError,
    NoFeatureFileDocumentsError,
    ValidFeatureFile,
)


class FeatureFileSourceFake:
    """Supply factory-built feature files and record reads without filesystem IO."""

    def __init__(
        self,
        documents: dict[str, str],
        references: tuple[str, ...],
        read_error: OSError | None = None,
    ) -> None:
        self.documents = documents
        self.references = references
        self.read_error = read_error
        self.reads: list[str] = []
        self.targets: list[str] = []

    @classmethod
    def create(
        cls,
        *,
        invalid: bool = False,
        later_read_fails: bool = False,
        no_files: bool = False,
        template_only: bool = False,
    ) -> FeatureFileSourceFake:
        """Build a source with intentionally unsorted feature-file references."""
        if no_files:
            if template_only:
                reference = "features/_template.md"
                return cls({reference: make_feature_file()}, (reference,))
            return cls({}, ())
        documents = {
            "features/_template.md": make_feature_file(),
            "features/a.md": (
                make_feature_file(requirement_entries=(make_malformed_requirement(),))
                if invalid
                else make_feature_file()
            ),
            "features/z.md": make_feature_file(),
        }
        return cls(
            documents,
            ("features/z.md", "features/_template.md", "features/a.md"),
            OSError("later feature file cannot be read") if later_read_fails else None,
        )

    def discover(self, target: str) -> tuple[str, ...]:
        """Return references in source order rather than policy order."""
        self.targets.append(target)
        return self.references

    def read(self, reference: str) -> str:
        """Return text or propagate the configured later-read boundary error."""
        self.reads.append(reference)
        if reference == "features/z.md" and self.read_error is not None:
            raise self.read_error
        return self.documents[reference]


def test_validation_sorts_feature_files_and_never_reads_the_template() -> None:
    source = FeatureFileSourceFake.create()

    results = list(execute("features", source))

    assert source.targets == ["features"]
    assert source.reads == ["features/a.md", "features/z.md"]
    assert all(isinstance(result, ValidFeatureFile) for result in results)
    assert [result.path for result in results] == source.reads


def test_valid_feature_file_carries_the_derived_status() -> None:
    source = FeatureFileSourceFake.create()

    results = list(execute("features", source))

    assert results[0].status == "partial"


def test_invalid_feature_file_is_returned_as_typed_error_with_original_findings() -> None:
    source = FeatureFileSourceFake.create(invalid=True)

    results = list(execute("features", source))

    rejection = results[0]
    assert isinstance(rejection, InvalidFeatureFileError)
    assert rejection.code == "FEATURE_FILE_INVALID"
    assert rejection.path == "features/a.md"
    assert any(
        finding.startswith("feature-file-requirement-entry:")
        for finding in rejection.findings
    )
    assert isinstance(results[1], ValidFeatureFile)


@pytest.mark.parametrize("template_only", (False, True))
def test_empty_selection_returns_typed_error_without_reads(template_only: bool) -> None:
    source = FeatureFileSourceFake.create(no_files=True, template_only=template_only)

    results = list(execute("features", source))

    assert len(results) == 1
    assert isinstance(results[0], NoFeatureFileDocumentsError)
    assert results[0].code == "NO_FEATURE_FILE_DOCUMENTS"
    assert source.targets == ["features"]
    assert source.reads == []


def test_validation_yields_earlier_result_before_later_read_exception() -> None:
    source = FeatureFileSourceFake.create(later_read_fails=True)

    results = iter(execute("features", source))
    first = next(results)

    assert isinstance(first, ValidFeatureFile)
    assert first.path == "features/a.md"
    assert source.reads == ["features/a.md"]
    with pytest.raises(OSError) as raised:
        next(results)
    assert raised.value is source.read_error
    assert source.reads == ["features/a.md", "features/z.md"]
