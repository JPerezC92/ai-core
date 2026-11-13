# Python testing guide

> **Status:** reference
> **Stack:** Python application, script, and CLI code; pytest reference implementation
> **Reviewed:** 2026-10-25 — `testing-architecture-layering`; entity-construction clause 2026-10-30; `architecture-agnostic-fallback` applicability and `T14`/`T24`–`T25` selection wording aligned to the agnostic fallback; the `T22`–`T23` and `T30`–`T36` `N/A` declaration was added and `T24`–`T25` cited as achieved; no `T` ID added, removed, moved or renumbered 2026-11-06; the parity table gained the `T9` and `T27` citations so both guides cite the same obligation set, reviewed 2026-11-06; 2026-11-12 — `T2`/`T4`/`T5`/`T10` applied to the file-organization, unit-test, integration-test and end-to-end sections: centralized root-level `tests/` placement, the approved unit targets with the parser/loader row kept at its original scope, an adapter against a real dependency isolated for its responsibility and the assembled CLI or service entry point; the three levels, the reference bindings and the observable assertions are unchanged, and no `T` ID was added, removed, moved or renumbered; 2026-11-12 — `T10` clarified to count test-owning units rather than repositories (ADR 0008): the single `tests/` directory sits at the unit's own root, which is the repository root for repository-wide tests or the package root for an independently deployable application, and the three levels, no-colocation rule and shared-support convention are unchanged; no `T` ID was added, removed, moved or renumbered
> **Contract:** `.aicore/core/architecture/testing/architecture.md`

## Applicability and ownership

This guide applies to Python application, script, and CLI code that follows the clean-architecture layers. The reference case is a skill suite: application operations, domain responsibilities, and infrastructure adapters live in importable packages, and an end-to-end test exercises the assembled entry point.

pytest is the reference runner. A destination owns its reviewed Python runner and configuration; a different runner uses its evidenced project-owned binding, retaining applicable mappings and using the agnostic contract for uncovered mechanisms rather than requiring a new guide (T20, T25). This guide does not cover a browser frontend, a JavaScript/TypeScript frontend, or a framework-specific adapter that has no selected guide. Uncovered concerns follow T24–T25; covered Python concerns retain their applicable mappings, without importing unrelated framework rules.

A destination may select a different Python runner, add a framework-specific adapter, or bind an isolated test database. It must preserve the contract rules this guide cites — `T1`–`T21` and `T24`–`T29` — which include the three levels (T2–T5), returned-business-failure classification (T6), one behavior per module and class (T11), factory-sourced test data (T15), hermeticity (T18), the separation of execution evidence from the verdict (T21), and the ownership of the reviewed test commands (T19). It must also keep T24–T25 routing an uncovered concern to the contract instead of inheriting this guide's mechanisms. T22–T23 and T30–T36 are declared N/A in the parity table below because they govern selection by a reviewer and the authoring of a new guide rather than this guide's content; T24–T25 are not N/A, because the applicability paragraph above and `Execution and evidence` route them.

## Test pyramid mapping

The three levels are the contract's; Python states their targets, doubles, and assertions as follows (T2–T5):

| Level | Target | Collaborators and doubles | Observable assertion |
|---|---|---|---|
| Unit | One application use-case class, or one parser/loader | Ports replaced with `unittest.mock` doubles or a small fake; the external parser library doubled for a parser | Returned values and returned domain errors |
| Unit — parser/loader | One parser or loader | External library mocked at its boundary | Mapping, coercion, extraction, and the documented failure result |
| Integration | One infrastructure adapter: repository, loader, builder, client, or parser | A real isolated store for a repository or persistence adapter; any other adapter against a real dependency isolated for its responsibility; the transport stubbed only for a capability that cannot be isolated | Raw external data to domain values |
| End to end | Assembled CLI or service entry point | Real adapters and composition | Exit status, output and the relevant effect |

Python does not add a fourth level (T1). A test that calls the CLI is not a unit test because the CLI is importable, and an in-memory adapter is not automatically a unit test (T4).

## File organization

- Every test lives under its test-owning unit's single `tests/` directory — the repository root for repository-wide tests, or the package root for an independently deployable application — in `tests/unit/`, `tests/integration/` or `tests/e2e/` (T10). No test module sits beside the module it exercises, and no test module lives inside a production package.
- Nested folders inside a level directory group tests by behavioural target and are chosen per project; this guide mandates none, and a role-named folder such as `parsers/`, `entities/`, `value_objects/` or `helpers/` is neither required nor approved as a level (T10).
- Test modules are named `test_*.py` and are collected project-wide by the project's reviewed runner. There is no per-subdirectory allowlist (T13).
- Shared factories, fixtures and test utilities live under the test root, for example `tests/support/`, and never inside a production package (T10).
- One behavior per test module and per class or group. A multi-behavior module or class is a violation and must be split by behavior (T11).
- A long `test_*.py` module holding one behavior stays whole and is never split by size (T12).
- Do not create an artificial use-case class just to satisfy a path or coverage expectation.

