"""Registry-wide verification and disclosed temporary cloning.

Existing cached checkouts are only read. A missing checkout is cloned into a
directory this process created, using the controlled Git environment. Cleanup
removes only those created directories, never an existing adopter.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Mapping, Sequence, TypedDict

from adoption_check import _check_report
from adoption_contracts import SyncError, _need
from adoption_git import (
    _GitRepo,
    _RevisionSnapshot,
    _controlled_git_environment,
    _resolve_catalog_path,
    _trusted_revision,
)
from adoption_loaders import load_catalog, load_registry


class VerificationResult(TypedDict):
    """One registered adopter's read-only verification outcome."""

    id: str
    repository: str
    checked_commit: str
    compliance: bool
    disposition_summary: str
    error: str


class OwnedTemporary(TypedDict):
    """A directory this process created and may later remove."""

    path: str
    device: int
    inode: int


def _make_owned_directory(prefix: str) -> OwnedTemporary:
    """Create one temporary directory and record the inode cleanup must match."""
    path = tempfile.mkdtemp(prefix=prefix)
    stat = os.stat(path)
    return {"path": path, "device": stat.st_dev, "inode": stat.st_ino}


def _remove_owned_directory(owned: OwnedTemporary) -> str | None:
    """Remove a created directory. A symlink, replacement, or other path is left untouched."""
    path = owned["path"]
    if os.path.islink(path):
        return f"refusing to remove symlink {path}"
    try:
        stat = os.stat(path)
    except FileNotFoundError:
        return None
    if not os.path.isdir(path):
        return f"refusing to remove non-directory {path}"
    if stat.st_dev != owned["device"] or stat.st_ino != owned["inode"]:
        return f"refusing to remove replaced directory {path}"
    try:
        shutil.rmtree(path)
    except OSError as exc:
        return str(exc)
    return None


def _git_clone(repository: str, destination: str, branch: str) -> str | None:
    """Clone into a caller-owned destination. Template cleanup owns only its own directory.

    Inherited template, hook, and filter execution is removed through the
    controlled environment plus an empty template and command config. The
    destination checkout remains a normal disposable clone. This does not
    delete ``destination``.
    """
    template = _make_owned_directory("aicore-git-template-")
    environment = _controlled_git_environment()
    environment["GIT_TEMPLATE_DIR"] = template["path"]
    command = [
        "gh",
        "repo",
        "clone",
        repository,
        destination,
        "--",
        "--branch",
        branch,
        "--depth",
        "1",
        "--template",
        template["path"],
        "--config",
        "core.fsmonitor=",
        "--config",
        f"core.hooksPath={template['path']}",
        "--config",
        "filter.lfs.required=false",
        "--config",
        "filter.lfs.smudge=",
        "--config",
        "filter.lfs.clean=",
        "--config",
        "filter.lfs.process=",
    ]
    try:
        try:
            proc = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                check=False,
                env=environment,
            )
        except FileNotFoundError:
            return "gh is not available"
        if proc.returncode != 0:
            lines = proc.stderr.decode("utf-8", "replace").strip().splitlines()
            return lines[-1] if lines else f"gh exited {proc.returncode}"
        return None
    finally:
        failure = _remove_owned_directory(template)
        if failure is not None:
            print(
                f"sync-aicore-adoption: temp cleanup failed for {template['path']}: {failure}",
                file=sys.stderr,
            )


def _summarize_dispositions(units: Sequence[Mapping[str, object]]) -> str:
    interesting = [
        f"{u.get('id')}:{u.get('disposition')}"
        for u in units
        if str(u.get("disposition")) not in ("current", "not_applicable")
    ]
    return ", ".join(interesting) if interesting else "all current"


def _registered_checkout(
    entry: Mapping[str, object],
    checkouts_root: str | None,
    owned_directories: list[OwnedTemporary],
) -> tuple[str | None, str | None, str | None]:
    """Resolve one registered checkout before any registry/catalog comparison.

    Returns the checkout path and HEAD commit when available, otherwise an
    offline error. An existing cached checkout is only read. A missing checkout
    is cloned into a directory this process created.
    """
    adopter_id = str(entry.get("id"))
    checkout: str | None = None
    if checkouts_root:
        candidate = os.path.join(str(checkouts_root), adopter_id)
        if os.path.isdir(candidate):
            checkout = candidate
    if checkout is None:
        owned = _make_owned_directory(f"aicore-verify-{adopter_id}-")
        owned_directories.append(owned)
        checkout = owned["path"]
        failure = _git_clone(
            str(entry.get("repository")),
            checkout,
            str(entry.get("default_branch")),
        )
        if failure is not None:
            return None, None, f"repository_unavailable: {failure}"
    head = _GitRepo(checkout).resolve("HEAD")
    if head is None:
        return checkout, None, "adopter_snapshot_unavailable: checkout HEAD is not a commit"
    return checkout, head, None


