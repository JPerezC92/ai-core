"""Factory helpers for ODD feature-validator test documents."""

from __future__ import annotations


def make_feature(
    *,
    status: str = "active",
    task_status: str = "open",
    commit: str = "pending",
    title: str = "Sample feature",
    owner: str = "Cipher (Lead Orchestrator)",
    created: str = "2026-10-23",
    include_status: bool = True,
    include_owner: bool = True,
    include_created: bool = True,
    include_closed_date: bool = True,
    include_close_entry: bool | None = None,
    specs_heading: str = "## Specs",
    tasks_heading: str = "## Tasks",
    log_heading: str = "## Log",
    spec_entries: tuple[str, ...] = ("- S1 — A requirement.",),
    task_entries: tuple[str, ...] | None = None,
    log_entries: tuple[str, ...] | None = None,
) -> str:
    """Build a complete feature document with targeted field overrides."""
    headers: list[str] = []
    if include_status:
        headers.append(f"> **Status:** {status}")
    if include_owner:
        headers.append(f"> **Owner:** {owner}")
    if include_created:
        headers.append(f"> **Created:** {created}")
    if status == "closed" and include_closed_date:
        headers.append("> **Closed:** 2026-10-23")

    if task_entries is None:
        task_entries = (
            f"- T1 | S1 | route | {task_status} | commit: {commit}",
        )
    if log_entries is None:
        include_close = status == "closed" if include_close_entry is None else include_close_entry
        generated_log = ["- L1 — original request"]
        if include_close:
            generated_log.append("- L2 — Close: done")
        log_entries = tuple(generated_log)

    return "\n".join(
        (
            f"# {title}",
            "",
            *headers,
            "",
            specs_heading,
            "",
            *spec_entries,
            "",
            tasks_heading,
            "",
            *task_entries,
            "",
            log_heading,
            "",
            *log_entries,
            "",
        )
    )
