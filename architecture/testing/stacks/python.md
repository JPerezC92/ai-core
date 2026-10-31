# Python testing guide

> **Status:** reference
> **Stack:** Python application, script, and CLI code; pytest reference implementation
> **Reviewed:** 2026-10-25 — `testing-architecture-layering`; entity-construction clause 2026-10-30
> **Contract:** `architecture/testing/architecture.md`

## Applicability and ownership

This guide applies to Python application, script, and CLI code that follows the clean-architecture layers. The reference case is a skill suite: application operations, domain responsibilities, and infrastructure adapters live in importable packages, and an end-to-end test exercises the assembled entry point.

pytest is the reference runner. A destination owns its reviewed Python runner and configuration; a different runner requires its own destination-owned guide, not an assumption that these rules still apply unchanged. This guide does not cover a browser frontend, a JavaScript/TypeScript frontend, or a framework-specific adapter that has no selected guide.

A destination may select a different Python runner, add a framework-specific adapter, or bind an isolated test database. It must preserve the three levels, returned-business-failure rule, one-behavior rule, factory rule, hermeticity rule, and execution/verdict separation.

## Test pyramid mapping

The three levels are the same as the agnostic contract:

| Level | Target | Collaborators and doubles | Observable assertion |
|---|---|---|---|
| Unit | One application operation's `execute()` or one pure domain responsibility | Ports replaced with `unittest.mock` doubles or a small fake | Returned values and returned domain errors |
| Unit — parser/loader | One parser or loader | External library mocked at its boundary | Mapping, coercion, extraction, and the documented failure result |
| Integration | One infrastructure adapter: repository, loader, builder, client, or parser | Real isolated dependency when possible; transport stubbed at its boundary | Raw external data to domain values |
| End to end | Assembled CLI or service entry point | Real adapters and composition | Exit code, output, or observable service result |

Python does not add a fourth level. A test that calls the CLI is not a unit test because the CLI is importable, and an in-memory adapter is not automatically a unit test.

## File organization

- Unit tests sit with the application operation or domain responsibility: `application/test_<operation>.py` or `domain/test_<responsibility>.py`.
- Integration tests sit with the infrastructure adapter: `infrastructure/test_<adapter>.py`.
- End-to-end tests sit in the project's end-to-end location: `e2e/test_<entrypoint>.py` or `tests/e2e/test_<entrypoint>.py`.
- Test files are named `test_*.py` and are collected project-wide by the project's reviewed runner. There is no per-subdirectory allowlist.
- One behavior per test module and per class or group. A multi-behavior module or class is a violation and must be split by behavior.
- There is no line cap; behavior, not size, sets the split boundary.
- A pure helper may be tested beside its owning layer. Do not create an artificial use-case wrapper just to satisfy a path convention.

## Unit tests

- Instantiate the use case or domain object directly. Do not go through the CLI, an HTTP server, or the full composition root.
- Call the application operation's `execute()` directly, or call the domain function under test.
- Replace each port with a `unittest.mock.Mock`/`MagicMock` or a small hand-written fake. `unittest.mock` is the suite's mocking library; do not add a second mocking library for the same job.
- Assert returned values. A business failure is a returned domain value:

```python
result = use_case.execute(command)
assert isinstance(result, TaskNotFoundError)
```

- Do not use `pytest.raises` to assert a returned business failure. Use it only for an expected exception at a boundary or a CLI `SystemExit`.
- Do not mock the use case or the domain function under test. Mock or fake its ports.
- Parser and loader unit tests mock the external library at its boundary and assert field mapping, type coercion, extraction, and the documented failure result. An empty or malformed input is a unit case when no real external service is needed.
- These tests must be compatible with the project's reviewed runner and discovery rules.

## Integration tests

- Instantiate the adapter directly with a real, isolated dependency: a temporary filesystem, an isolated test database, or a controlled local service.
- Use `tmp_path` for filesystem work. Do not write into the repository or a developer's home directory.
- When the dependency cannot be isolated, stub the transport boundary with `monkeypatch` or a small fake. Do not mock the adapter under test.
- Assert the mapping pipeline: raw record or payload, adapter method, domain value. Cover defaults and null handling, and assert that a missing identifier returns the documented empty value rather than throwing.
- Do not use collaborator mocks here when the real isolated dependency is available. This level exists to test the real adapter boundary.
- Keep setup and cleanup hermetic. A test must not depend on another test's files, database rows, environment variables, or process state.
- Use the reviewed runner's isolation facilities; do not replace `tmp_path` with a shared temporary directory.

