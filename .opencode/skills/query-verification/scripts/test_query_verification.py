"""Standard-library tests for the query-verification pilot.

The suite proves that ``query_verification.py`` validates a bounded, read-only,
adjacent incident verifier beneath an explicit query root and evaluates trusted
normalized adapter output entirely offline. Adversarial source, sidecar, and
output cases are written to temporary directories; the happy path uses the
static fixture trio under ``../fixtures/valid/``.

The static adapter fixture declares the real ``source_digest`` of the fixture
``.sql`` bytes. The happy-path loader asserts that declared digest equals the
digest recomputed from those bytes, so any source drift fails the suite.

Run: python3 .opencode/skills/query-verification/scripts/test_query_verification.py
"""

import contextlib
import copy
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Mapping, Optional, TypedDict, cast

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import query_verification as qv  # noqa: E402


SCRIPTS_DIR: Path = Path(__file__).parent
FIXTURES_DIR: Path = Path(__file__).parents[1] / "fixtures" / "valid"

VALID_SOURCE_NAME: str = "incident-check.sql"
VALID_SIDECAR_NAME: str = "incident-check.verifier.yaml"
VALID_ADAPTER_NAME: str = "adapter-output.json"
VALID_VERIFIER_ID: str = "incident.incident-check.v1"
VALID_VERDICT: str = "verified"
VALID_CASE_REFERENCE: str = "CASE-EXAMPLE-0001"
REDACTED: str = "[REDACTED]"
VERIFICATION_RESULT_SET: str = "verification"

# Code constructs that must never appear in a production pilot script. These
# target imports, process/network calls, environment reads, and dynamic SQL
# rendering — never prose words that legitimately appear in comments or in the
# module's own unsafe-keyword denylist.
_FORBIDDEN_SCRIPT_PATTERNS: tuple[str, ...] = (
    r"(?m)^\s*import\s+(?:sqlite3|psycopg2?|pymysql|MySQLdb|sqlalchemy|asyncpg|aiomysql|aiosqlite|pyodbc|oracledb|cx_Oracle|pymongo|redis|boto3|duckdb|clickhouse_driver)\b",
    r"(?m)^\s*from\s+(?:sqlite3|psycopg2?|pymysql|MySQLdb|sqlalchemy|asyncpg|aiomysql|aiosqlite|pyodbc|oracledb|cx_Oracle|pymongo|redis|boto3|duckdb|clickhouse_driver)\b",
    r"(?m)^\s*import\s+(?:socket|requests|httpx|aiohttp|urllib3|http\.client|urllib\.request)\b",
    r"(?m)^\s*from\s+(?:socket|requests|httpx|aiohttp|urllib3|http\.client|urllib\.request)\b",
    r"(?m)^\s*import\s+(?:subprocess|pty|shlex)\b",
    r"(?m)^\s*from\s+(?:subprocess|pty|shlex)\b",
    r"\bsubprocess\.\w+\s*\(",
    r"\bos\.system\s*\(",
    r"\bos\.popen\s*\(",
    r"\bos\.exec\w*\s*\(",
    r"\bos\.spawn\w*\s*\(",
    r"\bshell\s*=\s*True\b",
    r"\bos\.environ\b",
    r"\bos\.getenv\s*\(",
    r"(?m)^\s*(?:import|from)\s+dotenv\b",
    r"\bre\.sub\s*\(",
    r"\.format\s*\(",
    r"\bsubstitute\s*\(",
    r"\bTemplate\s*\(",
    r"[fF]['\"]{0,3}\s*(?:SELECT|INSERT|UPDATE|DELETE|WITH|DROP|ALTER|CREATE)\b",
    r"\+\s*['\"]\s*(?:SELECT|INSERT|UPDATE|DELETE|WITH|DROP|ALTER|CREATE)\b",
)

_DIGEST_RE: re.Pattern[str] = re.compile(r"^sha256:[0-9a-f]{64}$")


class AdapterRow(TypedDict):
    """One normalized adapter result row for the fixture verifier."""

    verification_verdict: str
    case_reference: str
    matched_rows: int


class SidecarDocument(TypedDict):
    """The fixture verifier sidecar document (closed v1 shape)."""

    schema_version: int
    id: str
    team: str
    source: str
    symptoms: list[str]
    purpose: str
    parameters: list[dict[str, object]]
    safety: dict[str, object]
    result_set: dict[str, object]
    evidence_columns: list[str]
    redact_columns: list[str]


