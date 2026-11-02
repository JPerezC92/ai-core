"""Read feature-document candidates and text from the local filesystem."""

from pathlib import Path

from feature_closure.domain.ports import FeatureDocumentSource


class FilesystemFeatureSource(FeatureDocumentSource):
    """Map filesystem paths and UTF-8 contents to the document-source port."""

    def discover(self, target: str) -> tuple[str, ...]:
        """Return directory Markdown candidates or the normalized target path."""
        path = Path(target)
        if path.is_dir():
            return tuple(str(candidate) for candidate in path.glob("*.md"))
        return (str(path),)

    def read(self, reference: str) -> str:
        """Read UTF-8 text without reclassifying filesystem exceptions."""
        return Path(reference).read_text(encoding="utf-8")
