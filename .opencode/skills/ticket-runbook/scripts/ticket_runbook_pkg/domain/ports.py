"""Injected domain ports for register-row loading and clock acquisition."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .entities import ProblemRow


class RegisterRowsPort(Protocol):
    """Injected IO port that loads problem-register rows on demand."""

    def __call__(self) -> list[ProblemRow]: ...


class ClockPort(Protocol):
    """Injected clock port returning one local naive timestamp per call."""

    def __call__(self) -> datetime: ...