def _read_source_bytes() -> bytes:
    """Return the raw bytes of the static fixture ``.sql`` source."""
    return (FIXTURES_DIR / VALID_SOURCE_NAME).read_bytes()


def _read_source_text() -> str:
    """Return the UTF-8 text of the static fixture ``.sql`` source."""
    return (FIXTURES_DIR / VALID_SOURCE_NAME).read_text(encoding="utf-8")


def _base_sidecar() -> SidecarDocument:
    """Return a fresh valid fixture sidecar document."""
    return {
        "schema_version": 1,
        "id": VALID_VERIFIER_ID,
        "team": "incident",
        "source": VALID_SOURCE_NAME,
        "symptoms": ["S-XX-INCIDENT-CHECK"],
        "purpose": "Confirm whether the declared incident symptom is present for one case.",
        "parameters": [{"name": "case_id", "type": "string", "required": True}],
        "safety": {"operation": "read_only", "max_rows": 1},
        "result_set": {
            "name": VERIFICATION_RESULT_SET,
            "columns": [
                {"name": "verification_verdict", "type": "string"},
                {"name": "case_reference", "type": "string"},
                {"name": "matched_rows", "type": "integer"},
            ],
        },
        "evidence_columns": [
            "verification_verdict",
            "case_reference",
            "matched_rows",
        ],
        "redact_columns": ["case_reference"],
    }


def _sidecar_variant() -> dict[str, object]:
    """Return a mutable deep copy of the valid fixture sidecar document."""
    return copy.deepcopy(dict(_base_sidecar()))


def _parameters(sidecar: dict[str, object]) -> list[dict[str, object]]:
    """Return the sidecar parameter list as mutable mappings."""
    return cast(list[dict[str, object]], sidecar["parameters"])


def _safety(sidecar: dict[str, object]) -> dict[str, object]:
    """Return the sidecar safety block as a mutable mapping."""
    return cast(dict[str, object], sidecar["safety"])


def _result_set(sidecar: dict[str, object]) -> dict[str, object]:
    """Return the sidecar result-set block as a mutable mapping."""
    return cast(dict[str, object], sidecar["result_set"])


def _columns(sidecar: dict[str, object]) -> list[dict[str, object]]:
    """Return the sidecar result-set columns as mutable mappings."""
    return cast(list[dict[str, object]], _result_set(sidecar)["columns"])


def _base_row() -> AdapterRow:
    """Return the valid fixture adapter row."""
    return {
        "verification_verdict": VALID_VERDICT,
        "case_reference": VALID_CASE_REFERENCE,
        "matched_rows": 1,
    }


def _base_adapter() -> dict[str, object]:
    """Return valid adapter output bound to the fixture source bytes."""
    return {
        "schema_version": 1,
        "verifier_id": VALID_VERIFIER_ID,
        "source_digest": qv.compute_sha256_digest(_read_source_bytes()),
        "result_set": VERIFICATION_RESULT_SET,
        "rows": [dict(_base_row())],
    }


def _load_static_adapter() -> dict[str, object]:
    """Load the static adapter fixture and assert its digest matches the source."""
    raw = json.loads(
        (FIXTURES_DIR / VALID_ADAPTER_NAME).read_text(encoding="utf-8")
    )
    if not isinstance(raw, dict):
        raise AssertionError("adapter fixture must be a JSON object")
    expected_digest = qv.compute_sha256_digest(_read_source_bytes())
    declared_digest = raw["source_digest"]
    if declared_digest != expected_digest:
        raise AssertionError(
            "adapter fixture source_digest "
            f"{declared_digest!r} does not match the fixture source digest "
            f"{expected_digest!r}"
        )
    return raw


def _load_definition() -> qv.SidecarDefinition:
    """Parse the valid fixture sidecar document into a validated definition."""
    document = yaml.safe_load(yaml.safe_dump(dict(_base_sidecar())))
    return qv.parse_sidecar_document(document)


def _sidecar_bytes() -> bytes:
    """Return canonical UTF-8 sidecar bytes for evidence-digest tests."""
    return yaml.safe_dump(dict(_base_sidecar())).encode("utf-8")


