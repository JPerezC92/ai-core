# TypeScript testing

AICore's TypeScript test suites run under one runner, with that runner's own assertions and mocking facility, so every TypeScript suite in the repository executes the same way and each suite's behaviour is verifiable independently of how any other suite is written.

**Status:** achieved

## Requirements

- [x] R1 — TypeScript test suites execute under Vitest, and no suite mixes it with another runner.
- [x] R2 — Assertions in TypeScript test suites use Vitest's own expectation matchers rather than a second assertion library.
- [x] R3 — Every TypeScript test file obtains its test API from Vitest explicitly, so no test depends on ambient globals.
- [x] R4 `upstream` — Doubled collaborators in TypeScript tests use the mocking facility the applicable TypeScript testing guide requires.
- [x] R5 — A package's TypeScript test suites remain runnable from that package alone, without a repository-root command.
- [x] R6 — Changing the runner of an existing TypeScript suite preserves every scenario it asserted and alters no production behavior.
- [x] R7 `local` — A first-party test suite written in another language is replaced only after its replacement asserts the same behaviour, and the replacement runs under Vitest from a package that owns it.
