"""Shared temporary runbook, ticket, and register fixture builders."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import validate_runbook as vr  # noqa: E402


TEMPLATE_ANALYSIS_DIR = Path(__file__).parents[1] / "references" / "analysis"
STEP_FILES = ["01-identify.md", "02-investigate.md", "03-synthesize.md"]
_DATETIME_FMT = "%Y-%m-%dT%H:%M"


def _state_md(
    phase: str = "synthesize",
    verdict: str = "pending",
    completed: list[str] | None = None,
) -> str:
    """Build state frontmatter and its ordered step index."""
    step_rows = [
        ("identify", "01-identify.md", "Cipher"),
        ("investigate", "02-investigate.md", "Investigator"),
        ("synthesize", "03-synthesize.md", "Cipher"),
        ("respond", "response-draft.md", "Quill"),
    ]
    rows = ""
    for name, fname, owner in step_rows:
        status = "✅" if fname in (completed or []) else "⬜"
        rows += f"| {name} | `{fname}` | {owner} | {status} |\n"
    return (
        "---\n"
        f'Phase: "{phase}"\n'
        'SLA-due: "2099-01-01T00:00"\n'
        'Updated: "2000-01-01T00:00"\n'
        'Hypotheses-outstanding: "0/3"\n'
        'Query-budget: "0/6"\n'
        f'identification_verdict: "{verdict}"\n'
        'Same-query-reruns: "0/2"\n'
        "---\n\n"
        "# Working analysis — Fixture\n\n"
        "## Step index\n\n"
        "| Step | File | Owner | Status |\n"
        "|---|---|---|---|\n"
        + rows
    )


def _filled_step(fname: str) -> str:
    """Build a structurally complete filled analysis step."""
    return (
        f"# {fname}\n\n"
        "> **Owner:** Investigator\n"
        "> **Pre:** none\n"
        "> **Reads:** none\n"
        "> **Writes:** none\n\n"
        "## Steps\n\n1. step one\n\n"
        "## Output\n\n- **Artifact:** filled output\n\n"
        "## Gate\n\n- \u2b1c done\n\n"
        "## Abort conditions\n\n- halt if broken\n"
    )


def _make_analysis(
    root: Path,
    step_files: list[str] | None = None,
    phase: str = "synthesize",
    verdict: str = "pending",
) -> Path:
    """Create a complete temporary analysis directory beneath ``root``."""
    root.mkdir(parents=True, exist_ok=True)
    analysis_dir = root / "analysis"
    analysis_dir.mkdir()
    (analysis_dir / "state.md").write_text(
        _state_md(phase=phase, verdict=verdict), encoding="utf-8"
    )
    for fname in (step_files if step_files is not None else STEP_FILES):
        (analysis_dir / fname).write_text(_filled_step(fname), encoding="utf-8")
    return analysis_dir


def _patch_header(analysis_dir: Path, updates: dict[str, str]) -> None:
    """Replace existing quoted frontmatter fields in the temporary state file."""
    state_md = analysis_dir / "state.md"
    content = state_md.read_text(encoding="utf-8")
    for field, value in updates.items():
        pattern = rf"(?m)^{field}: \"[^\n]*\"$"
        replacement = f'{field}: "{value}"'
        content, replacements = re.subn(pattern, replacement, content, count=1)
        assert replacements == 1, f"state.md has no quoted {field} field"
    state_md.write_text(content, encoding="utf-8")


def _copy_initialized_scaffold(root: Path) -> Path:
    """Copy the shipped analysis scaffold into pytest's temporary directory."""
    analysis_dir = root / "analysis"
    shutil.copytree(TEMPLATE_ANALYSIS_DIR, analysis_dir)
    _patch_header(
        analysis_dir,
        {
            "Phase": "identify",
            "SLA-due": "2099-01-01T00:00",
            "Updated": "2000-01-01T00:00",
            "Hypotheses-outstanding": "0/3",
            "Query-budget": "0/6",
            "identification_verdict": "pending",
            "Same-query-reruns": "0/2",
        },
    )
    return analysis_dir


