# Code style enforcement

AICore keeps one formatter, one linter and one editor-level whitespace contract for the whole repository, so that code and documentation have a single authoritative shape that every package and every agent-edited surface follows.

**Status:** achieved

## Requirements

- [x] R1 — One formatter owns formatting for every language the repository ships, and no second formatter is configured anywhere in the repository.
- [x] R2 — One linter owns linting, including rules that require type information, and no second linter is configured anywhere in the repository.
- [x] R3 — TypeScript and JavaScript indent with tab characters displayed at four columns, while JSON, JSONC, YAML and Markdown indent with spaces at the width conventional to each format.
- [x] R4 — Files are UTF-8 with LF line endings and a final newline, and Markdown preserves trailing whitespace because it can be significant.
- [x] R5 — The editor-level whitespace contract and the formatter agree on every value both of them control.
- [x] R6 — Generated, vendored and tool-owned files are outside the formatter's scope, and the formatter's scope is declared rather than subtracted: `files.includes` carries no negation, one class-scoped decision keeps verbatim-quoting ODD change records out of the Markdown formatter, and no remaining exclusion is needed for a file the formatter can process without damaging it.
- [x] R7 — Formatting never changes the meaning of a document, the contracts that agents and validators consume, or the behavior of the distribution and synchronization mechanisms.
- [x] R8 — Every enabled lint rule either passes or has a mechanical correction, and each package's import convention is enforced only where that package already uses it.
- [x] R9 — The repository exposes lint, fix, format, check, typecheck and verify entry points, and verification never writes to the working tree.
- [x] R10 — Migrating content never mixes mechanical formatting with a behavioral change.
- [x] R11 — One canonical definition of the formatter rules exists, the repository's own formatter configuration consumes it, and no second copy of those rules is declared anywhere.
- [x] R12 — One canonical definition of the lint rules exists, the repository's own lint configuration consumes it, and type-aware linting is stated as a mandatory standard with the project-local declaration and dependency it requires.
- [x] R13 — The compiler policy is stated in two layers — language-level standards, and a direct-execution profile that extends them — and every TypeScript project in the repository consumes the profile while declaring only its own inclusion.
- [x] R14 — The whitespace contract has one canonical statement that a project adopts by copy, and the repository's operational EditorConfig is byte-identical to it while indentation remains EditorConfig's to define.
- [x] R15 — The canonical formatter, linter, compiler and whitespace standards, with the contract that governs their adoption, are shared distributed resources that a destination cannot opt out of.
- [x] R16 — Receiving the shared tooling resources authorizes no dependency installation, no change to a project-owned configuration, and no repository-wide formatting or code change.
