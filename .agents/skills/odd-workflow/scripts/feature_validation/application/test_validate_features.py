"""Test feature-validation orchestration through a deterministic source fake."""

from __future__ import annotations

import sys
from pathlib import Path, PurePath

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from feature_testkit import make_feature  # noqa: E402
from feature_validation.application.validate_features import execute  # noqa: E402
from feature_validation.domain.records import (  # noqa: E402
    InvalidFeatureError,
    NoFeatureDocumentsError,
    ValidFeature,
)


class FeatureSourceFake:
    """Supply factory-built documents and record reads without filesystem IO."""

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
        mixed_case: bool = False,
        no_features: bool = False,
        template_only: bool = False,
    ) -> FeatureSourceFake:
        """Build a source with intentionally unsorted feature references."""
        if no_features:
            if template_only:
                reference = "features/_template.md"
                return cls({reference: make_feature(title="Feature name")}, (reference,))
            return cls({}, ())
        if mixed_case:
            references = (
                "features/b.md",
                "features/B.md",
                "features/a.md",
                "features/Z.md",
            )
            return cls(
                {reference: make_feature() for reference in references},
                references,
            )
        documents = {
            "features/_template.md": make_feature(title="Feature name"),
            "features/a.md": make_feature(
                title="Feature name" if invalid else "Sample feature"
            ),
            "features/z.md": make_feature(),
        }
        return cls(
            documents,
            ("features/z.md", "features/_template.md", "features/a.md"),
            OSError("later document cannot be read") if later_read_fails else None,
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


def test_validation_sorts_features_and_never_reads_template() -> None:
    source = FeatureSourceFake.create()

    results = list(execute("features", source))

    assert source.targets == ["features"]
    assert source.reads == ["features/a.md", "features/z.md"]
    assert all(isinstance(result, ValidFeature) for result in results)
    assert [result.path for result in results] == source.reads


def test_invalid_feature_is_returned_as_typed_error_with_original_findings() -> None:
    source = FeatureSourceFake.create(invalid=True)

    results = list(execute("features", source))

    assert len(results) == 2
    rejection = results[0]
    assert isinstance(rejection, InvalidFeatureError)
    assert rejection.code == "FEATURE_INVALID"
    assert rejection.path == "features/a.md"
    assert rejection.findings == ("title must not be the template placeholder",)
    assert isinstance(results[1], ValidFeature)


def test_validation_preserves_host_path_order_and_stable_equivalent_keys() -> None:
    source = FeatureSourceFake.create(mixed_case=True)
    expected = sorted(source.references, key=PurePath)

    results = list(execute("features", source))

    assert source.reads == expected
    assert [result.path for result in results] == expected
    first, second = source.references[:2]
    if PurePath(first) == PurePath(second):
        assert source.reads.index(first) < source.reads.index(second)


@pytest.mark.parametrize("template_only", (False, True))
def test_empty_selection_returns_typed_error_without_reads(template_only: bool) -> None:
    source = FeatureSourceFake.create(no_features=True, template_only=template_only)

    results = list(execute("features", source))

    assert len(results) == 1
    assert isinstance(results[0], NoFeatureDocumentsError)
    assert results[0].code == "NO_FEATURE_DOCUMENTS"
    assert source.targets == ["features"]
    assert source.reads == []


def test_validation_yields_earlier_result_before_later_read_exception() -> None:
    source = FeatureSourceFake.create(later_read_fails=True)

    results = iter(execute("features", source))
    first = next(results)

    assert isinstance(first, ValidFeature)
    assert first.path == "features/a.md"
    assert source.reads == ["features/a.md"]
    with pytest.raises(OSError) as raised:
        next(results)
    assert raised.value is source.read_error
    assert source.reads == ["features/a.md", "features/z.md"]