def _fill_template_identify(analysis_dir: Path) -> None:
    """Replace template tokens in the copied identify step."""
    identify = analysis_dir / "01-identify.md"
    content = identify.read_text(encoding="utf-8")
    identify.write_text(re.sub(r"<[^>]+>", "fixture", content), encoding="utf-8")


REGISTER_HEADER = "| " + " | ".join(
    column.upper() for column in vr.REGISTER_COLUMNS
) + " |"
REGISTER_SEP = "|" + "---|" * len(vr.REGISTER_COLUMNS)


def _row(**fields: str) -> str:
    """Build one register row using the validator's canonical column order."""
    values = [fields.get(column, "") for column in vr.REGISTER_COLUMNS]
    return "| " + " | ".join(values) + " |"


def _register(*rows: str) -> str:
    """Build a problem-register section with an optional row list."""
    return "\n".join(["## Register", "", REGISTER_HEADER, REGISTER_SEP, *rows])


def _ticket_dir(
    root: Path,
    with_working: bool = False,
    with_draft: bool = False,
    with_dirs: bool = True,
    image_exists: bool = True,
    verdict: str = "no_match",
    known: str = "[]",
) -> Path:
    """Build a durable ticket fixture entirely under the supplied temp root."""
    ticket_dir = root / "ticket"
    ticket_dir.mkdir()
    if with_dirs:
        (ticket_dir / "screenshots").mkdir()
        (ticket_dir / "validations").mkdir()
    if with_working:
        analysis_dir = ticket_dir / "analysis"
        analysis_dir.mkdir()
        (analysis_dir / "state.md").write_text("x", encoding="utf-8")
        (analysis_dir / "01-identify.md").write_text("x", encoding="utf-8")
    if with_draft:
        (ticket_dir / "response-draft.md").write_text("x", encoding="utf-8")
    image = "screenshots/01_source_entity.png"
    if image_exists and with_dirs:
        (ticket_dir / image).write_text("x", encoding="utf-8")
    content = (
        "---\n"
        "symptom_ids: []\n"
        f"known_problem_ids: {known}\n"
        f"identification_verdict: {verdict}\n"
        "---\n\n"
        "#### Imagen1\n"
        f"- **path:** {image}\n"
    )
    (ticket_dir / "ticket_999999.md").write_text(content, encoding="utf-8")
    return ticket_dir


def _pre_close_ticket_dir(
    root: Path,
    verdict: str = "no_match",
    known: str = "[]",
) -> Path:
    """Build the complete pre-close durable ticket and analysis set."""
    ticket_dir = _ticket_dir(root, with_draft=True, verdict=verdict, known=known)
    _make_analysis(ticket_dir, phase="synthesize", verdict="no_match")
    return ticket_dir


REPO_RELATIVE_IMAGE = "tickets/999999/screenshots/01_source_entity.png"


def _cite_repo_relative_spelling(root: Path, ticket_file: Path) -> None:
    """Add a repo-relative image twin and cite that spelling in the ticket."""
    repo_copy = root / REPO_RELATIVE_IMAGE
    repo_copy.parent.mkdir(parents=True, exist_ok=True)
    repo_copy.write_text("x", encoding="utf-8")
    ticket_file.write_text(
        ticket_file.read_text(encoding="utf-8").replace(
            "screenshots/01_source_entity.png", REPO_RELATIVE_IMAGE
        ),
        encoding="utf-8",
    )


def _filesystem_bytes(root: Path) -> tuple[dict[str, bytes], list[str]]:
    """Snapshot temporary file bytes and directory names for mutation checks."""
    files = {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    directories = [
        str(path.relative_to(root))
        for path in sorted(root.rglob("*"))
        if path.is_dir()
    ]
    return files, directories
