"""Factory for Problem.create table-cell arguments and valid Problem instances."""

from __future__ import annotations

from .entities import Problem


class _ProblemData:
    """Factory for Problem.create table-cell arguments."""

    ID = "P-001"
    DATE = "2026-01-01"
    TEAM = "incident"
    SYMPTOM = "S-05"
    SYSTEM = "sys"
    MODULE = "mod"
    PROBLEM = "slow CDN"
    DISCRIMINATORS = "host=cdn-a"
    EXCLUSIONS = "host=cdn-b"
    EVIDENCE = "log:42"
    ROOT_CAUSE = "cache miss"
    LIFECYCLE = "active"
    ALLOW_EXACT = "yes"
    STATUS = "open"
    TEAM_DEV = "dev"
    LIFECYCLE_CANDIDATE = "candidate"
    LIFECYCLE_MITIGATED = "mitigated"
    LIFECYCLE_RESOLVED = "resolved"
    LIFECYCLE_RETIRED = "retired"
    ALLOW_EXACT_NO = "no"
    INVALID_TEAM = "ops"
    INVALID_LIFECYCLE = "bogus"
    INVALID_ALLOW_EXACT = "maybe"
    INVALID_STATUS = "pending"
    NO_SYMPTOM = "no class"

    @classmethod
    def create(cls, **overrides: str) -> dict[str, str]:
        """Return one complete cell mapping, with optional field overrides."""
        cells = {
            "id": cls.ID,
            "date": cls.DATE,
            "team": cls.TEAM,
            "symptom": cls.SYMPTOM,
            "system": cls.SYSTEM,
            "module": cls.MODULE,
            "problem": cls.PROBLEM,
            "discriminators": cls.DISCRIMINATORS,
            "exclusions": cls.EXCLUSIONS,
            "evidence": cls.EVIDENCE,
            "root_cause": cls.ROOT_CAUSE,
            "lifecycle": cls.LIFECYCLE,
            "allow_exact": cls.ALLOW_EXACT,
            "status": cls.STATUS,
        }
        cells.update(overrides)
        return cells

    @classmethod
    def entity(cls, **overrides: str) -> Problem:
        """Create a valid Problem; fail when create rejects the cells."""
        result = Problem.create(**cls.create(**overrides))
        assert isinstance(result, Problem), result
        return result