## Unit tests

- Instantiate the use-case class directly. Do not go through the CLI, an HTTP server, or the full composition root (T2).
- Call `execute()` directly. A domain object, value object or helper is exercised through the use case that owns the behaviour, not by an independent unit test of its own (T2).
- Replace each port with a `unittest.mock.Mock`/`MagicMock` or a small hand-written fake. `unittest.mock` is the suite's mocking library; do not add a second mocking library for the same job (T16).
- Assert the returned object with a direct `assert`; the domain error the operation returns is asserted by type, so no exception path is involved (T3):

```python
result = use_case.execute(command)
assert isinstance(result, TaskNotFoundError)
```

- Do not use `pytest.raises` to assert a returned business failure. Use it only for an expected exception at a boundary or a CLI `SystemExit` (T6, T7).
- Do not mock the use case under test. Mock or fake its ports (T17).
- Parser and loader unit tests mock the external library at its boundary and assert field mapping, type coercion, extraction, and the documented failure result. An empty or malformed input is a unit case when no real external service is needed.
- These tests must be compatible with the project's reviewed runner and discovery rules.

## Integration tests

- Instantiate the adapter directly with a real, isolated dependency: a temporary filesystem, an isolated test database, or a controlled local service (T4).
- Use `tmp_path` for filesystem work. Do not write into the repository or a developer's home directory (T18).
- When the dependency cannot be isolated, stub the transport boundary with `monkeypatch` or a small fake. Do not mock the adapter under test (T17).
- Assert the mapping pipeline: raw record or payload, adapter method, domain value. Cover defaults and null handling, and assert that a missing identifier returns the documented empty value rather than throwing.
- Do not use collaborator mocks here when the real isolated dependency is available. This level exists to test the real adapter boundary (T8).
- Each test owns the state it creates: `tmp_path` for every file and directory, plus the reviewed runner's fixture lifecycle for setup and teardown. Nothing carries over from an earlier test — not a file left under `tmp_path`, a row in the isolated test database, an environment variable set through `monkeypatch`, a stub installed at a transport boundary, or module-level process state (T18).
- Use the reviewed runner's isolation facilities; do not replace `tmp_path` with a shared temporary directory.

```python
def test_repository_returns_the_domain_entity(tmp_path):
    repository = OrderRepository(create_test_database(tmp_path))
    repository.save(Order.reconstitute(order_id=1, total=Money(100)))

    order = repository.find_by_id(1)

    assert isinstance(order, Order)
    assert order.id == 1
```

## End-to-end tests

- Exercise the assembled entry point: a CLI `main()` function, a service entry point, or the project's equivalent composition root (T5).
- Use real adapters with isolated data: `tmp_path` for files, an isolated test database for persistence, or a controlled local dependency.
- Assert the observable result at the entry point cumulatively: exit status, output and the relevant effect — the persisted file, the created record or the service response. Use `capsys` for captured CLI output when the reviewed runner provides it.
- Use `pytest.raises(SystemExit)` only for an expected CLI exit. Do not use it for a returned business failure (T6, T7).
- Do not call the use case directly in an end-to-end test; the assertion belongs to `main()` and the adapters it wires (T5).
- Do not duplicate every unit or integration case here. Cover the end-to-end path, its wiring, and its user-visible failure behavior (T8).

```python
def test_cli_validates_a_document(tmp_path, capsys):
    target = tmp_path / "report.md"
    target.write_text("# report\n")

    exit_code = main(["validate", "--target", str(target)])

    assert exit_code == 0
    assert "validated" in capsys.readouterr().out
    assert (tmp_path / "report.validated.md").exists()
```

## Test data and doubles

- Use a shared test-data factory or helper, for example `tests/support/_test_support.py`, for domain objects and external payloads. It lives under the test root as a supporting resource, never inside a production package (T10). Do not use inline literals for test data (T15).
- The factory provides `create(**overrides)` and, when collections are needed, `create_many(count, **overrides)`. Deterministic values are acceptable; randomness is not required.
- When the test needs an entity rather than a data-only record, the factory builds it through the entity factory/`create()`; never assign entity fields directly to construct test data.
- Use `unittest.mock` for collaborator ports and controlled return values (T16).
- Use `monkeypatch` for process-wide boundaries such as environment variables, time, or transport. Do not use `monkeypatch` as a substitute for a port double, and do not mix `monkeypatch` and `unittest.mock` for the same collaborator.
- Isolate each fixture with `tmp_path` for filesystem work and the reviewed runner's fixture lifecycle for setup and teardown, so no fixture reads a file another test wrote or module-level state another test left behind (T18).
- Do not use `unittest.TestCase` or `unittest.main()`. Use pytest test functions or non-`TestCase` classes with `test_*` methods.
- Use direct `assert` statements and the reviewed runner's assertion helpers. Do not hide the expected value behind a custom assertion DSL.

