# Pull request publication

Pull request publication turns one structured input into the GitHub pull request description, so agents provide data and the utility generates the presentation.

**Status:** achieved

## Requirements

- [x] R1 — One JSON file per pull request is the only manually maintained publication content.
- [x] R2 — Agents populate and update that JSON; they never author or edit the Markdown description, its headings, tables, checkboxes, findings or evidence.
- [x] R3 — The utility validates the JSON on its own: syntax, required fields, supported schema version, field types and enumerations, and the consistency between test status, evidence, findings and verdict.
- [x] R4 — The utility generates the complete GitHub-compatible Markdown description deterministically, and the generated body is the artifact published to GitHub.
- [x] R5 — Invalid input is refused with a clear error, and no body is produced from invalid input.
- [x] R6 — Generating and publishing one description never depends on a previous JSON input, a previously published body, or any captured prior state.
- [x] R7 — Initial creation and later review updates use the same input and the same utility.
- [x] R8 — The content owner, the review evidence writer and the GitHub executor keep their distinct responsibilities.
- [x] R9 — Attribution scanning covers the published title and body, and the persisted description is confirmed byte-identical to the generated body.
- [x] R10 — The content and workflow utilities remain independently distributable and executable, with one authoritative validator and renderer.
