"""Read local inputs and exclusively create review artifacts without overwriting."""

from pathlib import Path


def read_text(path: str) -> str:
    """Read UTF-8 bytes without newline translation."""
    with Path(path).open("r", encoding="utf-8", newline="") as stream:
        return stream.read()


def create_text(path: str, content: str) -> None:
    """Create a new artifact exclusively, leaving existing files untouched."""
    with Path(path).open("x", encoding="utf-8", newline="") as stream:
        stream.write(content)