def _write_root(
    tmp: Path,
    source_text: str,
    sidecar: Mapping[str, object],
    source_name: str = VALID_SOURCE_NAME,
    sidecar_name: str = VALID_SIDECAR_NAME,
) -> Path:
    """Write one source/sidecar pair beneath a fresh ``sql/`` query root."""
    root = tmp / "sql"
    root.mkdir()
    (root / source_name).write_text(source_text, encoding="utf-8")
    (root / sidecar_name).write_text(
        yaml.safe_dump(dict(sidecar), sort_keys=True), encoding="utf-8"
    )
    return root


class QueryVerificationTests(unittest.TestCase):
    """Behavioral coverage for the incident query-verification pilot."""

    def _assert_rejected(
        self, root: Path, sidecar_path: Path, fragment: str
    ) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = qv.run_validate(str(root), str(sidecar_path))
        self.assertEqual(result, 1, stderr.getvalue())
        self.assertIn(fragment, stderr.getvalue())

    def _assert_source_rejected(self, source_text: str, fragment: str) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = _write_root(tmp, source_text, _base_sidecar())
            self._assert_rejected(root, root / VALID_SIDECAR_NAME, fragment)

    def _assert_sidecar_rejected(
        self, sidecar: dict[str, object], fragment: str
    ) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = _write_root(tmp, _read_source_text(), sidecar)
            self._assert_rejected(root, root / VALID_SIDECAR_NAME, fragment)

    def _evaluate(
        self,
        definition: Optional[qv.SidecarDefinition],
        source_bytes: Optional[bytes],
        adapter: object,
    ) -> qv.EvidenceRecord:
        return qv.build_evidence_record(
            definition, _sidecar_bytes(), source_bytes, adapter
        )

    def _assert_inconclusive(
        self, adapter: object, source_bytes: Optional[bytes]
    ) -> None:
        record = self._evaluate(_load_definition(), source_bytes, adapter)
        self.assertEqual(record["verdict"], "inconclusive")
        self.assertEqual(record["evidence"], {})

    # -- happy path: static fixture trio -----------------------------------

    def test_valid_fixture_trio_passes_validation(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = qv.run_validate(
                str(FIXTURES_DIR), str(FIXTURES_DIR / VALID_SIDECAR_NAME)
            )
        self.assertEqual(result, 0, stderr.getvalue())
        self.assertIn(VALID_VERIFIER_ID, stdout.getvalue())

    def test_static_adapter_fixture_shape(self) -> None:
        raw = json.loads(
            (FIXTURES_DIR / VALID_ADAPTER_NAME).read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(raw.keys()),
            {"schema_version", "verifier_id", "source_digest", "result_set", "rows"},
        )
        self.assertEqual(raw["schema_version"], 1)
        self.assertEqual(raw["verifier_id"], VALID_VERIFIER_ID)
        self.assertEqual(raw["result_set"], VERIFICATION_RESULT_SET)
        self.assertRegex(raw["source_digest"], _DIGEST_RE)
        self.assertEqual(len(raw["rows"]), 1)
        self.assertEqual(
            raw["rows"][0],
            {
                "verification_verdict": VALID_VERDICT,
                "case_reference": VALID_CASE_REFERENCE,
                "matched_rows": 1,
            },
        )

    def test_valid_fixture_evaluation_writes_verified_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            adapter_path = tmp / "adapter-output.json"
            adapter_path.write_text(
                json.dumps(_load_static_adapter()), encoding="utf-8"
            )
            evidence_path = tmp / "evidence.json"
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = qv.run_evaluate(
                    str(FIXTURES_DIR / VALID_SIDECAR_NAME),
                    str(adapter_path),
                    str(evidence_path),
                )
            self.assertEqual(result, 0, stderr.getvalue())
            record = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(record["verdict"], VALID_VERDICT)
            self.assertEqual(record["verifier_id"], VALID_VERIFIER_ID)
            self.assertEqual(record["result_set"], VERIFICATION_RESULT_SET)
            self.assertEqual(
                record["evidence"]["verification_verdict"], VALID_VERDICT
            )
            self.assertEqual(record["evidence"]["case_reference"], REDACTED)
            self.assertEqual(record["evidence"]["matched_rows"], 1)
            self.assertEqual(
                set(record.keys()),
                {
                    "schema_version",
                    "verifier_id",
                    "verdict",
                    "result_set",
                    "source_digest",
                    "definition_digest",
                    "evidence",
                    "evidence_digest",
                },
            )
            self.assertNotIn(VALID_CASE_REFERENCE, json.dumps(record))

    # -- path and layout rejections ----------------------------------------

    def test_rejects_absolute_source(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["source"] = "/etc/incident-check.sql"
        self._assert_sidecar_rejected(sidecar, "relative to the query root")

    def test_rejects_traversal_source(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["source"] = "../incident-check.sql"
        self._assert_sidecar_rejected(sidecar, "normalized path")

    def test_rejects_non_sql_source(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["source"] = "incident-check.txt"
        self._assert_sidecar_rejected(sidecar, "end with '.sql'")

    def test_rejects_non_incident_team(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["team"] = "dev"
        self._assert_sidecar_rejected(sidecar, "incident")

    def test_rejects_absent_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = _write_root(tmp, _read_source_text(), _base_sidecar())
            self._assert_rejected(
                root, root / "missing.verifier.yaml", "sidecar not found"
            )

    def test_rejects_absent_source(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = _write_root(tmp, _read_source_text(), _base_sidecar())
            (root / VALID_SOURCE_NAME).unlink()
            self._assert_rejected(
                root, root / VALID_SIDECAR_NAME, "source not found"
            )

    def test_rejects_non_adjacent_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = _write_root(
                tmp,
                _read_source_text(),
                _base_sidecar(),
                sidecar_name="other.verifier.yaml",
            )
            self._assert_rejected(
                root, root / "other.verifier.yaml", "not adjacent"
            )

    def test_rejects_sidecar_outside_query_root(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = _write_root(tmp, _read_source_text(), _base_sidecar())
            outside = tmp / "outside"
            outside.mkdir()
            outside_sidecar = outside / VALID_SIDECAR_NAME
            outside_sidecar.write_text(
                yaml.safe_dump(dict(_base_sidecar())), encoding="utf-8"
            )
            self._assert_rejected(
                root, outside_sidecar, "outside the query root"
            )

    def test_rejects_symlink_escape_source(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = _write_root(tmp, _read_source_text(), _base_sidecar())
            outside_source = tmp / "outside-source.sql"
            outside_source.write_text(_read_source_text(), encoding="utf-8")
            link = root / VALID_SOURCE_NAME
            link.unlink()
            try:
                os.symlink(outside_source, link)
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation unsupported: {exc}")
            self._assert_rejected(
                root, root / VALID_SIDECAR_NAME, "outside the query root"
            )

    # -- lexical SQL safety rejections -------------------------------------

    def test_rejects_unbounded_source(self) -> None:
        self._assert_source_rejected("SELECT 1", "unbounded")

    def test_rejects_mutating_source(self) -> None:
        self._assert_source_rejected(
            "WITH removed AS (DELETE FROM incident_events "
            "WHERE case_id = :case_id RETURNING case_id) "
            "SELECT verification_verdict FROM removed",
            "unsafe keyword",
        )

    def test_rejects_ddl_source(self) -> None:
        self._assert_source_rejected(
            "CREATE TABLE incident_events_copy AS SELECT 1",
            "must begin with SELECT or WITH",
        )

    def test_rejects_transaction_source(self) -> None:
        self._assert_source_rejected(
            "SELECT verification_verdict FROM incident_events "
            "WHERE case_id = :case_id AND COMMIT IS NULL",
            "transaction keyword",
        )

    def test_rejects_locking_source(self) -> None:
        self._assert_source_rejected(
            "SELECT verification_verdict FROM incident_events "
            "WHERE case_id = :case_id FOR SHARE",
            "locking clause",
        )

    def test_rejects_multi_statement_source(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = :case_id; SELECT 2",
            "statement separator",
        )

    def test_rejects_template_interpolation_source(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = {{case_id}}",
            "interpolation or template marker",
        )

    def test_rejects_dollar_interpolation_source(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = ${case_id}",
            "interpolation or template marker",
        )

    def test_rejects_undeclared_bind(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = :case_id AND other = :undeclared",
            "undeclared bind markers",
        )

    def test_rejects_missing_required_bind(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE 1 = 1",
            "missing required bind markers",
        )

    def test_rejects_positional_bind(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = ?",
            "positional bind marker",
        )

    def test_rejects_dollar_bind(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = $1",
            "dollar bind marker",
        )

    def test_rejects_at_bind(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = @case_id",
            "non-':' bind marker",
        )

    def test_rejects_string_concatenation(self) -> None:
        self._assert_source_rejected(
            "SELECT 1 WHERE case_id = :case_id || 'x'",
            "string concatenation",
        )

    # -- closed-schema sidecar rejections ----------------------------------

    def test_rejects_unknown_sidecar_field(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["unexpected"] = True
        self._assert_sidecar_rejected(sidecar, "unknown fields")

    def test_rejects_missing_sidecar_field(self) -> None:
        sidecar = _sidecar_variant()
        del sidecar["purpose"]
        self._assert_sidecar_rejected(sidecar, "missing required fields")

    def test_rejects_wrong_schema_version(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["schema_version"] = 2
        self._assert_sidecar_rejected(sidecar, "must be exactly 1")

    def test_rejects_empty_identifier(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["id"] = ""
        self._assert_sidecar_rejected(sidecar, "non-empty string")

    def test_rejects_empty_symptoms(self) -> None:
        sidecar = _sidecar_variant()
        sidecar["symptoms"] = []
        self._assert_sidecar_rejected(sidecar, "non-empty list")

    def test_rejects_unknown_parameter_field(self) -> None:
        sidecar = _sidecar_variant()
        _parameters(sidecar)[0]["default"] = 1
        self._assert_sidecar_rejected(sidecar, "unknown fields")

    def test_rejects_missing_parameter_field(self) -> None:
        sidecar = _sidecar_variant()
        del _parameters(sidecar)[0]["required"]
        self._assert_sidecar_rejected(sidecar, "missing required fields")

    def test_rejects_non_snake_case_parameter(self) -> None:
        sidecar = _sidecar_variant()
        _parameters(sidecar)[0]["name"] = "CaseId"
        self._assert_sidecar_rejected(sidecar, "lowercase snake_case")

    def test_rejects_unknown_parameter_type(self) -> None:
        sidecar = _sidecar_variant()
        _parameters(sidecar)[0]["type"] = "json"
        self._assert_sidecar_rejected(sidecar, "must be one of")

    def test_rejects_duplicate_parameter_names(self) -> None:
        sidecar = _sidecar_variant()
        _parameters(sidecar).append(
            {"name": "case_id", "type": "string", "required": True}
        )
        self._assert_sidecar_rejected(sidecar, "parameter names must be unique")

    def test_rejects_unknown_safety_field(self) -> None:
        sidecar = _sidecar_variant()
        _safety(sidecar)["timeout"] = 5
        self._assert_sidecar_rejected(sidecar, "unknown fields")

    def test_rejects_non_read_only_operation(self) -> None:
        sidecar = _sidecar_variant()
        _safety(sidecar)["operation"] = "write"
        self._assert_sidecar_rejected(sidecar, "read_only")

    def test_rejects_zero_max_rows(self) -> None:
        sidecar = _sidecar_variant()
        _safety(sidecar)["max_rows"] = 0
        self._assert_sidecar_rejected(sidecar, "at least 1")

    def test_rejects_unknown_result_set_field(self) -> None:
        sidecar = _sidecar_variant()
        _result_set(sidecar)["extra"] = 1
        self._assert_sidecar_rejected(sidecar, "unknown fields")

    def test_rejects_wrong_result_set_name(self) -> None:
        sidecar = _sidecar_variant()
        _result_set(sidecar)["name"] = "other"
        self._assert_sidecar_rejected(sidecar, "verification")

    def test_rejects_unknown_column_field(self) -> None:
        sidecar = _sidecar_variant()
        _columns(sidecar)[0]["nullable"] = True
        self._assert_sidecar_rejected(sidecar, "unknown fields")

    def test_rejects_duplicate_column_names(self) -> None:
        sidecar = _sidecar_variant()
        _columns(sidecar).append({"name": "matched_rows", "type": "integer"})
        self._assert_sidecar_rejected(sidecar, "column names must be unique")

    def test_rejects_missing_verdict_column(self) -> None:
        sidecar = _sidecar_variant()
        columns = _columns(sidecar)
        columns[:] = [
            column
            for column in columns
            if column["name"] != "verification_verdict"
        ]
        self._assert_sidecar_rejected(sidecar, "verification_verdict")

    def test_rejects_duplicate_evidence_columns(self) -> None:
        sidecar = _sidecar_variant()
        cast(list[str], sidecar["evidence_columns"]).append(
            "verification_verdict"
        )
        self._assert_sidecar_rejected(sidecar, "must not contain duplicates")

    def test_rejects_evidence_columns_outside_result_set(self) -> None:
        sidecar = _sidecar_variant()
        cast(list[str], sidecar["evidence_columns"]).append("nonexistent")
        self._assert_sidecar_rejected(sidecar, "subset of the declared columns")

    def test_rejects_redact_columns_outside_evidence(self) -> None:
        sidecar = _sidecar_variant()
        cast(list[str], sidecar["redact_columns"]).append("nonexistent")
        self._assert_sidecar_rejected(sidecar, "subset of evidence_columns")

    def test_rejects_redacting_verdict_column(self) -> None:
        sidecar = _sidecar_variant()
        cast(list[str], sidecar["redact_columns"]).append(
            "verification_verdict"
        )
        self._assert_sidecar_rejected(sidecar, "must not include")

    def test_rejects_duplicate_redact_columns(self) -> None:
        sidecar = _sidecar_variant()
        cast(list[str], sidecar["redact_columns"]).append("case_reference")
        self._assert_sidecar_rejected(sidecar, "must not contain duplicates")

    def test_rejects_malformed_yaml_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            root = tmp / "sql"
            root.mkdir()
            (root / VALID_SOURCE_NAME).write_text(
                _read_source_text(), encoding="utf-8"
            )
            (root / VALID_SIDECAR_NAME).write_text(
                "key: [unclosed", encoding="utf-8"
            )
            self._assert_rejected(
                root, root / VALID_SIDECAR_NAME, "not valid UTF-8 YAML"
            )

    def test_rejects_non_mapping_sidecar_document(self) -> None:
        with self.assertRaises(qv.ValidationError):
            qv.parse_sidecar_document(["not", "a", "mapping"])

    # -- evaluator verdicts -------------------------------------------------

    def test_evaluate_verified_redacts_and_binds_digests(self) -> None:
        definition = _load_definition()
        source_bytes = _read_source_bytes()
        record = self._evaluate(definition, source_bytes, _base_adapter())
        self.assertEqual(record["verdict"], "verified")
        self.assertEqual(record["verifier_id"], VALID_VERIFIER_ID)
        self.assertEqual(record["result_set"], VERIFICATION_RESULT_SET)
        self.assertEqual(
            record["source_digest"], qv.compute_sha256_digest(source_bytes)
        )
        self.assertEqual(
            record["definition_digest"],
            qv.compute_sha256_digest(_sidecar_bytes()),
        )
        self.assertEqual(record["evidence"]["case_reference"], REDACTED)
        self.assertEqual(record["evidence"]["matched_rows"], 1)
        self.assertEqual(
            record["evidence_digest"], qv.compute_evidence_digest(record)
        )
        self.assertNotIn(VALID_CASE_REFERENCE, json.dumps(record))

    def test_evaluate_not_verified(self) -> None:
        adapter = _base_adapter()
        cast(list[dict[str, object]], adapter["rows"])[0][
            "verification_verdict"
        ] = "not_verified"
        record = self._evaluate(_load_definition(), _read_source_bytes(), adapter)
        self.assertEqual(record["verdict"], "not_verified")
        self.assertEqual(
            record["evidence"]["verification_verdict"], "not_verified"
        )

    def test_evaluate_explicit_inconclusive_verdict(self) -> None:
        adapter = _base_adapter()
        cast(list[dict[str, object]], adapter["rows"])[0][
            "verification_verdict"
        ] = "inconclusive"
        record = self._evaluate(_load_definition(), _read_source_bytes(), adapter)
        self.assertEqual(record["verdict"], "inconclusive")
        self.assertEqual(record["evidence"]["case_reference"], REDACTED)

    def test_evaluate_unknown_verdict_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        cast(list[dict[str, object]], adapter["rows"])[0][
            "verification_verdict"
        ] = "maybe"
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_bad_verifier_id_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        adapter["verifier_id"] = "incident.other.v1"
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_bad_source_digest_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        adapter["source_digest"] = "sha256:" + "0" * 64
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_wrong_result_set_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        adapter["result_set"] = "other"
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_zero_rows_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        adapter["rows"] = []
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_multiple_rows_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        cast(list[dict[str, object]], adapter["rows"]).append(dict(_base_row()))
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_missing_column_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        del cast(list[dict[str, object]], adapter["rows"])[0]["matched_rows"]
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_extra_column_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        cast(list[dict[str, object]], adapter["rows"])[0]["extra"] = 1
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_type_mismatch_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        cast(list[dict[str, object]], adapter["rows"])[0]["matched_rows"] = "1"
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_missing_adapter_field_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        del adapter["schema_version"]
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_wrong_adapter_schema_version_is_inconclusive(self) -> None:
        adapter = _base_adapter()
        adapter["schema_version"] = 2
        self._assert_inconclusive(adapter, _read_source_bytes())

    def test_evaluate_non_mapping_adapter_is_inconclusive(self) -> None:
        self._assert_inconclusive(["not", "a", "mapping"], _read_source_bytes())

    def test_evaluate_missing_source_bytes_is_inconclusive(self) -> None:
        self._assert_inconclusive(_base_adapter(), None)

    def test_evaluate_missing_definition_is_inconclusive(self) -> None:
        record = self._evaluate(None, _read_source_bytes(), _base_adapter())
        self.assertEqual(record["verdict"], "inconclusive")
        self.assertEqual(record["evidence"], {})
        self.assertEqual(record["verifier_id"], VALID_VERIFIER_ID)

    def test_evaluate_missing_adapter_file_writes_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            evidence_path = tmp / "evidence.json"
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = qv.run_evaluate(
                    str(FIXTURES_DIR / VALID_SIDECAR_NAME),
                    str(tmp / "missing-adapter.json"),
                    str(evidence_path),
                )
            self.assertEqual(result, 0, stderr.getvalue())
            record = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(record["verdict"], "inconclusive")
            self.assertEqual(record["evidence"], {})

    # -- deterministic redaction and digests -------------------------------

    def test_evidence_digest_is_deterministic(self) -> None:
        definition = _load_definition()
        source_bytes = _read_source_bytes()
        first = self._evaluate(definition, source_bytes, _base_adapter())
        second = self._evaluate(definition, source_bytes, _base_adapter())
        self.assertEqual(first, second)
        self.assertEqual(first["evidence_digest"], second["evidence_digest"])

    def test_evidence_digest_changes_with_allowed_evidence(self) -> None:
        definition = _load_definition()
        source_bytes = _read_source_bytes()
        baseline = self._evaluate(definition, source_bytes, _base_adapter())
        changed_adapter = _base_adapter()
        cast(list[dict[str, object]], changed_adapter["rows"])[0][
            "matched_rows"
        ] = 2
        changed = self._evaluate(definition, source_bytes, changed_adapter)
        self.assertEqual(changed["verdict"], "verified")
        self.assertEqual(changed["evidence"]["matched_rows"], 2)
        self.assertNotEqual(
            baseline["evidence_digest"], changed["evidence_digest"]
        )

    def test_evidence_digest_changes_with_source_bytes(self) -> None:
        definition = _load_definition()
        baseline = self._evaluate(
            definition, _read_source_bytes(), _base_adapter()
        )
        changed_source = _read_source_bytes() + b"\n-- changed\n"
        changed_adapter = _base_adapter()
        changed_adapter["source_digest"] = qv.compute_sha256_digest(
            changed_source
        )
        changed = self._evaluate(definition, changed_source, changed_adapter)
        self.assertEqual(changed["verdict"], "verified")
        self.assertNotEqual(
            baseline["source_digest"], changed["source_digest"]
        )
        self.assertNotEqual(
            baseline["evidence_digest"], changed["evidence_digest"]
        )

    # -- static execution-surface guarantee --------------------------------

    def test_pilot_scripts_have_no_execution_surfaces(self) -> None:
        production_scripts = sorted(
            path
            for path in SCRIPTS_DIR.glob("*.py")
            if not path.name.startswith("test_")
        )
        self.assertTrue(
            production_scripts, "expected a production pilot script"
        )
        for path in production_scripts:
            source = path.read_text(encoding="utf-8")
            for pattern in _FORBIDDEN_SCRIPT_PATTERNS:
                self.assertIsNone(
                    re.search(pattern, source),
                    f"{path.name} matches forbidden pattern {pattern!r}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
