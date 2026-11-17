# Code style enforcement

AICore keeps one formatter, one linter and one editor-level whitespace contract for the whole repository, so that code and documentation have a single authoritative shape that every package and every agent-edited surface follows.

**Status:** achieved

## Requirements

- [x] R1 — One formatter owns formatting for every language the repository ships, and no second formatter is configured anywhere in the repository.
- [x] R2 — One linter owns linting, including rules that require type information, and no second linter is configured anywhere in the repository.
- [x] R3 — TypeScript and JavaScript indent with tab characters displayed at four columns, while JSON, JSONC, YAML and Markdown indent with spaces at the width conventional to each format.
- [x] R4 — Files are UTF-8 with LF line endings and a final newline, and Markdown preserves trailing whitespace because it can be significant.
- [x] R5 — The editor-level whitespace contract and the formatter agree on every value both of them control.
- [x] R6 — Generated, vendored and tool-owned files are outside the formatter's scope, and every remaining exclusion is justified by the file's owner or by a demonstrated formatter defect.
- [x] R7 — Formatting never changes the meaning of a document, the contracts that agents and validators consume, or the behavior of the distribution and synchronization mechanisms.
- [x] R8 — Every enabled lint rule either passes or has a mechanical correction, and each package's import convention is enforced only where that package already uses it.
- [x] R9 — The repository exposes lint, fix, format, check, typecheck and verify entry points, and verification never writes to the working tree.
- [x] R10 — Migrating content never mixes mechanical formatting with a behavioral change.
