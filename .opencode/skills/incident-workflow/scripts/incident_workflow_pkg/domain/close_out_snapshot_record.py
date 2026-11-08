"""Record for the filesystem snapshot used by the pre-close and close-out checks."""

from __future__ import annotations

from typing import Optional, TypedDict


class CloseOutSnapshot(TypedDict):
    """Filesystem values required to evaluate pre-close and close-out sets."""

    ticket_file_names: list[str]
    ticket_content: Optional[str]
    working_analysis_files: list[str]
    analysis_contents: dict[str, str]
    response_draft_present: bool
    screenshots_dir_present: bool
    validations_dir_present: bool
    missing_image_paths: list[str]
    missing_ticket_paths: list[str]
    unsafe_ticket_paths: list[str]
    leftover_download_files: list[str]
