"""Command exit contracts, lock proposal, and adopter registry tests."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
from pathlib import Path
from unittest import mock

import yaml

from adoption_test_repos import ENGINE_PATH, EngineTestCase

from adoption_digests import _snapshot_digest
from adoption_loaders import _raw_file_digest, load_registry
from adoption_registry import run_verify
import adoption_registry as engine_adoption_registry
from adoption_test_data import (
    CATALOG_REL,
    DESTINATION_OWNED_DECLARATION,
    EMPTY_REVIEW,
    GREETING_CATALOG,
    GREETING_DECLARATION,
    GREETING_DECISION_REVIEW,
    review_with_transition,
    sha256_text,
)


class ExitContractTests(EngineTestCase):
    def base_check_args(self, fixture: dict[str, object]) -> list[str]:
        return [
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", CATALOG_REL,
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
        ]

    def _check(
        self, fixture: dict[str, object], *extra: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
            *extra,
        )

    def test_compliant_exit_0(self) -> None:
        fixture = self.build_greeting()
        proc = self._check(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["compliance"]
        assert report["units"][0]["disposition"] == "current"

    def test_update_available_exit_1(self) -> None:
        fixture = self.build_greeting(advance="content")
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["units"][0]["disposition"] == "update_available"

    def test_baseline_advance_required_exit_1(self) -> None:
        fixture = self.build_greeting(advance="empty")
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["units"][0]["disposition"] == "baseline_advance_required"

    def test_mirror_changed_on_both_sides_is_conflict_exit_1(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            destination_text="hello world\n",
            lock_destination_text="hello\n",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["units"][0]["disposition"] == "conflict"

    def test_destination_owned_steady_state_is_unmanaged_exit_0(self) -> None:
        fixture = self.build_greeting(
            declaration=DESTINATION_OWNED_DECLARATION,
            mode="destination_owned",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["compliance"]
        assert report["units"][0]["disposition"] == "unmanaged"

    def test_destination_owned_upstream_changed_without_decision_reports_review_required(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            declaration=DESTINATION_OWNED_DECLARATION,
            mode="destination_owned",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["units"][0]["disposition"] == "review_required"

    def test_legacy_review_is_readable_but_rejects_fresh_candidate(self) -> None:
        fixture = self.build_greeting(
            advance="content",
            declaration=DESTINATION_OWNED_DECLARATION,
            review=GREETING_DECISION_REVIEW,
            mode="destination_owned",
        )
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["units"][0]["disposition"] == "review_required"
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", CATALOG_REL,
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_diagnostic_never_exit_0(self) -> None:
        fixture = self.build_greeting(advance="content")
        proc = self._check(fixture, "--diagnostic-revision", fixture["accepted"])
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["diagnostic"]

    def test_fatal_missing_declaration_exit_2(self) -> None:
        fixture = self.build_greeting()
        missing = self.root / "absent" / "adoption.yaml"
        args = [
            "check",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", CATALOG_REL,
            "--declaration", str(missing),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 2, "invalid_declaration")

    def test_missing_snapshot_selection_exit_2(self) -> None:
        fixture = self.build_greeting()
        self.assert_exit(self.run_cli("check", *self.base_check_args(fixture)), 2, "adopter_snapshot_unavailable")


class ProposeLockTests(EngineTestCase):
    def test_unit_option_is_unrecognized(self) -> None:
        self.assert_exit(self.run_cli("propose-lock", "--unit", "greeting"), 2, "unrecognized arguments")

    def test_candidate_is_single_revision_and_round_trips(self) -> None:
        fixture = self.build_greeting()
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh transition")
        proc = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", CATALOG_REL,
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 0)
        candidate = yaml.safe_load(proc.stdout)
        assert candidate["accepted_source_commit"] == fixture["target"]
        catalog = yaml.safe_load(GREETING_CATALOG)
        assert {row["id"] for row in candidate["units"]} == {unit["id"] for unit in catalog["units"]}
        for row in candidate["units"]:
            assert "accepted_source_commit" not in row
        actual_review = fixture["review"].read_text(encoding="utf-8")
        reproduced = _snapshot_digest(
            sha256_text(GREETING_DECLARATION), sha256_text(actual_review), candidate["units"]
        )
        assert candidate["accepted_snapshot_digest"] == reproduced
        candidate_path = self.write(self.root, "candidate.lock.yaml", proc.stdout)
        args = [
            "check", *self.base_check_args(fixture)[:-2], "--lock", str(candidate_path),
            "--adopter-revision", fixture["adopter_rev"],
        ]
        self.assert_exit(self.run_cli(*args), 0)



class VerifyAllTests(EngineTestCase):
    def _verify(
        self, fixture: dict[str, object], registry: Path
    ) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "verify-all",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", CATALOG_REL,
            "--registry", str(registry),
            "--checkouts-root", str(fixture["checkouts"]),
            "--format", "json",
        )

    def test_all_current_registry_exit_0(self) -> None:
        fixture = self.build_verify()
        proc = self._verify(fixture, fixture["current_registry"])
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert report["compliance"]
        by_id = {adopter["id"]: adopter for adopter in report["adopters"]}
        assert by_id["good"]["compliance"]
        assert report["blocking_reasons"] == []

    def test_stale_registered_adopter_exit_1_without_required_field(self) -> None:
        fixture = self.build_verify()
        proc = self._verify(fixture, fixture["stale_registry"])
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        by_id = {adopter["id"]: adopter for adopter in report["adopters"]}
        assert by_id["good"]["compliance"]
        assert not by_id["stale"]["compliance"]
        assert any("stale" in reason for reason in report["blocking_reasons"]), report["blocking_reasons"]

    def test_missing_checkout_is_blocking_without_network(self) -> None:
        fixture = self.build_verify()
        registry = self.write(self.root, "registry-missing.yaml", self._registry_text(["good", "ghost"]))
        namespace = argparse.Namespace(
            upstream_repo=str(fixture["upstream"]),
            catalog=CATALOG_REL,
            registry=str(registry),
            checkouts_root=str(fixture["checkouts"]),
            format="json",
        )
        buffer = io.StringIO()
        with mock.patch.object(engine_adoption_registry, "_git_clone", return_value="simulated offline checkout"):
            with contextlib.redirect_stdout(buffer):
                code = run_verify(namespace)
        assert code == 1
        report = json.loads(buffer.getvalue())
        ghost = next(adopter for adopter in report["adopters"] if adopter["id"] == "ghost")
        assert not ghost["compliance"]
        assert "repository_unavailable" in ghost["error"]
        assert any("ghost" in reason for reason in report["blocking_reasons"]), report["blocking_reasons"]

    def test_registry_entries_have_no_required_field(self) -> None:
        fixture = self.build_verify()
        document = yaml.safe_load(fixture["stale_registry"].read_text(encoding="utf-8"))
        assert document["adopters"]
        for adopter in document["adopters"]:
            assert "required" not in adopter
        assert isinstance(load_registry(str(fixture["stale_registry"])), dict)

    def test_t2_cli_promisor_check_does_not_fetch(self) -> None:
        fixture = self.build_greeting()
        repo = fixture["adopter"]
        sentinel = self.root / "cli-fetch-sentinel"
        script = self.root / "cli-fetch-helper.sh"
        script.write_text(
            "#!/bin/sh\ntouch " + str(sentinel) + "\nexit 1\n",
            encoding="utf-8",
        )
        script.chmod(0o755)
        self.git(repo, "config", "core.repositoryformatversion", "1")
        config = repo / ".git" / "config"
        config.write_text(
            config.read_text(encoding="utf-8")
            + "[extensions]\n\tpartialclone = origin\n"
            + '[remote "origin"]\n\tpromisor = true\n'
            + f"\turl = ext::{script}\n",
            encoding="utf-8",
        )
        index_before = (repo / ".git" / "index").read_bytes()
        files_before = self.worktree_bytes(repo)
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        assert proc.returncode != 0
        assert "adopter_snapshot_unavailable" in proc.stderr
        assert not sentinel.exists()
        assert (repo / ".git" / "index").read_bytes() == index_before
        assert self.worktree_bytes(repo) == files_before

    def test_t3_documented_cli_writes_no_engine_bytecode(self) -> None:
        fixture = self.build_greeting()
        cache = ENGINE_PATH.parent / "__pycache__"
        before = {
            path.name: path.read_bytes()
            for path in cache.glob("*")
            if path.is_file()
        } if cache.is_dir() else {}
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(proc, 0)
        after = {
            path.name: path.read_bytes()
            for path in cache.glob("*")
            if path.is_file()
        } if cache.is_dir() else {}
        assert after == before
        assert any(
            len(argv) >= 3 and argv[1] == "-B" and argv[2] == str(ENGINE_PATH)
            for argv in self.command_trace
        )
        help_text = self.run_cli("--help")
        self.assert_exit(help_text, 0)
        assert "python3 -B" in help_text.stdout
        assert "does not sandbox" in help_text.stdout
        assert "verifier-owned temporary" in help_text.stdout
        assert "read-only by construction" not in help_text.stdout
        verify_help = self.run_cli("verify-all", "--help")
        self.assert_exit(verify_help, 0)
        assert "verifier-owned temporary" in verify_help.stdout
        assert "supplied checkout unchanged" in verify_help.stdout

    def test_t3_clone_cleanup_does_not_touch_existing_checkout(self) -> None:
        fixture = self.build_verify()
        existing = fixture["checkouts"] / "good"
        before = self.worktree_bytes(existing)
        index_before = (existing / ".git" / "index").read_bytes()
        refs_before = self.git(existing, "for-each-ref").stdout
        registry = self.write(
            self.root, "registry-clone-scope.yaml", self._registry_text(["ghost"])
        )
        created: list[str] = []
        recorded: list[tuple[list[str], dict[str, str]]] = []
        original_mkdtemp = engine_adoption_registry.tempfile.mkdtemp
        real_run = engine_adoption_registry.subprocess.run

        def spy_mkdtemp(prefix: str = "tmp", dir: str | None = None) -> str:
            path = original_mkdtemp(prefix=prefix, dir=dir)
            created.append(path)
            return path

        def fake_run(
            command: list[str], **kwargs: object
        ) -> subprocess.CompletedProcess[bytes]:
            argv = list(command)
            if not argv or argv[0] != "gh":
                return real_run(command, **kwargs)
            environment = kwargs.get("env")
            assert isinstance(environment, dict)
            recorded.append((argv, environment))
            return subprocess.CompletedProcess(argv, 1, b"", b"offline\n")

        namespace = argparse.Namespace(
            upstream_repo=str(fixture["upstream"]),
            catalog=str(fixture["catalog"]),
            registry=str(registry),
            checkouts_root=str(fixture["checkouts"]),
            format="json",
        )
        trace = self.root / "clone.trace"
        poison = {"GIT_DIR": str(existing / ".git"), "GIT_TRACE": str(trace)}
        with mock.patch.object(
            engine_adoption_registry.tempfile, "mkdtemp", spy_mkdtemp
        ):
            with mock.patch.object(
                engine_adoption_registry.subprocess, "run", fake_run
            ):
                with mock.patch.dict(os.environ, poison, clear=False):
                    code = run_verify(namespace)
        assert code == 1
        assert created
        for path in created:
            assert not os.path.exists(path)
        assert recorded
        command, environment = recorded[0]
        assert "GIT_DIR" not in environment
        assert "GIT_TRACE" not in environment
        assert environment["GIT_NO_LAZY_FETCH"] == "1"
        assert environment["GIT_CONFIG_NOSYSTEM"] == "1"
        assert "--template" in command
        assert any(part.startswith("core.hooksPath=") for part in command)
        assert "core.fsmonitor=" in command
        assert str(existing) not in command
        assert self.worktree_bytes(existing) == before
        assert (existing / ".git" / "index").read_bytes() == index_before
        assert self.git(existing, "for-each-ref").stdout == refs_before
        assert not trace.exists()