def _verify_adopter(
    entry: Mapping[str, object],
    checkout: str,
    head: str,
    catalog_path: str,
    upstream: _GitRepo,
    target: str,
) -> VerificationResult:
    adopter_id = str(entry.get("id"))
    result: VerificationResult = {
        "id": adopter_id,
        "repository": str(entry.get("repository")),
        "checked_commit": "",
        "compliance": False,
        "disposition_summary": "",
        "error": "",
    }
    repo = _GitRepo(checkout)
    result["checked_commit"] = head
    declaration_path = os.path.join(checkout, str(entry.get("declaration_path")))
    lock_path = os.path.join(checkout, str(entry.get("lock_path")))
    review_path = os.path.join(checkout, str(entry.get("review_path")))
    try:
        report = _check_report(
            declaration_path,
            lock_path,
            review_path,
            catalog_path,
            upstream,
            target,
            False,
            lambda: _RevisionSnapshot(repo, head),
        )
    except SyncError as exc:
        result["error"] = f"{exc.code}: {exc.message}"
        return result
    result["compliance"] = bool(report.get("compliance"))
    result["disposition_summary"] = _summarize_dispositions(report.get("units", []))
    return result


def _print_verify_human(report: Mapping[str, object]) -> None:
    print(f"compliance: {str(report['compliance']).lower()}")
    for adopter in report["adopters"]:
        status = "pass" if adopter["compliance"] else "fail"
        detail = adopter["error"] or adopter["disposition_summary"]
        commit = adopter["checked_commit"] or "unresolved"
        print(
            f"  {adopter['id']} [{status}] {adopter['repository']} @ {commit} {detail}"
        )
    for reason in report["blocking_reasons"]:
        print(f"blocking: {reason}")


def run_verify(args: argparse.Namespace) -> int:
    """Verify every registered adopter; return 0 only when every adopter passes."""
    catalog_path = _resolve_catalog_path(str(args.catalog), str(args.upstream_repo))
    registry_path = (
        str(args.registry)
        if args.registry
        else os.path.join(str(args.upstream_repo), ".aicore/adopters.yaml")
    )
    registry = load_registry(registry_path)
    upstream = _GitRepo(str(args.upstream_repo))
    target, _diagnostic = _trusted_revision(upstream, None)
    results: list[VerificationResult] = []
    blocking: list[str] = []
    owned_directories: list[OwnedTemporary] = []
    try:
        resolved_checkouts: list[tuple[Mapping[str, object], str, str]] = []
        for entry in registry.get("adopters", []):
            checkout, head, offline_error = _registered_checkout(
                entry, args.checkouts_root, owned_directories
            )
            if offline_error is not None:
                result: VerificationResult = {
                    "id": str(entry.get("id")),
                    "repository": str(entry.get("repository")),
                    "checked_commit": "",
                    "compliance": False,
                    "disposition_summary": "",
                    "error": offline_error,
                }
                results.append(result)
                blocking.append(f"{result['id']}: {offline_error}")
                continue
            assert checkout is not None and head is not None
            resolved_checkouts.append((entry, checkout, head))
        if blocking:
            report = {
                "compliance": False,
                "adopters": results,
                "blocking_reasons": blocking,
            }
            if args.format == "json":
                print(json.dumps(report, indent=2))
            else:
                _print_verify_human(report)
            return 1
        catalog = load_catalog(catalog_path)
        block = catalog.get("catalog")
        _need(
            isinstance(block, Mapping)
            and block.get("upstream_repository") == registry.get("upstream_repository"),
            "repository_identity_mismatch",
            "catalog and registry upstream_repository differ",
        )
        for entry, checkout, head in resolved_checkouts:
            result = _verify_adopter(
                entry,
                checkout,
                head,
                catalog_path,
                upstream,
                target,
            )
            results.append(result)
            if not result["compliance"]:
                detail = result["error"] or (
                    "non-compliant (" + str(result["disposition_summary"]) + ")"
                )
                blocking.append(f"{result['id']}: {detail}")
    finally:
        for owned in owned_directories:
            failure = _remove_owned_directory(owned)
            if failure is not None:
                print(
                    "sync-aicore-adoption: temp cleanup failed for "
                    f"{owned['path']}: {failure}",
                    file=sys.stderr,
                )
    compliance = not blocking
    report = {
        "compliance": compliance,
        "adopters": results,
        "blocking_reasons": blocking,
    }
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        _print_verify_human(report)
    return 0 if compliance else 1
