"""Identity-bearing Problem register entity and named domain values."""

from __future__ import annotations

import re
from enum import Enum
from typing import Self

from .errors import (
    CODE_INVALID_ALLOW_EXACT,
    CODE_INVALID_LIFECYCLE,
    CODE_INVALID_STATUS,
    CODE_INVALID_TEAM,
    CODE_MISSING_SYMPTOM,
    DomainError,
)

_SYMPTOM_ID_RE = re.compile(r"S-\d{2}")


class _NamedCell(str, Enum):
    """A closed domain value parsed once from a table cell."""

    @classmethod
    def from_cell(cls, cell: str) -> Self | None:
        try:
            return cls(cell)
        except ValueError:
            return None


class Team(_NamedCell):
    """Owning team of a problem-register row."""

    INCIDENT = "incident"
    DEV = "dev"


class Lifecycle(_NamedCell):
    """Lifecycle of a problem-register row."""

    CANDIDATE = "candidate"
    ACTIVE = "active"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    RETIRED = "retired"


class AllowExact(_NamedCell):
    """Whether an incident row may produce an exact identification verdict."""

    YES = "yes"
    NO = "no"


class Status(_NamedCell):
    """Open or closed status of a problem-register row."""

    OPEN = "open"
    CLOSED = "closed"


class IdentificationVerdict(_NamedCell):
    """Identification verdict recorded against one or more Problems."""

    PENDING = "pending"
    EXACT = "exact"
    STRUCTURAL = "structural"
    NO_MATCH = "no_match"


MATCHABLE_LIFECYCLES: frozenset[Lifecycle] = frozenset(
    {
        Lifecycle.CANDIDATE,
        Lifecycle.ACTIVE,
        Lifecycle.MITIGATED,
    }
)


class Problem:
    """One valid problem-register row with identity and row-owned rules."""

    def __init__(
        self,
        id: str,
        date: str,
        team: Team,
        symptom: str,
        system: str,
        module: str,
        problem: str,
        discriminators: str,
        exclusions: str,
        evidence: str,
        root_cause: str,
        lifecycle: Lifecycle,
        allow_exact: AllowExact,
        status: Status,
    ) -> None:
        self._id = id
        self._date = date
        self._team = team
        self._symptom = symptom
        self._system = system
        self._module = module
        self._problem = problem
        self._discriminators = discriminators
        self._exclusions = exclusions
        self._evidence = evidence
        self._root_cause = root_cause
        self._lifecycle = lifecycle
        self._allow_exact = allow_exact
        self._status = status

    @classmethod
    def create(
        cls,
        id: str,
        date: str,
        team: str,
        symptom: str,
        system: str,
        module: str,
        problem: str,
        discriminators: str,
        exclusions: str,
        evidence: str,
        root_cause: str,
        lifecycle: str,
        allow_exact: str,
        status: str,
    ) -> Problem | DomainError:
        """Map table-cell text once and return a valid Problem or a domain error."""
        named_team = Team.from_cell(team)
        if named_team is None:
            return DomainError(code=CODE_INVALID_TEAM, message=team)
        named_lifecycle = Lifecycle.from_cell(lifecycle)
        if named_lifecycle is None:
            return DomainError(code=CODE_INVALID_LIFECYCLE, message=lifecycle)
        named_allow_exact = AllowExact.from_cell(allow_exact)
        if named_allow_exact is None:
            return DomainError(code=CODE_INVALID_ALLOW_EXACT, message=allow_exact)
        named_status = Status.from_cell(status)
        if named_status is None:
            return DomainError(code=CODE_INVALID_STATUS, message=status)
        if _SYMPTOM_ID_RE.search(symptom) is None:
            return DomainError(code=CODE_MISSING_SYMPTOM, message=symptom)
        return cls(
            id=id,
            date=date,
            team=named_team,
            symptom=symptom,
            system=system,
            module=module,
            problem=problem,
            discriminators=discriminators,
            exclusions=exclusions,
            evidence=evidence,
            root_cause=root_cause,
            lifecycle=named_lifecycle,
            allow_exact=named_allow_exact,
            status=named_status,
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def date(self) -> str:
        return self._date

    @property
    def team(self) -> Team:
        return self._team

    @property
    def symptom(self) -> str:
        return self._symptom

    @property
    def system(self) -> str:
        return self._system

    @property
    def module(self) -> str:
        return self._module

    @property
    def problem(self) -> str:
        return self._problem

    @property
    def discriminators(self) -> str:
        return self._discriminators

    @property
    def exclusions(self) -> str:
        return self._exclusions

    @property
    def evidence(self) -> str:
        return self._evidence

    @property
    def root_cause(self) -> str:
        return self._root_cause

    @property
    def lifecycle(self) -> Lifecycle:
        return self._lifecycle

    @property
    def allow_exact(self) -> AllowExact:
        return self._allow_exact

    @property
    def status(self) -> Status:
        return self._status

    @property
    def is_incident(self) -> bool:
        return self._team is Team.INCIDENT

    @property
    def is_matchable(self) -> bool:
        return self._lifecycle in MATCHABLE_LIFECYCLES

    @property
    def is_exact_match_eligible(self) -> bool:
        return (
            self._lifecycle is Lifecycle.ACTIVE
            and self._allow_exact is AllowExact.YES
        )