## Execution and evidence

- The project owns its reviewed whole-project Python command (T19). This guide does not authorize running tests or installing dependencies.
- Discovery is project-wide: a new `test_*.py` file joins the approved suite without a per-file grant or a subdirectory allowlist.
- Verdicts are issued from the reviewed test files; the reviewed command's `pytest` output is separate execution evidence and never the verdict itself (T21).
- Every feature-spec happy case and rejection case must trace to a test at the appropriate level.
- Report `[FAIL]` for a declared-review-scope file lacking required scoped test evidence. A concern outside this guide's coverage uses the contract's agnostic selection route, not an automatic `[UNCERTAIN]` verdict (T14, T25).
- The reviewed runner's configuration is the execution authority; the file locations above are reference layout, not a narrower execution grant.

## Cross-stack parity

| Contract section | Cited rule IDs | Language-specific achievement or N/A reason |
|---|---|---|
| Applicability and ownership | T20, T24, T25, T26 | Application, script, and CLI packages follow the layers; pytest is the reference runner and a destination selecting another runner uses its evidenced binding and retains applicable mappings, with uncovered mechanisms following the agnostic contract. Python has no browser frontend, so the frontend scope has no equivalent here, and an unselected adapter has no inferred runner or file convention — T24–T25 route it to the contract and the applicable implementation contract/shapes, so uncovered coverage alone never becomes an uncertainty verdict; the `reference` status records its review. |
| Test pyramid mapping | T1, T2, T3, T4, T5 | The three levels are instantiated with Python targets and no fourth level is added: one application use-case class with its ports doubled, one parser/loader, one adapter across its real boundary, and the assembled CLI or service entry point. The UI-specific frontend row has no Python equivalent. |
| File organization | T10, T11, T12, T13 | Every test lives under its test-owning unit's single `tests/` directory — the repository root for repository-wide tests, or the package root for an independently deployable application — in `tests/unit/`, `tests/integration/` or `tests/e2e/`, with behavioural grouping inside a level and no role-named folder mandated; `test_*.py` naming with project-wide discovery and no per-subdirectory allowlist; one behavior per module and per class, and a cohesive module is never split by size. |
| Unit tests | T2, T3, T6, T7, T16, T17 | The use-case class is instantiated directly and `execute()` is called; each port is replaced with `unittest.mock` or a small fake, a parser's external library is doubled at its boundary, and `pytest.raises` covers only a boundary exception or a CLI `SystemExit`, never a returned domain error. |
| Integration tests | T4, T8, T17, T18 | One adapter runs against a real isolated dependency — `tmp_path`, an isolated test database, or a controlled local service — with `monkeypatch` at the transport only for a capability that cannot be isolated. The residue classes are declared in the body: files under `tmp_path`, database rows, environment variables, transport stubs, and module-level state. |
| End-to-end tests | T5, T7, T8 | The assembled `main()` or service entry point runs with real adapters and isolated data, asserting exit status, `capsys` output and the relevant effect; unit and integration cases are not duplicated here. |
| Test data and doubles | T15, T16, T18 | A shared `_test_support.py` factory provides `create(**overrides)` and `create_many(...)` and builds entities through the entity factory; `unittest.mock` is the single mocking library, with `monkeypatch` reserved for process-wide boundaries such as environment variables, time, and transport. |
| Execution and evidence | T9, T14, T19, T21, T25 | The project owns the reviewed whole-project command and project-wide discovery; missing required evidence for a file in review scope is `[FAIL]`, uncovered mechanisms follow the contract's T25 agnostic selection route rather than an uncertainty verdict, and the run's output stays separate from the verdict. The verdict is issued from the reviewed `test_*.py` files, while a passing `pytest` run, a keyword or token presence check, or a coverage number stays execution or static evidence beside it and never conformance by itself. |
| Cross-stack parity | T27, T28, T29 | The guide keeps the contract's ten sections in order and declares every semantic difference in this table; a section with no Python mechanism would be marked `N/A` with its reason rather than thinned. This guide's own row in the contract's `## Stack guides` index records its `reference` status and parity evidence, and a change to this guide updates that index row and this table together. |
| Open decisions | T20, T22, T23, T30–T36 | No open decision is used to hide a missing rule; a Python web framework or database adapter may be documented in a destination-owned guide that adds no level and weakens no cited rule. T22–T23 and T30–T36 are N/A — they govern selection by a reviewer and new-guide authoring, not this guide's body; T24–T25 are achieved above, not N/A. |

## Open decisions

None. A Python web framework, database library, or other framework-specific adapter may be documented in a destination-owned guide without changing the three levels or the shared rules (T20).