## End-to-end tests

- Exercise the assembled entry point: a CLI `main()` function, a service entry point, or the project's equivalent composition root.
- Use real adapters with isolated data: `tmp_path` for files, an isolated test database for persistence, or a controlled local dependency.
- Assert the observable result at the entry point: exit code, stdout/stderr, service response, or persisted output. Use `capsys` for captured CLI output when the reviewed runner provides it.
- Use `pytest.raises(SystemExit)` only for an expected CLI exit. Do not use it for a returned business failure.
- Do not call the use case directly in an end-to-end test. The test exists to prove the assembled entry point and its real composition.
- Do not duplicate every unit or integration case here. Cover the end-to-end path, its wiring, and its user-visible failure behavior.

## Test data and doubles

- Use a shared test-data factory or helper, for example `_test_support.py`, for domain objects and external payloads. Do not use inline literals for test data.
- The factory provides `create(**overrides)` and, when collections are needed, `create_many(count, **overrides)`. Deterministic values are acceptable; randomness is not required.
- When the test needs an entity rather than a data-only record, the factory builds it through the entity factory/`create()`; never assign entity fields directly to construct test data.
- Use `unittest.mock` for collaborator ports and controlled return values.
- Use `monkeypatch` for process-wide boundaries such as environment variables, time, or transport. Do not use `monkeypatch` as a substitute for a port double, and do not mix `monkeypatch` and `unittest.mock` for the same collaborator.
- Keep fixtures hermetic. Use `tmp_path` for filesystem isolation and the reviewed runner's fixture lifecycle for setup and teardown.
- Do not use `unittest.TestCase` or `unittest.main()`. Use pytest test functions or non-`TestCase` classes with `test_*` methods.
- Use direct `assert` statements and the reviewed runner's assertion helpers. Do not hide the expected value behind a custom assertion DSL.

## Execution and evidence

- The project owns its reviewed whole-project Python command. This guide does not authorize running tests or installing dependencies.
- Discovery is project-wide: a new `test_*.py` file joins the approved suite without a per-file grant or a subdirectory allowlist.
- Test-architecture verdicts are separate from execution results. A passing run does not establish conformance.
- Every feature-spec happy case and rejection case must trace to a test at the appropriate level.
- Missing scoped evidence for a file covered by this guide is a `[FAIL]`. `[UNCERTAIN]` is reserved for a file outside the declared scope or one with no applicable guide.
- The reviewed runner's configuration is the execution authority; the file locations above are reference layout, not a narrower execution grant.

## Cross-stack parity

| Contract section | Coverage | Difference or N/A reason |
|---|---|---|
| Applicability and ownership | Covered | Python has no browser frontend; application, script, and CLI shapes are covered. |
| Test pyramid mapping | Covered | The UI-specific frontend row has no Python equivalent; the CLI/service entry point is the end-to-end target. |
| File organization | Covered | Python uses package-relative test modules and project-wide discovery; no TypeScript test-directory convention applies. |
| Unit tests | Covered | Use-case/domain units use the same boundary and returned-value rules; parser/loader rules cover Python imports. |
| Integration tests | Covered | Real isolated dependencies and transport stubs are defined; `tmp_path` replaces the frontend fetch stub. |
| End-to-end tests | Covered | CLI/service entry points replace the browser and HTTP reference phases; no browser-phase rules apply. |
| Test data and doubles | Covered | `unittest.mock` and a shared factory replace `MockProxy`/`faker`; deterministic data is declared as the Python difference. |
| Execution and evidence | Covered | pytest is the reference runner; the project owns the command, as with Vitest. |
| Cross-stack parity | Covered | This table declares every semantic difference. |
| Open decisions | Covered | None; framework-specific adapters belong in a destination-owned guide. |

## Open decisions

None. A Python web framework, database library, or other framework-specific adapter may be documented in a destination-owned guide without changing the three levels or the shared rules.
